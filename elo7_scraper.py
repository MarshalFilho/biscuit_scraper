import json
import requests
import time
from bs4 import BeautifulSoup
from config import TERMOS_BUSCA

OUTPUT_FILE = "dados_elo7.json"
PLATAFORMA = "Elo7"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

def scrape_elo7_termo(termo):
    \"\"\"
    Função base para buscar um termo no Elo7.
    \"\"\"
    print(f"[{PLATAFORMA}] Buscando termo: {termo}")
    url = f"https://www.elo7.com.br/lista/{termo.replace(' ', '-')}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Erro ao acessar {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    resultados = []
    
    # TODO: Implementar extração real usando seletores do Elo7
    
    # Mock de dados para exemplificar a estrutura
    item_mock = {
        "termo_busca": termo,
        "plataforma": PLATAFORMA,
        "titulo": "Exemplo Produto Elo7 - " + termo,
        "preco_atual": 0.0,
        "preco_original": 0.0,
        "vendas_quantidade": 0,
        "avaliacao_nota": 0.0,
        "avaliacao_quantidade": 0,
        "url_anuncio": url,
        "url_imagem": ""
    }
    resultados.append(item_mock)
    
    return resultados

def main():
    todos_dados = []
    
    for termo in TERMOS_BUSCA:
        dados_termo = scrape_elo7_termo(termo)
        todos_dados.extend(dados_termo)
        time.sleep(2)
        
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(todos_dados, f, ensure_ascii=False, indent=4)
    print(f"[{PLATAFORMA}] Extração concluída. Dados salvos em {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
