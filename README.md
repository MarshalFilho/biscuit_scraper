# Pipeline de Inteligência e Extração para E-commerce

Este é um pipeline automatizado de raspagem de dados e inteligência competitiva para e-commerce. O sistema utiliza **Playwright** e **BeautifulSoup** para pesquisar termos, extrair informações estruturadas de anúncios (título, preço, volume de vendas, link) do Mercado Livre, Shopee e Elo7, aplicando filtros dinâmicos de relevância antes de consolidar tudo em um relatório premium no **Excel** e em um **Dashboard Interativo** via Streamlit.

O projeto segue a **Arquitetura Medalhão (Medallion Architecture)** para gerenciamento e limpeza de dados (divido em camadas Bronze, Prata e Ouro) e foi reestruturado de forma totalmente genérica, permitindo analisar qualquer nicho de mercado (como biscuit, crochê, velas, MDF, etc.) apenas alterando configurações simples.

---

## 📂 Estrutura do Projeto

```text
biscuit_scraper/
│
├── dashboard.py                     # Dashboard interativo em Streamlit (Interface principal)
├── config_app.json                  # Configurações de busca e filtros persistentes
├── data/                            # Camadas de dados organizadas por plataforma
│   ├── auth/                        # Dados de login/sessão persistidos do navegador
│   │   └── auth.json
│   └── mercado_livre/               # Dados do Mercado Livre (exemplo de plataforma)
│       ├── bronze/                  # HTML bruto indexado por termo e página
│       ├── prata/                   # HTML mesclado e limpo de tags desnecessárias
│       └── ouro/                    # JSON consolidado, limpo, filtrado e ordenado
│           └── dados_meli.json
│
├── reports/                         # Relatórios exportados para análise humana
│   └── Relatorio_Inteligencia.xlsx  # Planilha premium gerada automaticamente
│
└── src/                             # Código fonte da aplicação
    ├── __init__.py
    ├── config.py                    # Ponte para carregar config_app.json
    ├── main.py                      # Ponto de entrada central (CLI)
    │
    ├── scrapers/                    # Robôs de coleta específicos de cada site
    │   ├── __init__.py
    │   ├── meli_scraper.py          # Scraper do Mercado Livre
    │   ├── shopee_scraper.py        # Scraper da Shopee
    │   └── elo7_scraper.py          # Scraper do Elo7
    │
    └── utils/                       # Ferramentas auxiliares do pipeline
        ├── __init__.py
        ├── gerador_excel.py         # Carrega dados Ouro e monta o Excel formatado
        └── salvar_login.py          # Script para login manual no navegador
```

---

## ⚙️ Configurações de Busca e Filtros (`config_app.json`)

Todas as regras de relevância e buscas ficam salvas em `config_app.json` e podem ser configuradas de forma visual e direta na aba **"⚙️ Configurações da IA"** do Dashboard Interativo.

### Principais parâmetros configuráveis:

- `TERMOS_BUSCA`: Lista de palavras a pesquisar nas plataformas.
- `PALAVRA_OBRIGATORIA_GLOBAL`: Palavra que **deve** aparecer em qualquer anúncio para ele ser válido (ex: `"biscuit"`). Se deixado em branco (`""`), essa verificação é desativada.
- `PALAVRAS_NEGATIVAS`: Lista de palavras indesejadas (ex: ferramentas, colas, moldes, resina). Se o anúncio tiver alguma delas parcial ou totalmente no título, será sumariamente ignorado.
- `PALAVRAS_NEGATIVAS_EXATAS`: Palavras descartadas apenas se aparecerem inteiras (evita confundir `"ração"` com `"numeração"`).
- `REGRAS_TIPO_PRODUTO`: Garante que, se você pesquisar por `"chaveiro"`, o anúncio aceito tenha palavras como `"chaveir"`.
- `REGRAS_CONTEUDO_BUSCA`: Validações de tema adicionais específicas por termo de busca (ex: se pesquisar `"rim"`, o título precisa ter `"rim"` ou `"rins"`).

---

## 🚀 Como Usar o Projeto

### 1. Pré-requisitos

Certifique-se de ter o Python 3 instalado. Instale as bibliotecas necessárias rodando no seu terminal:

```powershell
pip install pandas beautifulsoup4 playwright xlsxwriter openpyxl streamlit plotly
```

E instale o navegador controlado pelo Playwright:

```powershell
playwright install
```

---

### 2. Acessar o Dashboard Interativo (Recomendado)

A melhor forma de utilizar o sistema é através do painel visual. No terminal, execute:

```powershell
streamlit run dashboard.py
```

Isso abrirá uma página no seu navegador com três abas principais:

1. **📊 Dashboard Analítico:** Visualize gráficos de mercado, os top nichos mais vendidos e explore os anúncios em uma tabela interativa com opções de exportação CSV.
2. **⚙️ Configurações da IA:** Edite facilmente seus termos de busca, quantidade de páginas e palavras negativas, salvando tudo diretamente no `config_app.json`.
3. **🚀 Centro de Extração:** Inicie varreduras (robôs) em plataformas (Mercado Livre e Shopee) com apenas um clique e acompanhe os logs em tempo real.

---

### 3. Comandos de Execução (CLI Opcional)

Se você preferir executar sem interface gráfica, você pode usar o terminal gerenciando tudo a partir do arquivo central `src/main.py`.

#### A. Salvar Login (Evitar Bloqueios/Captchas)

Se o Mercado Livre começar a pedir verificação de identidade ou Captchas constantes, você pode logar manualmente uma vez e salvar a sessão no seu computador para o robô utilizar:

```powershell
py src/main.py --login
```

_Uma janela do navegador Chrome abrirá. Faça login com seu e-mail e senha normalmente. Quando estiver logado na página inicial, volte ao terminal e pressione **ENTER**._

#### B. Rodar a Raspagem Completa via CLI

Para rodar a raspagem (Fases Bronze, Prata e Ouro) para uma plataforma via terminal:

```powershell
py src/main.py --plataforma meli
```

_Ao final da coleta, ele gerará automaticamente o arquivo Excel atualizado em `reports/Relatorio_Inteligencia.xlsx`._

#### C. Gerar Apenas o Excel

Se você já rodou os scrapers e apenas quer gerar a planilha a partir dos dados já salvos localmente:

```powershell
py src/main.py --excel
```

> 💡 **Nota sobre Erros de Permissão no Excel:** Se você tentar gerar a planilha enquanto o arquivo `Relatorio_Inteligencia.xlsx` estiver aberto no Microsoft Excel, o script não irá quebrar. Ele exibirá uma mensagem amigável no console solicitando que você feche a planilha e tente novamente.
