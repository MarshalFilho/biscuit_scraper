import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')
from dotenv import load_dotenv

load_dotenv()

# Definição dinâmica de caminhos do projeto
current_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(current_dir) in ["src", "backend"]:
    BASE_DIR = os.path.dirname(current_dir)
else:
    BASE_DIR = current_dir

DATA_DIR = os.path.join(BASE_DIR, "data")
AUTH_DIR = os.path.join(DATA_DIR, "auth")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# Garante que as pastas básicas globais existam
for folder in [AUTH_DIR, REPORTS_DIR]:
    os.makedirs(folder, exist_ok=True)

def get_platform_dirs(plataforma):
    plat_dir = os.path.join(DATA_DIR, plataforma)
    dirs = {
        "bronze": os.path.join(plat_dir, "bronze"),
        "prata": os.path.join(plat_dir, "prata"),
        "ouro": os.path.join(plat_dir, "ouro")
    }
    for folder in dirs.values():
        os.makedirs(folder, exist_ok=True)
    return dirs

# ==========================================
# CONFIGURAÇÕES DE FILTRAGEM (NUVEM)
# ==========================================

DEFAULT_CONFIG = {
    "termos_busca": ["meu produto teste"],
    "blacklist": ["termo_indesejado"],
    "palavras_negativas_exatas": ["racao", "racoes", "papel"],
    "regras_tipo_produto": {},
    "regras_conteudo_busca": {},
    "palavra_obrigatoria_global": "",
    "max_paginas": 1
}

config_atual = DEFAULT_CONFIG.copy()

def recarregar_config():
    """
    Conecta ao Supabase e baixa as configurações ativas da Nuvem.
    Chamado a cada ciclo do daemon antes de iniciar o scrape.
    """
    global config_atual
    user_id = os.environ.get("SUPABASE_USER_ID")
    
    if not user_id:
        print("⚠️ AVISO: Variável SUPABASE_USER_ID ausente no .env. Executando com configurações locais de teste.")
        return config_atual
        
    try:
        from utils.supabase_client import conectar_supabase
        supabase = conectar_supabase()
        response = supabase.table("configuracoes_scraper").select("termos_busca, blacklist, regras_categoria").eq("user_id", user_id).execute()
        
        if response.data and len(response.data) > 0:
            data = response.data[0]
            config_atual["termos_busca"] = data.get("termos_busca", DEFAULT_CONFIG["termos_busca"])
            config_atual["blacklist"] = data.get("blacklist", DEFAULT_CONFIG["blacklist"])
            
            # Aqui podemos mapear regras de categoria do JSON para algo compatível no backend, 
            # se necessitar regras complexas, mas inicialmente usamos as default de teste
            # ou injetamos na pipeline.
            print("✅ Configurações dinâmicas injetadas com sucesso a partir do Supabase.")
        else:
            print("⚠️ AVISO: Nenhuma linha encontrada na tabela configuracoes_scraper para o seu user_id.")
            
    except Exception as e:
        print(f"❌ Erro ao baixar configurações do Supabase: {e}")
        
    return config_atual

# Carrega na inicialização padrão
recarregar_config()

# Funções Getters Dinâmicas para os Scrapers
def get_nome_projeto(): return config_atual.get("nome_projeto", "Market Scraper Pro")
def get_nicho_atual(): return config_atual.get("nicho_atual", "biscuit")
def get_termos_busca(): return config_atual["termos_busca"]
def get_blacklist(): return config_atual["blacklist"]
def get_produtos_bloqueados(): return config_atual.get("blocked_products", [])
def get_palavras_negativas_exatas(): return config_atual["palavras_negativas_exatas"]
def get_regras_tipo_produto(): return config_atual["regras_tipo_produto"]
def get_regras_conteudo_busca(): return config_atual["regras_conteudo_busca"]
def get_palavra_obrigatoria_global(): return config_atual["palavra_obrigatoria_global"]
def get_max_paginas(): return config_atual["max_paginas"]