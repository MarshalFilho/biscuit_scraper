import sys
import os
import unicodedata
sys.stdout.reconfigure(encoding='utf-8')
import json
import re
import time
import random
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Permite importação dos módulos da pasta src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_platform_dirs, AUTH_DIR
import config
from utils.relevancia import verificar_relevancia
from utils.supabase_client import conectar_supabase, upsert_produto, registrar_historico

# Configuração dinâmica de diretórios para a Shopee
PLATFORM_DIRS = get_platform_dirs("shopee")
BRONZE_DIR = PLATFORM_DIRS["bronze"]
PRATA_DIR = PLATFORM_DIRS["prata"]
OURO_DIR = PLATFORM_DIRS["ouro"]

def limpar_preco(texto_preco):
    if not texto_preco: return 0.0
    # Shopee costuma usar "R$ 10,00" ou "R$10,00 - R$20,00". Pegamos o primeiro valor.
    texto_preco = texto_preco.split("-")[0]
    num = texto_preco.replace("R$", "").replace(".", "").replace(",", ".").strip()
    try:
        return float(re.sub(r"[^\d.]", "", num))
    except ValueError:
        return 0.0

def limpar_vendas(texto_vendas):
    if not texto_vendas: return 0
    # Shopee usa formatos como "1,2 mil vendidos" ou "50 vendidos"
    texto_vendas = texto_vendas.replace(".", "").replace(",", ".").lower()
    
    multiplicador = 1
    if "mil" in texto_vendas or "k" in texto_vendas:
        multiplicador = 1000
        
    match = re.search(r"([\d.]+)\s*(?:mil|k)?\s*vendido", texto_vendas)
    if match:
        valor = float(match.group(1))
        return int(valor * multiplicador)
    return 0



def fase_bronze():
    """
    Fase Bronze: Abre o navegador, acessa a Shopee e salva a página HTML bruta
    de cada termo de busca na pasta data/shopee/bronze/ (coleta até MAX_PAGINAS páginas).
    """
    print(f"\n🚀 [Etapa Bronze - Shopee] Iniciando raspagem da web (até {MAX_PAGINAS} páginas por termo)...")
    
    with sync_playwright() as p:
        browser_args = {
            "headless": False,
            "args": ["--disable-blink-features=AutomationControlled"]
        }
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if os.path.exists(chrome_path):
            browser_args["executable_path"] = chrome_path
            
        browser = p.chromium.launch(**browser_args) 
        
        auth_path = os.path.join(AUTH_DIR, "auth_shopee.json")
        context_args = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        if os.path.exists(auth_path):
            context_args["storage_state"] = auth_path
            
        context = browser.new_context(**context_args)

        for termo in config.get_termos_busca():
            # Abrir uma nova aba por termo de busca evita cache/cookies suspeitos acumulados
            page = context.new_page()
            nome_arquivo_base = termo.replace(" ", "_")
            print(f"\n🔎 Termo de busca: '{termo}'")
            
            termo_url = termo.replace(' ', '%20')
            url = f"https://shopee.com.br/search?keyword={termo_url}"
            
            # Acessa a primeira página
            print(f"   Acessando página 1: {url}")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                print(f"   ⏳ Falha ao carregar a página inicial: {e}")
                page.close()
                continue
                
            max_pags = config.get_max_paginas()
            for pagina in range(1, max_pags + 1):
                if pagina > 1:
                    print(f"   Processando página {pagina}...")
                    
                try:
                    # Checagem de segurança da Shopee (Login modal ou Captcha)
                    time.sleep(random.uniform(3.0, 5.0))
                    if page.locator(".shopee-popup__close-btn").is_visible():
                        page.locator(".shopee-popup__close-btn").click()
                        print("   ℹ️ Modal promocional fechado.")
                        
                    # SCROLL AGRESSIVO PARA LAZY LOADING
                    print("   Rolando a página para carregar todos os produtos...")
                    for _ in range(12):
                        page.mouse.wheel(0, 800)
                        time.sleep(random.uniform(1.0, 2.0))
                    
                    html_renderizado = page.content()
                    
                    bronze_path = os.path.join(BRONZE_DIR, f"bronze_{nome_arquivo_base}_p{pagina}.html")
                    with open(bronze_path, "w", encoding="utf-8") as f:
                        f.write(html_renderizado)
                    print(f"   🥉 BRONZE: Arquivo salvo em '{bronze_path}'.")
                    
                    if pagina == MAX_PAGINAS:
                        break
                        
                    # Clica no botão "Próximo" para ir para a próxima página
                    next_btn = page.locator("button.shopee-icon-button--right")
                    if next_btn.is_visible() and not next_btn.is_disabled():
                        print("   Navegando para a próxima página...")
                        next_btn.click()
                        page.wait_for_load_state("domcontentloaded")
                        time.sleep(random.uniform(4.0, 7.0))
                    else:
                        print("   ℹ️ Última página alcançada ou botão 'Próximo' indisponível.")
                        break
                        
                except Exception as e:
                    print(f"   ⚠️ Erro ao processar a página {pagina} do termo '{termo}': {e}")
                    if "closed" in str(e).lower():
                        print("   ❌ O navegador foi fechado. Encerrando scraper para este termo.")
                    break
            
            # Fecha a aba atual e espera um pouco antes de abrir a próxima para simular navegação humana
            page.close()
            tempo_espera = random.uniform(6.0, 12.0)
            print(f"   ⏳ Aguardando {tempo_espera:.1f}s antes da próxima busca...")
            time.sleep(tempo_espera)

        browser.close()
    print("✅ [Etapa Bronze] Concluída!")


def fase_prata():
    print("\n🚀 [Etapa Prata] Estruturando dados da Shopee (Bronze -> Prata)...")
    
    for termo in config.get_termos_busca():
        nome_arquivo_base = termo.replace(" ", "_")
        bronze_path = os.path.join(BRONZE_DIR, f"bronze_{nome_arquivo_base}.html")
        prata_path = os.path.join(PRATA_DIR, f"prata_{nome_arquivo_base}.html")
        
        if not os.path.exists(bronze_path):
            print(f"⚠️ [Prata] Arquivo de origem não encontrado: '{termo}'.")
            continue
            
        with open(bronze_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            
        combinado_soup = BeautifulSoup("", "html.parser")
        container_pai = combinado_soup.new_tag("div", attrs={"class": "shopee-search-results"})
        combinado_soup.append(container_pai)
        
        # A Shopee usa a classe shopee-search-item-result__item ou o atributo data-sqe="item"
        produtos = soup.find_all(["div", "li"], attrs={"data-sqe": "item"})
        
        if not produtos:
            # Fallback caso a estrutura mude
            produtos = soup.find_all("a", attrs={"data-sqe": "link"})
            
        if produtos:
            for p in produtos:
                container_pai.append(p)
            with open(prata_path, "w", encoding="utf-8") as f:
                f.write(str(combinado_soup))
            print(f"   🥈 PRATA: {len(produtos)} cards estruturados em '{prata_path}'.")
        else:
            print(f"   ⚠️ AVISO [Prata]: Nenhum produto encontrado para '{termo}'.")
            
    print("✅ [Etapa Prata] Concluída!")


def fase_ouro():
    print("\n🚀 [Etapa Ouro] Extração e deduplicação Shopee (Prata -> Ouro)...")
    todos_dados_ouro = []
    
    for termo in config.get_termos_busca():
        nome_arquivo_base = termo.replace(" ", "_")
        prata_path = os.path.join(PRATA_DIR, f"prata_{nome_arquivo_base}.html")
        
        if not os.path.exists(prata_path):
            continue
            
        with open(prata_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            
        # A Shopee tem os cards de produtos dentro do container estruturado no arquivo Prata.
        produtos_cards = soup.find_all(["div", "li"], attrs={"data-sqe": "item"})
        if not produtos_cards:
            produtos_cards = soup.find_all("a", attrs={"data-sqe": "link"})
        resultados_ouro = []
        urls_processadas = set()
        
        for produto in produtos_cards:
            try:
                # 1. LINK E TÍTULO
                link_tag = produto.find("a") if produto.name != "a" else produto
                if not link_tag or "href" not in link_tag.attrs:
                    continue
                    
                url_path = link_tag["href"]
                url_anuncio = f"https://shopee.com.br{url_path}" if url_path.startswith("/") else url_path
                
                # Deduplicação
                if url_anuncio in urls_processadas: continue
                urls_processadas.add(url_anuncio)
                
                # A Shopee costuma colocar o título dentro de uma div com linha cortada
                titulo_tag = produto.find("div", class_=re.compile(r"ie3A\+n|bName"))
                if not titulo_tag:
                    # Fallback para o primeiro texto longo dentro do link
                    textos = list(link_tag.stripped_strings)
                    titulo = textos[0] if textos else ""
                else:
                    titulo = titulo_tag.text.strip()
                    
                if not titulo or not verificar_relevancia(titulo, termo):
                    continue

                # 2. PREÇO
                # Procura por qualquer texto que tenha "R$" e pega o pai/avô para obter o valor completo
                preco_text = ""
                elementos_preco = produto.find_all(string=re.compile(r"R\$"))
                if elementos_preco:
                    p_elem = elementos_preco[0].parent
                    if p_elem:
                        if p_elem.text.strip() == "R$" and p_elem.parent:
                            preco_text = p_elem.parent.text
                        else:
                            preco_text = p_elem.text
                preco = limpar_preco(preco_text)

                # 3. VENDAS
                vendas_texto = ""
                elementos_vendas = produto.find_all(string=re.compile(r"vendid", re.IGNORECASE))
                if elementos_vendas:
                    vendas_texto = elementos_vendas[0].parent.text
                vendas = limpar_vendas(vendas_texto)

                resultados_ouro.append({
                    "termo_busca": termo,
                    "plataforma": "shopee",
                    "titulo": titulo,
                    "preco": preco,
                    "vendas_quantidade": vendas,
                    "url_anuncio": url_anuncio,
                })
            except Exception as e:
                continue

        print(f"   🥇 OURO: {len(resultados_ouro)} produtos extraídos para '{termo}'.")
        todos_dados_ouro.extend(resultados_ouro)

    todos_dados_ouro.sort(key=lambda x: x.get("vendas_quantidade", 0), reverse=True)

    ouro_path = os.path.join(OURO_DIR, "dados_shopee.json")
    with open(ouro_path, "w", encoding="utf-8") as f:
        json.dump(todos_dados_ouro, f, indent=4, ensure_ascii=False)
        
    print(f"✅ [Etapa Ouro] JSON gerado! {len(todos_dados_ouro)} itens salvos em '{ouro_path}'.")
    
    print("\n☁️ [Etapa Nuvem] Enviando dados para o Supabase...")
    try:
        supabase = conectar_supabase()
        enviados = 0
        for item in todos_dados_ouro:
            try:
                # Extrai o id do produto da url (geralmente formato ...-i.<shop_id>.<item_id>)
                match_id = re.search(r"-i\.(\d+\.\d+)", item["url_anuncio"])
                id_externo = match_id.group(1) if match_id else item["titulo"][:20]
                
                produto_id = upsert_produto(
                    supabase=supabase,
                    plataforma="shopee",
                    id_externo=id_externo,
                    titulo=item["titulo"],
                    link=item["url_anuncio"]
                )
                registrar_historico(
                    supabase=supabase,
                    produto_id=produto_id,
                    preco=item["preco"],
                    vendas_totais=item["vendas_quantidade"]
                )
                enviados += 1
            except Exception as e:
                print(f"Erro ao enviar produto {item['titulo']}: {e}")
                
        print(f"✅ [Etapa Nuvem] {enviados} produtos da Shopee sincronizados com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao conectar com Supabase: {e}")

if __name__ == "__main__":
    fase_bronze()
    fase_prata()
    fase_ouro()