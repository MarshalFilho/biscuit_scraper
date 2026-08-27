# 🚀 Plano de Desenvolvimento & Arquitetura Oficial (SaaS Multi-Tenant & Dashboard Puro)

Este documento é a **referência oficial da arquitetura do produto**, estabelecendo a transição definitiva para um **SaaS de Inteligência de Mercado 100% Visual (Dashboard Puro)** com **Scraping Automatizado no Backend (GitHub Actions)** e **Isolamento Total por Cliente (Multi-Tenancy via Supabase Auth & RLS)**.

---

## 🏛️ PARTE 1: ARQUITETURA GERAL DO PRODUTO (SAAS PURO)

### 💡 Por que este modelo é a melhor decisão de engenharia e produto?

1. **Zero Invasão no Computador do Cliente:** O cliente não precisa instalar Python, Node, extensões ou deixar o computador ligado raspando dados.
2. **Proteção Anti-Bot e Custo Zero:** O scraping roda em servidores isolados na nuvem (GitHub Actions com proxies/headers rotativos), sem expor a conta pessoal do cliente.
3. **Escalabilidade Multi-Tenant:** Clientes de nichos totalmente distintos (ex: _Marshal_ com Peças de Computador/Gamer vs _Isadora_ com Biscuit/Artesanato) usam a mesma aplicação web, mas cada um só enxerga os seus respectivos dados após o login.
4. **Alta Performance (Edge & CDN):** O frontend na Vercel se torna um painel analítico ultra-rápido, focado exclusivamente em UX, gráficos, filtros e relatórios de IA.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    PORTAL WEB / DASHBOARD SAAS (Vercel)                      │
│                                                                              │
│   🔒 TELA DE LOGIN OBRIGATÓRIA (Supabase Auth)                                │
│   ┌──────────────────────────────────────────────────────────────────────┐   │
│   │ [Login: marshal@email.com]  ➔  Filtra dados de PEÇAS DE COMPUTADOR   │   │
│   │ [Login: julia@email.com]    ➔  Filtra dados de BISCUIT & ARTESANATO  │   │
│   └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   📊 Painel Analítico: KPIs, Gráficos ApexCharts, Linha do Tempo,            │
│      Filtro Estilo Upwork, Tabela Dinâmica e Relatórios de IA (PT / EN)      │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │
                      (Consultas isoladas por `user_id`)
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                       BANCO DE DADOS NUVEM (Supabase)                        │
│    PostgreSQL com Row Level Security (RLS) ativo por `user_id`:              │
│   • `produtos` (id, user_id, plataforma, titulo, link, vendedor, ...)        │
│   • `historico_coletas` (id, produto_id, preco, vendas_totais, data_coleta)  │
│   • `configuracoes_scraper` (user_id, termos_busca, blacklist, relatorio_ia) │
└──────────────────────────────────────▲───────────────────────────────────────┘
                                       │
                      (Gravação diária via Service Role Key)
                                       │
┌──────────────────────────────────────┴───────────────────────────────────────┐
│                 ENGINE DE SCRAPING & IA (GitHub Actions Cron)                │
│   Execução automatizada diária (ex: 06:00 UTC) em ambiente Linux Headless:   │
│   1. Consulta no Supabase a lista de tenants ativos e seus termos de busca   │
│   2. Executa a raspagem no Mercado Livre e Shopee para cada `user_id`        │
│   3.Dispara a IA (Gemini 1.5 Flash) para gerar o Relatório Executivo Bilíngue│
│   4. Atualiza o banco de dados e notifica o término da coleta                │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔒 PARTE 2: MODELAGEM DE DADOS & SEGURANÇA MULTI-TENANT

### 2.1. Estrutura das Tabelas no Supabase

1. **`auth.users` (Nativo do Supabase):**
   - Gerencia credenciais (e-mail, senha criptografada, tokens JWT de sessão).
2. **`configuracoes_scraper`:**
   - `user_id` (UUID, Foreign Key para `auth.users.id`, PRIMARY KEY)
   - `nome_cliente` (ex: "Marshal Gamer Store", "Ateliê da Júlia Biscuit")
   - `nicho_mercado` (ex: "Hardware & Games", "Biscuit & Artesanato")
   - `termos_busca` (JSONB array, ex: `["placa de video", "memoria ram"]`)
   - `blacklist` (JSONB array, ex: `["usado", "defeito", "quebrado"]`)
   - `regras_categoria` (JSONB array com palavras-chave para categorização dinâmica)
   - `relatorio_insights` (JSONB com o relatório bilíngue PT/EN gerado pela IA)
3. **`produtos`:**
   - `id` (UUID / BIGSERIAL, PRIMARY KEY)
   - `user_id` (UUID, Foreign Key para `auth.users.id`, INDEXADO)
   - `plataforma` (`'meli' | 'shopee'`)
   - `titulo`, `link`, `vendedor`, `categoria_ia`, `silenciado` (BOOLEAN)
4. **`historico_coletas`:**
   - `id` (BIGSERIAL, PRIMARY KEY)
   - `produto_id` (Foreign Key para `produtos.id`, INDEXADO)
   - `preco` (NUMERIC), `vendas_totais` (INTEGER), `data_coleta` (TIMESTAMPTZ)

### 2.2. Políticas de Row Level Security (RLS)

```sql
-- Ativar RLS nas tabelas
ALTER TABLE produtos ENABLE ROW LEVEL SECURITY;
ALTER TABLE configuracoes_scraper ENABLE ROW LEVEL SECURITY;

-- Política de Leitura/Escrita: Usuário só acessa seus próprios registros
CREATE POLICY "Tenant pode visualizar apenas seus produtos"
ON produtos FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Tenant pode editar apenas suas configuracoes"
ON configuracoes_scraper FOR ALL
USING (auth.uid() = user_id);
```

---

## 🎨 PARTE 3: FLUXO DE EXPERIÊNCIA DO USUÁRIO NO FRONTEND

### 3.1. Tela Inicial de Login (Auth Gate)

- Quando o usuário acessa o link do dashboard (ex: `biscuit-scraper.vercel.app`):
  - Se **não autenticado**: Exibe uma tela de login moderna em vidro fosco (_Glassmorphism_), solicitando e-mail e senha, com alternador de idioma no topo (PT / EN).
  - Se **autenticado**: Redireciona imediatamente para o Dashboard carregando exclusivamente o nicho daquele cliente.

### 3.2. Dashboard Personalizado por Tenant

- O cabeçalho exibe o nome do projeto/loja do cliente logado (ex: _"✨ Hardware Analytics Pro"_ ou _"✨ Biscuit Market Intelligence"_).
- Todos os componentes são alimentados com dados do `user_id` ativo:
  - **KPIs:** Faturamento, vendas e produtos do nicho dele.
  - **Filtros e Categorias:** Sugestões baseadas nas categorias cadastradas para a conta dele.
  - **Linha do Tempo:** Histórico de raspagens executadas pelo robô para o nicho dele.
  - **Relatório de IA:** Insights estratégicos gerados especificamente para o segmento dele.

---

## 🤖 PARTE 4: AUTOMAÇÃO DO SCRAPER NO GITHUB ACTIONS

### 4.1. Workflow Agendado (`.github/workflows/daily_scrape.yml`)

- Roda automaticamente todos os dias às 06:00 UTC (ou acionamento manual por webhook/dispatch).
- Executa o pipeline Python:
  ```bash
  python src/main.py --all-tenants
  # Ou para um cliente específico:
  python src/main.py --user-id <UUID_DO_CLIENTE>
  ```
- O script lê os termos de cada tenant ativo no Supabase, roda a extração no Mercado Livre e Shopee, calcula os rankings, gera o relatório com Gemini 1.5 Flash e salva com `user_id`.

---

## 📌 PARTE 5: CHECKLIST DE TAREFAS DE IMPLEMENTAÇÃO

### 📋 Fase 1: Limpeza & Desacoplamento (Remoção do Scraper do Frontend)

- [ ] Remover endpoint `/api/trigger-local.post.ts` (eliminar dependência de processos locais).
- [ ] Remover botões e avisos de "disparar robô local" da interface.
- [ ] Manter no frontend apenas o consumo de APIs de leitura e persistência de filtros no Supabase.

### 📋 Fase 2: Autenticação Central & Guarda de Rotas

- [ ] Criar tela de Login principal como porta de entrada da aplicação (Glassmorphism elegante com suporte a PT/EN).
- [ ] Configurar interceptador de sessão no Nuxt (`useSupabaseUser` ou listener de sessão do `@supabase/supabase-js`).
- [ ] Bloquear renderização dos dados até a confirmação do login.

### 📋 Fase 3: Filtragem de Dados Multi-Tenant no Frontend

- [ ] Vincular todas as queries do `index.vue` ao `user.id` do usuário logado:
  - `produtos` com filtro `.eq('user_id', user.id)`.
  - `configuracoes_scraper` com filtro `.eq('user_id', user.id)`.
- [ ] Exibir o nome do nicho/projeto no título da `Navbar.vue` dinamicamente conforme o cliente logado.

### 📋 Fase 4: Adaptação do Script Python para Múltiplos Tenants

- [ ] Atualizar `src/main.py` para aceitar `--user-id <UUID>` ou `--all-tenants`.
- [ ] O script consulta os termos de busca e blacklist cadastrados para aquele `user_id` em `configuracoes_scraper`.
- [ ] Gravar novos produtos e coletas associando o `user_id` correspondente.

### 📋 Fase 5: GitHub Actions Cron

- [ ] Criar workflow de execução periódica no GitHub Actions com secrets (`SUPABASE_URL`, `SUPABASE_KEY`, `GEMINI_API_KEY`).
