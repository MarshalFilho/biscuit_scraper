import os
import sys
import unicodedata

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

# Configuração dinâmica de diretórios para o Mercado Livre
PLATFORM_DIRS = get_platform_dirs("mercado_livre")
BRONZE_DIR = PLATFORM_DIRS["bronze"]
PRATA_DIR = PLATFORM_DIRS["prata"]
OURO_DIR = PLATFORM_DIRS["ouro"]

def limpar_preco(texto_preco):
    """
    Extrai o primeiro valor monetário válido de uma string.
    Evita contatenar parcelas (ex: 12x R$ 100) ou faixas de variação.
    """
    if not texto_preco: return 0.0
    matches = re.findall(r"(?:R\$\s*)?(\d+(?:\.\d{3})*(?:,\d{1,2})?)", str(texto_preco), re.IGNORECASE)
    if not matches: return 0.0
    for m in matches:
        try:
            val_clean = m.replace(".", "").replace(",", ".")
            val = float(val_clean)
            if val > 0: return val
        except ValueError: continue
    return 0.0

def extrair_preco_card_meli(produto):
    """
    Extrai com precisão o preço promocional/vigente do card do Mercado Livre,
    filtrando rigorosamente preços originais riscados, parcelamentos e anúncios relacionados.
    """
    container_atual = produto.find(class_=re.compile(r"poly-price__current|ui-search-price__second-line|andes-money-amount--main-price"))

    if not container_atual:
        cand_amounts = produto.find_all("span", class_=re.compile(r"andes-money-amount|price-tag-amount"))
        for cand in cand_amounts:
            is_previous = False
            for p in [cand] + list(cand.parents):
                p_classes = " ".join(p.get("class", [])) if hasattr(p, "get") and p.get("class") else ""
                p_tag = getattr(p, "name", "")
                if "previous" in p_classes or "original" in p_classes or "installment" in p_classes or "poly-price__original" in p_classes or p_tag in ["s", "del", "strike"]:
                    is_previous = True
                    break
            if not is_previous:
                container_atual = cand
                break

    if not container_atual:
        container_atual = produto

    frac_tags = container_atual.find_all("span", class_=re.compile(r"andes-money-amount__fraction|price-tag-fraction"))
    for frac_tag in frac_tags:
        is_bad = False
        for p in [frac_tag] + list(frac_tag.parents):
            if p == container_atual and container_atual != produto: break
            p_classes = " ".join(p.get("class", [])) if hasattr(p, "get") and p.get("class") else ""
            p_tag = getattr(p, "name", "")
            if "previous" in p_classes or "original" in p_classes or "installment" in p_classes or "poly-price__original" in p_classes or p_tag in ["s", "del", "strike"]:
                is_bad = True
                break
        if not is_bad:
            frac_str = frac_tag.text.strip().replace(".", "")
            parent_amount = frac_tag.find_parent("span", class_=re.compile(r"andes-money-amount|price-tag-amount"))
            cents_tag = parent_amount.find("span", class_=re.compile(r"andes-money-amount__cents|price-tag-cents")) if parent_amount else None
            cents_str = cents_tag.text.strip() if cents_tag else "00"
            try:
                price_val = float(f"{frac_str}.{cents_str}")
                return price_val, f"Preço Vigente OK: R$ {price_val:.2f}"
            except ValueError: pass

    raw_text = container_atual.text.strip()
    price_val = limpar_preco(raw_text)
    return price_val, f"Texto Bruto: '{raw_text}'"

def limpar_vendas(texto_vendas):
    if not texto_vendas: return 0
    texto_vendas = texto_vendas.replace(".", "")
    match = re.search(r"(\d+)\s*(?:produtos?\s*)?vendidos?", texto_vendas, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0

def normalizar_texto(texto):
    if not texto: return ""
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode('utf-8')
    return texto.lower()

def extrair_vendas_texto(produto):
    # 1. Procura em tags com classes conhecidas primeiro
    for tag in produto.find_all(["span", "div"], class_=re.compile(r"andes-visually-hidden|polylabel-label|poly-component__review-compacted|poly-component__sales")):
        texto = tag.text.strip()
        if "vend" in texto.lower():
            return texto
            
    # 2. Se não achou, procura por qualquer texto com 'vend' em tags folha
    for tag in produto.find_all(["span", "div"]):
        if not tag.find(True):
            texto = tag.text.strip()
            if "vend" in texto.lower() and len(texto) < 100:
                return texto
    return ""

def fase_bronze():
    """
    Fase Bronze: Abre o navegador, acessa o Mercado Livre e salva a página HTML bruta
    de cada termo de busca na pasta data/mercado_livre/bronze/ (coleta até N páginas).
    """
    print(f"\n🚀 [Etapa Bronze] Iniciando raspagem da web (até {config.get_max_paginas()} páginas por termo)...", flush=True)
    
    auth_dir = AUTH_DIR
    profile_dir = os.path.join(auth_dir, "chrome_profile_meli")
    os.makedirs(profile_dir, exist_ok=True)
    
    is_headless = os.environ.get("HEADLESS", "false").lower() == "true"
    
    with sync_playwright() as p:
        chrome_installed = os.path.exists(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        launch_args = {
            "user_data_dir": profile_dir,
            "headless": is_headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage"
            ],
            "viewport": {"width": 1366, "height": 768},
            "locale": "pt-BR",
            "timezone_id": "America/Sao_Paulo",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }
        if chrome_installed:
            launch_args["channel"] = "chrome"

        context = p.chromium.launch_persistent_context(**launch_args)
        page = context.pages[0] if context.pages else context.new_page()
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
            Object.defineProperty(navigator, 'languages', { get: () => ['pt-BR', 'pt', 'en-US'] });
            window.chrome = { runtime: {} };
        """)

        # Inicializa a sessão navegando pela página principal do Mercado Livre
        try:
            print("🌐 Inicializando sessão de navegação no Mercado Livre...", flush=True)
            page.goto("https://www.mercadolivre.com.br", wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Aviso ao carregar página principal: {e}", flush=True)
 
        for termo in config.get_termos_busca():
            nome_arquivo_base = termo.replace(" ", "_")
            print(f"\n🔎 Termo de busca: '{termo}'")
            
            termo_url = termo.replace(' ', '-')
            url = f"https://lista.mercadolivre.com.br/{termo_url}"
            
            # Acessa a primeira página
            print(f"   Acessando página 1: {url}")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                try:
                    page.wait_for_selector(".ui-search-results, .poly-card, .ui-search-layout, .ui-search-item", timeout=15000)
                except Exception:
                    pass
                page.mouse.wheel(0, 800)
                time.sleep(1.5)
            except Exception as e:
                print(f"   ⏳ Falha ao carregar a página inicial: {e}. Pulando para o próximo termo...")
                continue
            
            max_pags = config.get_max_paginas()
            for pagina in range(1, max_pags + 1):
                if pagina > 1:
                    print(f"   Processando página {pagina}...")
                
                # SIMULAÇÃO HUMANA
                time.sleep(random.uniform(2.0, 4.0))
                for i in range(2):
                    page.mouse.wheel(0, random.randint(500, 900))
                    time.sleep(random.uniform(1.0, 2.0))
                
                # Checagem de Captcha
                from utils.bot_detector import verificar_bloqueio_meli
                verificar_bloqueio_meli(page)
                
                html_renderizado = page.content()
                
                title = page.title()
                curr_url = page.url
                html_len = len(html_renderizado)
                print(f"   🔍 [DIAGNÓSTICO ML BRONZE] Título: '{title}' | URL: '{curr_url}' | Tamanho HTML: {html_len} bytes")
                verificar_bloqueio_meli(page, html_content=html_renderizado)

                # Salva o arquivo Bronze localmente
                bronze_path = os.path.join(BRONZE_DIR, f"bronze_{nome_arquivo_base}_p{pagina}.html")
                with open(bronze_path, "w", encoding="utf-8") as f:
                    f.write(html_renderizado)
                print(f"   🥉 BRONZE: Arquivo '{bronze_path}' salvo com sucesso.")
                
                # Se já alcançamos a página máxima configurada, interrompemos
                if pagina == max_pags:
                    break
                
                # Verifica próxima página
                soup = BeautifulSoup(html_renderizado, "html.parser")
                next_btn = soup.find("li", class_=re.compile(r"andes-pagination__button--next"))
                
                # Se não houver próxima página ou se o botão estiver desabilitado
                if not next_btn or "andes-pagination__button--disabled" in next_btn.get("class", []):
                    print("   ℹ️ Última página alcançada ou botão 'Próximo' indisponível/desabilitado.")
                    break
                
                # Clica no botão "Próximo" para ir para a próxima página
                print("   Navegando para a próxima página...")
                try:
                    page.click("li.andes-pagination__button--next a", timeout=15000)
                    page.wait_for_load_state("domcontentloaded")
                except Exception as e:
                    print(f"   ⏳ Falha ao clicar no botão 'Próximo': {e}. Interrompendo paginação...")
                    break
                    
                time.sleep(random.uniform(4.5, 7.2))
 
        context.close()
    print("✅ [Etapa Bronze] Concluída!", flush=True)

def fase_prata():
    """
    Fase Prata: Lê os arquivos HTML brutos das páginas na pasta data/mercado_livre/bronze/,
    extrai os blocos de produtos e os combina em um único HTML estruturado em data/mercado_livre/prata/.
    """
    print("\n🚀 [Etapa Prata] Iniciando processamento e mesclagem de estrutura (Bronze -> Prata)...")
    
    for termo in config.get_termos_busca():
        nome_arquivo_base = termo.replace(" ", "_")
        prata_path = os.path.join(PRATA_DIR, f"prata_{nome_arquivo_base}.html")
        
        # Procura arquivos paginados (_p1, _p2...) correspondentes a este termo
        arquivos_para_processar = []
        for p in range(1, config.get_max_paginas() + 1):
            path = os.path.join(BRONZE_DIR, f"bronze_{nome_arquivo_base}_p{p}.html")
            if os.path.exists(path):
                arquivos_para_processar.append(path)
                
        # Fallback para o arquivo antigo caso o scraper antigo tenha sido rodado antes
        if not arquivos_para_processar:
            path_antigo = os.path.join(BRONZE_DIR, f"bronze_{nome_arquivo_base}.html")
            if os.path.exists(path_antigo):
                arquivos_para_processar.append(path_antigo)
                
        if not arquivos_para_processar:
            print(f"⚠️ [Prata] Arquivo de origem não encontrado para: '{termo}'. Pulando...")
            continue
            
        combinado_soup = BeautifulSoup("", "html.parser")
        container_pai = combinado_soup.new_tag("div", attrs={"class": "ui-search-results"})
        combinado_soup.append(container_pai)
        tem_conteudo = False
        
        for path in arquivos_para_processar:
            with open(path, "r", encoding="utf-8") as f:
                html_content = f.read()
                
            soup = BeautifulSoup(html_content, "html.parser")
            bloco_produtos = soup.find(["ol", "section", "div"], class_=re.compile(r"ui-search-layout|poly-card-container|ui-search-results"))
            
            if bloco_produtos:
                container_pai.append(bloco_produtos)
                tem_conteudo = True
            else:
                body = soup.find("body")
                if body:
                    container_pai.append(body)
                    tem_conteudo = True
                    
        if tem_conteudo:
            with open(prata_path, "w", encoding="utf-8") as f:
                f.write(str(combinado_soup))
            print(f"   🥈 PRATA: Arquivo estruturado '{prata_path}' gerado combinando {len(arquivos_para_processar)} página(s).")
        else:
            print(f"   ⚠️ AVISO [Prata]: Nenhum container de produtos encontrado para o termo '{termo}'.")
            
    print("✅ [Etapa Prata] Concluída!")

def fase_ouro():
    """
    Fase Ouro: Lê os HTMLs estruturados da pasta data/mercado_livre/prata/, extrai as informações dos cards de produtos
    e grava a lista final em formato JSON consolidado em data/mercado_livre/ouro/dados_meli.json.
    """
    print("\n🚀 [Etapa Ouro] Iniciando extração e deduplicação de dados (Prata -> Ouro)...")
    todos_dados_ouro = []
    urls_processadas = set()
    titulos_processados = set()
    
    for termo in config.get_termos_busca():
        nome_arquivo_base = termo.replace(" ", "_")
        prata_path = os.path.join(PRATA_DIR, f"prata_{nome_arquivo_base}.html")
        
        if not os.path.exists(prata_path):
            print(f"⚠️ [Ouro] Arquivo estruturado não encontrado: '{prata_path}'. Pulando...")
            continue
            
        with open(prata_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Tenta carregar o mapeamento de avaliações do JSON-LD a partir dos arquivos BRONZE deste termo (onde os scripts estão intactos)
        reviews_map = {}
        for p in range(1, config.get_max_paginas() + 1):
            bronze_path = os.path.join(BRONZE_DIR, f"bronze_{nome_arquivo_base}_p{p}.html")
            if os.path.exists(bronze_path):
                try:
                    with open(bronze_path, "r", encoding="utf-8") as bf:
                        b_soup = BeautifulSoup(bf.read(), "html.parser")
                        ld_json_tag = b_soup.find('script', type='application/ld+json')
                        if ld_json_tag:
                            ld_data = json.loads(ld_json_tag.string)
                            if isinstance(ld_data, dict) and "@graph" in ld_data:
                                for item in ld_data["@graph"]:
                                    if item.get("@type") == "Product":
                                        name = item.get("name", "").strip().lower()
                                        rating_count = item.get("aggregateRating", {}).get("ratingCount", 0)
                                        if name:
                                            reviews_map[name] = int(rating_count)
                except Exception as e:
                    print(f"   ⚠️ Erro ao ler JSON-LD do arquivo Bronze p{p} para '{termo}': {e}")
        
        produtos_cards = soup.find_all(["li", "div"], class_=re.compile(r"ui-search-layout__item|poly-card|ui-search-result"))
        if not produtos_cards:
            title_tags = soup.find_all(["h2", "a"], class_=re.compile(r"ui-search-item__title|poly-component__title|poly-box"))
            cards_seen = set()
            for t in title_tags:
                parent_card = t.find_parent(["li", "div"], class_=re.compile(r"ui-search-layout__item|poly-card|ui-search-result|poly-card-container"))
                if not parent_card:
                    parent_card = t.parent
                if parent_card and id(parent_card) not in cards_seen:
                    cards_seen.add(id(parent_card))
                    produtos_cards.append(parent_card)
        
        resultados_ouro = []
        
        for produto in produtos_cards:
            try:
                titulo_tag = produto.find(["h2", "a"], class_=re.compile(r"ui-search-item__title|poly-component__title|poly-box"))
                if not titulo_tag: continue
                titulo = titulo_tag.text.strip()
                
                # Aplica o filtro de relevância
                if not verificar_relevancia(titulo, termo):
                    continue
                
                link_tag = produto.find("a")
                url_anuncio = link_tag["href"] if link_tag and "href" in link_tag.attrs else ""
                
                if not url_anuncio:
                    continue
                
                # Deduplicação por Título normalizado ou URL
                norm_title = re.sub(r"[^\w\s]", "", titulo.lower()).strip()
                if url_anuncio in urls_processadas or norm_title in titulos_processados:
                    continue
                urls_processadas.add(url_anuncio)
                titulos_processados.add(norm_title)
                
                preco, preco_debug_log = extrair_preco_card_meli(produto)
                print(f"   🔎 [AUDITORIA PREÇO ML] '{titulo[:35]}...' => R$ {preco:.2f} ({preco_debug_log})")
                
                # Extrai vendas do HTML
                vendas_texto = extrair_vendas_texto(produto)
                vendas = limpar_vendas(vendas_texto)
                
                # Se não encontrou vendas explícitas (comum no layout novo do ML), usa o ratingCount como proxy
                if vendas == 0:
                    titulo_normalizado = titulo.strip().lower()
                    vendas = reviews_map.get(titulo_normalizado, 0)
                
                # Extrai vendedor do HTML (Prioridade para Nome do Vendedor/Loja Oficial, Fallback para Localização e ID Único)
                vendedor_tag = produto.find(["span", "div", "a"], class_=re.compile(r"poly-component__seller|ui-search-official-store-label|ui-search-item__group__element|ui-search-item__seller"))
                vendedor = None
                if vendedor_tag:
                    raw_seller = vendedor_tag.text.replace("Por", "").replace("por", "").strip()
                    if raw_seller and len(raw_seller) < 45:
                        vendedor = raw_seller
                
                loc_name = None
                loc_tag = produto.find(["span", "div"], class_=re.compile(r"ui-search-item__location|poly-component__location"))
                if loc_tag and loc_tag.text.strip() and len(loc_tag.text.strip()) < 40:
                    loc_name = loc_tag.text.strip()
                if not loc_name:
                    loc_match = re.search(r"\b(São Paulo|Minas Gerais|Santa Catarina|Rio de Janeiro|Paraná|Rio Grande do Sul|Bahia|Ceará|Pernambuco|Goiás|Espírito Santo|Distrito Federal|Maranhão|Paraíba|Amazonas|Mato Grosso|Rio Grande do Norte|Piauí|Alagoas|Sergipe|Rondônia|Tocantins|Acre|Amapá|Roraima|Internacional)\b", produto.text)
                    if loc_match:
                        loc_name = loc_match.group(1)

                # Extrai sufixo do ID do anúncio ML (ex: MLB-4211214797 -> #4797)
                ml_id_match = re.search(r"MLB-?(\d+)", url_anuncio)
                ml_suffix = ml_id_match.group(1)[-4:] if ml_id_match else None

                if vendedor:
                    pass
                elif loc_name and ml_suffix:
                    vendedor = f"Loja em {loc_name} (#{ml_suffix})"
                elif loc_name:
                    vendedor = f"Loja em {loc_name}"
                elif ml_suffix:
                    vendedor = f"Loja Mercado Livre (#{ml_suffix})"
                else:
                    vendedor = "Loja Mercado Livre"
                
                resultados_ouro.append({
                    "termo_busca": termo,
                    "plataforma": "mercado_livre",
                    "titulo": titulo,
                    "preco": preco,
                    "vendas_quantidade": vendas,
                    "url_anuncio": url_anuncio,
                    "vendedor": vendedor
                })
            except Exception:
                continue
  
        if len(resultados_ouro) == 0:
            print(f"   ⚠️ DIAGNÓSTICO ML OURO: 0 produtos extraídos para o termo '{termo}'!")
            h2_list = [t.text.strip()[:40] for t in soup.find_all("h2")[:5]]
            print(f"      -> Primeiros H2s no HTML: {h2_list}")
            print(f"      -> Quantidade de links <a> no HTML: {len(soup.find_all('a'))}")
            print(f"      -> Quantidade de <li> no HTML: {len(soup.find_all('li'))}")
            snippet = soup.text.strip()[:200].replace('\n', ' ')
            print(f"      -> Trecho de texto do HTML: '{snippet}'")

        print(f"   🥇 OURO: {len(resultados_ouro)} produtos extraídos para o termo '{termo}'.")
        todos_dados_ouro.extend(resultados_ouro)
  
    # Ordena os produtos pela quantidade de vendas em ordem decrescente (mais vendidos primeiro)
    todos_dados_ouro.sort(key=lambda x: x.get("vendas_quantidade", 0), reverse=True)
  
    # Grava o JSON final
    ouro_path = os.path.join(OURO_DIR, "dados_meli.json")
    with open(ouro_path, "w", encoding="utf-8") as f:
        json.dump(todos_dados_ouro, f, indent=4, ensure_ascii=False)
        
    print(f"✅ [Etapa Ouro] JSON gerado! {len(todos_dados_ouro)} itens salvos em '{ouro_path}'.")
    
    print("\n☁️ [Etapa Nuvem] Enviando dados para o Supabase...")
    try:
        supabase = conectar_supabase()
        enviados = 0
        for item in todos_dados_ouro:
            try:
                produto_id = upsert_produto(
                    supabase=supabase,
                    plataforma="meli",
                    id_externo=item["url_anuncio"].split("-")[1] if "-" in item["url_anuncio"] else item["titulo"][:20],
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
                
        print(f"✅ [Etapa Nuvem] {enviados} produtos do Mercado Livre sincronizados com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao conectar com Supabase: {e}")

if __name__ == "__main__":
    fase_bronze()
    fase_prata()
    fase_ouro()
