import json
import pandas as pd
import os

ARQUIVOS_JSON = [
    "dados_shopee.json",
    "dados_meli.json",
    "dados_elo7.json"
]

ARQUIVO_SAIDA = "Relatorio_Inteligencia.xlsx"

def carregar_dados():
    todos_dados = []
    for arquivo in ARQUIVOS_JSON:
        if os.path.exists(arquivo):
            with open(arquivo, 'r', encoding='utf-8') as f:
                try:
                    dados = json.load(f)
                    todos_dados.extend(dados)
                except json.JSONDecodeError:
                    print(f"Aviso: Erro ao ler o arquivo {arquivo}. Ele pode estar vazio ou corrompido.")
        else:
            print(f"Aviso: Arquivo {arquivo} não encontrado. Execute os scrapers primeiro.")
            
    return todos_dados

def gerar_relatorio():
    dados = carregar_dados()
    
    if not dados:
        print("Nenhum dado encontrado para gerar o relatório.")
        return
        
    # Converter para DataFrame
    df = pd.DataFrame(dados)
    
    # Criar um escritor Pandas Excel usando XlsxWriter como engine
    writer = pd.ExcelWriter(ARQUIVO_SAIDA, engine='xlsxwriter')
    
    # Escrever o DataFrame na aba 'Dados Gerais'
    df.to_excel(writer, sheet_name='Dados Gerais', index=False)
    
    # Obter os objetos workbook e worksheet do xlsxwriter
    workbook  = writer.book
    worksheet = writer.sheets['Dados Gerais']
    
    # Definir formatos premium
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#D7E4BC',
        'border': 1
    })
    
    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00'})
    
    # Escrever os cabeçalhos com o formato
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
        
    # Ajustar as larguras das colunas
    worksheet.set_column('A:B', 20)  # termo_busca, plataforma
    worksheet.set_column('C:C', 50)  # titulo
    worksheet.set_column('D:E', 15, currency_format) # precos
    worksheet.set_column('F:H', 15)  # vendas, avaliacoes
    worksheet.set_column('I:J', 60)  # urls
    
    # Salvar o arquivo
    writer.close()
    print(f"Relatório gerado com sucesso: {ARQUIVO_SAIDA}")

if __name__ == "__main__":
    gerar_relatorio()
