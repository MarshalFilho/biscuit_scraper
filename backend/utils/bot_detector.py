
class BotDetectionError(Exception):
    def __init__(self, plataforma, mensagem):
        self.plataforma = plataforma
        self.mensagem = mensagem
        super().__init__(f"[{plataforma}] {mensagem}")

def notificar_e_interromper_bloqueio(plataforma: str, user_id: str = None, detalhe: str = ""):
    """
    Exibe um aviso em destaque no console, atualiza a nuvem (Supabase) 
    e lança um erro para parar imediatamente a raspagem.
    """
    msg_curta = f"🛑 Bloqueio anti-robô detectado na {plataforma}! Por favor, execute 'py src/main.py --login' no terminal para resolver o captcha."
    
    # 1. Atualiza o status no Supabase se user_id estiver disponível
    if user_id:
        try:
            from utils.supabase_client import atualizar_status_scraper
            atualizar_status_scraper(user_id, msg_curta)
        except Exception as e:
            print(f"⚠️ Aviso ao atualizar status de bloqueio na nuvem: {e}")

    # 2. Imprime um Banner de Alerta proeminente no Console
    print("\n" + "=" * 75, flush=True)
    print(f"🛑 SCRAPER INTERROMPIDO: BLOQUEIO / CAPTCHA DETECTADO NA {plataforma.upper()}", flush=True)
    print("=" * 75, flush=True)
    print(f"⚠️ A {plataforma} detectou comportamento automatizado e enviou uma verificação.", flush=True)
    if detalhe:
        print(f"ℹ️ Motivo: {detalhe}", flush=True)
    print("\n👉 AÇÃO NECESSÁRIA:", flush=True)
    print("   Abra o seu terminal e execute o comando abaixo para logar no Chrome real:")
    print("   ------------------------------------------------------------")
    print("   py src/main.py --login")
    print("   ------------------------------------------------------------")
    print("   Resolva o Captcha na janela nativa que se abrirá e pressione ENTER.")
    print("=" * 75 + "\n", flush=True)

    # 3. Interrompe a raspagem lançando a exceção
    raise BotDetectionError(plataforma, msg_curta)

def verificar_bloqueio_shopee(page, html_content: str = "", user_id: str = None):
    """
    Verifica se a página atual da Shopee é um captcha ou página de bloqueio anti-robô.
    """
    try:
        url = page.url.lower()
        title = page.title().lower()
        content = (html_content or page.content()).lower()
    except Exception:
        # Se a página foi fechada abruptamente por bloqueio WAF da Shopee
        notificar_e_interromper_bloqueio("Shopee", user_id, "O navegador ou a conexão foram encerrados pela página de segurança da Shopee.")
        return

    # Sinais reais de redirecionamento anti-bot da Shopee
    sinais_url = ["verify/captcha", "verify/traffic", "scene=crawler", "traffic_control"]
    sinais_titulo = ["verify captcha", "security check", "acesso bloqueado", "robot check"]
    sinais_conteudo = ["verify/captcha", "scene=crawler_item", "desculpe, estamos enfrentando alguns problemas", "id=\"captcha\"", "class=\"captcha\""]

    if any(s in url for s in sinais_url):
        notificar_e_interromper_bloqueio("Shopee", user_id, f"Redirecionado para URL de verificação: {page.url}")

    if any(s in title for s in sinais_titulo):
        notificar_e_interromper_bloqueio("Shopee", user_id, f"Página de captcha no título: '{page.title()}'")

    if any(s in content for s in ["verify/captcha", "scene=crawler_item"]):
        notificar_e_interromper_bloqueio("Shopee", user_id, "Página de bloqueio/captcha da Shopee detectada.")

def verificar_bloqueio_meli(page, html_content: str = "", user_id: str = None):
    """
    Verifica se a página atual do Mercado Livre é um captcha ou bloqueio anti-robô.
    """
    try:
        url = page.url.lower()
        title = page.title().lower()
        content = (html_content or page.content()).lower()
    except Exception:
        notificar_e_interromper_bloqueio("Mercado Livre", user_id, "A página do Mercado Livre foi fechada abruptamente.")
        return

    if "/captcha/" in url or "abuse-china-wall" in content or "acesso negado" in title:
        notificar_e_interromper_bloqueio("Mercado Livre", user_id, f"Captcha detectado no Mercado Livre (URL: {page.url})")
