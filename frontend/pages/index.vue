<template>
  <div class="container">
    <Navbar :projectName="nomeProjeto" />

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ t('global.connecting_db', 'Carregando dados de inteligência de mercado...') }}</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>
        <AlertTriangle :size="16" class="inline-error-icon" />
        {{ t('global.error_loading', 'Ocorreu um erro ao carregar os dados:') }} {{ error }}
      </p>
    </div>

    <div v-else>
      <!-- 1. Métricas Principais (KPIs) no Topo da Página -->
      <KpiCards 
        :totalProducts="totalProducts"
        :averagePrice="averagePrice"
        :topPlatform="topPlatform"
        :topProduct="topProduct"
        :estimatedRevenue="estimatedRevenue"
        :dateRangeText="dateRangeText"
      />

      <!-- 2. Relatório de Inteligência Executiva por IA -->
      <AiExecutiveReport 
        :isLoading="loading" 
        :reportData="aiReportData"
        :products="processedProducts"
      />

      <!-- 3. Comparativo de Marketplaces Fixo e Independente -->
      <MarketplaceComparisonCard 
        :products="processedProducts"
        class="marketplace-standalone-card"
      />

      <!-- 4. Bloco de Filtros Globais em Tempo Real -->
      <div class="glass-panel unified-control-panel animate-fade-in">
        <div class="filters-grid">
          <!-- Grupo Esquerda: Filtros Globais -->
          <div class="filters-left-group">
            <!-- Plataforma -->
            <div class="filter-item platform-item">
              <label>{{ t('filters.platform', 'Plataforma:') }}</label>
              <div class="toggle-group">
                <button 
                  type="button" 
                  :class="['toggle-btn', { active: selectedPlatform === 'Todas' }]" 
                  @click="selectedPlatform = 'Todas'"
                >
                  <Globe :size="14" />
                  <span>{{ t('filters.both', 'Todas') }}</span>
                </button>
                <button 
                  type="button" 
                  :class="['toggle-btn meli-btn', { active: selectedPlatform === 'meli' }]" 
                  @click="selectedPlatform = 'meli'"
                >
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" class="plat-icon">
                    <circle cx="12" cy="12" r="11" fill="#FFE600"/>
                    <path d="M7 12.5L10.5 15.5L17 8.5" stroke="#2D3277" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>Mercado Livre</span>
                </button>
                <button 
                  type="button" 
                  :class="['toggle-btn shopee-btn', { active: selectedPlatform === 'shopee' }]" 
                  @click="selectedPlatform = 'shopee'"
                >
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" class="plat-icon">
                    <rect width="24" height="24" rx="5" fill="#EE4D2D"/>
                    <path d="M7 9V7C7 4.79086 8.79086 3 11 3H13C15.2091 3 17 4.79086 17 7V9M5 9H19L17.5 21H6.5L5 9Z" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M12 11V15M12 15C11 15 9.5 14.2 9.5 13C9.5 11.8 12 12.2 12 11M12 15C13 15 14.5 15.8 14.5 17" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round"/>
                  </svg>
                  <span>Shopee</span>
                </button>
              </div>
            </div>

            <!-- Categoria -->
            <div class="filter-item category-item">
              <label>{{ t('filters.category', 'Categoria:') }}</label>
              <select v-model="selectedCategory" class="glass-input">
                <option value="Todas">{{ t('filters.all_categories', 'Todas as Categorias') }}</option>
                <option v-for="cat in dynamicCategories" :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </div>

            <!-- Sublinha de Vendas Mínimas e Checkbox (compacto e alinhado) -->
            <div class="filter-sub-row">
              <div class="filter-item sales-item">
                <label>{{ t('filters.min_sales', 'Vendas Mín:') }}</label>
                <input type="number" v-model="minSales" :placeholder="t('filters.min_sales_placeholder', 'Ex: 50')" class="glass-input sales-input" />
              </div>

              <div class="filter-item checkboxes-item">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="hideZeroSales" />
                  {{ t('filters.hide_zero', 'Ocultar 0 vendas') }}
                </label>
              </div>
            </div>
          </div>

          <!-- Grupo Direita: Histograma de Faixa de Preço -->
          <div class="filters-right-group">
            <PriceRangeHistogramFilter 
              :items="processedProducts" 
              @filter="(r) => { minPrice = r.min; maxPrice = r.max }" 
            />
          </div>
        </div>
      </div>

      <!-- 5. Abas de Navegação das Visões Grudadas no Bloco de Conteúdo -->
      <div class="views-navigation-wrapper">
        <div class="view-tabs-container">
          <button 
            :class="['view-tab-pill', { active: activeViewTab === 'overview' }]" 
            @click="activeViewTab = 'overview'"
          >
            <BarChart3 :size="16" />
            <span>{{ t('tabs.overview', 'Visão Geral de Mercado') }}</span>
          </button>
          <button 
            :class="['view-tab-pill', { active: activeViewTab === 'trending' }]" 
            @click="activeViewTab = 'trending'"
          >
            <Flame :size="16" />
            <span>{{ t('tabs.trending', 'Produtos em Alta & Aceleração') }}</span>
          </button>
          <button 
            :class="['view-tab-pill', { active: activeViewTab === 'pricing' }]" 
            @click="activeViewTab = 'pricing'"
          >
            <Tag :size="16" />
            <span>{{ t('tabs.pricing', 'Estratégias de Preço & Oportunidades') }}</span>
          </button>
        </div>
      </div>

      <!-- VISÃO 1: Visão Geral de Mercado (Gráficos e Tabela) -->
      <div v-if="activeViewTab === 'overview'" class="overview-layout content-view-attached">
        <!-- SEÇÃO: Mapeamento Visual de Concorrência & Gráficos -->
        <section class="dashboard-section">
          <div class="section-header">
            <div class="section-title-box">
              <h3>{{ t('sections.charts_title', 'Mapeamento Visual de Concorrência') }}</h3>
            </div>
            <p class="section-subtitle">{{ t('sections.charts_subtitle', 'Distribuição de lojas líderes, faixas de preço e categorias de mercado.') }}</p>
          </div>
          
          <div class="charts-container">
            <!-- Linha 1: Top 10 Produtos em Crescimento ocupando linha inteira -->
            <div class="charts-row">
              <TopProductsChart :items="filteredProducts" :isComparing="true" class="full-width" />
            </div>

            <!-- Linha 2: Distribuição de Vendas por Faixa de Preço dividindo com Share de Volume de Vendas por Categoria -->
            <div class="charts-row">
              <PriceVsSalesChart :items="filteredProducts" :isComparing="true" class="half-width" />
              <CategoryVolumeChart :items="filteredProducts" :isComparing="true" class="half-width" />
            </div>
            
            <!-- Linha 3: Ranking de Lojas Líderes -->
            <div class="charts-row">
              <TopSellersChart :items="filteredProducts" :isComparing="true" class="full-width" />
            </div>
          </div>
        </section>

        <!-- SEÇÃO: Catálogo Detalhado de Produtos -->
        <section class="dashboard-section">
          <div class="section-header">
            <div class="section-title-box">
              <h3>{{ t('sections.table_title', 'Catálogo Completo de Produtos') }}</h3>
            </div>
            <p class="section-subtitle">{{ t('sections.table_subtitle', 'Detalhamento de cada produto coletado com preço, vendedor e link oficial.') }}</p>
          </div>
          <DataTable :items="filteredProducts" class="full-width" />
        </section>
      </div>

      <!-- VISÃO 2: Ranking de Aceleração & Tendências -->
      <div v-else-if="activeViewTab === 'trending'" class="content-view-attached">
        <TrendingProductsTab :products="filteredProducts" />
      </div>

      <!-- VISÃO 3: Monitor de Estratégias de Preço -->
      <div v-else-if="activeViewTab === 'pricing'" class="content-view-attached">
        <PriceStrategyMonitor :products="filteredProducts" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Globe, BarChart3, Flame, Tag, AlertTriangle } from 'lucide-vue-next'
import Navbar from '~/components/Navbar.vue'
import KpiCards from '~/components/KpiCards.vue'
import DataTable from '~/components/DataTable.vue'
import TopProductsChart from '~/components/TopProductsChart.client.vue'
import PriceVsSalesChart from '~/components/PriceVsSalesChart.client.vue'
import CategoryVolumeChart from '~/components/CategoryVolumeChart.client.vue'
import TopSellersChart from '~/components/TopSellersChart.client.vue'
import PriceRangeHistogramFilter from '~/components/PriceRangeHistogramFilter.vue'
import MarketplaceComparisonCard from '~/components/MarketplaceComparisonCard.vue'
import TrendingProductsTab from '~/components/TrendingProductsTab.vue'
import PriceStrategyMonitor from '~/components/PriceStrategyMonitor.vue'
import AiExecutiveReport from '~/components/AiExecutiveReport.client.vue'

const supabase = useSupabase()
const { t, locale } = useAppI18n()

// Estados Básicos
const productsRaw = ref([])
const loading = ref(true)
const error = ref(null)
const nomeProjeto = ref('BiscuitInsights')
const aiReportData = ref(null)

// Estado das Visões da Dashboard
const activeViewTab = ref('overview') // 'overview', 'trending', 'pricing'

// Estado dos Filtros Globais
const selectedCategory = ref('Todas')
const selectedPlatform = ref('Todas')
const minPrice = ref(null)
const maxPrice = ref(null)
const minSales = ref(null)
const hideZeroSales = ref(false)

const defaultCategoryRules = [
  { keyword: 'vela', category: 'Velas de Aniversário' },
  { keyword: 'topo', category: 'Topos de Bolo' },
  { keyword: 'noivinho', category: 'Topos de Bolo' },
  { keyword: 'lembrancinha', category: 'Lembrancinhas' },
  { keyword: 'chaveiro', category: 'Chaveiros' },
  { keyword: 'massa', category: 'Kits & Insumos' },
  { keyword: 'base', category: 'Kits & Insumos' },
  { keyword: 'cortador', category: 'Kits & Insumos' },
  { keyword: 'boneco', category: 'Bonecos & Esculturas' },
  { keyword: 'funko', category: 'Bonecos & Esculturas' },
  { keyword: 'escultura', category: 'Bonecos & Esculturas' },
  { keyword: 'aplique', category: 'Lembrancinhas' },
  { keyword: 'caneca', category: 'Canecas Decoradas' }
]

const dynamicCategories = computed(() => {
  const cats = new Set(defaultCategoryRules.map(r => r.category))
  cats.add('Outros')
  return Array.from(cats)
})

function sanitizeProductLink(rawLink, platform) {
  if (!rawLink || typeof rawLink !== 'string') return ''
  if (platform === 'meli' || rawLink.includes('mercadolivre.com')) {
    try {
      const decoded = decodeURIComponent(decodeURIComponent(rawLink))
      const match = decoded.match(/MLB-?(\d{8,12})/)
      if (match) {
        return `https://produto.mercadolivre.com.br/MLB-${match[1]}`
      }
    } catch (e) {}
  }
  return rawLink
}

function getCategoryByRules(title) {
  const t = (title || '').toLowerCase()
  for (const rule of defaultCategoryRules) {
    if (t.includes(rule.keyword.toLowerCase())) return rule.category
  }
  return 'Outros'
}

async function loadDashboardData() {
  try {
    loading.value = true
    error.value = null

    // 1. Carrega configurações globais / insights de IA
    try {
      const { data: cfg } = await supabase
        .from('configuracoes_scraper')
        .select('relatorio_insights, nome_projeto')
        .limit(1)
        .maybeSingle()
      
      if (cfg) {
        if (cfg.relatorio_insights) aiReportData.value = cfg.relatorio_insights
        if (cfg.nome_projeto) nomeProjeto.value = cfg.nome_projeto
      }
    } catch (e) {
      console.warn("Configurações não puderam ser carregadas:", e)
    }

    // 2. Carrega todos os produtos de biscuit diretamente
    const { data: prodData, error: prodErr } = await supabase
      .from('produtos')
      .select(`
        id, plataforma, titulo, link, id_externo, vendedor, criado_em,
        historico_coletas ( preco, vendas_totais, data_coleta )
      `)
      
    if (prodErr) throw prodErr
    
    if (prodData) {
      productsRaw.value = prodData.map(p => {
        const sortedHistory = p.historico_coletas ? p.historico_coletas.sort((a, b) => new Date(b.data_coleta) - new Date(a.data_coleta)) : []
        const latestHistory = sortedHistory.length > 0 ? sortedHistory[0] : {}
        return {
          id: p.id,
          plataforma: p.plataforma,
          titulo: p.titulo,
          link: sanitizeProductLink(p.link, p.plataforma),
          vendedor: p.vendedor || null,
          criado_em: p.criado_em,
          preco: latestHistory.preco || 0,
          vendas_totais: latestHistory.vendas_totais || 0,
          historico_coletas: sortedHistory
        }
      })
    }
  } catch (err) {
    console.error(err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboardData()
})

// Texto explicativo do período para os KPIs
const dateRangeText = computed(() => {
  if (productsRaw.value.length === 0) return t('global.loading_dates', 'Carregando dados...')
  return t('global.real_time_updates', 'Histórico completo consolidado em tempo real')
})

// Processa métricas e variações com base em todo o histórico coletado (100% do período)
const processedProducts = computed(() => {
  return productsRaw.value
    .map(p => {
      const history = p.historico_coletas || []
      let snapshot = { ...p }
      let hist = null
      let varInfo = null
      let salesDiff = 0
      let isNew = false

      if (history.length >= 2) {
        // Ponto mais recente (index 0) e ponto inicial mais antigo coletado (index length - 1)
        const entryLatest = history[0]
        const entryOldest = history[history.length - 1]

        const priceLatest = entryLatest.preco ?? p.preco ?? 0
        const salesLatest = entryLatest.vendas_totais ?? p.vendas_totais ?? 0
        const priceOldest = entryOldest.preco ?? priceLatest
        const salesOldest = entryOldest.vendas_totais ?? 0

        snapshot = { ...p, preco: priceLatest, vendas_totais: salesLatest }
        hist = { preco: priceOldest, vendas_totais: salesOldest }
        salesDiff = Math.max(0, salesLatest - salesOldest)

        if (priceOldest > 0) {
          const diff = priceLatest - priceOldest
          if (Math.abs(diff) > 0.05) {
            varInfo = {
              diff,
              perc: (diff / priceOldest) * 100,
              isPositive: diff > 0,
              isNegative: diff < 0
            }
          }
        }
      } else {
        // Produto recém-extraído com apenas 1 coleta registrada
        // Não conta o total de vendas histórico da plataforma como novas vendas recentes!
        isNew = true
        salesDiff = 0
        hist = null
        varInfo = null
      }

      return {
        ...snapshot,
        categoria: getCategoryByRules(snapshot.titulo),
        isNew,
        hist,
        varInfo,
        salesDiff
      }
    })
    .sort((a, b) => (b.vendas_totais || 0) - (a.vendas_totais || 0))
})

// Aplica os Filtros Globais
const filteredProducts = computed(() => {
  let result = processedProducts.value

  if (selectedCategory.value !== 'Todas') {
    result = result.filter(p => p.categoria === selectedCategory.value)
  }
  if (selectedPlatform.value !== 'Todas') {
    result = result.filter(p => p.plataforma === selectedPlatform.value)
  }
  if (minPrice.value !== null && minPrice.value !== '') {
    result = result.filter(p => p.preco >= Number(minPrice.value))
  }
  if (maxPrice.value !== null && maxPrice.value !== '') {
    result = result.filter(p => p.preco <= Number(maxPrice.value))
  }
  if (minSales.value !== null && minSales.value !== '') {
    result = result.filter(p => (p.vendas_totais || 0) >= Number(minSales.value))
  }
  if (hideZeroSales.value) {
    result = result.filter(p => (p.vendas_totais || 0) > 0)
  }

  return result
})

// KPIs Globais
const totalProducts = computed(() => filteredProducts.value.length)
const averagePrice = computed(() => {
  if (filteredProducts.value.length === 0) return 0
  const validPrices = filteredProducts.value.filter(p => p.preco > 0)
  if (validPrices.length === 0) return 0
  const sum = validPrices.reduce((acc, p) => acc + p.preco, 0)
  return sum / validPrices.length
})
const topPlatform = computed(() => {
  if (filteredProducts.value.length === 0) return ''
  const counts = filteredProducts.value.reduce((acc, p) => {
    acc[p.plataforma] = (acc[p.plataforma] || 0) + 1
    return acc
  }, {})
  return Object.keys(counts).reduce((a, b) => counts[a] > counts[b] ? a : b)
})
const topProduct = computed(() => filteredProducts.value.length > 0 ? filteredProducts.value[0] : null)
const estimatedRevenue = computed(() => filteredProducts.value.reduce((acc, p) => acc + ((p.preco || 0) * (p.vendas_totais || 0)), 0))
</script>

<style scoped>
.marketplace-standalone-card {
  margin-bottom: 1.4rem;
}

.overview-layout {
  display: flex;
  flex-direction: column;
  gap: 1.4rem;
}

.content-view-attached {
  animation: fadeIn 0.25s ease;
}

.dashboard-section {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 1.35rem;
  box-shadow: 0 4px 15px -2px rgba(15, 23, 42, 0.04);
}

.section-header {
  margin-bottom: 1.1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid #f1f5f9;
}

.section-title-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.25rem;
}

.section-title-box h3 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 800;
  color: #0f172a;
}

.section-subtitle {
  margin: 0;
  font-size: 0.82rem;
  color: #64748b;
}

.charts-container {
  display: flex;
  flex-direction: column;
  gap: 1.35rem;
}

.charts-row {
  display: flex;
  gap: 1.35rem;
  flex-wrap: wrap;
}

.full-width {
  width: 100%;
}

.half-width {
  flex: 1;
  min-width: 380px;
}

.unified-control-panel {
  padding: 0.85rem 1.25rem;
  margin-bottom: 1.2rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 16px;
  box-shadow: 0 4px 15px -2px rgba(15, 23, 42, 0.04);
}

.filters-grid {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem 1.4rem;
  width: 100%;
}

.filters-left-group {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.85rem 1.2rem;
  flex: 1;
}

.filter-sub-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.filters-right-group {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  flex-shrink: 0;
}

.filter-item label {
  font-size: 0.85rem;
  font-weight: 700;
  color: #475569;
  white-space: nowrap;
}

.category-item {
  flex: 0 1 210px;
  min-width: 160px;
  max-width: 240px;
}

.category-item select {
  width: 100%;
}

.glass-input {
  background: #ffffff;
  border: 1.5px solid #cbd5e1;
  color: #0f172a;
  padding: 0.45rem 0.75rem;
  border-radius: 9px;
  outline: none;
  font-size: 0.86rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.glass-input:focus {
  border-color: #d97706;
  box-shadow: 0 0 0 3px rgba(217, 119, 6, 0.15);
}

.sales-item {
  flex-shrink: 0;
}

.sales-input {
  width: 75px;
}

.checkboxes-item {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.84rem;
  font-weight: 700;
  color: #475569;
  cursor: pointer;
  white-space: nowrap;
}

/* Abas de Navegação das Visões Grudadas no Conteúdo */
.views-navigation-wrapper {
  margin-bottom: 1rem;
}

.view-tabs-container {
  display: flex;
  gap: 0.5rem;
  background: #f1f5f9;
  padding: 0.35rem;
  border-radius: 12px;
  border: 1px solid #cbd5e1;
  width: 100%;
}

.view-tab-pill {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.65rem 1rem;
  font-size: 0.88rem;
  font-weight: 700;
  color: #475569;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 9px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-tab-pill:hover {
  background: #ffffff;
  color: #0f172a;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.04);
}

.view-tab-pill.active {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
  color: #ffffff;
  border-color: #b45309;
  box-shadow: 0 3px 10px rgba(217, 119, 6, 0.25);
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 40vh;
  color: #64748b;
  font-size: 1.1rem;
  font-weight: 600;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #fde68a;
  border-left-color: #d97706;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 880px) {
  .half-width {
    min-width: 100%;
    width: 100%;
  }
  .charts-row {
    flex-direction: column;
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  .unified-control-panel {
    padding: 0.85rem 0.9rem;
    border-radius: 14px;
  }
  .filters-grid {
    flex-direction: column;
    align-items: stretch;
    gap: 0.85rem;
  }
  .filters-left-group {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
    width: 100%;
  }
  .platform-item {
    width: 100%;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.35rem;
  }
  .platform-item .toggle-group {
    width: 100%;
    display: flex;
  }
  .platform-item .toggle-btn {
    flex: 1;
    justify-content: center;
    padding: 0.45rem 0.25rem;
    font-size: 0.76rem;
    gap: 0.2rem;
  }
  .category-item {
    max-width: 100%;
    width: 100%;
    flex: 1 1 100%;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.35rem;
  }
  .category-item select {
    width: 100%;
    font-size: 0.88rem;
    padding: 0.5rem 0.75rem;
  }
  .filter-sub-row {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    flex-wrap: nowrap;
  }
  .filter-sub-row .sales-item {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 0.35rem;
    flex-shrink: 0;
  }
  .filter-sub-row .sales-item label {
    font-size: 0.78rem;
    white-space: nowrap;
  }
  .filter-sub-row .sales-input {
    width: 58px;
    padding: 0.4rem 0.45rem;
    font-size: 0.84rem;
  }
  .filter-sub-row .checkboxes-item {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-end;
    flex-shrink: 0;
  }
  .filter-sub-row .checkbox-label {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.78rem;
    white-space: nowrap;
  }
  .filters-right-group {
    width: 100%;
  }
  .view-tabs-container {
    flex-direction: column;
    gap: 0.4rem;
  }
  .view-tab-pill {
    width: 100%;
    padding: 0.6rem 0.8rem;
    font-size: 0.84rem;
  }
}
</style>
