# 🍪 Biscuit Scraper & Market Intelligence

> Sistema de extração de dados (**Mercado Livre** e **Shopee**), análise de concorrência e geração de insights com **Inteligência Artificial (Google Gemini)** para o nicho de **Biscuit e Artesanato**, integrado a um painel web analítico em **Nuxt 3**.

---

## 🎯 Objetivo do Projeto

Automatizar o monitoramento do mercado de Biscuit nos principais marketplaces do Brasil, coletando dados de anúncios, preços, vendas e concorrentes para responder perguntas estratégicas como:
- Quais são os produtos e topos de bolo mais vendidos?
- Quais são os maiores vendedores do nicho?
- Qual é a faixa de preço ideal para cada tipo de peça de biscuit?
- Quais oportunidades de mercado e palavras-chave em alta a IA identifica?

---

## 🛠️ Tecnologias Utilizadas

- **Backend & Scraping**: Python 3.12, BeautifulSoup4, `curl_cffi` (bypass de proteções TLS/WAF), Playwright, Pandas.
- **Inteligência Artificial**: Google Gemini API (geração de relatórios estratégicos e categorização).
- **Banco de Dados & Autenticação**: Supabase (PostgreSQL com Row Level Security).
- **Frontend**: Nuxt 3, Vue 3, ApexCharts, Lucide Icons, Vanilla CSS (tema escuro com Glassmorphism).

---

## 🏗️ Como Funciona o Pipeline

```
[Mercado Livre / Shopee]
         │
         ▼
[1. Bronze] Coleta do HTML bruto das buscas
         │
         ▼
[2. Prata]  Extração, limpeza de preços e deduplicação de anúncios
         │
         ▼
[3. Ouro]   Consolidação de KPIs, métricas e envio ao Supabase
         │
         ▼
[4. IA]     Geração de diagnósticos de mercado com Google Gemini
         │
         ▼
[5. Web]    Visualização no Dashboard Nuxt 3 (Gráficos, Filtros e Relatórios)
```

---

## 📂 Estrutura de Arquivos

```text
biscuit_scraper/
│
├── iniciar_worker.bat               # Atalho Windows para iniciar o extrator/worker
├── requirements.txt                 # Dependências Python do backend
├── config_app.json                  # Termos de busca, blacklist e regras de categorias
│
├── backend/                         # Motor de raspagem, IA e sincronização
│   ├── main.py                      # Script principal (CLI e Daemon)
│   ├── config.py                    # Leitor das configurações do app
│   ├── ai/
│   │   ├── categorizer.py           # Categorização de produtos
│   │   └── insights_generator.py   # Geração de relatórios com Gemini
│   ├── scrapers/
│   │   ├── meli_scraper.py          # Extrator do Mercado Livre
│   │   ├── shopee_scraper.py        # Extrator da Shopee
│   │   └── login_session.py         # Gerenciamento de cookies/sessão
│   ├── scripts/
│   │   ├── init_user_configs.py     # Inicialização de configurações no Supabase
│   │   └── setup_roles_and_users.py # Configuração inicial de usuários
│   └── utils/
│       ├── ai_engine.py             # Conexão com a API do Google Gemini
│       ├── bot_detector.py          # Detecção de bloqueios/CAPTCHA
│       ├── limpar_dados_antigos.py  # Limpeza de coletas legadas
│       ├── relevancia.py            # Filtros de relevância e palavras-chave
│       └── supabase_client.py       # Integração com banco Supabase
│
├── frontend/                        # Painel analítico em Nuxt 3
│   ├── assets/css/main.css          # Estilos e design system do painel
│   ├── components/                  # Componentes do dashboard (Gráficos, Tabelas, Filtros)
│   ├── composables/                 # Composables (i18n, Supabase, Toasts, Modais)
│   ├── pages/
│   │   ├── index.vue                # Dashboard analítico principal
│   │   ├── config.vue               # Configurações de busca e categorias
│   │   └── login.vue                # Autenticação de usuário
│   ├── nuxt.config.ts               # Configuração do Nuxt
│   └── package.json                 # Dependências do frontend
│
├── database/
│   └── database_setup.sql           # Schema SQL para criação das tabelas no Supabase
│
└── tests/
    └── test_parsers.py              # Testes unitários dos parsers de dados
```

---

## 🚀 Como Rodar o Projeto

### 1. Configurar o `.env`
Crie um arquivo `.env` na raiz do projeto seguindo o modelo do `.env.example`:

```env
# Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_service_role_key
SUPABASE_USER_ID=seu_user_id

# Google Gemini
GEMINI_API_KEY=sua_chave_gemini

# Frontend Nuxt
NUXT_PUBLIC_SUPABASE_URL=https://seu-projeto.supabase.co
NUXT_PUBLIC_SUPABASE_ANON_KEY=sua_anon_key
```

### 2. Configurar o Banco no Supabase
1. No painel do **Supabase**, abra o **SQL Editor**.
2. Execute o script [`database/database_setup.sql`](database/database_setup.sql) para criar as tabelas e políticas necessárias.

### 3. Rodar o Backend / Scraper

- **Modo Coleta Manual:**
  ```bash
  python backend/main.py --plataforma todos
  ```
  *(ou `--plataforma meli` / `--plataforma shopee`)*

- **Modo Daemon (Segundo plano):**
  - No Windows, dê dois cliques em `iniciar_worker.bat` ou execute:
  ```bash
  python backend/main.py --daemon
  ```

### 4. Rodar o Frontend (Dashboard)
```bash
cd frontend
npm install
npm run dev
```
Abra no navegador em `http://localhost:3000`.

---

## 🧪 Testes

Para rodar os testes unitários dos parsers de extração:
```bash
python -m pytest tests/
```
