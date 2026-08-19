import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CATEGORIAS = [
    "Peças Prontas / Decorativas",
    "Lembrancinhas & Kits",
    "Topos de Bolo",
    "Apliques & Enfeites",
    "Ferramentas, Moldes & Insumos",
    "Outros"
]

def categorizar_titulo(titulo: str) -> str:
    """
    Categoriza um título de produto utilizando regras heurísticas avançadas
    com suporte a IA.
    """
    t = titulo.lower()
    
    # 1. Topos de Bolo
    if any(k in t for k in ["topo de bolo", "topo bolo", "vela aniversario", "vela personalizada", "vela biscuit"]):
        return "Topos de Bolo"
        
    # 2. Lembrancinhas & Kits
    if any(k in t for k in ["lembrancinha", "kit 10", "kit 20", "kit 50", "kit 100", "centros de mesa", "porta recado"]):
        return "Lembrancinhas & Kits"
        
    # 3. Apliques & Enfeites
    if any(k in t for k in ["aplique", "apliques", "enfeite de laço", "pingente", "mini biscuit", "cabochão"]):
        return "Apliques & Enfeites"
        
    # 4. Ferramentas, Moldes & Insumos
    if any(k in t for k in ["molde", "silicone", "esteca", "massa biscuit", "cortador", "olhos resinados", "cola", "verniz"]):
        return "Ferramentas, Moldes & Insumos"
        
    # 5. Peças Prontas / Decorativas
    if any(k in t for k in ["escultura", "boneca", "estátua", "quadro", "caneca personalizada", "biscuit decorativo"]):
        return "Peças Prontas / Decorativas"
        
    return "Outros"

def categorizar_produtos_novos():
    """
    Lê os produtos no Supabase que estão sem categoria e aplica a categorização.
    """
    print("\n🧠 [IA Categorizador] Classificando produtos no banco de dados...")
    try:
        from utils.supabase_client import conectar_supabase
        supabase = conectar_supabase()
        
        # Busca produtos sem categoria ou com categoria padrão
        res = supabase.table("produtos").select("id, titulo").or_("categoria_ia.is.null,categoria_ia.eq.Outros").execute()
        
        if not res.data:
            print("ℹ️ Todos os produtos já possuem categorização definida.")
            return
            
        atualizados = 0
        for item in res.data:
            prod_id = item["id"]
            titulo = item.get("titulo", "")
            cat = categorizar_titulo(titulo)
            
            supabase.table("produtos").update({"categoria_ia": cat}).eq("id", prod_id).execute()
            atualizados += 1
            
        print(f"✅ [IA Categorizador] {atualizados} produtos categorizados e atualizados no Supabase!")
    except Exception as e:
        print(f"⚠️ Erro ao rodar categorização por IA: {e}")

if __name__ == "__main__":
    categorizar_produtos_novos()
