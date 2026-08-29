import json
import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import AUTH_DIR


def find_chrome():
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\Application\chrome.exe")
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def inicializar_sessao_mercadolivre():
    print("\n==========================================")
    print("🔑 INICIALIZADOR DE SESSÃO: MERCADO LIVRE")
    print("==========================================")
    
    os.makedirs(AUTH_DIR, exist_ok=True)
    profile_dir = os.path.join(AUTH_DIR, "chrome_profile_meli")
    os.makedirs(profile_dir, exist_ok=True)

    print("🌐 Abrindo navegador para o Mercado Livre...")
    
    with sync_playwright() as p:
        chrome_executable = find_chrome()
        launch_args = {
            "user_data_dir": profile_dir,
            "headless": False,
            "viewport": {"width": 1280, "height": 800},
            "locale": "pt-BR",
            "args": ["--disable-blink-features=AutomationControlled"]
        }
        if chrome_executable:
            launch_args["executable_path"] = chrome_executable

        try:
            context = p.chromium.launch_persistent_context(**launch_args)
            page = context.pages[0] if context.pages else context.new_page()
            page.goto("https://lista.mercadolivre.com.br/biscuit", wait_until="domcontentloaded")

            print("\n👉 A janela do Mercado Livre está aberta na sua tela!")
            print("   Se houver Captcha ou login, resolva-o diretamente no navegador.")
            input("\n👉 QUANDO TERMINAR (ou fechar a janela), pressione [ENTER] aqui no terminal... ")

            try:
                cookies = context.cookies()
                auth_file = os.path.join(AUTH_DIR, "auth_meli.json")
                with open(auth_file, "w", encoding="utf-8") as f:
                    json.dump(cookies, f, indent=2)
                print(f"✅ Cookies e Sessão do Mercado Livre salvos com sucesso ({len(cookies)} cookies)!")
            except Exception:
                print("✅ Sessão do Mercado Livre gravada com sucesso no perfil do navegador!")

            try:
                context.close()
            except Exception:
                pass
        except Exception as e:
            print(f"⚠️ Aviso no Mercado Livre: {e}")


def inicializar_sessao_shopee():
    print("\n==========================================")
    print("🔑 INICIALIZADOR DE SESSÃO: SHOPEE")
    print("==========================================")
    
    os.makedirs(AUTH_DIR, exist_ok=True)
    profile_dir = os.path.join(AUTH_DIR, "chrome_profile_shopee")
    os.makedirs(profile_dir, exist_ok=True)

    print("🌐 Abrindo navegador para a Shopee...")
    
    with sync_playwright() as p:
        chrome_executable = find_chrome()
        launch_args = {
            "user_data_dir": profile_dir,
            "headless": False,
            "viewport": {"width": 1280, "height": 800},
            "locale": "pt-BR",
            "args": ["--disable-blink-features=AutomationControlled"]
        }
        if chrome_executable:
            launch_args["executable_path"] = chrome_executable

        try:
            context = p.chromium.launch_persistent_context(**launch_args)
            page = context.pages[0] if context.pages else context.new_page()
            page.goto("https://shopee.com.br/search?keyword=biscuit", wait_until="domcontentloaded")

            print("\n👉 A janela da Shopee está aberta na sua tela!")
            print("   Se houver Captcha ou login, resolva-o diretamente no navegador.")
            input("\n👉 QUANDO TERMINAR (ou fechar a janela), pressione [ENTER] aqui no terminal... ")

            try:
                cookies = context.cookies()
                auth_file = os.path.join(AUTH_DIR, "auth_shopee.json")
                with open(auth_file, "w", encoding="utf-8") as f:
                    json.dump(cookies, f, indent=2)
                print(f"✅ Cookies e Sessão da Shopee salvos com sucesso ({len(cookies)} cookies)!")
            except Exception:
                print("✅ Sessão da Shopee gravada com sucesso no perfil do navegador!")

            try:
                context.close()
            except Exception:
                pass
        except Exception as e:
            print(f"⚠️ Aviso na Shopee: {e}")


if __name__ == "__main__":
    inicializar_sessao_mercadolivre()
    inicializar_sessao_shopee()
