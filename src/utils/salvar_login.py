import os
import sys

from playwright.sync_api import sync_playwright

# Permite importação dos módulos da pasta src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import AUTH_DIR


def gerar_sessao(plataforma="meli"):
    with sync_playwright() as p:
        # Passamos o caminho do seu Chrome real e uma flag para esconder a automação
        browser = p.chromium.launch(
            headless=False,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe", 
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        if plataforma == "shopee":
            print("Navegando para a Shopee...")
            page.goto("https://shopee.com.br/buyer/login")
            auth_filename = "auth_shopee.json"
        else:
            print("Navegando para o Mercado Livre...")
            page.goto("https://www.mercadolivre.com.br")
            auth_filename = "auth.json"
        
        print("\n" + "="*50)
        print("⚠️ AÇÃO MANUAL NECESSÁRIA ⚠️")
        print("1. Vá na janela do navegador que abriu.")
        print("2. Faça o login na plataforma (resolva os captchas se necessário).")
        print("3. Quando estiver na tela inicial logado, volte aqui e dê ENTER.")
        print("="*50 + "\n")
        
        input("👉 Pressione ENTER aqui no terminal APÓS terminar o login...")
        
        auth_path = os.path.join(AUTH_DIR, auth_filename)
        context.storage_state(path=auth_path)
        print(f"✅ Sessão salva com sucesso no arquivo '{auth_path}'!")
        
        browser.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--plataforma", choices=["meli", "shopee"], default="meli")
    args = parser.parse_args()
    gerar_sessao(args.plataforma)
