import sys
import os
import argparse

# Permite importação dos módulos da pasta src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    parser = argparse.ArgumentParser(description="Pipeline de Inteligência e Extração para Biscuit")
    parser.add_argument("--plataforma", choices=["meli", "shopee", "todos"], default="todos",
                        help="Plataforma de e-commerce a raspar (padrão: todos)")
    parser.add_argument("--excel", action="store_true", help="Gerar apenas o relatório consolidado em Excel")
    parser.add_argument("--login", action="store_true", help="Executar ferramenta para salvar login manual do ML")
    parser.add_argument("--login-shopee", action="store_true", help="Executar ferramenta para salvar login manual da Shopee")
    
    args = parser.parse_args()
    
    if args.login:
        from utils.salvar_login import gerar_sessao
        gerar_sessao("meli")
        return

    if args.login_shopee:
        from utils.salvar_login import gerar_sessao
        gerar_sessao("shopee")
        return
        
    if args.excel:
        from utils.gerador_excel import gerar_relatorio
        gerar_relatorio()
        return
        
    # Executa os scrapers selecionados
    if args.plataforma in ["meli", "todos"]:
        print("\n=== Executando Scraper Mercado Livre ===")
        from scrapers.meli_scraper import fase_bronze, fase_prata, fase_ouro
        fase_bronze()
        fase_prata()
        fase_ouro()
        
    if args.plataforma in ["shopee", "todos"]:
        print("\n=== Executando Scraper Shopee ===")
        from scrapers.shopee_scraper import fase_bronze, fase_prata, fase_ouro
        fase_bronze()
        fase_prata()
        fase_ouro()
            
    # Auto-geração do relatório ao fim de rodar tudo ou uma plataforma
    print("\n=== Gerando Relatório Consolidado Excel ===")
    from utils.gerador_excel import gerar_relatorio
    gerar_relatorio()

if __name__ == "__main__":
    main()
