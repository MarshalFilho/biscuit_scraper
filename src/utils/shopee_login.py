import os
import sys

from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import AUTH_DIR


def login_shopee():
    print("\n=== Login Manual Shopee ===")
    print("Um navegador será aberto. Faça o login na sua conta Shopee e resolva qualquer Captcha.")
    print("Você tem 2 minutos para fazer isso.")
    
    auth_path = os.path.join(AUTH_DIR, "auth_shopee.json")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        page.goto("https://shopee.com.br/buyer/login")
        
        # Espera 120 segundos para o usuário fazer login
        try:
            page.wait_for_timeout(120000)
        except:
            pass
            
        print("\nSalvando cookies de sessão...")
        context.storage_state(path=auth_path)
        print(f"✅ Sessão salva com sucesso em: {auth_path}")
        browser.close()

if __name__ == "__main__":
    login_shopee()
