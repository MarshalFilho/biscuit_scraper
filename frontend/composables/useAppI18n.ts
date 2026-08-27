import { ref } from 'vue'

const currentLocale = ref<'pt' | 'en'>('pt')

const dictionary: Record<'pt' | 'en', Record<string, any>> = {
  pt: {
    navbar: {
      badge: 'Inteligência Ativa',
      login: 'Entrar',
      logout: 'Sair',
      toggle_tooltip: 'Mudar para Inglês'
    },
    global: {
      connecting_db: 'Conectando à base de dados segura do Supabase...',
      error_loading: '⚠️ Ocorreu um erro ao carregar os dados:',
      no_scrapes: 'Sem registros de raspagem',
      loading_dates: 'Carregando datas...',
      real_time_updates: 'Dados atualizados em tempo real',
      all_history: 'Todo o Histórico',
      last_days: 'Últimos {days} Dias',
      until: 'até',
      at: 'às',
      chart: 'Gráfico',
      table: 'Tabela',
      view_ad: 'Ver Anúncio ↗',
      both: 'Ambas',
      actions: 'Ações'
    },
    filters: {
      title: 'Super Filtros Globais',
      subtitle: 'Altera em tempo real todos os KPIs, gráficos e tabelas do painel',
      platform: 'Plataforma:',
      both: '🌐 Ambas',
      category: 'Categoria:',
      all_categories: 'Todas as Categorias',
      min_sales: 'Vendas Mínimas:',
      min_sales_placeholder: 'Ex: 50',
      hide_zero: 'Ocultar produtos com 0 vendas',
      show_hidden: 'Mostrar anúncios silenciados',
      price_range: 'Faixa de Preço:',
      timeline_title: 'Linha do Tempo de Coletas',
      latest_scrape: 'Última atualização:'
    },
    tabs: {
      overview: '📊 Visão Geral de Mercado',
      trending: '🚀 Produtos em Alta & Aceleração',
      pricing: '🏷️ Estratégias de Preço & Oportunidades'
    },
    kpis: {
      total_items: 'Total de Produtos',
      avg_price: 'Preço Médio',
      top_platform: 'Top Plataforma',
      champion_product: 'Produto Campeão',
      revenue: 'Faturamento Est.',
      sales: 'Vendas Totais',
      sales_suffix: 'vendas',
      unit_million: 'mi',
      unit_thousand: 'mil',
      total_items_sub: 'Anúncios monitorados',
      avg_price_sub: 'Média de valor ativo',
      top_platform_sub: 'Canal com maior oferta',
      champion_product_sub: 'Líder em vendas',
      revenue_sub: 'Estimativa (Preço × Vendas)'
    },
    sections: {
      ai_title: '🧠 Inteligência Executiva & IA',
      ai_subtitle: 'Diagnóstico automatizado de mercado para orientar suas decisões estratégicas.',
      kpi_title: '💰 Resultados & Métricas Consolidadas',
      kpi_subtitle: 'Resumo dos valores, preços e volume capturados no nicho monitorado.',
      charts_title: '📊 Mapeamento Visual de Concorrência',
      charts_subtitle: 'Distribuição de lojas líderes, faixas de preço e categorias de mercado.',
      table_title: '🔍 Catálogo Completo de Anúncios',
      table_subtitle: 'Detalhamento de cada anúncio coletado com preço, vendedor e link oficial.'
    },
    timeline: {
      badge: 'LINHA DO TEMPO DE COLETAS',
      title: 'Explore a Evolução Histórica do Mercado',
      subtitle: 'Selecione uma data específica para ver o Retrato do Mercado daquele dia ou ative a comparação entre datas',
      mode_single: 'Modo Único',
      mode_compare: 'Modo Comparar Datas',
      compare_tooltip: 'Comparar duas coletas passadas lado a lado',
      records: 'registros',
      point_a: 'Ponto A (Base):',
      point_b: 'Ponto B (Atual):',
      latest: 'Última'
    },
    table: {
      title: 'Tabela de Produtos Monitorados',
      subtitle: 'Clique nas colunas para ordenar os dados (▲ / ▼)',
      search_placeholder: 'Buscar por título...',
      export_csv: '⬇️ Exportar CSV',
      col_platform: 'Plataforma',
      col_category: 'Categoria',
      col_product: 'Título Anúncio',
      col_price: 'Preço Atual',
      col_old_price: 'Preço Ant.',
      col_variation: 'Variação',
      col_sales: 'Vendas Totais',
      col_actions: 'Ações',
      new_badge: '✨ Novo',
      new_badge_title: 'Identificado recentemente',
      sales_growth_title: 'Vendas novas registradas no período selecionado',
      sales_stable_title: 'Sem novas vendas no período',
      view_details_title: 'Ver detalhes completos do anúncio',
      open_store_title: 'Abrir anúncio original na loja',
      silence_ad_title: 'Ocultar / Silenciar este anúncio',
      restore_ad_title: 'Restaurar produto',
      confirm_hide: 'Deseja silenciar/ocultar o anúncio:\n\n"{title}"\n\nVocê pode desfazer isso depois.',
      empty: 'Nenhum produto encontrado com os filtros aplicados.',
      loading_more: 'Carregando mais produtos...',
      btn_load_more: 'Carregar mais produtos ↓',
      csv_headers: ['Plataforma', 'Categoria', 'Título', 'Preço Atual (R$)', 'Vendas Totais', 'Crescimento de Vendas', 'Variação Preço (R$)', 'Data Criação', 'Link']
    },
    charts: {
      top_sellers: '🏆 Ranking de Vendedores Líderes por Faturamento',
      top_sellers_desc: 'Lojas e vendedores com maior volume de vendas no mercado',
      top_products: '🔥 Top 10 Produtos Mais Vendidos no Nicho',
      category_share: '🥧 Share de Volume de Vendas por Categoria',
      category_share_desc: 'Fatia de mercado e total de unidades vendidas em cada segmento',
      price_vs_sales: '🎯 Distribuição de Vendas por Faixa de Preço',
      price_vs_sales_desc: 'Descubra em qual faixa de preço o mercado mais vende',
      units_short: 'un',
      units_sold: 'unidades vendidas',
      sales_analyzed: 'vendas analisadas',
      waiting_data: 'Aguardando dados para calcular a distribuição...',
      up_to: 'Até',
      above: 'Acima',
      col_seller: 'Vendedor / Loja',
      col_ads: 'Anúncios Ativos',
      ad: 'anúncio',
      ads: 'anúncios',
      empty_sellers: 'Sem dados de vendedores para exibir no momento.',
      seller_note: 'Nota sobre Vendedores:',
      seller_note_desc: 'Os nomes oficiais dos vendedores serão sincronizados e preenchidos automaticamente na próxima execução do robô de raspagem.',
      view_chart_title: 'Ver como gráfico de barras',
      view_table_title: 'Ver como tabela detalhada'
    },
    trending: {
      title: '🔥 Ranking de Aceleração & Tendências de Vendas',
      subtitle: 'Produtos que registraram o maior volume de <strong>novas vendas</strong> entre a coleta mais recente e o histórico selecionado.',
      top_accelerator: 'Top Acelerador:',
      na: 'N/A',
      units: 'un.',
      total_new_sales: 'Total Novas Vendas:',
      col_position: 'Posição',
      col_platform_store: 'Plataforma / Loja',
      col_ad: 'Anúncio',
      col_current_price: 'Preço Atual',
      col_total_sales: 'Vendas Totais',
      col_velocity: 'Velocidade & Novas Vendas',
      col_action: 'Ação',
      unknown_seller: 'Vendedor Desconhecido',
      high_acceleration: '⚡ Alta Aceleração',
      growing: '📈 Em Crescimento',
      stable: '🌱 Estável',
      empty_state: '🔍 Nenhum produto apresentou novas vendas no período selecionado.',
      view_ad: 'Ver Anúncio ↗',
      open_ad_title: 'Abrir anúncio no marketplace'
    },
    strategy: {
      title: '🏷️ Monitor de Estratégias de Preço & Precificação',
      subtitle: 'Análise comportamental dos concorrentes: identifique produtos com <strong>aumento de margem</strong> vs produtos em <strong>guerra de preço/desconto</strong>.',
      price_increased: 'Aumentaram Preço',
      price_dropped: 'Reduziram Preço',
      card1_title: 'Aumento de Preço & Margem',
      card1_desc: 'Produtos que subiram o valor sem estagnar vendas',
      col_product: 'Produto / Vendedor',
      col_before: 'Antes',
      col_now: 'Agora',
      col_variation: 'Variação',
      seller: 'Vendedor',
      no_increases: 'Nenhum aumento de preço registrado no período.',
      card2_title: 'Guerra de Preço & Descontos',
      card2_desc: 'Produtos que baixaram o valor para ganhar volume',
      no_drops: 'Nenhuma redução de preço registrada no período.'
    },
    report: {
      title: 'Relatório de Inteligência Executiva de Mercado',
      badge: 'IA Analytics',
      subtitle: 'Diagnóstico estratégico avançado baseado em análise quantitativa em tempo real',
      expand: '▼ Expandir Insights',
      collapse: '▲ Minimizar',
      updated_at: 'Atualizado em',
      loading: 'Gerando relatório com Inteligência Artificial...',
      tab_strategy: '🎯 Estratégia & Nichos',
      tab_sellers: '🏆 Top Lojas & Produtos',
      tab_seo: '🏷️ Estratégia de SEO',
      tab_platforms: '⚔️ Batalha de Marketplaces',
      sub_recommendations: '💡 Recomendações Estratégicas Acionáveis',
      sub_niches: '🚀 Oportunidades de Nicho & Demanda Oculta',
      sub_keywords: '🏷️ Termos de Maior Frequência nos Anúncios Top',
      sub_titles: '🎯 Modelos de Título de Alta Conversão',
      sub_longtail: '🔗 Estruturas Long-Tail Recomendadas',
      view_store: 'Ver Loja 🔎',
      sales_units: 'vendas',
      active_stores: 'Lojas Ativas:',
      sales_volume: 'Volume de Vendas:',
      est_revenue: 'Faturamento Estimado:',
      default_model: 'Modelo Padrão',
      mod1_desc: 'Diagnósticos acionáveis baseados em dados reais e oportunidades de alta demanda reprimida.',
      rec1: '🎯 **Foco em Velas e Topos**: Estas categorias representam mais de 65% do volume consolidado. Oportunidade clara em criar variações de kits.',
      rec2: '💵 **Faixa Ideal de Preço**: O sweet spot de conversão está entre R$ 25,00 e R$ 60,00, concentrando a maior tração de vendas.',
      rec3: '⚡ **Kits com Envio Rápido**: Anúncios com marcação de "Envio 24h" ou "FULL" apresentam velocidade de tração 2.8x superior.',
      niche1: '✨ **Temas Infantis Específicos**: Temas como "Safari Baby", "Moana" e "Sonic" possuem altíssima procura e baixa variação de preço.',
      niche2: '💍 **Noivinhos & Topos Personalizados**: Peças acima de R$ 120,00 possuem margem líquida superior a 45% com excelente aceitação.',
      niche3: '📦 **Lotes de Lembrancinhas (10 a 30 un)**: Combos para aniversários infantis aumentam o Ticket Médio por pedido em 40%.',
      mod2_desc: 'Ranking combinado dos principais vendedores e itens com maior tração no mercado.',
      fake_prod1: 'Vela Personalizada Luxo',
      fake_prod2: 'Topo de Bolo Casamento',
      mod3_desc: 'Termos mais frequentes nos títulos líderes, combinações long-tail e modelos de alta conversão.',
      kw1: 'Personalizado',
      kw2: 'Kit Festa',
      kw3: 'Topo Bolo',
      kw4: 'Pronta Entrega',
      title1: 'Vela Aniversário Biscuit Personalizada Tema Infantil + Envio 24h',
      title2: 'Topo De Bolo Casamento Noivinhos Biscuit Personalizados Luxo',
      title3: 'Kit 10 Lembrancinhas Safari Biscuit Festa Infantil Pronta Entrega',
      lt1: 'Vela personalizada + [Nome da Criança] + [Idade]',
      lt2: 'Topo de bolo biscuit + [Tema] + [Envio Rápido]',
      lt3: 'Kit lembrancinha biscuit + [Quantidade] unidades + [Tema]',
      mod4_desc: 'Participação entre Mercado Livre e Shopee, e volume por zona de preço.'
    },
    product_modal: {
      title: '🔎 Análise Detalhada:',
      general: 'Geral',
      platform: 'Plataforma',
      current_price: 'Preço Atual',
      total_sales: 'Vendas Acumuladas',
      units_label: 'unidades',
      unit_short: 'un',
      seller_origin: 'Vendedor / Origem',
      original_ad: 'Anúncio Original',
      view_in_store: 'Acessar na Loja ↗',
      history_chart_title: '📈 Histórico de Evolução (Preço x Vendas)',
      loading_chart: 'Carregando dados históricos do anúncio...',
      scrape_records: '📅 Registro de Coletas',
      col_date: 'Data da Coleta',
      close_window: 'Fechar janela'
    },
    seller_modal: {
      store_ads: 'Anúncios da Loja:',
      mapped_ads: 'Anúncios Mapeados',
      products_count: 'produtos',
      total_sales: 'Vendas Totais',
      estimated_revenue: 'Faturamento Estimado',
      ads_list: '📦 Lista de Anúncios deste Vendedor',
      col_title: 'Título do Anúncio',
      col_price: 'Preço Atual',
      col_sales: 'Vendas Totais',
      col_actions: 'Ações',
      empty: 'Nenhum anúncio encontrado para este vendedor.',
      inspect_tooltip: 'Ver gráfico e histórico do anúncio',
      store_tooltip: 'Abrir anúncio na loja original',
      close_window: 'Fechar janela'
    },
    login_modal: {
      connected: '🟢 Conectado',
      logout: 'Sair',
      login: 'Entrar',
      email_placeholder: 'E-mail admin',
      password_placeholder: 'Senha',
      login_failed: 'Falha no login'
    },
    category_manager: {
      title: '🏷️ Gerenciador Dinâmico de Categorias',
      local_sim: 'Simulação Local',
      expand: '▼ Expandir',
      collapse: '▲ Minimizar',
      subtitle: 'Associe palavras-chave aos nomes das categorias para organizar os produtos.',
      if_title_contains: 'Se o título contiver:',
      category_label: '➔ Categoria:',
      keyword_placeholder: 'ex: noivos',
      category_placeholder: 'ex: Casamento',
      add_rule: '+ Adicionar Regra',
      save_rules: '💾 Aplicar e Salvar Regras',
      error_cloud: 'Erro ao salvar categorias na nuvem!',
      success_cloud: 'Categorias salvas na nuvem!',
      saved_local: 'Regras salvas localmente (Logue para persistir na nuvem)'
    },
    ai_filter: {
      title: '🤖 Gerador de Filtros Assistido por IA',
      natural_lang: 'Linguagem Natural',
      description: 'Descreva em uma frase o que você deseja monitorar no mercado e a IA preencherá as palavras-chave e a blacklist automaticamente.',
      input_placeholder: 'Ex: Quero monitorar topos de bolo infantis de biscuit, mas sem ver moldes de silicone nem estecas',
      btn_processing: '⏳ Processando...',
      btn_generate: '✨ Gerar Filtros',
      generated_title: '✅ Filtros Gerados pela IA:',
      suggested_terms: '🔍 Termos de Busca sugeridos:',
      blacklist_label: '🚫 Blacklist (Palavras a ignorar):',
      btn_apply: '🚀 Aplicar aos Meus Filtros do Robô'
    },
    auth: {
      login_title: 'Acesso à Plataforma',
      login_subtitle: 'Painel de Inteligência Competitiva e Análise de Mercado',
      email_label: 'E-mail de Acesso',
      email_placeholder: 'seu@email.com',
      password_label: 'Sua Senha',
      password_placeholder: '••••••••',
      btn_login: 'Entrar no Dashboard 🚀',
      btn_logging_in: 'Autenticando...',
      login_failed: 'Credenciais inválidas. Verifique seu e-mail e senha.',
      secure_access: 'Acesso Seguro & Criptografado',
      logout: 'Sair',
      logged_as: 'Conectado como'
    },
    alert: {
      anti_bot_title: 'Alerta de Coleta Automática',
      anti_bot_desc: 'O robô de coleta encontrou uma verificação de segurança (Anti-bot/Captcha) na última execução. Os dados históricos anteriores continuam disponíveis.',
      dismiss: 'Entendido'
    }
  },
  en: {
    navbar: {
      badge: 'Active Intelligence',
      login: 'Sign In',
      logout: 'Sign Out',
      toggle_tooltip: 'Switch to Portuguese'
    },
    global: {
      connecting_db: 'Connecting to secure Supabase database...',
      error_loading: '⚠️ An error occurred while loading data:',
      no_scrapes: 'No scrape records',
      loading_dates: 'Loading dates...',
      real_time_updates: 'Real-time updated data',
      all_history: 'All History',
      last_days: 'Last {days} Days',
      until: 'until',
      at: 'at',
      chart: 'Chart',
      table: 'Table',
      view_ad: 'View Ad ↗',
      both: 'Both',
      actions: 'Actions'
    },
    filters: {
      title: 'Global Super Filters',
      subtitle: 'Updates all dashboard KPIs, charts, and tables in real-time',
      platform: 'Platform:',
      both: '🌐 Both',
      category: 'Category:',
      all_categories: 'All Categories',
      min_sales: 'Minimum Sales:',
      min_sales_placeholder: 'Ex: 50',
      hide_zero: 'Hide zero-sales items',
      show_hidden: 'Show silenced ads',
      price_range: 'Price Range:',
      timeline_title: 'Scrape Timeline',
      latest_scrape: 'Last updated:'
    },
    tabs: {
      overview: '📊 Market Overview',
      trending: '🚀 Trending & Viral Products',
      pricing: '🏷️ Price Strategy & Sweet Spots'
    },
    kpis: {
      total_items: 'Total Products',
      avg_price: 'Average Price',
      top_platform: 'Top Platform',
      champion_product: 'Top Product',
      revenue: 'Estimated Revenue',
      sales: 'Total Sales',
      sales_suffix: 'sales',
      unit_million: 'M',
      unit_thousand: 'k',
      total_items_sub: 'Monitored listings',
      avg_price_sub: 'Average active price',
      top_platform_sub: 'Channel with highest supply',
      champion_product_sub: 'Sales volume leader',
      revenue_sub: 'Est. (Price × Sales)'
    },
    sections: {
      ai_title: '🧠 Executive AI Intelligence',
      ai_subtitle: 'Automated market diagnostics to guide your strategic decisions.',
      kpi_title: '💰 Financial & Consolidated Metrics',
      kpi_subtitle: 'Overview of values, pricing and volume captured across the monitored niche.',
      charts_title: '📊 Visual Competition & Category Mapping',
      charts_subtitle: 'Distribution of leading stores, price brackets and market categories.',
      table_title: '🔍 Complete Product Catalog',
      table_subtitle: 'Breakdown of each scraped ad with price, seller, and official links.'
    },
    timeline: {
      badge: 'SCRAPE TIMELINE',
      title: 'Explore Historical Market Evolution',
      subtitle: 'Select a specific date to view the Market Snapshot for that day, or enable date comparison',
      mode_single: 'Single Mode',
      mode_compare: 'Compare Dates Mode',
      compare_tooltip: 'Compare two past scrapes side by side',
      records: 'records',
      point_a: 'Point A (Base):',
      point_b: 'Point B (Current):',
      latest: 'Latest'
    },
    table: {
      title: 'Monitored Products Database',
      subtitle: 'Click column headers to sort ascending / descending (▲ / ▼)',
      search_placeholder: 'Search by title...',
      export_csv: '⬇️ Export CSV',
      col_platform: 'Platform',
      col_category: 'Category',
      col_product: 'Product Title',
      col_price: 'Current Price',
      col_old_price: 'Old Price',
      col_variation: 'Variation',
      col_sales: 'Total Sales',
      col_actions: 'Actions',
      new_badge: '✨ New',
      new_badge_title: 'Recently identified',
      sales_growth_title: 'New sales recorded in the selected period',
      sales_stable_title: 'No new sales in the period',
      view_details_title: 'View full ad details',
      open_store_title: 'Open original ad in store',
      silence_ad_title: 'Hide / Mute this ad',
      restore_ad_title: 'Restore product',
      confirm_hide: 'Do you want to hide/mute the ad:\n\n"{title}"\n\nYou can undo this later.',
      empty: 'No products found matching the applied filters.',
      loading_more: 'Loading more products...',
      btn_load_more: 'Load more products ↓',
      csv_headers: ['Platform', 'Category', 'Title', 'Current Price (R$)', 'Total Sales', 'Sales Growth', 'Price Variation (R$)', 'Creation Date', 'Link']
    },
    charts: {
      top_sellers: '🏆 Top Selling Stores by Revenue',
      top_sellers_desc: 'Stores and sellers with the highest sales volume in the market',
      top_products: '🔥 Top 10 Best Selling Products in Niche',
      category_share: '🥧 Sales Volume Share by Category',
      category_share_desc: 'Market share and total units sold in each segment',
      price_vs_sales: '🎯 Sales Volume Distribution by Price Range',
      price_vs_sales_desc: 'Discover which price range generates the most sales in the market',
      units_short: 'units',
      units_sold: 'units sold',
      sales_analyzed: 'sales analyzed',
      waiting_data: 'Waiting for data to calculate distribution...',
      up_to: 'Up to',
      above: 'Above',
      col_seller: 'Seller / Store',
      col_ads: 'Active Ads',
      ad: 'ad',
      ads: 'ads',
      empty_sellers: 'No seller data to display at this time.',
      seller_note: 'Note on Sellers:',
      seller_note_desc: 'Official seller names will be automatically synced and populated on the next scrape run.',
      view_chart_title: 'View as bar chart',
      view_table_title: 'View as detailed table'
    },
    trending: {
      title: '🔥 Acceleration Ranking & Sales Trends',
      subtitle: 'Products that recorded the highest volume of <strong>new sales</strong> between the latest scrape and the selected history.',
      top_accelerator: 'Top Accelerator:',
      na: 'N/A',
      units: 'units',
      total_new_sales: 'Total New Sales:',
      col_position: 'Position',
      col_platform_store: 'Platform / Store',
      col_ad: 'Product Ad',
      col_current_price: 'Current Price',
      col_total_sales: 'Total Sales',
      col_velocity: 'Velocity & New Sales',
      col_action: 'Action',
      unknown_seller: 'Unknown Seller',
      high_acceleration: '⚡ High Acceleration',
      growing: '📈 Growing',
      stable: '🌱 Stable',
      empty_state: '🔍 No products showed new sales in the selected period.',
      view_ad: 'View Ad ↗',
      open_ad_title: 'Open ad in marketplace'
    },
    strategy: {
      title: '🏷️ Pricing & Strategy Monitor',
      subtitle: 'Competitor behavioral analysis: identify products with <strong>margin increase</strong> vs products in a <strong>price/discount war</strong>.',
      price_increased: 'Increased Price',
      price_dropped: 'Dropped Price',
      card1_title: 'Price & Margin Increase',
      card1_desc: 'Products that raised their value without stagnating sales',
      col_product: 'Product / Seller',
      col_before: 'Before',
      col_now: 'Now',
      col_variation: 'Variation',
      seller: 'Seller',
      no_increases: 'No price increases recorded in the period.',
      card2_title: 'Price War & Discounts',
      card2_desc: 'Products that lowered their value to gain volume',
      no_drops: 'No price reductions recorded in the period.'
    },
    report: {
      title: 'Executive Market Intelligence Report',
      badge: 'AI Analytics',
      subtitle: 'Advanced strategic diagnosis based on real-time quantitative market data',
      expand: '▼ Expand Insights',
      collapse: '▲ Minimize',
      updated_at: 'Updated at',
      loading: 'Generating report with Artificial Intelligence...',
      tab_strategy: '🎯 Strategy & Niches',
      tab_sellers: '🏆 Top Stores & Products',
      tab_seo: '🏷️ SEO Strategy',
      tab_platforms: '⚔️ Marketplace Battle',
      sub_recommendations: '💡 Actionable Strategic Recommendations',
      sub_niches: '🚀 High-Demand Hidden Niches',
      sub_keywords: '🏷️ Top Converting Keyword Frequency',
      sub_titles: '🎯 High-Converting Title Templates',
      sub_longtail: '🔗 Recommended Long-Tail Formulas',
      view_store: 'View Store 🔎',
      sales_units: 'sales',
      active_stores: 'Active Stores:',
      sales_volume: 'Sales Volume:',
      est_revenue: 'Estimated Revenue:',
      default_model: 'Default Model',
      mod1_desc: 'Actionable diagnostics based on real data and high repressed demand opportunities.',
      rec1: '🎯 **Focus on Candles and Toppers**: These categories represent over 65% of consolidated volume. Clear opportunity to create kit variations.',
      rec2: '💵 **Ideal Price Range**: The conversion sweet spot is between R$ 25.00 and R$ 60.00, concentrating the most sales traction.',
      rec3: '⚡ **Fast Shipping Kits**: Ads marked "24h Shipping" or "FULL" show 2.8x higher traction velocity.',
      niche1: '✨ **Specific Kids Themes**: Themes like "Safari Baby", "Moana", and "Sonic" have very high demand and low price variation.',
      niche2: '💍 **Wedding Toppers & Custom Figures**: Pieces over R$ 120.00 have a net margin above 45% with excellent acceptance.',
      niche3: '📦 **Party Favor Bundles (10-30 pcs)**: Combos for kids birthdays increase Average Order Value by 40%.',
      mod2_desc: 'Combined ranking of top sellers and items with the highest market traction.',
      fake_prod1: 'Custom Luxury Candle',
      fake_prod2: 'Wedding Cake Topper',
      mod3_desc: 'Most frequent terms in leading titles, long-tail combinations, and high-converting templates.',
      kw1: 'Custom',
      kw2: 'Party Kit',
      kw3: 'Cake Topper',
      kw4: 'Ready to Ship',
      title1: 'Custom Biscuit Birthday Candle Kids Theme + 24h Ship',
      title2: 'Wedding Cake Topper Custom Biscuit Figures Luxury',
      title3: 'Kit 10 Biscuit Safari Party Favors Kids Ready to Ship',
      lt1: 'Custom candle + [Child Name] + [Age]',
      lt2: 'Biscuit cake topper + [Theme] + [Fast Ship]',
      lt3: 'Biscuit party favor kit + [Quantity] units + [Theme]',
      mod4_desc: 'Market share between Mercado Livre and Shopee, and volume by price zone.'
    },
    product_modal: {
      title: '🔎 Detailed Analysis:',
      general: 'General',
      platform: 'Platform',
      current_price: 'Current Price',
      total_sales: 'Accumulated Sales',
      units_label: 'units',
      unit_short: 'units',
      seller_origin: 'Seller / Origin',
      original_ad: 'Original Ad',
      view_in_store: 'Open in Store ↗',
      history_chart_title: '📈 Historical Evolution (Price vs Sales)',
      loading_chart: 'Loading historical ad data...',
      scrape_records: '📅 Scrape Records',
      col_date: 'Scrape Date',
      close_window: 'Close window'
    },
    seller_modal: {
      store_ads: 'Store Ads:',
      mapped_ads: 'Mapped Ads',
      products_count: 'products',
      total_sales: 'Total Sales',
      estimated_revenue: 'Estimated Revenue',
      ads_list: '📦 Ads List for this Seller',
      col_title: 'Ad Title',
      col_price: 'Current Price',
      col_sales: 'Total Sales',
      col_actions: 'Actions',
      empty: 'No ads found for this seller.',
      inspect_tooltip: 'View ad chart and history',
      store_tooltip: 'Open ad in original store',
      close_window: 'Close window'
    },
    login_modal: {
      connected: '🟢 Connected',
      logout: 'Sign Out',
      login: 'Sign In',
      email_placeholder: 'Admin email',
      password_placeholder: 'Password',
      login_failed: 'Login failed'
    },
    category_manager: {
      title: '🏷️ Dynamic Category Manager',
      local_sim: 'Local Simulation',
      expand: '▼ Expand',
      collapse: '▲ Minimize',
      subtitle: 'Associate keywords with category names to organize products.',
      if_title_contains: 'If title contains:',
      category_label: '➔ Category:',
      keyword_placeholder: 'ex: wedding',
      category_placeholder: 'ex: Wedding',
      add_rule: '+ Add Rule',
      save_rules: '💾 Apply and Save Rules',
      error_cloud: 'Error saving categories to cloud!',
      success_cloud: 'Categories saved to cloud!',
      saved_local: 'Rules saved locally (Log in to persist to cloud)'
    },
    ai_filter: {
      title: '🤖 AI-Assisted Filter Generator',
      natural_lang: 'Natural Language',
      description: 'Describe in a sentence what you want to monitor in the market and AI will automatically populate keywords and blacklist.',
      input_placeholder: 'Ex: I want to monitor biscuit birthday cake toppers, but without silicone molds or sculpting tools',
      btn_processing: '⏳ Processing...',
      btn_generate: '✨ Generate Filters',
      generated_title: '✅ AI Generated Filters:',
      suggested_terms: '🔍 Suggested Search Terms:',
      blacklist_label: '🚫 Blacklist (Words to ignore):',
      btn_apply: '🚀 Apply to My Scraper Filters'
    },
    auth: {
      login_title: 'Platform Login',
      login_subtitle: 'Competitive Market Intelligence & Analytics Dashboard',
      email_label: 'Email Address',
      email_placeholder: 'you@email.com',
      password_label: 'Password',
      password_placeholder: '••••••••',
      btn_login: 'Sign in to Dashboard 🚀',
      btn_logging_in: 'Signing in...',
      login_failed: 'Invalid credentials. Please check your email and password.',
      secure_access: 'Secure & Encrypted Access',
      logout: 'Logout',
      logged_as: 'Logged in as'
    },
    alert: {
      anti_bot_title: 'Automated Collection Alert',
      anti_bot_desc: 'The automated scraper encountered a security challenge (Anti-bot/Captcha) on its last run. Previous historical data remains available.',
      dismiss: 'Dismiss'
    }
  }
}

export function useAppI18n() {
  if (process.client) {
    const saved = localStorage.getItem('app_user_locale')
    if (saved === 'pt' || saved === 'en') {
      currentLocale.value = saved
    }
  }

  function setLocale(lang: 'pt' | 'en') {
    currentLocale.value = lang
    if (process.client) {
      localStorage.setItem('app_user_locale', lang)
    }
  }

  function toggleLanguage() {
    setLocale(currentLocale.value === 'pt' ? 'en' : 'pt')
  }

  function t(path: string, fallback?: string): string {
    const lang = currentLocale.value || 'pt'
    const keys = path.split('.')
    let curr: any = dictionary[lang]
    for (const k of keys) {
      if (curr && typeof curr === 'object' && k in curr) {
        curr = curr[k]
      } else {
        curr = null
        break
      }
    }
    if (typeof curr === 'string') return curr

    if (lang !== 'pt') {
      let ptCurr: any = dictionary.pt
      for (const k of keys) {
        if (ptCurr && typeof ptCurr === 'object' && k in ptCurr) {
          ptCurr = ptCurr[k]
        } else {
          ptCurr = null
          break
        }
      }
      if (typeof ptCurr === 'string') return ptCurr
    }

    return fallback || path
  }

  function getRaw(path: string): any {
    const lang = currentLocale.value || 'pt'
    const keys = path.split('.')
    let curr: any = dictionary[lang]
    for (const k of keys) {
      if (curr && typeof curr === 'object' && k in curr) {
        curr = curr[k]
      } else {
        curr = null
        break
      }
    }
    if (curr !== null && curr !== undefined) return curr
    if (lang !== 'pt') {
      let ptCurr: any = dictionary.pt
      for (const k of keys) {
        if (ptCurr && typeof ptCurr === 'object' && k in ptCurr) {
          ptCurr = ptCurr[k]
        } else {
          ptCurr = null
          break
        }
      }
      if (ptCurr !== null && ptCurr !== undefined) return ptCurr
    }
    return null
  }

  return {
    locale: currentLocale,
    setLocale,
    toggleLanguage,
    t,
    getRaw
  }
}
