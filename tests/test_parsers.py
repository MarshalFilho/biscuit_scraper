import pytest

def test_deduplicate_sponsored_url():
    """
    Testa se URLs patrocinadas (click1.mercadolivre.com.br) 
    têm o parâmetro 'ad' removido ou são normalizadas corretamente.
    (Exemplo de validação teórica para o parser)
    """
    raw_url = "https://click1.mercadolivre.com.br/mclics/clicks/mac?ad=123&url=https://produto.mercadolivre.com.br/MLB-123"
    
    # Simulação da função de limpeza de URL
    def limpar_url(url):
        import urllib.parse
        if "click1.mercadolivre" in url or "mclics" in url:
            parsed = urllib.parse.urlparse(url)
            qs = urllib.parse.parse_qs(parsed.query)
            if 'url' in qs:
                return qs['url'][0]
        return url
        
    cleaned = limpar_url(raw_url)
    assert cleaned == "https://produto.mercadolivre.com.br/MLB-123"


def test_extract_discount_price():
    """
    Garante que o parser reconheça qual é o preço final 
    quando o HTML tem preço cortado (<del> ou <s>).
    """
    html_snippet = '''
    <div class="price">
      <del class="old-price">R$ 50,00</del>
      <span class="current-price">R$ 35,00</span>
    </div>
    '''
    
    # Simulação do parser
    def parse_price(html):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        current = soup.find("span", class_="current-price")
        if current:
            return float(current.text.replace("R$", "").replace(",", ".").strip())
        return 0.0
        
    price = parse_price(html_snippet)
    assert price == 35.0
