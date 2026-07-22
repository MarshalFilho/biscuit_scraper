import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def conectar_supabase() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não configuradas.")
        
    return create_client(url, key)

def atualizar_status_scraper(user_id, status_mensagem):
    try:
        supabase = conectar_supabase()
        supabase.table("configuracoes_scraper").update({"status_scraper": status_mensagem}).eq("user_id", user_id).execute()
    except Exception as e:
        print(f"⚠️ Erro ao atualizar status na nuvem: {e}")


def upsert_produto(supabase: Client, plataforma: str, id_externo: str, titulo: str, link: str) -> str:
    """
    Verifica se o produto existe. Se não, insere.
    Retorna o UUID do produto no banco.
    """
    # Verifica se já existe
    response = supabase.table("produtos").select("id").eq("plataforma", plataforma).eq("id_externo", id_externo).execute()
    
    if response.data and len(response.data) > 0:
        return response.data[0]["id"]
        
    # Se não existir, insere
    novo_produto = {
        "plataforma": plataforma,
        "id_externo": id_externo,
        "titulo": titulo,
        "link": link,
        "criado_em": datetime.utcnow().isoformat()
    }
    
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
