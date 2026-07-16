import sys
import os
import argparse
import time

# Permite importação dos módulos da pasta src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config

def executar_scrapers(plataforma):
    if plataforma in ["meli", "todos"]:
        print("\n=== Executando Scraper Mercado Livre ===")
        from scrapers.meli_scraper import fase_bronze, fase_prata, fase_ouro
        fase_bronze()
        fase_prata()
        fase_ouro()
        
    if plataforma in ["shopee", "todos"]:
        print("\n=== Executando Scraper Shopee ===")
        from scrapers.shopee_scraper import fase_bronze, fase_prata, fase_ouro
        fase_bronze()
        fase_prata()
        fase_ouro()

def main():
    parser = argparse.ArgumentParser(description="Pipeline de Inteligência e Extração para Biscuit")
    parser.add_argument("--plataforma", choices=["meli", "shopee", "todos"], default="todos",
                        help="Plataforma de e-commerce a raspar (padrão: todos)")
    parser.add_argument("--login", action="store_true", help="Executar ferramenta para salvar login manual do ML")
    parser.add_argument("--login-shopee", action="store_true", help="Executar ferramenta para salvar login manual da Shopee")
    parser.add_argument("--daemon", action="store_true", help="Modo Polling Contínuo escutando Supabase")
    
    args = parser.parse_args()
    
    if args.login:
        from utils.salvar_login import gerar_sessao
        gerar_sessao("meli")
        return

    if args.login_shopee:
        from utils.salvar_login import gerar_sessao
        gerar_sessao("shopee")
        return
        
    if args.daemon:
        from utils.supabase_client import conectar_supabase
        
        print("\n🎧 Modo Daemon ativado. Escutando a nuvem (Supabase)...")
        user_id = os.environ.get("SUPABASE_USER_ID")
        if not user_id:
            print("❌ ERRO: SUPABASE_USER_ID não encontrado no .env. Não é possível rodar o daemon.")
            return

        try:
            supabase = conectar_supabase()
        except Exception as e:
            print(f"❌ Erro ao conectar no Supabase: {e}")
            return
            
        while True:
            try:
                print(f"\n[{time.strftime('%H:%M:%S')}] Checando status de disparo_pendente para usuário: {user_id}...")
                response = supabase.table("configuracoes_scraper").select("disparo_pendente").eq("user_id", user_id).execute()
                
                if response.data and len(response.data) > 0:
                    pendente = response.data[0].get("disparo_pendente", False)
                    if pendente:
                        print("🚀 DISPARO PENDENTE DETECTADO! Iniciando extração...")
                        
                        # 1. Recarrega as configurações dinâmicas mais recentes
                        config.recarregar_config()
                        
                        # 2. Roda os scrapers
                        executar_scrapers(args.plataforma)
                            
                        print("\n✅ Extração concluída. Atualizando status na nuvem...")
                        # 3. Reseta o status
                        supabase.table("configuracoes_scraper").update({"disparo_pendente": False}).eq("user_id", user_id).execute()
                        print("✅ Status resetado. Aguardando novo comando...")
                    else:
                        print("💤 Nenhum disparo pendente. Dormindo...")
                else:
                    print("⚠️ Usuário não encontrado na tabela configuracoes_scraper. Verifique seu ID.")
                    
            except Exception as e:
                print(f"❌ Erro no loop do daemon: {e}")
                
            # Dorme por 5 minutos (300 segundos)
            time.sleep(300)
            
    else:
        # Modo execução única e manual (sem escutar Nuvem)
        print("\n⚙️ Modo de Execução Única Manual.")
        config.recarregar_config()
        executar_scrapers(args.plataforma)

if __name__ == "__main__":
    main()
