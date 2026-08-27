import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.supabase_client import conectar_supabase


def deletar_produtos_sem_vendedor():
    """
    Remove do Supabase os produtos antigos que não possuem vendedor registrado.
    """
    try:
        supabase = conectar_supabase()
        print("🔍 Buscando produtos legados sem vendedor no Supabase...")
        
        # Seleciona produtos onde vendedor é null
        res = supabase.table("produtos").select("id, titulo, plataforma").is_("vendedor", "null").execute()
        produtos_sem_vendedor = res.data or []
        
        if not produtos_sem_vendedor:
            print("✨ Nenhum produto antigo sem vendedor encontrado no Supabase!")
            return

        print(f"⚠️ Encontrados {len(produtos_sem_vendedor)} produtos legados sem vendedor.")
        ids_para_deletar = [p["id"] for p in produtos_sem_vendedor]
        
        # 1. Deleta do historico_coletas primeiro (chave estrangeira)
        for p_id in ids_para_deletar:
            supabase.table("historico_coletas").delete().eq("produto_id", p_id).execute()
        print("🗑️ Histórico de coletas dos produtos antigos removido com sucesso!")
        
        # 2. Deleta da tabela produtos
        for p_id in ids_para_deletar:
            supabase.table("produtos").delete().eq("id", p_id).execute()
            
        print(f"🎉 {len(produtos_sem_vendedor)} produtos antigos sem vendedor foram excluídos do Supabase com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao deletar produtos antigos: {e}")

def deletar_todo_historico():
    """
    Reseta 100% dos dados de produtos e histórico no Supabase e limpa os arquivos locais da pasta data/.
    """
    try:
        supabase = conectar_supabase()
        print("⚠️ Zerando tabelas no Supabase (historico_coletas e produtos)...")
        supabase.table("historico_coletas").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        supabase.table("produtos").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print("🧹 Banco de dados do Supabase zerado com sucesso!")
        
        # Limpa arquivos locais na pasta data/
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(os.path.dirname(base_dir), "data")
        
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                if file.endswith((".html", ".json")) and file not in ["auth.json", "auth_shopee.json"]:
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass
        print("🧹 Arquivos locais de raspagem (HTMLs e JSONs) removidos com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao zerar historico: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--reset-total":
        deletar_todo_historico()
    else:
        deletar_produtos_sem_vendedor()
