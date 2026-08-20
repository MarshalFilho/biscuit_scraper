import os
from datetime import datetime

from dotenv import load_dotenv

from supabase import Client, create_client

load_dotenv()

def conectar_supabase() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY (ou SUPABASE_SERVICE_ROLE_KEY) não configuradas.")
        
    return create_client(url, key)

def atualizar_status_scraper(user_id, status_mensagem):
    if not user_id:
        return
    try:
        supabase = conectar_supabase()
        supabase.table("configuracoes_scraper").update({"status_scraper": status_mensagem}).eq("user_id", user_id).execute()
    except Exception as e:
        print(f"⚠️ Erro ao atualizar status na nuvem: {e}")


def upsert_produto(supabase: Client, plataforma: str, id_externo: str, titulo: str, link: str, vendedor: str = None, user_id: str = None) -> str:
    """
    Verifica se o produto existe para aquele user_id. Se não, insere.
    Retorna o UUID do produto no banco.
    """
    query = supabase.table("produtos").select("id").eq("plataforma", plataforma)
    if user_id:
        query = query.eq("user_id", user_id)
        
    # 1. Verifica se já existe por id_externo
    response = query.eq("id_externo", id_externo).execute()
    
    # 2. Fallback por título se for um link de clique patrocinado
    if (not response.data or len(response.data) == 0) and titulo:
        query_title = supabase.table("produtos").select("id").eq("plataforma", plataforma)
        if user_id:
            query_title = query_title.eq("user_id", user_id)
        response = query_title.eq("titulo", titulo).execute()

    if response.data and len(response.data) > 0:
        produto_id = response.data[0]["id"]
        # Se recebemos vendedor e o registro antigo não tinha, atualiza
        if vendedor:
            supabase.table("produtos").update({"vendedor": vendedor}).eq("id", produto_id).execute()
        return produto_id
        
    # Se não existir, insere
    novo_produto = {
        "plataforma": plataforma,
        "id_externo": id_externo,
        "titulo": titulo,
        "link": link,
        "vendedor": vendedor,
        "criado_em": datetime.utcnow().isoformat()
    }
    
    if user_id:
        novo_produto["user_id"] = user_id
    
    # O Supabase retorna os dados inseridos
    res_insert = supabase.table("produtos").insert(novo_produto).execute()
    return res_insert.data[0]["id"]

def registrar_historico(supabase: Client, produto_id: str, preco: float, vendas_totais: int):
    """
    Adiciona uma nova entrada no histórico de coletas com a data atual.
    """
    hoje = datetime.utcnow().date().isoformat()
    
    # Verifica se já temos coleta para esse produto na data de hoje (para evitar duplicatas num mesmo dia)
    check = supabase.table("historico_coletas").select("id").eq("produto_id", produto_id).eq("data_coleta", hoje).execute()
    if check.data and len(check.data) > 0:
        # Atualiza a coleta de hoje se já existir
        historico_id = check.data[0]["id"]
        supabase.table("historico_coletas").update({
            "preco": preco,
            "vendas_totais": vendas_totais
        }).eq("id", historico_id).execute()
        return
        
    # Insere nova coleta
    novo_historico = {
        "produto_id": produto_id,
        "preco": preco,
        "vendas_totais": vendas_totais,
        "data_coleta": hoje
    }
    
    supabase.table("historico_coletas").insert(novo_historico).execute()
