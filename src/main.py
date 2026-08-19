import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')
import argparse
import json
import time

# Permite importação dos módulos da pasta src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import structlog

import config

logger = structlog.get_logger()

def sincronizar_sessao_nuvem(user_id):
    """
    Se o usuário salvou o auth.json no Supabase, baixa para a pasta data/auth local.
    """
    try:
        from utils.supabase_client import conectar_supabase
        supabase = conectar_supabase()
        res = supabase.table("configuracoes_scraper").select("auth_state_meli, modo_paginacao").eq("user_id", user_id).execute()
        if res.data and len(res.data) > 0:
            row = res.data[0]
            auth_json = row.get("auth_state_meli")
            modo = row.get("modo_paginacao", "anonimo")
            
            if auth_json:
                os.makedirs(config.AUTH_DIR, exist_ok=True)
                auth_path = os.path.join(config.AUTH_DIR, "auth.json")
                with open(auth_path, "w", encoding="utf-8") as f:
                    json.dump(auth_json, f, indent=2)
                print("🔑 [Nuvem] Sessão de login 'auth.json' baixada do Supabase com sucesso!")
            
            if modo == "anonimo":
                logger.info("auth_sync", status="success", mode="anonimo", msg="Modo Anônimo ativado (Limites: 1 página por busca).")
            else:
                logger.info("auth_sync", status="success", mode="logado", msg="Modo Logado ativado (Múltiplas páginas ativadas).")
    except Exception as e:
        logger.error("auth_sync_error", error=str(e))

def executar_scrapers(plataforma, user_id, rodar_ia=True):
    from utils.bot_detector import BotDetectionError
    from utils.supabase_client import atualizar_status_scraper
    
    try:
        if plataforma in ["meli", "todos"]:
            print("\n=== Executando Scraper Mercado Livre ===")
            atualizar_status_scraper(user_id, "🛒 Mercado Livre [1/3]: Acessando as páginas da web...")
            from scrapers.meli_scraper import fase_bronze, fase_ouro, fase_prata
            fase_bronze()
            
            atualizar_status_scraper(user_id, "🛒 Mercado Livre [2/3]: Processando a estrutura dos anúncios...")
            fase_prata()
            
            atualizar_status_scraper(user_id, "🛒 Mercado Livre [3/3]: Extraindo produtos e enviando ao Supabase...")
            fase_ouro()
            
        if plataforma in ["shopee", "todos"]:
            print("\n=== Executando Scraper Shopee ===")
            atualizar_status_scraper(user_id, "🧡 Shopee [1/3]: Acessando as páginas da web...")
            from scrapers.shopee_scraper import fase_bronze, fase_ouro, fase_prata
            fase_bronze()
            
            atualizar_status_scraper(user_id, "🧡 Shopee [2/3]: Processando a estrutura dos anúncios...")
            fase_prata()
            
            atualizar_status_scraper(user_id, "🧡 Shopee [3/3]: Extraindo produtos e enviando ao Supabase...")
            fase_ouro()
    except BotDetectionError as e:
        logger.critical("bot_detection", error=e.mensagem)
        sys.exit(1)

    if rodar_ia:
        print("\n=== Executando Módulos de IA ===")
        atualizar_status_scraper(user_id, "🧠 IA: Categorizando produtos e gerando insights...")
        try:
            from ai.categorizer import categorizar_produtos_novos
            categorizar_produtos_novos()
        except Exception as e:
            print(f"⚠️ Aviso na categorização por IA: {e}")

        try:
            from utils.ai_engine import gerar_relatorio_ia_executivo
            gerar_relatorio_ia_executivo()
        except Exception as e:
            logger.warning("ai_report_error", error=str(e))

def main():
    parser = argparse.ArgumentParser(description="Pipeline de Inteligência e Extração para E-commerce")
    parser.add_argument("--plataforma", choices=["meli", "shopee", "todos"], default="todos",
                        help="Plataforma de e-commerce a raspar (padrão: todos)")
    parser.add_argument("--daemon", action="store_true", help="Modo Polling Contínuo escutando Supabase")
    parser.add_argument("--cloud", action="store_true", help="Modo One-Shot para rodar no GitHub Actions")
    parser.add_argument("--login", action="store_true", help="Abre o navegador visível para validar verificação/login inicial")
    
    args = parser.parse_args()
    
    if args.login:
        from scrapers.login_session import (
            inicializar_sessao_mercadolivre,
            inicializar_sessao_shopee,
        )
        inicializar_sessao_mercadolivre()
        inicializar_sessao_shopee()
        return
    
    if args.daemon:
        from utils.supabase_client import atualizar_status_scraper, conectar_supabase
        
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
                        atualizar_status_scraper(user_id, "🤖 Robô acordou na Nuvem! Baixando preferências...")
                        
                        sincronizar_sessao_nuvem(user_id)
                        config.recarregar_config()
                        executar_scrapers(args.plataforma, user_id)
                            
                        print("\n✅ Extração concluída. Atualizando status na nuvem...")
                        supabase.table("configuracoes_scraper").update({
                            "disparo_pendente": False,
                            "status_scraper": "🎉 Raspagem concluída com sucesso!"
                        }).eq("user_id", user_id).execute()
                        print("✅ Status resetado. Aguardando novo comando...")
                        
                        time.sleep(6)
                        supabase.table("configuracoes_scraper").update({"status_scraper": None}).eq("user_id", user_id).execute()
                    else:
                        print("💤 Nenhum disparo pendente. Dormindo...")
                else:
                    print("⚠️ Nenhuma configuração encontrada para este usuário.")
                    
            except Exception as e:
                print(f"❌ Erro no loop do daemon: {e}")
                
            time.sleep(300)
            
    elif args.cloud:
        # MODO ONE-SHOT / CHECAGEM DE NUVEM (GitHub Actions)
        print("\n☁️ Modo Nuvem (GitHub Actions) ativado. Verificando agendamento...")
        user_id = os.environ.get("SUPABASE_USER_ID")
        if not user_id:
            print("❌ ERRO: SUPABASE_USER_ID não configurado no ambiente. Abortando.")
            return

        from utils.supabase_client import atualizar_status_scraper, conectar_supabase
        try:
            supabase = conectar_supabase()
            res = supabase.table("configuracoes_scraper").select("disparo_pendente").eq("user_id", user_id).execute()
            
            if res.data and len(res.data) > 0:
                pendente = res.data[0].get("disparo_pendente", False)
                if not pendente:
                    print("💤 Nenhum disparo pendente no Supabase. Encerrando execução em nuvem graciosamente sem raspar.")
                    return
            else:
                print("⚠️ Nenhuma linha de configuração encontrada no Supabase para este usuário. Encerrando.")
                return
        except Exception as e:
            print(f"⚠️ Erro ao checar disparo pendente no Supabase: {e}")
            return

        print("🚀 DISPARO PENDENTE DETECTADO NO SUPABASE! Iniciando pipeline de extração...")
        atualizar_status_scraper(user_id, "🤖 Robô acordou no GitHub Actions! Sincronizando sessão...")
        
        sincronizar_sessao_nuvem(user_id)
        config.recarregar_config()
        executar_scrapers(args.plataforma, user_id)
        
        print("\n✅ Extração na nuvem concluída.")
        try:
            supabase.table("configuracoes_scraper").update({
                "disparo_pendente": False,
                "status_scraper": "🎉 Raspagem concluída com sucesso!"
            }).eq("user_id", user_id).execute()
            
            time.sleep(6)
            supabase.table("configuracoes_scraper").update({"status_scraper": None}).eq("user_id", user_id).execute()
        except Exception as e:
            print(f"Erro ao finalizar status no Supabase: {e}")
            
    else:
        # Modo execução única e manual local
        print("\n⚙️ Modo de Execução Única Manual Local.")
        config.recarregar_config()
        executar_scrapers(args.plataforma, None)

if __name__ == "__main__":
    main()
