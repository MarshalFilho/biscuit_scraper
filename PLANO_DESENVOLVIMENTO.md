# 🚀 Plano de Desenvolvimento & Arquitetura Oficial de Produção

Este documento é a referência oficial da arquitetura do sistema, contemplando os **recursos já implementados no código-fonte** e a **arquitetura de produção na nuvem (100% Custo Zero)** validada para publicação.

---

## 📌 PARTE 1: FUNCIONALIDADES E RECURSOS JÁ IMPLEMENTADOS

O sistema possui uma arquitetura funcional composta por um motor de extração em Python com Playwright, inteligência generativa com a API do Google Gemini e um Dashboard em Nuxt 3.

### 1.1. Motor de Extração & Scraping (Mercado Livre + Shopee)
- **Extração Precisa de Preços**: Filtro de preços cortados (`<del>`, `<s>`), ofertas promocionais e banners de frete grátis (*"Frete grátis em R$ 140"*), capturando o valor à vista real.
- **Deduplicação Inteligente**: Normalização de URLs patrocinadas (`click1.mercadolivre.com.br/...`) e agrupamento automático por título/ID no banco de dados para evitar registros duplicados.
- **Detecção de CAPTCHAs & Bot Blocks**: Mapeamento de desafios anti-robô e atualização em tempo real do status no banco.
- **Script de Purga Total**: Ferramenta de limpeza (`py src/utils/limpar_dados_antigos.py --reset-total`) para zerar históricos locais e remotos quando necessário.

### 1.2. Módulo de Inteligência Artificial Generativa (Google Gemini API)
- **100% Genérico e Multinicho**: Prompts e análises parametrizados dinamicamente com base no `nome_projeto` do usuário, adaptando-se a qualquer segmento de e-commerce.
- **Otimização de Tokens (>80%)**: Envio de payload minimalista `[{t, p, plat, v, d}]` e recepção em formato JSON estrito (`response_mime_type="application/json"`).
- **Relatório Executivo de 7 Módulos**:
  1. *Lojas & Vendedores Líderes*: Ranking de vendedores por faturamento e volume.
  2. *Produtos Virais & Mais Vendidos*: Itens de maior velocidade de vendas.
  3. *Palavras-Chave de Alta Conversão*: Análise de termos SEO líderes.
  4. *Zonas de Preço & Oceano Azul*: Mapeamento de volume por faixa de valor.
  5. *Comparativo entre Plataformas*: Participação de mercado (% Share ML vs Shopee).
  6. *Recomendações Estratégicas da IA*: Diagnósticos de precificação e logística.
  7. *Oportunidades de Nicho*: Identificação de demandas reprimidas.
- **Gerador de Filtros por Linguagem Natural**: Endpoint em Nuxt que interpreta o texto livre do usuário e gera os termos de busca e blacklist sem omissão de itens.

### 1.3. Frontend Dashboard (Nuxt 3)
- **Linha do Tempo Histórica (`TimelineScrapeSelector.vue`)**: Inspeção por data e *Modo Comparar Datas* (Data A vs Data B).
- **Ranking de Produtos Virais (`TrendingProductsTab.vue`)**: Destaque para produtos em aceleração de vendas.
- **Monitor de Guerra de Preços & Margens (`PriceStrategyMonitor.vue`)**: Separação de anúncios em aumento de preço vs descontos.
- **Central de Conexão das Lojas de 1-Clique**:
  - Botão de login que abre o navegador para validação de sessão de forma transparente.
  - Banner explicativo de garantia de privacidade (não salvamento de senhas).
  - Alerta pulsante de CAPTCHA detectado com atalho para resolução na Web.

### 1.4. Infraestrutura de Container Pré-Configurada
- `Dockerfile` configurado com Python e dependências do Playwright.
- Servidor Webhook Flask (`src/cloud_server.py`) pronto na porta `8080`.

---

## 📌 PARTE 2: ARQUITETURA OFICIAL DE PRODUÇÃO NA NUVEM (100% CUSTO ZERO)

A infraestrutura de produção foi desenhada para rodar 100% online sem depender de máquina local ligada e sem custos de hospedagem (Free Tier perene).

```
   ┌─────────────────────────────────────────────────────────────┐
   │                    PAINEL WEB / DASHBOARD                   │
   │                    Hospedado na VERCEL                      │
   │               (Nuxt 3 SSR + Server Routes)                  │
   └───────────────┬─────────────────────────────┬───────────────┘
                   │                             │
    1. Escuta Status Realtime     2. Disparo Webhook (POST /trigger)
                   │                             │
                   ▼                             ▼
   ┌─────────────────────────────┐   ┌───────────────────────────┐
   │    BANCO DE DADOS NUVEM     │   │   ENGINE DE SCRAPING & IA │
   │          SUPABASE           │   │     GOOGLE CLOUD RUN      │
   │  (PostgreSQL + Websockets)  │   │  (Playwright Docker + IA)  │
   └───────────────▲─────────────┘   └───────────▲───────────────┘
                   │                             │
                   └────── 3. Salva Coletas ─────┘
                                                 │
                                 4. Ativação Cron Diária (03:00)
                                                 │
                                     ┌───────────┴───────────┐
                                     │ GOOGLE CLOUD SCHEDULER│
                                     └───────────────────────┘
```

---

### Componente 1: Hospedagem Frontend — **Vercel**
- **Provedor**: Vercel (Plano Hobby / Free Tier).
- **Função**: Publicação da aplicação Web construída em **Nuxt 3** (`frontend/`).
- **Recursos**:
  - Compilação automática de rotas do Nitro (`/api/report`, `/api/ai-filter`, `/api/trigger-scrape`) como Serverless Functions.
  - Suporte nativo a SSR (Server-Side Rendering) e SSL (HTTPS) automático.
  - Deploy contínuo via integração com o repositório do GitHub (CI/CD).

### Componente 2: Banco de Dados na Nuvem — **Supabase**
- **Provedor**: Supabase (PostgreSQL Gerenciado / Free Tier de 500 MB).
- **Função**: Armazenamento relacional de produtos, históricos de coletas e configurações do scraper.
- **Recursos**:
  - Realtime Subscriptions via Websockets: O dashboard atualiza a tela do usuário instantaneamente quando o robô envia atualizações de status.
  - Compatibilidade 100% com o código Python (`supabase-py`) e Vue (`@supabase/supabase-js`).

### Componente 3: Engine de Scraping & Automação — **Google Cloud Run + Cloud Scheduler**
- **Provedor**: Google Cloud Run + Google Cloud Scheduler (Free Tier GCP: 2M chamadas/mês).
- **Função**: Execução do Playwright Chromium Headless e geração do relatório de IA via container Docker.
- **Recursos**:
  - **Container Serverless (`src/cloud_server.py`)**: Publicado via Dockerfile expondo a porta `8080`.
  - **Disparo Sob Demanda**: Ao clicar em *"Disparar Scraper Agora"* no site, a Vercel faz um POST para o Cloud Run, que executa a raspagem com resposta imediata.
  - **Disparo Programado (Cron Job)**: O Cloud Scheduler executa uma chamada HTTP às 03:00 todos os dias para manter o histórico atualizado.
  - **Scale to Zero**: O container escala para zero quando ocioso, garantindo consumo dentro da cota gratuita do GCP.

---

## 📌 PARTE 3: CHECKLIST DE DEPLOY & EXECUÇÃO

- [x] **Código & Containers**: `Dockerfile`, `src/cloud_server.py` e endpoints do Nuxt prontos.
- [x] **IA Generativa**: Integração com Gemini API (`gemini-flash-latest`) validada.
- [x] **Variáveis de Ambiente**: Arquivo [`.env.example`](file:///c:/Users/marsh/OneDrive/Desktop/trabalhos/projetos_pessoais/biscuit_scraper/.env.example) estruturado.
- [x] **Passo 1 (Banco de Dados Cloud)**: Tabelas e Realtime configurados no Supabase Cloud.
- [ ] **Passo 2 (Frontend Vercel)**: Conectar o repositório GitHub na Vercel e adicionar as variáveis do `.env` *(Em andamento)*.
- [ ] **Passo 3 (Engine GCP)**: Publicar o container no Google Cloud Run e configurar o Cloud Scheduler.
