import sys
import os
import json
import pandas as pd
import random

# Permite importação dos módulos da pasta src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_DIR, REPORTS_DIR

# Lista de caminhos para os dados das plataformas
ARQUIVOS_JSON = [
    os.path.join(DATA_DIR, "shopee", "ouro", "dados_shopee.json"),
    os.path.join(DATA_DIR, "mercado_livre", "ouro", "dados_meli.json")
]

ARQUIVO_SAIDA = os.path.join(REPORTS_DIR, "Relatorio_Inteligencia.xlsx")

def carregar_dados():
    todos_dados = []
    for caminho_completo in ARQUIVOS_JSON:
        if os.path.exists(caminho_completo):
            with open(caminho_completo, 'r', encoding='utf-8') as f:
                try:
                    dados = json.load(f)
                    for d in dados:
                        # Unifica preco se vier do formato antigo
                        if "preco" not in d:
                            d["preco"] = d.get("preco_atual", d.get("preco_original", 0.0))
                        d["preco"] = float(d.get("preco", 0.0))
                        d["vendas_quantidade"] = int(d.get("vendas_quantidade", 0))
                    todos_dados.extend(dados)
                except json.JSONDecodeError:
                    print(f"Aviso: Erro ao ler o arquivo {caminho_completo}. Ele pode estar vazio ou corrompido.")
        else:
            print(f"Aviso: Arquivo {caminho_completo} não encontrado. Execute o respectivo scraper primeiro.")
            
    return todos_dados

def gerar_relatorio():
    dados = carregar_dados()
    
    if not dados:
        print("Nenhum dado encontrado para gerar o relatório.")
        return
        
    df_todos = pd.DataFrame(dados)
    
    # Remover duplicados globais (mantém a ocorrência com maior quantidade de vendas)
    if not df_todos.empty and "url_anuncio" in df_todos.columns:
        # Ordenar antes para garantir que a linha com maior venda seja preservada no keep='first'
        if "vendas_quantidade" in df_todos.columns:
            df_todos = df_todos.sort_values(by="vendas_quantidade", ascending=False)
        df_todos = df_todos.drop_duplicates(subset=["url_anuncio"], keep="first")
        
    # Ordenar por vendas geral (caso já não esteja)
    if "vendas_quantidade" in df_todos.columns:
        df_todos = df_todos.sort_values(by="vendas_quantidade", ascending=False)
        
    # Filtrar os dataframes individuais do Top 20 mais vendidos
    df_shopee_top = df_todos[df_todos["plataforma"].str.lower() == "shopee"].head(20)
    df_meli_top = df_todos[df_todos["plataforma"].str.lower() == "mercado_livre"].head(20)
    
    cols_indiv = ["termo_busca", "titulo", "preco", "vendas_quantidade", "url_anuncio"]
    
    # Se algum df estiver vazio, garante a estrutura correta de colunas
    df_shopee_top = df_shopee_top[cols_indiv] if not df_shopee_top.empty else pd.DataFrame(columns=cols_indiv)
    df_meli_top = df_meli_top[cols_indiv] if not df_meli_top.empty else pd.DataFrame(columns=cols_indiv)
    
    try:
        # Criar escritor do pandas excel
        writer = pd.ExcelWriter(ARQUIVO_SAIDA, engine='xlsxwriter')
        workbook = writer.book
        worksheet = workbook.add_worksheet('Dados Gerais')
        
        # Habilitar linhas de grade
        worksheet.hide_gridlines(0)
        
        # Cores temáticas para os cabeçalhos mesclados
        color_shopee = '#FE5722'  # Laranja Shopee
        color_meli = '#FFE600'    # Amarelo Mercado Livre
        color_todos = '#4CAF50'   # Verde Consolidado
        
        # Definição dos formatos premium de cabeçalhos
        title_shopee = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'fg_color': color_shopee, 'font_color': '#FFFFFF', 'font_size': 12, 'border': 1})
        title_meli = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'fg_color': color_meli, 'font_color': '#000000', 'font_size': 12, 'border': 1})
        title_todos = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'fg_color': color_todos, 'font_color': '#FFFFFF', 'font_size': 12, 'border': 1})
        
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#F2F2F2', 'border': 1, 'font_size': 10})
        
        # Formatos das células
        cell_center = workbook.add_format({'border': 1, 'font_size': 9, 'align': 'center', 'valign': 'vcenter'})
        cell_left = workbook.add_format({'border': 1, 'font_size': 9, 'align': 'left', 'valign': 'vcenter'})
        currency_format = workbook.add_format({'num_format': 'R$ #,##0.00', 'border': 1, 'font_size': 9, 'align': 'right', 'valign': 'vcenter'})
        integer_format = workbook.add_format({'num_format': '#,##0', 'border': 1, 'font_size': 9, 'align': 'center', 'valign': 'vcenter'})
        hyperlink_format = workbook.add_format({'font_color': 'blue', 'underline': 1, 'border': 1, 'font_size': 9, 'align': 'center', 'valign': 'vcenter'})
        
        # Função interna auxiliar para desenhar uma tabela
        def escrever_tabela(df_tabela, start_col, titulo, formato_titulo, is_consolidated=False):
            # Cabeçalho mesclado da tabela
            end_col = start_col + (5 if is_consolidated else 4)
            worksheet.merge_range(0, start_col, 0, end_col, titulo, formato_titulo)
            
            # Subcabeçalhos
            headers = ["Termo de Busca", "Plataforma", "Título", "Preço", "Vendas", "Link"] if is_consolidated else ["Termo de Busca", "Título", "Preço", "Vendas", "Link"]
            for col_idx, header_text in enumerate(headers):
                worksheet.write(1, start_col + col_idx, header_text, header_format)
                
            # Dados da tabela
            row_idx = 2
            for _, row in df_tabela.iterrows():
                if is_consolidated:
                    vals = [
                        row.get("termo_busca", ""),
                        row.get("plataforma", ""),
                        row.get("titulo", ""),
                        row.get("preco", 0.0),
                        row.get("vendas_quantidade", 0),
                        row.get("url_anuncio", "")
                    ]
                else:
                    vals = [
                        row.get("termo_busca", ""),
                        row.get("titulo", ""),
                        row.get("preco", 0.0),
                        row.get("vendas_quantidade", 0),
                        row.get("url_anuncio", "")
                    ]
                    
                for col_idx, val in enumerate(vals):
                    curr_col = start_col + col_idx
                    # Descobrir tipo de campo
                    is_link = (col_idx == len(vals) - 1)
                    is_price = (headers[col_idx] == "Preço")
                    is_sales = (headers[col_idx] == "Vendas")
                    is_title = (headers[col_idx] == "Título")
                    
                    if is_link:
                        if val:
                            worksheet.write_url(row_idx, curr_col, val, string="Ver Anúncio", cell_format=hyperlink_format)
                        else:
                            worksheet.write(row_idx, curr_col, "-", cell_center)
                    elif is_price:
                        worksheet.write_number(row_idx, curr_col, float(val), currency_format)
                    elif is_sales:
                        worksheet.write_number(row_idx, curr_col, int(val), integer_format)
                    elif is_title:
                        worksheet.write_string(row_idx, curr_col, str(val), cell_left)
                    else:
                        worksheet.write_string(row_idx, curr_col, str(val), cell_center)
                row_idx += 1
        
        # 1. Escrever Tabela Shopee (Colunas A-E | 0-4)
        escrever_tabela(df_shopee_top, 0, "TOP 20 - SHOPEE", title_shopee)
        
        # Coluna F (5) é o separador vazio
        
        # 2. Escrever Tabela Mercado Livre (Colunas G-K | 6-10)
        escrever_tabela(df_meli_top, 6, "TOP 20 - MERCADO LIVRE", title_meli)
        
        # Coluna L (11) é o separador vazio
        
        # 3. Escrever Tabela Consolidada (Colunas M-R | 12-17)
        escrever_tabela(df_todos, 12, "CONSOLIDADO - TODOS OS PRODUTOS", title_todos, is_consolidated=True)
        
        # Definir larguras de colunas padronizadas
        col_widths = {
            # Shopee
            0: 16, 1: 35, 2: 12, 3: 10, 4: 12,
            # Separador
            5: 3,
            # Mercado Livre
            6: 16, 7: 35, 8: 12, 9: 10, 10: 12,
            # Separador
            11: 3,
            # Consolidado
            12: 16, 13: 15, 14: 35, 15: 12, 16: 10, 17: 12
        }
        for col_idx, width in col_widths.items():
            worksheet.set_column(col_idx, col_idx, width)
            
        # Altura das linhas de cabeçalho
        worksheet.set_row(0, 26)
        worksheet.set_row(1, 20)
        
        # Altura das linhas de dados
        max_rows = max(len(df_shopee_top), len(df_meli_top), len(df_todos))
        for r in range(2, max_rows + 5):
            worksheet.set_row(r, 18)
            
        # Fechar o gravador para salvar
        writer.close()
        print(f"Relatório gerado com sucesso: {ARQUIVO_SAIDA}")
    except PermissionError:
        print(f"\n[ERRO DE PERMISSÃO] Não foi possível salvar o arquivo Excel porque ele está aberto no Microsoft Excel ou outro programa.")
        print(f"Por favor, FECHE o arquivo '{ARQUIVO_SAIDA}' e tente novamente.")

if __name__ == "__main__":
    gerar_relatorio()
