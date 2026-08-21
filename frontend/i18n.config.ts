export default defineI18nConfig(() => ({
  legacy: false,
  locale: 'pt',
  fallbackLocale: 'pt',
  messages: {
    pt: {
      navbar: {
        badge: 'Inteligência Ativa',
        login: 'Entrar na Conta',
        logout: 'Sair da Conta'
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
        est_revenue: 'Faturamento Estimado:'
      },
      filters: {
        title: 'Super Filtros Globais',
        subtitle: 'Altera em tempo real todos os KPIs, gráficos e tabelas do painel',
        platform: 'Plataforma:',
        both: '🌐 Ambas',
        category: 'Categoria:',
        all_categories: 'Todas as Categorias',
        min_sales: 'Vendas Mínimas:',
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
        total_items: 'Itens Monitorados',
        revenue: 'Faturamento Estimado',
        sales: 'Vendas Totais',
        avg_price: 'Ticket Médio'
      },
      table: {
        title: 'Base de Produtos Coletada',
        subtitle: 'Visualização individual dos anúncios com cálculo de velocidade e variação',
        search_placeholder: 'Buscar por título ou loja...',
        export_csv: 'Exportar CSV ⬇',
        col_platform: 'Plataforma',
        col_category: 'Categoria',
        col_product: 'Título Anúncio',
        col_price: 'Preço Atual',
        col_old_price: 'Preço Ant.',
        col_variation: 'Variação',
        col_sales: 'Vendas Totais',
        col_actions: 'Ações',
        empty: 'Nenhum produto encontrado com os filtros aplicados.',
        loading_more: 'Carregando mais produtos...',
        btn_load_more: 'Carregar mais produtos ↓'
      },
      charts: {
        top_sellers: '🏆 Ranking de Vendedores Líderes por Faturamento',
        top_products: '🔥 Top 10 Produtos Mais Vendidos no Nicho',
        category_share: '🥧 Share de Volume de Vendas por Categoria',
        price_vs_sales: '🎯 Distribuição de Vendas por Faixa de Preço'
      }
    },
    en: {
      navbar: {
        badge: 'Active Intelligence',
        login: 'Sign In',
        logout: 'Sign Out'
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
        est_revenue: 'Estimated Revenue:'
      },
      filters: {
        title: 'Global Super Filters',
        subtitle: 'Updates all dashboard KPIs, charts, and tables in real-time',
        platform: 'Platform:',
        both: '🌐 Both',
        category: 'Category:',
        all_categories: 'All Categories',
        min_sales: 'Minimum Sales:',
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
        total_items: 'Monitored Items',
        revenue: 'Estimated Revenue',
        sales: 'Total Sales',
        avg_price: 'Average Ticket'
      },
      table: {
        title: 'Raw Products Database',
        subtitle: 'Individual item tracking with speed metrics and price variation history',
        search_placeholder: 'Search title or store...',
        export_csv: 'Export CSV ⬇',
        col_platform: 'Platform',
        col_category: 'Category',
        col_product: 'Product Title',
        col_price: 'Current Price',
        col_old_price: 'Old Price',
        col_variation: 'Variation',
        col_sales: 'Total Sales',
        col_actions: 'Actions',
        empty: 'No products found matching the applied filters.',
        loading_more: 'Loading more products...',
        btn_load_more: 'Load more products ↓'
      },
      charts: {
        top_sellers: '🏆 Top Selling Stores by Revenue',
        top_products: '🔥 Top 10 Best Selling Products in Niche',
        category_share: '🥧 Sales Volume Share by Category',
        price_vs_sales: '🎯 Sales Volume Distribution by Price Range'
      }
    }
  }
}))
