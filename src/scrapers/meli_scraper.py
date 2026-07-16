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

# Configuração dinâmica de diretórios para o Mercado Livre
PLATFORM_DIRS = get_platform_dirs("mercado_livre")
BRONZE_DIR = PLATFORM_DIRS["bronze"]
PRATA_DIR = PLATFORM_DIRS["prata"]
OURO_DIR = PLATFORM_DIRS["ouro"]

def limpar_preco(texto_preco):
    if not texto_preco: return 0.0
    num = texto_preco.replace(".", "").replace(",", ".").strip()
    try:
        return float(re.sub(r"[^\d.]", "", num))
    except ValueError:
        return 0.0

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
    de cada termo de busca na pasta data/mercado_livre/bronze/ (coleta até MAX_PAGINAS páginas).
    """
    print(f"\n🚀 [Etapa Bronze] Iniciando raspagem da web (até {MAX_PAGINAS} páginas por termo)...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            args=["--disable-blink-features=AutomationControlled"]
        ) 
        
        auth_path = os.path.join(AUTH_DIR, "auth_meli.json")
        context_args = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        if os.path.exists(auth_path):
            context_args["storage_state"] = auth_path
            
        context = browser.new_context(**context_args)
        page = context.new_page()
 
        for termo in config.get_termos_busca():
            nome_arquivo_base = termo.replace(" ", "_")
            print(f"\n🔎 Termo de busca: '{termo}'")
            
            termo_url = termo.replace(' ', '-')
            url = f"https://lista.mercadolivre.com.br/{termo_url}"
            
            # Acessa a primeira página
            print(f"   Acessando página 1: {url}")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
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
                if "/captcha/" in page.url or "abuse-china-wall" in page.content():
                    print("   ⚠️ CAPTCHA detectado! Resolva no navegador...")
                    try:
                        page.wait_for_selector(".ui-search-results, .poly-search-results", timeout=60000)
                    except:
                        print("   ⏳ Falha no captcha ou timeout excedido. Pulando termo...")
                        break
                
                html_renderizado = page.content()
                
                # Salva o arquivo Bronze localmente
                bronze_path = os.path.join(BRONZE_DIR, f"bronze_{nome_arquivo_base}_p{pagina}.html")
                with open(bronze_path, "w", encoding="utf-8") as f:
                    f.write(html_renderizado)
                print(f"   🥉 BRONZE: Arquivo '{bronze_path}' salvo com sucesso.")
                
                # Se já alcançamos a página máxima configurada, interrompemos
                if pagina == MAX_PAGINAS:
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
 
        browser.close()
    print("✅ [Etapa Bronze] Concluída!")

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
        for p in range(1, MAX_PAGINAS + 1):
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
        for p in range(1, MAX_PAGINAS + 1):
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
        
        produtos_cards = soup.find_all(["li", "div"], class_=re.compile(r"ui-search-layout__item|poly-card"))
        
        resultados_ouro = []
        urls_processadas = set()
        
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
                
                if not url_anuncio or url_anuncio in urls_processadas:
                    continue
                urls_processadas.add(url_anuncio)
                
                preco_tag = produto.find("span", class_="andes-money-amount__fraction")
                preco = limpar_preco(preco_tag.text) if preco_tag else 0.0
                
                # Extrai vendas do HTML
                vendas_texto = extrair_vendas_texto(produto)
                vendas = limpar_vendas(vendas_texto)
                
                # Se não encontrou vendas explícitas (comum no layout novo do ML), usa o ratingCount como proxy
                if vendas == 0:
                    titulo_normalizado = titulo.strip().lower()
                    vendas = reviews_map.get(titulo_normalizado, 0)
                
                resultados_ouro.append({
                    "termo_busca": termo,
                    "plataforma": "mercado_livre",
                    "titulo": titulo,
                    "preco": preco,
                    "vendas_quantidade": vendas,
                    "url_anuncio": url_anuncio,
                })
            except Exception as e:
                continue
  
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
                
        print(f"✅ [Etapa Nuvem] {enviados} produtos do Mercado Livre sincronizados com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao conectar com Supabase: {e}")

if __name__ == "__main__":
    fase_bronze()
    fase_prata()
    fase_ouro()
