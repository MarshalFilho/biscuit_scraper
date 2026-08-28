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
            
            if modo == "anonimo":
                auth_path = os.path.join(config.AUTH_DIR, "auth.json")
                if os.path.exists(auth_path):
                    try: os.remove(auth_path)
                    except: pass
                auth_meli_path = os.path.join(config.AUTH_DIR, "auth_meli.json")
                if os.path.exists(auth_meli_path):
                    try: os.remove(auth_meli_path)
                    except: pass
                logger.info("auth_sync", status="success", mode="anonimo", msg="Modo Anônimo Limpo ativado (Cookies limpos para evitar WAF).")
            else:
                if auth_json:
                    os.makedirs(config.AUTH_DIR, exist_ok=True)
                    auth_path = os.path.join(config.AUTH_DIR, "auth.json")
                    with open(auth_path, "w", encoding="utf-8") as f:
                        json.dump(auth_json, f, indent=2)
                    print("🔑 [Nuvem] Sessão de login 'auth.json' baixada do Supabase com sucesso!")
                logger.info("auth_sync", status="success", mode="logado", msg="Modo Logado ativado (Múltiplas páginas ativadas).")
    except Exception as e:
        logger.error("auth_sync_error", error=str(e))

def executar_scrapers(plataforma, user_id, rodar_ia=True):
    from utils.bot_detector import BotDetectionError
    from utils.supabase_client import atualizar_status_scraper, registrar_alerta_antibot
    
    agora_str = time.strftime('%d/%m/%Y às %H:%M')
    
    if plataforma in ["meli", "todos"]:
        try:
            print("\n=== Executando Scraper Mercado Livre ===")
            atualizar_status_scraper(user_id, "🛒 Mercado Livre [1/3]: Acessando as páginas da web...")
            from scrapers.meli_scraper import fase_bronze, fase_ouro, fase_prata
            fase_bronze()
            
            atualizar_status_scraper(user_id, "🛒 Mercado Livre [2/3]: Processando a estrutura dos anúncios...")
            fase_prata()
            
            atualizar_status_scraper(user_id, "🛒 Mercado Livre [3/3]: Extraindo produtos e enviando ao Supabase...")
            fase_ouro(user_id=user_id)
        except BotDetectionError as e:
            print(f"🚨 [Anti-Bot] Bloqueio detectado no Mercado Livre: {e.mensagem}")
            registrar_alerta_antibot(user_id, "meli", e.mensagem)
        except Exception as e:
            print(f"⚠️ Erro inesperado no scraper do Mercado Livre: {e}")
        
    if plataforma in ["shopee", "todos"]:
        try:
            print("\n=== Executando Scraper Shopee ===")
            atualizar_status_scraper(user_id, "🧡 Shopee [1/3]: Acessando as páginas da web...")
            from scrapers.shopee_scraper import fase_bronze, fase_ouro, fase_prata
            fase_bronze()
            
            atualizar_status_scraper(user_id, "🧡 Shopee [2/3]: Processando a estrutura dos anúncios...")
            fase_prata()
            
            atualizar_status_scraper(user_id, "🧡 Shopee [3/3]: Extraindo produtos e enviando ao Supabase...")
            fase_ouro(user_id=user_id)
        except BotDetectionError as e:
            print(f"🚨 [Anti-Bot] Bloqueio detectado na Shopee: {e.mensagem}")
            registrar_alerta_antibot(user_id, "shopee", e.mensagem)
        except Exception as e:
            print(f"⚠️ Erro inesperado no scraper da Shopee: {e}")

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
            gerar_relatorio_ia_executivo(user_id=user_id)
            atualizar_status_scraper(user_id, f"✅ Coleta diária finalizada com sucesso em {agora_str}")
        except Exception as e:
            logger.warning("ai_report_error", error=str(e))

def main():
    parser = argparse.ArgumentParser(description="Pipeline de Inteligência e Extração para E-commerce")
    parser.add_argument("--plataforma", choices=["meli", "shopee", "todos"], default="todos",
                        help="Plataforma de e-commerce a raspar (padrão: todos)")
    parser.add_argument("--daily-cron", action="store_true", help="Executa a rotina agendada diária para todos os clientes ativos")
    parser.add_argument("--daemon", action="store_true", help="Modo Polling Contínuo escutando Supabase")
    parser.add_argument("--cloud", action="store_true", help="Modo One-Shot para rodar no GitHub Actions")
    parser.add_argument("--login", action="store_true", help="Abre o navegador visível para validar verificação/login inicial")
    parser.add_argument("--user-id", type=str, help="Executa o scraper para um usuário específico do Supabase")
    
    args = parser.parse_args()
    
    if args.login:
        from scrapers.login_session import (
            inicializar_sessao_mercadolivre,
            inicializar_sessao_shopee,
        )
        inicializar_sessao_mercadolivre()
        inicializar_sessao_shopee()
        return

    if args.daily_cron:
        print("\n⏰ [Cron Diário Nuvem] Iniciando rotina diária de coleta automatizada...")
        from utils.supabase_client import conectar_supabase, listar_tenants_ativos
        
        try:
            supabase = conectar_supabase()
            tenants = listar_tenants_ativos(supabase)
        except Exception as e:
            print(f"⚠️ Erro ao conectar no Supabase para buscar tenants: {e}")
            tenants = []

        if not tenants:
            fallback_user_id = os.environ.get("SUPABASE_USER_ID", "693b19e1-936e-4322-ac9a-79467d143566")
            print(f"ℹ️ Nenhum tenant listado dinamicamente. Executando com fallback para o tenant padrão ({fallback_user_id}).")
            tenants = [{"user_id": fallback_user_id, "nome_projeto": "Projeto Padrão"}]

        print(f"📊 Total de clientes/tenants a processar: {len(tenants)}")
        for idx, tenant in enumerate(tenants, 1):
            user_id = tenant.get("user_id")
            nome = tenant.get("nome_projeto") or f"Tenant #{idx}"
            print(f"\n──────────────────────────────────────────────")
            print(f"🚀 [{idx}/{len(tenants)}] Processando Cliente: {nome} ({user_id})")
            print(f"──────────────────────────────────────────────")
            
            os.environ["CURRENT_USER_ID"] = user_id
            sincronizar_sessao_nuvem(user_id)
            config.recarregar_config()
            executar_scrapers(args.plataforma, user_id)
            time.sleep(2)

        print("\n🎉 [Cron Diário Nuvem] Todos os clientes foram processados com sucesso!")
        return
    
    if args.daemon:
        from datetime import date
        from utils.supabase_client import atualizar_status_scraper, conectar_supabase, listar_tenants_ativos
        
        print("\n" + "=" * 70)
        print("🎧 [MarketPulse AI] Worker Local Ativo & Monitorando em Segundo Plano")
        print("=" * 70)
        print("⚡ Resposta Imediata: Escutando cliques de 'Disparar Raspagem' da Vercel")
        print("⏰ Agendamento Diário: Coleta automática programada para todos os dias às 22:00")
        print("🛡️ IP Residencial: Raspagem limpa e veloz sem bloqueios de WAF / Datacenter")
        print("=" * 70 + "\n", flush=True)

        user_id = os.environ.get("SUPABASE_USER_ID", "693b19e1-936e-4322-ac9a-79467d143566")
        try:
            supabase = conectar_supabase()
        except Exception as e:
            print(f"❌ Erro ao conectar no Supabase: {e}")
            return

        ultimo_dia_cron = None

        while True:
            try:
                agora_hora = time.strftime('%H:%M')
                hoje = date.today()

                # 1. DISPARO AGENDADO DIÁRIO ÀS 22:00
                if agora_hora == "22:00" and ultimo_dia_cron != hoje:
                    print(f"\n⏰ [22:00] HORÁRIO PROGRAMADO ATINGIDO! Iniciando Coleta Diária Automática...", flush=True)
                    ultimo_dia_cron = hoje
                    
                    tenants = listar_tenants_ativos(supabase)
                    if not tenants:
                        tenants = [{"user_id": user_id, "nome_projeto": "Projeto Principal"}]

                    for idx, t in enumerate(tenants, 1):
                        t_user_id = t.get("user_id")
                        t_nome = t.get("nome_projeto") or f"Tenant #{idx}"
                        print(f"🚀 [{idx}/{len(tenants)}] Executando Coleta Agendada para: {t_nome}...")
                        os.environ["CURRENT_USER_ID"] = t_user_id
                        sincronizar_sessao_nuvem(t_user_id)
                        config.recarregar_config()
                        executar_scrapers(args.plataforma, t_user_id)

                    print("🎉 [22:00] Coleta diária das 22h concluída para todos os clientes!", flush=True)

                # 2. DISPARO INSTANTÂNEO SOB DEMANDA (CLIQUES NO DASHBOARD VERCEL)
                response = supabase.table("configuracoes_scraper").select("user_id, nome_projeto, disparo_pendente").eq("disparo_pendente", True).execute()
                
                if response.data and len(response.data) > 0:
                    for row in response.data:
                        target_user_id = row.get("user_id")
                        nome_cli = row.get("nome_projeto") or "Cliente"
                        print(f"\n🚀 [DISPARO INSTANTÂNEO DETECTADO] Solicitado pelo Dashboard para: {nome_cli} ({target_user_id})!", flush=True)
                        
                        atualizar_status_scraper(target_user_id, "🤖 Robô Local acordou! Sincronizando e iniciando extração...")
                        os.environ["CURRENT_USER_ID"] = target_user_id
                        sincronizar_sessao_nuvem(target_user_id)
                        config.recarregar_config()
                        executar_scrapers(args.plataforma, target_user_id)
                        
                        print(f"\n✅ Extração concluída para {nome_cli}. Atualizando status no Supabase...", flush=True)
                        supabase.table("configuracoes_scraper").update({
                            "disparo_pendente": False,
                            "status_scraper": "🎉 Raspagem e IA concluídas com sucesso!"
                        }).eq("user_id", target_user_id).execute()
                        
                        time.sleep(5)
                        supabase.table("configuracoes_scraper").update({"status_scraper": None}).eq("user_id", target_user_id).execute()
                
            except Exception as e:
                print(f"⚠️ Erro no loop do daemon: {e}", flush=True)
                
            time.sleep(10)
            
    else:
        user_id = args.user_id or os.environ.get("SUPABASE_USER_ID")
        if user_id:
            os.environ["CURRENT_USER_ID"] = user_id
            print(f"\n⚙️ Modo de Execução Única Manual Local (Usuário: {user_id}).")
            sincronizar_sessao_nuvem(user_id)
        else:
            print("\n⚙️ Modo de Execução Única Manual Local.")
            
        config.recarregar_config()
        executar_scrapers(args.plataforma, user_id)

if __name__ == "__main__":
    main()
