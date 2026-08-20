# 🚀 Plano de Desenvolvimento & Arquitetura Oficial (Multi-Tenant & Backend Only)

Este documento é a referência oficial da arquitetura do sistema, contemplando os **recursos implementados**, a **reestruturação de segurança multi-tenant** e os **próximos passos de evolução do produto**.

---

## 🏛️ PARTE 1: NOVA ARQUITETURA DE SEGURANÇA E MODELO DE OPERAÇÃO

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

### 1.1. Princípios da Nova Arquitetura:
1. **Frontend Seguro & Read-Only para Clientes**: O cliente final acessa apenas a visualização de métricas, gráficos e insights da sua própria conta. Não há botões de disparo de scraping abertos na Web para clientes comuns.
2. **Isolamento de Contas (Multi-Tenant RLS)**: Cada cliente possui seu login via Supabase Auth e acessa estritamente os produtos, termos e relatórios vinculados ao seu `user_id`.
3. **Scraping Centralizado no Backend (CLI Seletivo)**: O administrador executa a extração via terminal selecionando o cliente desejado por ID/UUID (`python src/main.py --user-id <ID>`) ou via rotina agendada (Cron diário).
4. **Internacionalização Nativa (i18n)**: Suporte bilíngue completo no Dashboard (**Português 🇧🇷 / Inglês 🇺🇸**) para expansão de mercado.

---

## 📌 PARTE 2: FUNCIONALIDADES E REFINAMENTOS DE IA & UX

### 2.1. Relatório de Inteligência Executiva de Mercado (IA Gemini)
- **Recomendações Estratégicas & Oportunidades de Nicho (Módulo Principal no Topo)**:
  - Posicionamento da aba de recomendações no início do relatório.
  - Fusão de diagnóstico tático com oportunidades de demanda reprimida.
  - **Justificativa baseada em dados**: Cada recomendação deve conter dados empíricos concretos (ex: *"Criar kits entre R$ 45 e R$ 60 pois esta faixa concentra 64% do volume de vendas com apenas 18% da concorrência ativa"*).
- **Comparativo de Plataformas com Métrica de Vendedores**:
  - Além de volume de vendas acumulado e % market share, inclusão da **quantidade de lojas/vendedores únicos** ativos no Mercado Livre vs Shopee.
- **Módulos Estratégicos Mantidos**: Top Vendedores em Ascensão, Produtos Virais, Estratégia de SEO/Palavras-Chave e Oceano Azul de Preços.

### 2.2. Tabela Principal de Produtos (UX & Anti-CLS)
- **Modo Ocultar/Silenciar em vez de Excluir**:
  - O botão de ação permite ao cliente "ocultar/silenciar" um anúncio irrelevante da sua visão, sem deletar fisicamente o registro do banco de dados.
  - Adição de filtro na barra superior: *"Mostrar itens ocultos (Sim/Não)"* para recuperação rápida.
- **Scroll Vertical com Cabeçalho Sticky**:
  - Limite de altura responsivo (`max-height: 580px; overflow-y: auto`) com cabeçalho fixo no topo (`position: sticky; top: 0`), mantendo a navegação fluida em grandes bases de produtos.

---

## 📌 PARTE 3: ESPECIFICAÇÃO TÉCNICA DAS ETAPAS DE IMPLEMENTAÇÃO

### 📋 Etapa A: Refinamento de IA e Comparativo de Plataformas
- [ ] Atualizar `src/ai/insights_generator.py` e `src/utils/ai_engine.py` para calcular a contagem de vendedores únicos por plataforma.
- [ ] Reordenar os módulos do relatório executivo colocando **Recomendações & Oportunidades de Nicho** como primeiro item, com justificativas baseadas em números da coleta.
- [ ] Atualizar `AiExecutiveReport.client.vue` para exibir a métrica de quantidade de vendedores no comparativo de plataformas.

### 📋 Etapa B: UX da Tabela e Ocultação Inteligente
- [ ] Modificar `DataTable.vue` para substituir a exclusão definitiva por um status `oculto: true/false`.
- [ ] Adicionar filtro de alternância na barra de filtros globais para exibir/ocultar itens silenciados.

### 📋 Etapa C: Internacionalização (i18n PT / EN)
- [ ] Instalar e configurar `@nuxtjs/i18n` no `frontend/`.
- [ ] Criar arquivos de tradução `locales/pt.json` e `locales/en.json`.
- [ ] Adicionar seletor de idioma (🇧🇷 PT / 🇺🇸 EN) na `Navbar.vue`.

### 📋 Etapa D: Multi-Tenant & CLI Administrativa de Scraping
- [ ] Adicionar suporte a argumento CLI `--user-id` e `--listar-clientes` em `src/main.py`.
- [ ] Atualizar tela de Login no Frontend para vincular a sessão do usuário ao seu respectivo `user_id` no Supabase.
- [ ] Remover a aba aberta de disparo do frontend para clientes comuns, deixando a configuração apenas administrativa.

---

## 📌 PARTE 4: STATUS ATUAL DO CHECKLIST

- [x] **Código & Containers**: `Dockerfile`, `src/cloud_server.py` e endpoints do Nuxt prontos.
- [x] **IA Generativa**: Integração com Gemini API (`gemini-flash-latest`) com otimização de tokens (>80%).
- [x] **Variáveis de Ambiente**: Arquivo [`.env.example`](file:///c:/Users/marsh/OneDrive/Desktop/trabalhos/projetos_pessoais/biscuit_scraper/.env.example) estruturado.
- [x] **Passo 1 (Banco de Dados Cloud)**: Tabelas e Realtime configurados no Supabase Cloud.
- [x] **Passo 2 (Frontend Vercel)**: Dashboard publicado e integrado ao Supabase via Vercel.
- [ ] **Passo 3 (Evolução Multi-Tenant & i18n)**: Implementação dos refinamentos do novo plano.
