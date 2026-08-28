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

def atualizar_status_scraper(user_id, status_mensagem, status_alerta=None):
    if not user_id:
        return
    try:
        supabase = conectar_supabase()
        payload = {"status_scraper": status_mensagem}
        if status_alerta is not None:
            payload["status_alerta"] = status_alerta
        supabase.table("configuracoes_scraper").update(payload).eq("user_id", user_id).execute()
    except Exception as e:
        print(f"⚠️ Erro ao atualizar status na nuvem: {e}")

def listar_tenants_ativos(supabase: Client = None):
    """
    Retorna lista de todos os tenants/usuários cadastrados com configurações no Supabase.
    Possui fallback seguro caso a coluna nicho_mercado ainda não exista.
    """
    client = supabase or conectar_supabase()
    try:
        res = client.table("configuracoes_scraper").select("user_id, nome_projeto, nicho_mercado, termos_busca, blacklist, modo_paginacao").execute()
        return res.data or []
    except Exception:
        try:
            res = client.table("configuracoes_scraper").select("user_id, nome_projeto, termos_busca, blacklist, modo_paginacao").execute()
            return res.data or []
        except Exception as e2:
            print(f"⚠️ Erro ao listar tenants ativos no Supabase: {e2}")
            return []

def registrar_alerta_antibot(user_id: str, plataforma: str, mensagem: str, screenshot_path: str = None, supabase: Client = None):
    """
    Registra um alerta de Anti-Bot / CAPTCHA no Supabase para notificar o Dashboard.
    """
    if not user_id:
        return
    try:
        client = supabase or conectar_supabase()
        agora = datetime.utcnow().strftime("%d/%m/%Y às %H:%M UTC")
        alerta_obj = {
            "tipo": "antibot_detected",
            "plataforma": plataforma,
            "mensagem": f"⚠️ [{plataforma.upper()}] {mensagem} ({agora})",
            "data": agora,
            "screenshot_path": screenshot_path or None
        }
        client.table("configuracoes_scraper").update({
            "status_alerta": alerta_obj,
            "status_scraper": f"⚠️ Pausado por Anti-Bot na {plataforma.upper()} em {agora}"
        }).eq("user_id", user_id).execute()
        print(f"🚨 [Alerta] Anti-bot registrado no Supabase para o usuário {user_id}!")
    except Exception as e:
        print(f"⚠️ Erro ao registrar alerta de anti-bot no Supabase: {e}")

def upsert_produto(supabase: Client, plataforma: str, id_externo: str, titulo: str, link: str, vendedor: str = None, user_id: str = None) -> str:
    """
    Verifica se o produto existe para aquele user_id. Se não, insere.
    Retorna o UUID do produto no banco.
    """
    effective_user_id = user_id or os.environ.get("CURRENT_USER_ID") or os.environ.get("SUPABASE_USER_ID")
    
    query = supabase.table("produtos").select("id").eq("plataforma", plataforma)
    if effective_user_id:
        query = query.eq("user_id", effective_user_id)
        
    # 1. Verifica se já existe por id_externo
    response = query.eq("id_externo", id_externo).execute()
    
    # 2. Fallback por título se for um link de clique patrocinado
    if (not response.data or len(response.data) == 0) and titulo:
        query_title = supabase.table("produtos").select("id").eq("plataforma", plataforma)
        if effective_user_id:
            query_title = query_title.eq("user_id", effective_user_id)
        response = query_title.eq("titulo", titulo).execute()

    if response.data and len(response.data) > 0:
        produto_id = response.data[0]["id"]
        if vendedor:
            supabase.table("produtos").update({"vendedor": vendedor}).eq("id", produto_id).execute()
        return produto_id
        
    novo_produto = {
        "plataforma": plataforma,
        "id_externo": id_externo,
        "titulo": titulo,
        "link": link,
        "vendedor": vendedor,
        "criado_em": datetime.utcnow().isoformat()
    }
    
    if effective_user_id:
        novo_produto["user_id"] = effective_user_id
    
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
