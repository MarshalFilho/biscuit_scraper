import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import time
from bs4 import BeautifulSoup

# Ajuste de path para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from scrapers.meli_scraper import extrair_preco_card_meli, limpar_vendas
from scrapers.shopee_scraper import extrair_preco_card_shopee, limpar_vendas as limpar_vendas_shopee

try:
    from curl_cffi import requests
except ImportError:
    print("⚠️ 'curl_cffi' não instalado. Instale com: pip install curl_cffi")
    sys.exit(1)

def carregar_cookies(plataforma):
    candidatos = [
        os.path.join(config.AUTH_DIR, f"auth_{plataforma}.json"),
        os.path.join(config.AUTH_DIR, "auth.json") if plataforma in ["meli", "mercado_livre"] else None
    ]
    for auth_file in candidatos:
        if auth_file and os.path.exists(auth_file):
            try:
                with open(auth_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                    cookies_list = state.get('cookies', [])
                    cookies = {c['name']: c['value'] for c in cookies_list if 'name' in c and 'value' in c}
                    if cookies:
                        print(f"🔑 Cookies locais carregados de '{os.path.basename(auth_file)}' ({len(cookies)} cookies) para {plataforma}")
                        return cookies
            except Exception as e:
                print(f"⚠️ Erro ao carregar cookies {auth_file}: {e}")
    print(f"⚠️ Nenhum cookie válido encontrado para {plataforma}")
    return {}

def testar_mercado_livre_leve():
    print("\n--- 🛒 TESTE LEVE: MERCADO LIVRE ---")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1'
    }
    
    termos = config.get_termos_busca()
    termo = termos[0] if termos else "biscuit"
    url = f"https://lista.mercadolivre.com.br/{termo.replace(' ', '-')}"
    
    cookies = carregar_cookies("meli")
    print(f"Acessando: {url}")
    
    response = requests.get(url, headers=headers, cookies=cookies, impersonate="chrome120")
    
    print(f"Status Code: {response.status_code}")
    print(f"URL Final: {response.url}")
    
    if "account-verification" in response.url or "captcha" in response.text.lower():
        print("❌ BLOQUEIO: WAF/Captcha detectado mesmo com curl_cffi. Verifique se os cookies de sessão estão ativos e válidos.")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    cards = soup.find_all(class_=["ui-search-layout__item", "poly-card"])
    print(f"✅ Itens encontrados no HTML (Bronze -> Prata): {len(cards)}")
    
    if cards:
        card = cards[0]
        titulo_tag = card.find("h2", class_=lambda x: x and "poly-component__title" in x)
        titulo = titulo_tag.text.strip() if titulo_tag else "Sem Título"
        
        preco_val, debug_preco = extrair_preco_card_meli(card)
        vendas = limpar_vendas(card.text)
        
        print(f"\n[Exemplo Ouro extraído do HTML Leve]")
        print(f"Título: {titulo}")
        print(f"Preço Promocional Limpo: R$ {preco_val} (Debug: {debug_preco})")
        print(f"Vendas Estimadas: {vendas}")


def testar_shopee_leve():
    print("\n--- 🧡 TESTE LEVE: SHOPEE ---")
    termos = config.get_termos_busca()
    termo = termos[0] if termos else "biscuit"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'pt-BR,pt;q=0.9',
        'Referer': f'https://shopee.com.br/search?keyword={termo}',
        'x-api-source': 'pc',
        'x-shopee-language': 'pt',
        'x-requested-with': 'XMLHttpRequest',
    }
    
    url = f"https://shopee.com.br/api/v4/search/search_items?keyword={termo}&limit=10&page_type=search"
    cookies = carregar_cookies("shopee")
    print(f"Acessando API JSON: {url}")
    
    response = requests.get(url, headers=headers, cookies=cookies, impersonate="chrome120")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 403 or "error" in response.text:
        print("❌ BLOQUEIO: API da Shopee retornou erro.")
        try:
            print("Resposta:", response.json())
        except:
            pass
        return

    try:
        dados = response.json()
        itens = dados.get("items", [])
        print(f"✅ Itens encontrados na API JSON: {len(itens)}")
        
        if itens:
            item = itens[0].get("item_basic", {})
            titulo = item.get("name", "Sem título")
            
            # API Shopee divide o preço por 100000
            preco_val = item.get("price", 0) / 100000
            vendas = item.get("sold", 0)
            
            print(f"\n[Exemplo Ouro extraído da API Leve]")
            print(f"Título: {titulo}")
            print(f"Preço Promocional Limpo: R$ {preco_val:.2f}")
            print(f"Vendas Estimadas: {vendas}")
            
    except Exception as e:
        print(f"⚠️ Erro ao processar JSON da Shopee: {e}")

if __name__ == "__main__":
    print("Iniciando testes de Extração Leve (Bypass WAF)...")
    testar_mercado_livre_leve()
    time.sleep(2)
    testar_shopee_leve()
    print("\nTeste concluído.")
