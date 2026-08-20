# 🚀 Plano de Desenvolvimento & Arquitetura Oficial (Multi-Tenant & Backend Only)

Este documento é a referência oficial da arquitetura do sistema, contemplando a **reestruturação de segurança multi-tenant**, a **evolução visual e analítica do Dashboard** e os **planos de ação para os próximos sprints**.

---

## 🏛️ PARTE 1: ARQUITETURA DE SEGURANÇA & OPERAÇÃO (MULTI-TENANT)

Para garantir segurança máxima, **custo zero perpétuo** e evitar vulnerabilidades (como usuários mal-intencionados disparando requisições excessivas que onerem o servidor ou a invasão de scripts locais), o sistema adota um modelo **Multi-Tenant com Scraping Exclusivo no Backend**:

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                     DASHBOARD WEB MULTI-TENANT (Vercel)                │
 │  Nuxt 3 SSR + Supabase Auth + i18n (PT/EN) + Visualização de Dados    │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │
                    (Leitura isolada via Supabase RLS)
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      BANCO DE DADOS NUVEM (Supabase)                   │
 │  PostgreSQL: Tabelas isoladas por `user_id` (Produtos, Histórico, IA)  │
 └───────────────────────────────────▲────────────────────────────────────┘
                                     │
                    (Gravação e Análise via Service Role)
                                     │
 ┌───────────────────────────────────┴────────────────────────────────────┐
 │               ENGINE DE SCRAPING & IA (CLI Admin / Cloud)              │
 │  Execução restrita ao Administrador via Terminal / Cron agendado       │
 │  Comando com seleção de Tenant: `python src/main.py --user-id <UUID>`  │
 └────────────────────────────────────────────────────────────────────────┘
```

---

## 📌 PARTE 2: ROADMAP DE MELHORIAS & NOVO ESCOPO DE REQUISITOS

### 🧠 2.1. Reestruturação dos Relatórios da IA (Consolidados & Equilibrados)
- **Consolidação em 4 Macro-Módulos Integrados** (em vez de 7 abas fragmentadas):
  1. 🎯 **Recomendações Estratégicas & Oportunidades de Nicho**: Diagnósticos acionáveis no topo, justificados com dados matemáticos concretos (ex: *"Recomendamos kits entre R$ 45 e R$ 60 pois concentram 64% do volume com apenas 18% de concorrência"*).
  2. 🏆 **Top Vendedores & Produtos Virais**: Ranking combinado dos maiores faturamentos e dos itens com maior aceleração de vendas.
  3. 🏷️ **Estratégia de SEO & Palavras-Chave de Alta Conversão**: Termos mais frequentes nos títulos líderes.
  4. ⚔️ **Batalha de Marketplaces & Oceano Azul de Preços**: Comparativo direto ML vs Shopee (% share, volume e **número de vendedores únicos**) integrado com a distribuição de faixas de preço.
- **Equilíbrio Multi-Plataforma**: Garantir que a extração e a síntese da IA analisem com peso proporcional anúncios do **Mercado Livre** e da **Shopee** (corrigindo viés de plataforma única).

---

### 📊 2.2. Reformulação dos Gráficos & Filtro Estilo Upwork
- **Filtro de Faixa de Preço Estilo Upwork (Range Slider com Histograma)**:
  - Substituição dos inputs numéricos tradicionais por um componente visual interativo: histograma de volume de anúncios por faixa de valor com controles de arrastar (*Dual Range Slider*).
- **Redefinição dos Gráficos da Visão Geral**:
  - 📈 **Gráfico de Análise de Vendedores (`TopSellersChart`)**: Expandido para largura dupla (tamanho de 2 cards / full width), pois é a visualização mais rica de faturamento e anúncios.
  - 🗑️ **Remoção do Gráfico de Market Share (`MarketShareChart`)**: Retirado para limpar o layout e eliminar redundância com a Batalha de Plataformas.
  - 📦 **Gráfico de Top Produtos (`TopProductsChart`)**: Redesenhado com paleta de cores sóbria e moderna, expandindo de 5 para o **Top 10 produtos líderes**.

---

### 📦 2.3. Tabela Principal de Produtos (UX & Anti-CLS)
- **Infinite Scroll 100% Automático**:
  - Ao rolar o scroll interno até o fim, a tabela carrega automaticamente o próximo lote de 50 produtos via *IntersectionObserver*, sem exigir clique em botão.
- **Ocultar em vez de Excluir**:
  - Substituição da ação destrutiva de exclusão por "Ocultar/Silenciar anúncio", acompanhada de um toggle de visualização na barra de filtros (*"Exibir ocultos"*).
- **Cabeçalho Sticky e Scroll Vertical**: Mantido o cabeçalho fixo (`position: sticky; top: 0`) para rolagem confortável.

---

### 🐛 2.4. Correção de Bugs e Ajustes de Layout
- **Cards de KPI (Visão Geral)**:
  - Correção de overflow de texto (palavras cortadas ou sobrepostas em resoluções menores).
  - Remoção de caracteres quebrados no sufixo de vendas (ex: `"1000 e "` corrigido para `"1.000 un"`).
- **Filtro da Linha do Tempo (`TimelineScrapeSelector.vue`)**:
  - Correção da reatividade no `index.vue`: vincular `timelineSelectedDate` ao filtro `filteredProducts` para que a seleção de uma data passada filtre os dados imediatamente no modo único e alimente o comparativo no modo duplo.

---

### 🌐 2.5. Internacionalização (i18n PT / EN)
- Configuração de `@nuxtjs/i18n` com suporte a Português 🇧🇷 e Inglês 🇺🇸.
- Seletor de idioma na `Navbar.vue`.

---

## 📌 PARTE 3: CHECKLIST DE TAREFAS DE IMPLEMENTAÇÃO

### 📋 Bloco 1: Correções de Bugs Imediatas
- [ ] Vincular a data selecionada da Linha do Tempo (`TimelineScrapeSelector`) na computação de `filteredProducts` em `index.vue`.
- [ ] Ajustar formatação de números e evitar quebra/corte de texto nos cards de KPI (`KpiCards.vue`).
- [ ] Corrigir viés do Gemini em `src/utils/ai_engine.py` para balancear a amostragem de dados da Shopee e Mercado Livre.

### 📋 Bloco 2: Reformulação de Gráficos e Filtro Upwork
- [ ] Remover `MarketShareChart.client.vue` da tela inicial.
- [ ] Expandir `TopSellersChart.client.vue` para largura dupla (`full-width`).
- [ ] Redesenhar `TopProductsChart.client.vue` com Top 10 e cores elegantes.
- [ ] Desenvolver componente `PriceRangeHistogramFilter.vue` (Range Slider com gráfico de barras de distribuição integrado).

### 📋 Bloco 3: Relatório Executivo Consolidado (4 Módulos)
- [ ] Atualizar `AiExecutiveReport.client.vue` para a nova estrutura de 4 macro-módulos integrados.
- [ ] Adicionar contagem de vendedores únicos por plataforma.

### 📋 Bloco 4: Tabela com Infinite Scroll Automático e Ocultação
- [ ] Implementar `IntersectionObserver` em `DataTable.vue` para auto-carregamento no fim da rolagem.
- [ ] Substituir exclusão por flag de ocultação com toggle no filtro global.

### 📋 Bloco 5: Internacionalização & CLI Multi-Tenant
- [ ] Configurar i18n (PT / EN).
- [ ] Adicionar parâmetro `--user-id` na CLI do Python para raspagem seletiva por cliente.
