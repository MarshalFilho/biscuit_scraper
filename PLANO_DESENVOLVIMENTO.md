# 🚀 Plano de Desenvolvimento e Roadmap (`biscuit_scraper`)

> **Documento Interno de Acompanhamento**  
> *Este arquivo está listado no `.gitignore` para não ser sincronizado no repositório público.*

---

## 📌 Visão Geral do Projeto & Arquitetura Alvo

- **Front-end / Dashboard:** Nuxt 3 + Vue 3 (Hospedado no GitHub Pages: `https://marshalfilho.github.io/biscuit_scraper/`)
- **Banco de Dados & Backend Serverless:** Supabase (PostgreSQL + API REST / Realtime)
- **Robô de Raspagem:** Python + Playwright + BeautifulSoup (`src/main.py`)
- **Automação Nuvem:** GitHub Actions (`.github/workflows/`)
- **Inteligência Artificial:** API Gemini / OpenAI (Categorização, Insights e Auxílio de Filtros)

---

## 🗺️ Roadmap de Execução (Do Mais Fácil ao Mais Difícil)

---

### 🟢 FASE 1: Ajustes Rápidos de Interface & UX Simples (Quick Wins)
*Objetivo: Pequenas melhorias visuais e funcionais no front-end para rápido retorno visual.*

#### 1.1. Alternador de Plataformas (Toggle Group em vez de Select)
- **O que fazer:** Substituir o elemento `<select>` de seleção de plataforma por um grupo de botões estilo *Toggle* (`[ Ambas ] [ Shopee ] [ Mercado Livre ]`).
- **Arquivos afetados:** [`frontend/pages/index.vue`](file:///c:/Users/marsh/OneDrive/Desktop/trabalhos/projetos_pessoais/biscuit_scraper/frontend/pages/index.vue)
- **Benefício:** Acesso direto com 1 clique, visual moderno e melhor usabilidade em dispositivos móveis.

#### 1.2. Ordenação Interativa na Tabela por Cabeçalho de Coluna
- **O que fazer:**
  - Remover o dropdown estático "Ordenar por".
  - Tornar os cabeçalhos da tabela (`Título`, `Preço`, `Vendas`, `Variação`, `Plataforma`) clicáveis.
  - Alternar ordenação ao clicar: `Crescente (▲)` ➔ `Decrescente (▼)` ➔ `Padrão`.
- **Arquivos afetados:** [`frontend/components/DataTable.vue`](file:///c:/Users/marsh/OneDrive/Desktop/trabalhos/projetos_pessoais/biscuit_scraper/frontend/components/DataTable.vue)

#### 1.3. Mudar Paleta de Cores (Design Mais Claro e Amigável)
- **O que fazer:**
  - Substituir o tema escuro/neon ("gritando IA") por um tema claro (*Light Mode*), com tons pastéis suaves, fundo neutro e alto contraste de texto.
  - Adequar tipografia e tamanho de fontes pensando em clientes mais velhos/sêniores.
- **Arquivos afetados:** [`frontend/assets/css/main.css`](file:///c:/Users/marsh/OneDrive/Desktop/trabalhos/projetos_pessoais/biscuit_scraper/frontend/assets/css/main.css) (ou estilos globais no Nuxt).

#### 1.4. Reformulação do Botão e Modal "Raio-X" (Detalhes do Produto)
- **O que fazer:**
  - Mudar o nome do botão "Raio-X" para **"🔎 Análise do Anúncio"** ou **"📊 Ver Detalhes"**.
  - Enriquecer o modal ([`ProductModal.vue`](file:///c:/Users/marsh/OneDrive/Desktop/trabalhos/projetos_pessoais/biscuit_scraper/frontend/components/ProductModal.vue)):
    - Exibir foto do produto, vendedor, plataforma, link direto.
    - Gráfico de histórico de preço e variação de vendas no período selecionado.
    - Tag da Categoria definida pela IA.

---

### 🟡 FASE 2: Métricas de Período, Filtros Globais & Novos Gráficos
*Objetivo: Tornar o dashboard verdadeiramente dinâmico com base em intervalos de tempo.*

#### 2.1. Filtro Global de Período no Topo
- **O que fazer:**
  - Criar um seletor de intervalo de tempo fixo no topo da página:
    - `[ Últimos 7 dias ] [ Últimos 15 dias ] [ Últimos 30 dias ] [ Todo o Período ] [ Personalizado ]`
  - Este filtro deve governar todos os componentes da página (KPIs, gráficos, tabelas e vendedores).
- **Arquivos afetados:** [`frontend/pages/index.vue`](file:///c:/Users/marsh/OneDrive/Desktop/trabalhos/projetos_pessoais/biscuit_scraper/frontend/pages/index.vue)

#### 2.2. Cartões de Métricas (KPIs) com Indicadores de Data Claros
- **O que fazer:**
  - Adicionar um sub-título explicativo no topo do dashboard: ex: *"Exibindo dados coletados de **01/07/2026** a **23/07/2026**"*.
  - Exibir a variação percentual clara (ex: `+18% vendas em relação ao período anterior`).
- **Arquivos afetados:** [`frontend/components/KpiCards.vue`](file:///c:/Users/marsh/OneDrive/Desktop/trabalhos/projetos_pessoais/biscuit_scraper/frontend/components/KpiCards.vue)

#### 2.3. Clareza na Tabela de Comparação (Aumento de Vendas e Preços)
- **O que fazer:**
  - Ajustar a lógica da coluna de vendas para mostrar a diferença exata no período: ex: `+15 vendas (7 dias)` ou `-2 vendas`.
  - Deixar explícito que o aumento é calculado subtraindo `(Vendas na data final) - (Vendas na data inicial do filtro)`.

#### 2.4. Substituição do Gráfico de Dispersão ("Bolinha") por Gráfico de Barras
- **O que fazer:**
  - Substituir o gráfico de dispersão ([`PriceVsSalesChart.client.vue`](file:///c:/Users/marsh/OneDrive/Desktop/trabalhos/projetos_pessoais/biscuit_scraper/frontend/components/PriceVsSalesChart.client.vue)) por um **Gráfico de Barras / Histograma de Faixas de Preço** (ex: *Volume de Vendas por Faixa de Preço: R$0-20, R$20-50, R$50-100, R$100+*).

#### 2.5. Novo Módulo / Visão de Vendedores (Top Sellers)
- **O que fazer:**
  - Criar um novo componente `TopSellersChart.vue` ou tabela dedicada de vendedores:
    - Vendedores que mais venderam no período.
    - Quantidade de anúncios por vendedor.
    - Categorias principais onde cada vendedor atua.

#### 2.6. Organização das Páginas (Arquitetura Multi-Página)
- **O que fazer:**
  - Dividir a aplicação em 2 páginas/abas principais via barra de navegação superior:
    1. **📊 Painel Analítico (`/`):** KPIs, Filtro de Data, Gráficos, Vendedores, Tabela de Anúncios e Insights da IA.
    2. **⚙️ Configurações & Scraper (`/config`):** Ajustes de busca, palavras negativas, gerador por IA, disparo manual e logs do robô.
- **Arquivos afetados:** `frontend/pages/index.vue` e `frontend/pages/config.vue` (novo).

---

### 🟠 FASE 3: Correção do GitHub Actions & Acompanhamento de Progresso
*Objetivo: Garantir execução automatizada estável e feedback visual em tempo real.*

#### 3.1. Correção e Homologação das GitHub Actions
- **O que fazer:**
  - Revisar [`scraper_bot.yml`](file:///c:/Users/marsh/OneDrive/Desktop/trabalhos/projetos_pessoais/biscuit_scraper/.github/workflows/scraper_bot.yml) e [`scraper_semanal.yml`](file:///c:/Users/marsh/OneDrive/Desktop/trabalhos/projetos_pessoais/biscuit_scraper/.github/workflows/scraper_semanal.yml).
  - Garantir injeção correta dos *Secrets*: `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_USER_ID`.
  - Configurar disparo agendado (`cron: '0 3 * * 1'`) e disparo manual (`workflow_dispatch`).

#### 3.2. Acompanhamento de Progresso em Tempo Real (Disparo Manual)
- **O que fazer:**
  - Quando o usuário clicar em "Iniciar Raspagem" no dashboard:
    - O Python envia atualizações detalhadas do status para a coluna `status_scraper` na tabela `configuracoes_scraper` do Supabase.
    - O front-end Vue escuta essa coluna (via Supabase Realtime ou Polling de 3s) e exibe uma barra de progresso / modal com as etapas:
      - `[1/4] Acessando Mercado Livre...`
      - `[2/4] Extraindo anúncios e preços...`
      - `[3/4] Executando análise e categorização de IA...`
      - `[4/4] Finalizado com sucesso!`

#### 3.3. Solução Elegante para Sessão de Login & Controle de Páginas
- **Regra de Negócio de Autenticação:**
  1. **Modo Rápido / Anônimo (1 Página por busca):**
     - Não exige login. O robô raspa apenas a primeira página de cada termo de busca (ideal para coletas rápidas e sem fricção).
  2. **Modo Profundo / Logado (Múltiplas Páginas):**
     - Exige sessão salva no Supabase. A Shopee e Mercado Livre bloqueiam paginação contínua sem autenticação.
     - **Como Funciona:** O usuário realiza o login 1 vez (localmente ou via importador no Dashboard) e salva a sessão no Supabase. O GitHub Actions lê o `auth.json` da nuvem e raspa quantas páginas o usuário definiu (ex: 3 a 5+ páginas por busca).

---

### 🔴 FASE 4: Integração Avançada de IA & Assistente Inteligente
*Objetivo: Automatizar tarefas complexas e reduzir o esforço cognitivo do usuário.*

#### 4.1. Categorização Automática de Produtos por IA (Pós-Scraping)
- **O que fazer:**
  - Após o robô raspar os produtos, o script Python aciona a API da IA (Gemini ou OpenAI) enviando os títulos e preços dos novos anúncios.
  - A IA classifica cada produto em categorias pré-definidas ou dinâmicas (ex: *"Topo de Bolo"*, *"Lembrancinhas"*, *"Ferramentas/Moldes"*, *"Insumos/Massa"*).
  - Salva o resultado no campo `categoria_ia` da tabela `produtos` no Supabase.

#### 4.2. Geração Automatizada de Insights Executivos pela IA (Relatório de Inteligência)
- **O que fazer:**
  - Ao final do scraping, o Python cruza os dados do histórico no Supabase e aciona a IA para gerar um relatório analítico estruturado (salvo na tabela `insights_ia`).
  - **Módulos de Insights Gerados pela IA:**
    1. **🚀 Vendedores em Maior Ascensão (Top Growth Sellers):**
       - Identificar quais vendedores tiveram o maior crescimento absoluto e percentual de vendas entre as últimas coletas (ex: *"Vendedor X cresceu +42% em vendas esta semana no Mercado Livre"*).
       - Identificar novos vendedores que acabaram de entrar no ranking com alto volume.
    2. **🔥 Produtos Virais / Tendências Quentes (Trending Products):**
       - Anúncios com aceleração atípica de vendas em curtos intervalos de tempo.
       - Lançamentos recentes com alta conversão.
    3. **🎯 Estratégia de Títulos & SEO para E-commerce:**
       - Análise dos termos mais recorrentes nos 10 anúncios mais vendidos (ex: *"80% dos anúncios topo de vendas utilizam as palavras 'Kit', 'Pronta Entrega' e 'Personalizado'"*).
    4. **💡 Lacunas de Preço & Oportunidades de Mercado (Oceanos Azuis):**
       - A IA mapeia faixas de preço desatendidas onde a demanda é alta mas há pouca concorrência (ex: *"Faixa de R$ 40,00 a R$ 65,00 possui alta demanda e apenas 2 concorrentes ativos no Mercado Livre"*).
    5. **⚔️ Comparativo de Força entre Plataformas (Mercado Livre vs Shopee):**
       - Qual plataforma domina qual subclasse de produto (ex: *"Shopee domina 70% das vendas de insumos/massas, enquanto Mercado Livre domina 80% das peças prontas/personalizadas"*).
    6. **📉 Alertas de Estagnação & Queda de Preço (Guerra de Preços):**
       - Anúncios que sofreram queda acentuada de vendas ou vendedores que reduziram preços para desovar estoque.
    7. **💡 Recomendações Práticas de Ação (Para o Negócio):**
       - A IA sugere ações diretas para a tomada de decisão (ex: *"Recomendação: Crie um anúncio de Kit com 5 peças de lembrancinhas na faixa de R$ 45,00, aproveitando o vácuo de concorrência detectado no Shopee."*).
  - **Exibição no Front-end:** O Painel Analítico terá um painel retrátil ou carrossel de *Cards de Insights Inteligentes* no topo, com linguagem clara e visualmente fácil de ler.


#### 4.3. Gerador Assistido de Filtros (IA para Palavras Positivas/Negativas)
- **O que fazer:**
  - Na página de configurações, adicionar o campo: *"Descreva em linguagem natural o que deseja monitorar"*.
  - *Exemplo de input:* `"Quero analisar vendas de lembrancinhas de biscuit para festa infantil, mas não quero ver ferramentas, moldes de silicone nem colas."`
  - A IA processa e sugere automaticamente:
    - `TERMOS_BUSCA`: `["lembrancinha biscuit", "topo de bolo biscuit"]`
    - `PALAVRA_OBRIGATORIA`: `"biscuit"`
    - `PALAVRAS_NEGATIVAS`: `["molde", "silicone", "cola", "esteca", "ferramenta"]`
  - O usuário só precisa revisar e clicar em **Salvar**.

---

### 🟣 FASE 5: Arquitetura 100% Dinâmica (Configuração Orientada a Banco / Multi-Nicho)
*Objetivo: Tornar o software agnóstico a nicho (reutilizável para qualquer produto/cliente).*

#### 5.1. Eliminar Qualquer Código "Hardcoded"
- **O que fazer:**
  - Garantir que nenhum termo como `"biscuit"` ou categorias específicas fiquem gravados de forma fixa no código Python ou JS.
  - Toda a inteligência de busca, títulos das páginas, marcas e regras são carregadas da tabela `configuracoes_scraper` do cliente logado no Supabase.
- **Resultado:** O mesmo Dashboard e Scraper pode ser vendido ou reutilizado para nichos como Crochê, Velas Aromáticas, Artigos em MDF, Impressão 3D, Moda, etc.

---

## 📝 Checklist de Acompanhamento (Status)

| Item | Descrição | Complexidade | Status |
| :--- | :--- | :--- | :---: |
| 1.1 | Alternador de Plataformas (Toggle) | 🟢 Fácil | ✅ Concluído |
| 1.2 | Ordenação por Coluna na Tabela | 🟢 Fácil | ✅ Concluído |
| 1.3 | Paleta de Cores Suave (Light Mode) | 🟢 Fácil | ✅ Concluído |
| 1.4 | Reformulação do Modal "Raio-X" | 🟢 Fácil | ✅ Concluído |
| 2.1 | Filtro Global de Período no Topo | 🟡 Média | ✅ Concluído |
| 2.2 | KPIs com Datas Explícitas | 🟡 Média | ✅ Concluído |
| 2.3 | Tabela de Comparação com Período Claro | 🟡 Média | ✅ Concluído |
| 2.4 | Gráfico de Barras (Substituindo Dispersão) | 🟡 Média | ✅ Concluído |
| 2.5 | Módulo de Análise de Vendedores | 🟡 Média | ✅ Concluído |
| 2.6 | Separação em 2 Páginas (Dashboard / Config) | 🟡 Média | ✅ Concluído |
| 3.1 | Correção das GitHub Actions | 🟠 Média/Alta | ✅ Concluído |
| 3.2 | Progresso em Tempo Real do Scraping | 🟠 Média/Alta | ✅ Concluído |
| 3.3 | Gestão de Sessão & Controle de Páginas | 🟠 Média/Alta | ✅ Concluído |
| 4.1 | Categorização Automática por IA | 🔴 Complexo | ✅ Concluído |
| 4.2 | Relatório de Insights por IA | 🔴 Complexo | ✅ Concluído |
| 4.3 | Gerador de Filtros Assistido por IA | 🔴 Complexo | ✅ Concluído |
| 5.1 | Arquitetura 100% Genérica por Banco | 🟣 Estrutural | ✅ Concluído |

---
