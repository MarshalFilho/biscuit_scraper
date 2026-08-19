# 🚀 E-Commerce Market Intelligence & AI Scraping Engine

Pipeline autônomo e genérico de raspagem de dados, inteligência competitiva e análise preditiva de mercado para e-commerce (Mercado Livre e Shopee). 

O sistema coleta dados de preços, estoque e velocidade de vendas, armazena em **PostgreSQL (Supabase)**, sintetiza insights estratégicos via **Google Gemini AI** e disponibiliza um dashboard em **Nuxt 3** com animações fluidas, skeletons e design moderno.

---

## 🏛️ Arquitetura do Sistema (100% Custo Zero)

O projeto adota uma arquitetura bifurcada e serverless, projetada para operar no **Free Tier perpétuo**:

```
 ┌────────────────────────────────────────────────────────┐
 │                   FRONTEND (Vercel)                    │
 │  Nuxt 3 (SSR/Nitro) + Vue 3 + Tailwind/Glassmorphism   │
 └───────────────────────────┬────────────────────────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
 ┌──────────────────────┐          ┌──────────────────────┐
 │ DATABASE (Supabase)  │          │   ENGINE SCRAPER     │
 │  PostgreSQL Relativo │          │   Google Cloud Run   │
 │  + Realtime Status   │          │   Python + Docker    │
 └──────────────────────┘          └──────────┬───────────┘
                                              │
                                              ▼
                                   ┌──────────────────────┐
                                   │  IA ANALYTICS ENGINE │
                                   │  Google Gemini 2.5   │
                                   └──────────────────────┘
```

1. **Dashboard Frontend (Vercel)**: Aplicação Nuxt 3 reativa que consome o Supabase em tempo real, exibe gráficos interativos (ApexCharts), ranking de produtos virais, monitor de guerra de preços e relatórios executivos de IA.
2. **Engine de Extração (Google Cloud Run / Local)**: Robô em Python usando **Playwright**, **curl_cffi** (anti-bot) e **BeautifulSoup**, estruturado sob a **Arquitetura Medalhão** (Bronze ➔ Prata ➔ Ouro).
3. **Módulo de Inteligência Artificial (Google Gemini)**: Categorização automática de novos produtos e geração de relatórios com 7 pilares estratégicos (Top Vendedores, Produtos Virais, Estratégia de SEO, Faixas de Preço/Oceano Azul, Batalha de Plataformas, Alertas e Recomendações).

---

## 📂 Estrutura de Diretórios

```text
biscuit_scraper/
│
├── frontend/                        # Dashboard Web em Nuxt 3
│   ├── assets/css/main.css          # Design System (Glassmorphism, Shimmer Skeletons)
│   ├── components/                  # Componentes Vue reativos
│   │   ├── AiExecutiveReport.client.vue  # Relatório executivo de 7 módulos (IA)
│   │   ├── DataTable.vue            # Tabela de produtos com Infinite Scroll anti-CLS
│   │   ├── PriceStrategyMonitor.vue # Monitor de aumentos vs guerra de preços
│   │   ├── TrendingProductsTab.vue  # Ranking de produtos virais / aceleração
│   │   ├── ScraperConfig.vue        # Central de preferências & disparo com Realtime
│   │   └── TimelineScrapeSelector.vue # Comparador histórico de coletas
│   ├── server/api/                  # Server Routes Nitro (Webhooks e proxy Gemini)
│   ├── biome.json                   # Configuração de Linter & Formatter ultrarrápido
│   └── playwright.config.ts         # Testes E2E do Frontend
│
├── src/                             # Engine Python (Scraping & IA)
│   ├── cloud_server.py              # Microserviço Flask / Webhook para o Cloud Run
│   ├── main.py                      # Ponto de entrada CLI e execução de pipeline
│   ├── config.py                    # Gerenciador de configurações e regras de busca
│   ├── ai/                          # Módulos de IA (Categorizador e Prompts)
│   ├── scrapers/                    # Robôs de coleta (Mercado Livre e Shopee)
│   │   ├── meli_scraper.py
│   │   ├── shopee_scraper.py
│   │   └── login_session.py
│   └── utils/                       # Utilitários (Supabase client, Bot detector, AI Engine)
│
├── tests/                           # Suíte de Testes Automatizados
│   └── test_parsers.py              # Testes unitários de parsing de preço e links
│
├── requirements.txt                 # Dependências Python (Playwright, Supabase, Structlog, Ruff)
├── AGENTS_GUIDELINES.md             # Diretrizes de Governança, UX e Qualidade para IAs
├── PLANO_DESENVOLVIMENTO.md         # Roadmap e arquitetura de implantação
└── .env.example                     # Template de variáveis de ambiente
```

---

## ⚙️ Variáveis de Ambiente (`.env`)

Crie um arquivo `.env` na raiz do projeto com base no [`.env.example`](file:///c:/Users/marsh/OneDrive/Desktop/trabalhos/projetos_pessoais/biscuit_scraper/.env.example):

```ini
# Supabase (Banco de Dados & Autenticação)
SUPABASE_URL=https://sua-url.supabase.co
SUPABASE_KEY=sua-service-role-key-aqui
SUPABASE_USER_ID=seu-uuid-de-usuario-aqui

# Frontend Nuxt (Público)
NUXT_PUBLIC_SUPABASE_URL=https://sua-url.supabase.co
NUXT_PUBLIC_SUPABASE_ANON_KEY=sua-anon-key-aqui

# Inteligência Artificial (Google Gemini)
GEMINI_API_KEY=sua-gemini-api-key-aqui

# Webhook Cloud (Opcional - Google Cloud Run)
SCRAPER_WEBHOOK_URL=https://seu-servico-cloudrun.a.run.app/trigger
```

---

## 🚀 Como Executar o Projeto

### 1. Rodando o Dashboard Frontend (Nuxt 3)

```powershell
cd frontend
npm install --legacy-peer-deps
npm run dev
```

Acesse no navegador: `http://localhost:3000`

---

### 2. Rodando o Engine de Scraping (Python)

Instale as dependências e o navegador do Playwright:

```powershell
pip install -r requirements.txt
playwright install chromium
```

#### A. Execução Manual via Terminal
```powershell
# Executar para todas as plataformas (Meli + Shopee + IA)
python src/main.py --plataforma todos

# Executar apenas Mercado Livre
python src/main.py --plataforma meli

# Executar apenas Shopee
python src/main.py --plataforma shopee
```

#### B. Modo Servidor / Webhook (Cloud Run)
```powershell
python src/cloud_server.py
```
O servidor escutará na porta `8080` e responderá a requisições `POST /trigger` disparadas pelo Dashboard.

#### C. Salvar Sessão de Login (Evitar CAPTCHAs)
```powershell
python src/main.py --login
```

---

## 🧪 Qualidade de Código e Testes

O projeto segue padrões de qualidade estritos definidos no [`AGENTS_GUIDELINES.md`](file:///c:/Users/marsh/OneDrive/Desktop/trabalhos/projetos_pessoais/biscuit_scraper/AGENTS_GUIDELINES.md):

### Python (Backend)
- **Linter & Formatação com Ruff**:
  ```powershell
  python -m ruff check src/ --fix
  ```
- **Testes Unitários com Pytest**:
  ```powershell
  python -m pytest tests/
  ```

### TypeScript / Vue (Frontend)
- **Linter & Formatação com Biome**:
  ```powershell
  cd frontend
  npm run lint
  ```
- **Testes E2E com Playwright**:
  ```powershell
  cd frontend
  npm run test:e2e
  ```

---

## 📄 Licença e Uso

Desenvolvido para fins de inteligência competitiva e automação em e-commerce. Estrutura 100% modular e adaptável para qualquer nicho de produtos.
