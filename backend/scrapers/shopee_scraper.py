import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
import json
import random
import re
import time

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Permite importação dos módulos da pasta src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from config import AUTH_DIR, get_platform_dirs
from utils.relevancia import verificar_relevancia
from utils.supabase_client import conectar_supabase, registrar_historico, upsert_produto

# Configuração dinâmica de diretórios para a Shopee
PLATFORM_DIRS = get_platform_dirs("shopee")
BRONZE_DIR = PLATFORM_DIRS["bronze"]
PRATA_DIR = PLATFORM_DIRS["prata"]
OURO_DIR = PLATFORM_DIRS["ouro"]

def limpar_preco(texto_preco):
    """
    Extrai o primeiro valor monetário válido de uma string na Shopee.
    Suporta faixas de preço como "R$ 38,90 - R$ 250,00" (extrai R$ 38.90).
    """
    if not texto_preco: return 0.0
    texto_preco = str(texto_preco).split("-")[0]
    matches = re.findall(r"(?:R\$\s*)?(\d+(?:\.\d{3})*(?:,\d{1,2})?)", texto_preco, re.IGNORECASE)
    if not matches: return 0.0
    for m in matches:
        try:
            val_clean = m.replace(".", "").replace(",", ".")
            val = float(val_clean)
            if val > 0: return val
        except ValueError: continue
    return 0.0

def extrair_preco_card_shopee(produto):
    elementos_preco = produto.find_all(string=re.compile(r"R\$"))
    if elementos_preco:
        for elem in elementos_preco:
            p_elem = elem.parent
            if p_elem:
                is_bad = False
                for p in [p_elem] + list(p_elem.parents):
                    p_classes = " ".join(p.get("class", [])) if hasattr(p, "get") and p.get("class") else ""
                    p_tag = getattr(p, "name", "")
                    if "discount" in p_classes.lower() or "original" in p_classes.lower() or "strike" in p_classes.lower() or "previous" in p_classes.lower() or p_tag in ["s", "del", "strike"]:
                        is_bad = True
                        break
                if is_bad:
                    continue
                    
                full_txt = p_elem.parent.text if p_elem.text.strip() == "R$" and p_elem.parent else p_elem.text
                val = limpar_preco(full_txt)
                if val > 0:
                    return val, f"Texto Bruto: '{full_txt.strip()}'"
    return 0.0, "Nenhum preço encontrado"

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
    de cada termo de busca na pasta data/shopee/bronze/ (coleta até N páginas).
    """
    print(f"\n🚀 [Etapa Bronze - Shopee] Iniciando raspagem da web (até {config.get_max_paginas()} páginas por termo)...")
    
    auth_dir = AUTH_DIR
    profile_dir = os.path.join(auth_dir, "chrome_profile_shopee")
    os.makedirs(profile_dir, exist_ok=True)
    
    is_headless = os.environ.get("HEADLESS", "true").lower() == "true"
    
    with sync_playwright() as p:
        chrome_installed = os.path.exists(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        launch_args = {
            "user_data_dir": profile_dir,
            "headless": is_headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process"
            ],
            "viewport": {"width": 1366, "height": 768},
            "locale": "pt-BR",
            "timezone_id": "America/Sao_Paulo",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }
        if chrome_installed:
            launch_args["channel"] = "chrome"

        context = p.chromium.launch_persistent_context(**launch_args)
        
        # Injeta cookies de sessão autenticados APENAS se o usuário estiver no modo logado
        if config.get_modo_paginacao() == "logado":
            auth_file = os.path.join(AUTH_DIR, "auth_shopee.json")
            if os.path.exists(auth_file):
                try:
                    with open(auth_file, "r", encoding="utf-8") as f:
                        cookies = json.load(f)
                        if isinstance(cookies, list) and len(cookies) > 0:
                            context.add_cookies(cookies)
                            print(f"🍪 [{len(cookies)} Cookies] Sessão autenticada da Shopee injetada com sucesso!", flush=True)
                except Exception as e:
                    print(f"⚠️ Aviso ao injetar cookies da Shopee: {e}", flush=True)
        else:
            print("🌐 Modo Anônimo Limpo ativado para Shopee.", flush=True)

        for termo in config.get_termos_busca():
            page = context.new_page()
            page.add_init_script("""
                delete Object.getPrototypeOf(navigator).webdriver;
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['pt-BR', 'pt', 'en-US'] });
                window.chrome = { runtime: { connect: () => {}, sendMessage: () => {} } };
            """)
            nome_arquivo_base = termo.replace(" ", "_")
            print(f"\n🔎 Termo de busca: '{termo}'")
            
            termo_url = termo.replace(' ', '%20')
            url = f"https://shopee.com.br/search?keyword={termo_url}"
            
            # Acessa a primeira página
            print(f"   Acessando página 1: {url}")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(random.uniform(2.0, 3.5))
                
                # Se cair em verificação por causa dos cookies de outro IP, limpa e tenta anônimo
                if "verify/captcha" in page.url or "anti_bot_tracking_id" in page.url:
                    print("⚠️ [Shopee] Sessão com cookies gerou verificação (IP de nuvem). Limpando cookies e tentando modo público...", flush=True)
                    context.clear_cookies()
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    time.sleep(3)

                # VERIFICAÇÃO RIGOROSA ANTI-ROBÔ / CAPTCHA
                from utils.bot_detector import (
                    notificar_e_interromper_bloqueio,
                    verificar_bloqueio_shopee,
                )
                verificar_bloqueio_shopee(page)

                try:
                    page.wait_for_selector('a[href*="-i."], [data-sqe="item"], .shopee-search-item-result__item', timeout=12000)
                except Exception:
                    verificar_bloqueio_shopee(page)

            except Exception as e:
                from utils.bot_detector import (
                    BotDetectionError,
                    notificar_e_interromper_bloqueio,
                )
                if isinstance(e, BotDetectionError):
                    try: page.close()
                    except: pass
                    try: context.close()
                    except: pass
                    raise e
                
                print(f"   ⏳ Falha ao carregar a página inicial: {e}")
                if "closed" in str(e).lower() or "target" in str(e).lower():
                    notificar_e_interromper_bloqueio("Shopee", detalhe="O navegador foi fechado ou bloqueado pela Shopee.")
                try: page.close()
                except Exception: pass
                continue
                
            max_pags = config.get_max_paginas()
            for pagina in range(1, max_pags + 1):
                if pagina > 1:
                    print(f"   Processando página {pagina}...")
                    
                try:
                    # Checagem de segurança da Shopee (Login modal ou Captcha)
                    time.sleep(random.uniform(3.0, 5.0))
                    verificar_bloqueio_shopee(page)

                    if page.locator(".shopee-popup__close-btn").is_visible():
                        page.locator(".shopee-popup__close-btn").click()
                        print("   ℹ️ Modal promocional fechado.")
                        
                    # SCROLL AGRESSIVO PARA LAZY LOADING
                    print("   Rolando a página para carregar todos os produtos...")
                    for _ in range(12):
                        page.mouse.wheel(0, 800)
                        time.sleep(random.uniform(1.0, 2.0))
                    
                    html_renderizado = page.content()
                    
                    title = page.title()
                    curr_url = page.url
                    html_len = len(html_renderizado)
                    print(f"   🔍 [DIAGNÓSTICO SHOPEE BRONZE] Título: '{title}' | URL: '{curr_url}' | Tamanho HTML: {html_len} bytes")
                    
                    # VERIFICAÇÃO RIGOROSA ANTI-ROBÔ / CAPTCHA NO CONTEÚDO
                    verificar_bloqueio_shopee(page, html_content=html_renderizado)

                    bronze_path = os.path.join(BRONZE_DIR, f"bronze_{nome_arquivo_base}_p{pagina}.html")
                    with open(bronze_path, "w", encoding="utf-8") as f:
                        f.write(html_renderizado)
                    print(f"   🥉 BRONZE: Arquivo salvo em '{bronze_path}'.")
                    
                    if pagina == max_pags:
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

        context.close()
    print("✅ [Etapa Bronze - Shopee] Concluída!")


def fase_prata():
    print("\n🚀 [Etapa Prata] Estruturando dados da Shopee (Bronze -> Prata)...")
    
    for termo in config.get_termos_busca():
        nome_arquivo_base = termo.replace(" ", "_")
        prata_path = os.path.join(PRATA_DIR, f"prata_{nome_arquivo_base}.html")
        
        # Procura arquivos paginados (_p1, _p2...) correspondentes a este termo
        arquivos_para_processar = []
        for p in range(1, config.get_max_paginas() + 1):
            path = os.path.join(BRONZE_DIR, f"bronze_{nome_arquivo_base}_p{p}.html")
            if os.path.exists(path):
                arquivos_para_processar.append(path)
                
        if not arquivos_para_processar:
            print(f"⚠️ [Prata] Arquivo de origem não encontrado: '{termo}'.")
            continue
            
        combinado_soup = BeautifulSoup("", "html.parser")
        container_pai = combinado_soup.new_tag("div", attrs={"class": "shopee-search-results"})
        combinado_soup.append(container_pai)
        
        total_produtos = 0
        
        for path in arquivos_para_processar:
            with open(path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                
            produtos = soup.find_all(["div", "li", "a"], attrs={"data-sqe": "item"})
            if not produtos:
                produtos = soup.find_all("a", attrs={"data-sqe": "link"})
            if not produtos:
                produtos = soup.find_all(["div", "li", "a"], class_=re.compile(r"shopee-search-item-result|col-xs-2-4"))
            if not produtos:
                produtos = [a for a in soup.find_all("a", href=re.compile(r"-i\.\d+\.\d+|\/product\/"))]
                
            if produtos:
                for p in produtos:
                    container_pai.append(p)
                    total_produtos += 1
                    
        if total_produtos > 0:
            with open(prata_path, "w", encoding="utf-8") as f:
                f.write(str(combinado_soup))
            print(f"   🥈 PRATA: Arquivo estruturado '{prata_path}' gerado combinando {len(arquivos_para_processar)} página(s) e {total_produtos} produtos.")
        else:
            print(f"   ⚠️ AVISO [Prata]: Nenhum produto encontrado para '{termo}'.")
            if arquivos_para_processar:
                with open(arquivos_para_processar[0], "r", encoding="utf-8") as f:
                    diag_soup = BeautifulSoup(f.read(), "html.parser")
                print(f"      -> Quantidade de links <a> no HTML: {len(diag_soup.find_all('a'))}")
                print(f"      -> Quantidade de divs no HTML: {len(diag_soup.find_all('div'))}")
                snippet = diag_soup.text.strip()[:200].replace('\n', ' ')
                print(f"      -> Trecho de texto do HTML: '{snippet}'")
            
    print("✅ [Etapa Prata] Concluída!")



def fase_ouro():
    print("\n🚀 [Etapa Ouro] Extração e deduplicação Shopee (Prata -> Ouro)...")
    todos_dados_ouro = []
    urls_processadas = set()
    titulos_processados = set()
    
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
        
        for produto in produtos_cards:
            try:
                # 1. LINK E TÍTULO
                link_tag = produto.find("a") if produto.name != "a" else produto
                if not link_tag or "href" not in link_tag.attrs:
                    continue
                    
                url_path = link_tag["href"]
                url_anuncio = f"https://shopee.com.br{url_path}" if url_path.startswith("/") else url_path
                
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

                # Deduplicação por Título normalizado ou URL
                norm_title = re.sub(r"[^\w\s]", "", titulo.lower()).strip()
                if url_anuncio in urls_processadas or norm_title in titulos_processados:
                    continue
                urls_processadas.add(url_anuncio)
                titulos_processados.add(norm_title)

                # 2. PREÇO
                preco, preco_debug_log = extrair_preco_card_shopee(produto)
                print(f"   🔎 [AUDITORIA PREÇO SHOPEE] '{titulo[:35]}...' => R$ {preco:.2f} ({preco_debug_log})")

                # 3. VENDAS
                vendas_texto = ""
                elementos_vendas = produto.find_all(string=re.compile(r"vendid", re.IGNORECASE))
                if elementos_vendas:
                    vendas_texto = elementos_vendas[0].parent.text
                vendas = limpar_vendas(vendas_texto)

                # Extrai vendedor (Nome da loja em prioridade, com fallback para Cidade/Estado e ID Único da Loja)
                vendedor = None
                shop_name_tag = produto.find(["div", "span", "a"], class_=re.compile(r"shopee-search-item-result__shop-name|shop-name|seller-name|username", re.IGNORECASE))
                if shop_name_tag and shop_name_tag.text.strip() and len(shop_name_tag.text.strip()) < 40:
                    vendedor = shop_name_tag.text.strip()

                # Busca localização (Cidade/Estado)
                loc_name = None
                vendedor_tag = produto.find(["div", "span"], class_=re.compile(r"shopee-search-item-result__shop-location"))
                if vendedor_tag and vendedor_tag.text.strip() and len(vendedor_tag.text.strip()) < 40:
                    loc_name = vendedor_tag.text.strip()
                if not loc_name:
                    loc_match = re.search(r"\b(São Paulo|Minas Gerais|Santa Catarina|Rio de Janeiro|Paraná|Rio Grande do Sul|Bahia|Ceará|Pernambuco|Goiás|Espírito Santo|Distrito Federal|Maranhão|Paraíba|Amazonas|Mato Grosso|Rio Grande do Norte|Piauí|Alagoas|Sergipe|Rondônia|Tocantins|Acre|Amapá|Roraima|Internacional)\b", produto.text)
                    if loc_match:
                        loc_name = loc_match.group(1)

                # Extrai ID único da Loja na Shopee a partir do link (-i.SHOPID.ITEMID)
                shop_id = None
                shop_match = re.search(r"-i\.(\d+)\.", url_anuncio)
                if shop_match:
                    shop_id = shop_match.group(1)[-4:]

                if vendedor:
                    pass
                elif loc_name and shop_id:
                    vendedor = f"Loja em {loc_name} (#{shop_id})"
                elif loc_name:
                    vendedor = f"Loja em {loc_name}"
                elif shop_id:
                    vendedor = f"Loja Shopee (#{shop_id})"
                else:
                    vendedor = "Loja Shopee"

                resultados_ouro.append({
                    "termo_busca": termo,
                    "plataforma": "shopee",
                    "titulo": titulo,
                    "preco": preco,
                    "vendas_quantidade": vendas,
                    "url_anuncio": url_anuncio,
                    "vendedor": vendedor
                })
            except Exception:
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
                    link=item["url_anuncio"],
                    vendedor=item.get("vendedor")
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