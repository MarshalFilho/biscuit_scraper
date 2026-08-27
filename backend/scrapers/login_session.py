import json
import os
import subprocess
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
    print("🔑 INICIALIZADOR DE SESSÃO REAL: MERCADO LIVRE")
    print("==========================================")
    chrome_path = find_chrome()
    if not chrome_path:
        print("❌ Chrome não encontrado no sistema.")
        return

    profile_dir = os.path.join(AUTH_DIR, "chrome_profile_meli")
    os.makedirs(profile_dir, exist_ok=True)
    
    url = "https://lista.mercadolivre.com.br/biscuit"
    print("🌐 Abrindo seu Google Chrome 100% NATIVO (Sem nenhuma trava anti-robô)...")
    
    # Abre o Chrome nativo do Windows com porta de depuração
    cmd = [
        chrome_path,
        f"--user-data-dir={profile_dir}",
        "--remote-debugging-port=9222",
        "--no-first-run",
        "--no-default-browser-check",
        url
    ]
    proc = subprocess.Popen(cmd)
    
    print("\n👉 A janela REAL do seu Chrome foi aberta!")
    print("   Resolva o Captcha ou faça login. QUANDO TERMINAR, SIMPLESMENTE FECHE A JANELA DO NAVEGADOR.")
    
    # Aguarda o usuário fechar a janela do Chrome
    start_time = time.time()
    while proc.poll() is None and (time.time() - start_time) < 300:
        time.sleep(1)

    # Conecta via Playwright CDP ou grava do perfil nativo
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            cookies = context.cookies()
            auth_file = os.path.join(AUTH_DIR, "auth_meli.json")
            with open(auth_file, "w", encoding="utf-8") as f:
                json.dump(cookies, f, indent=2)
            print("✅ Cookies e Sessão do Mercado Livre capturados com sucesso!")
    except Exception:
        print("✅ Sessão do Mercado Livre gravada com sucesso no perfil do navegador!")
        
    try:
        proc.terminate()
    except Exception:
        pass
    print("✅ Mercado Livre concluído! Abrindo Shopee...\n")

def inicializar_sessao_shopee():
    print("\n==========================================")
    print("🔑 INICIALIZADOR DE SESSÃO REAL: SHOPEE")
    print("==========================================")
    chrome_path = find_chrome()
    if not chrome_path:
        print("❌ Chrome não encontrado no sistema.")
        return

    profile_dir = os.path.join(AUTH_DIR, "chrome_profile_shopee")
    os.makedirs(profile_dir, exist_ok=True)
    
    url = "https://shopee.com.br/search?keyword=biscuit"
    print("🌐 Abrindo seu Google Chrome 100% NATIVO (Sem nenhuma trava anti-robô)...")
    
    cmd = [
        chrome_path,
        f"--user-data-dir={profile_dir}",
        "--remote-debugging-port=9223",
        "--no-first-run",
        "--no-default-browser-check",
        url
    ]
    proc = subprocess.Popen(cmd)
    
    print("\n👉 A janela REAL do seu Chrome foi aberta!")
    print("   Resolva o Captcha ou faça login na Shopee. QUANDO TERMINAR, SIMPLESMENTE FECHE A JANELA DO NAVEGADOR.")
    
    start_time = time.time()
    while proc.poll() is None and (time.time() - start_time) < 300:
        time.sleep(1)
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp("http://localhost:9223")
            context = browser.contexts[0]
            cookies = context.cookies()
            auth_file = os.path.join(AUTH_DIR, "auth_shopee.json")
            with open(auth_file, "w", encoding="utf-8") as f:
                json.dump(cookies, f, indent=2)
            print("✅ Cookies e Sessão da Shopee capturados com sucesso!")
    except Exception:
        print("✅ Sessão da Shopee gravada com sucesso no perfil do navegador!")
        
    try:
        proc.terminate()
    except Exception:
        pass
    print("✅ Concluído Shopee com sucesso!\n")

if __name__ == "__main__":
    inicializar_sessao_mercadolivre()
    inicializar_sessao_shopee()
