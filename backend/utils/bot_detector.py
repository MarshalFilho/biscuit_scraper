import os
import time

class BotDetectionError(Exception):
    def __init__(self, plataforma, mensagem):
        self.plataforma = plataforma
        self.mensagem = mensagem
        super().__init__(f"[{plataforma}] {mensagem}")

def notificar_e_interromper_bloqueio(plataforma: str, user_id: str = None, detalhe: str = ""):
    """
    Exibe um aviso em destaque no console, atualiza a nuvem (Supabase) 
    e lança um erro para parar a raspagem em ambientes sem interface (cloud/headless).
    """
    msg_curta = f"🛑 Bloqueio anti-robô detectado na {plataforma}!"
    
    if user_id:
        try:
            from utils.supabase_client import atualizar_status_scraper
            atualizar_status_scraper(user_id, msg_curta)
        except Exception as e:
            print(f"⚠️ Aviso ao atualizar status de bloqueio na nuvem: {e}")

    print("\n" + "=" * 75, flush=True)
    print(f"🛑 SCRAPER INTERROMPIDO: BLOQUEIO / CAPTCHA DETECTADO NA {plataforma.upper()}", flush=True)
    print("=" * 75, flush=True)
    print(f"⚠️ A {plataforma} detectou comportamento automatizado e enviou uma verificação.", flush=True)
    if detalhe:
        print(f"ℹ️ Motivo: {detalhe}", flush=True)
    print("=" * 75 + "\n", flush=True)

    raise BotDetectionError(plataforma, msg_curta)

def resolver_bloqueio_interativo(page, plataforma: str, user_id: str = None, detalhe: str = ""):
    """
    Em execução local com interface gráfica, pausa a execução e aguarda o usuário
    resolver o captcha diretamente na janela aberta. Ao pressionar ENTER, continua
    a raspagem sem fechar nem abortar!
    """
    is_headless = os.environ.get("HEADLESS", "false").lower() == "true"
    is_cloud = os.environ.get("GITHUB_ACTIONS", "false").lower() == "true" or os.environ.get("CLOUD_MODE", "false").lower() == "true"

    if is_headless or is_cloud:
        notificar_e_interromper_bloqueio(plataforma, user_id, detalhe)
        return

    print("\n" + "=" * 75, flush=True)
    print(f"🧩 [PAUSA PARA CAPTCHA] VERIFICAÇÃO DETECTADA NA {plataforma.upper()}!", flush=True)
    print("=" * 75, flush=True)
    print(f"⚠️ A {plataforma} exibiu uma tela de verificação/captcha.", flush=True)
    if detalhe:
        print(f"ℹ️ Detalhe: {detalhe}", flush=True)
    print("\n👉 AÇÃO RÁPIDA:", flush=True)
    print("   1. Vá até a janela do navegador aberta na sua tela.")
    print("   2. Resolva o Captcha (deslize o quebra-cabeça / selecione as imagens).")
    print("   3. Assim que a página de produtos carregar...")
    input("\n👉 Pressione [ENTER] AQUI NO TERMINAL para continuar a coleta automaticamente! ")
    print("=" * 75 + "\n", flush=True)

    # Captura novos cookies pós-captcha para persistir no disco
    try:
        context = page.context
        cookies = context.cookies()
        if cookies:
            import json
            from config import AUTH_DIR
            plat_key = "shopee" if "shopee" in plataforma.lower() else "meli"
            auth_file = os.path.join(AUTH_DIR, f"auth_{plat_key}.json")
            with open(auth_file, "w", encoding="utf-8") as f:
                json.dump(cookies, f, indent=2)
            print(f"✅ Sessão/Cookies atualizados salvos com sucesso ({len(cookies)} cookies)!", flush=True)
    except Exception as e:
        print(f"ℹ️ Aviso ao salvar cookies pós-captcha: {e}", flush=True)

    time.sleep(2)
    return True

def verificar_bloqueio_shopee(page, html_content: str = "", user_id: str = None):
    """
    Verifica se a página atual da Shopee é um captcha ou página de bloqueio anti-robô.
    Se for e estiver rodando localmente, pausa e pede confirmação no terminal.
    """
    try:
        url = page.url.lower()
        title = page.title().lower()
        content = (html_content or page.content()).lower()
    except Exception:
        resolver_bloqueio_interativo(page, "Shopee", user_id, "O navegador ou conexão receberam verificação de segurança.")
        return

    sinais_url = ["verify/captcha", "verify/traffic", "scene=crawler", "traffic_control"]
    sinais_titulo = ["verify captcha", "security check", "robot check"]
    sinais_conteudo = ["verify/captcha", "scene=crawler_item", "desculpe, estamos enfrentando alguns problemas", "id=\"captcha\"", "class=\"captcha\""]

    if any(s in url for s in sinais_url):
        resolver_bloqueio_interativo(page, "Shopee", user_id, f"URL de verificação: {page.url}")

    elif any(s in title for s in sinais_titulo):
        resolver_bloqueio_interativo(page, "Shopee", user_id, f"Título de captcha: '{page.title()}'")

    elif any(s in content for s in ["verify/captcha", "scene=crawler_item"]):
        resolver_bloqueio_interativo(page, "Shopee", user_id, "Elemento de captcha na página.")

def verificar_bloqueio_meli(page, html_content: str = "", user_id: str = None):
    """
    Verifica se a página atual do Mercado Livre é um captcha ou bloqueio anti-robô.
    Se for e estiver rodando localmente, pausa e pede confirmação no terminal.
    """
    try:
        url = page.url.lower()
        title = page.title().lower()
        content = (html_content or page.content()).lower()
    except Exception:
        resolver_bloqueio_interativo(page, "Mercado Livre", user_id, "Página do Mercado Livre solicitou validação.")
        return

    if "/captcha/" in url or "abuse-china-wall" in content or "acesso negado" in title:
        resolver_bloqueio_interativo(page, "Mercado Livre", user_id, f"Captcha no Mercado Livre (URL: {page.url})")
