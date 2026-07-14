import os
import json

# Definição dinâmica de caminhos do projeto
current_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(current_dir) == "src":
    BASE_DIR = os.path.dirname(current_dir)
else:
    BASE_DIR = current_dir

DATA_DIR = os.path.join(BASE_DIR, "data")
AUTH_DIR = os.path.join(DATA_DIR, "auth")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
CONFIG_FILE = os.path.join(BASE_DIR, "config_app.json")

# Garante que as pastas básicas globais existam
for folder in [AUTH_DIR, REPORTS_DIR]:
    os.makedirs(folder, exist_ok=True)

def get_platform_dirs(plataforma):
    """
    Retorna os caminhos bronze, prata e ouro específicos de uma plataforma
    e garante que as respectivas pastas existam.
    """
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
# CONFIGURAÇÕES DE FILTRAGEM E RELEVÂNCIA (VIA JSON)
# ==========================================

DEFAULT_CONFIG = {
    "TERMOS_BUSCA": [
        "rim biscuit",
        "coração biscuit",
        "topo de bolo biscuit",
        "vela biscuit",
        "lembrancinha biscuit",
        "chaveiro biscuit",
        "cachorro biscuit",
        "biscuit pet",
        "boneco biscuit",
        "pessoa biscuit",
        "biscuit"
    ],
    "PALAVRA_OBRIGATORIA_GLOBAL": "",
    "PALAVRAS_NEGATIVAS": [
        "base acril", "bases acril", "base de acril", "bases de acril", "base para biscuit", "bases para biscuit",
        "base espelhad", "bases espelhad", "bolacha mdf", "bolachas mdf",
        "molde", "moldes", "forma de silicone", "formas de silicone", "forma para biscuit", "formas para biscuit",
        "cortador", "cortadores", "ejetor", "ejetores", "modelador", "modeladores",
        "cortar biscoito", "cortar biscuit", "cortar",
        "apostila", "curso", "passo a passo", "tutorial", "videoaula", "video aula",
        "cola para biscuit", "massa de biscuit", "massa para biscuit", "massas de biscuit", "massas para biscuit",
        "textura", "carimbo", "estojo de marcadores", "esteca", "estecas", "marcador", "marcadores", "regua", "reguas",
        "ferramenta", "ferramentas", "pitão", "pitao", "pitões", "pitoes", "olhinho", "olhinhos", "resina",
        "petisco", "formula natural", "dog biscuit", "dog biscuits", "biscuits",
        "impresso em 3d", "impressao 3d", "impressão 3d", "impressa em 3d", "impressora 3d", "fimo", "enchimento",
        "tapete", "tapetes",
        "feltro", "eva", "papelaria", "bauducco", "biscoito", "bolacha", "chocolate", "pla", "abs", "petg", "massa", "massas", "porcelana fria", "homeopatia", "medicamento", "remedio", "veterinario", "veterinaria", "mdf", "acrilico", "gesso", "cimento", "cerâmica", "ceramica", "pelúcia", "pelucia", "amigurumi", "crochê", "croche", "tampa de vaso", "assento", "livro", "livros", "pincel", "pinceis", "pincéis", "boleador", "boleadores"
    ],
    "MAX_PAGINAS": 1,
    "PALAVRAS_NEGATIVAS_EXATAS": [
        "racao", "racoes", "papel"
    ],
    "REGRAS_TIPO_PRODUTO": {
        "chaveiro": ["chaveir"],
        "lembrancinha": ["lembranc", "brinde", "mimo", "lembrac", "aplique"],
        "topo de bolo": ["topo", "bolo", "vela"]
    },
    "REGRAS_CONTEUDO_BUSCA": {
        "rim": ["rim", "rins", "pulmao", "órgão", "orgao"],
        "cora": ["coracao"],
        "cachorro": ["cachorr", "dog"],
        "pet": ["pet", "animal", "cachorr", "gato", "dog"]
    }
}

# Inicializa as configurações
def carregar_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=4)
        return DEFAULT_CONFIG
        
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar config.json: {e}")
        return DEFAULT_CONFIG

def salvar_config(nova_config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(nova_config, f, ensure_ascii=False, indent=4)

# Carrega na inicialização do módulo
config_atual = carregar_config()

TERMOS_BUSCA = config_atual.get("TERMOS_BUSCA", DEFAULT_CONFIG["TERMOS_BUSCA"])
PALAVRA_OBRIGATORIA_GLOBAL = config_atual.get("PALAVRA_OBRIGATORIA_GLOBAL", DEFAULT_CONFIG["PALAVRA_OBRIGATORIA_GLOBAL"])
PALAVRAS_NEGATIVAS = config_atual.get("PALAVRAS_NEGATIVAS", DEFAULT_CONFIG["PALAVRAS_NEGATIVAS"])
PALAVRAS_NEGATIVAS_EXATAS = config_atual.get("PALAVRAS_NEGATIVAS_EXATAS", DEFAULT_CONFIG["PALAVRAS_NEGATIVAS_EXATAS"])
REGRAS_TIPO_PRODUTO = config_atual.get("REGRAS_TIPO_PRODUTO", DEFAULT_CONFIG["REGRAS_TIPO_PRODUTO"])
REGRAS_CONTEUDO_BUSCA = config_atual.get("REGRAS_CONTEUDO_BUSCA", DEFAULT_CONFIG["REGRAS_CONTEUDO_BUSCA"])
MAX_PAGINAS = config_atual.get("MAX_PAGINAS", DEFAULT_CONFIG["MAX_PAGINAS"])