<template>
  <div class="container">
    <Navbar :projectName="nomeProjeto" />

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ t('global.connecting_db', 'Carregando dados de inteligência de mercado...') }}</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>{{ t('global.error_loading', '⚠️ Ocorreu um erro ao carregar os dados:') }} {{ error }}</p>
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

      <!-- 3. Super Bloco Unificado de Controle (Filtros Globais + Barra de Intervalo Histórico + Abas de Visão) -->
      <div class="glass-panel unified-control-panel animate-fade-in">
        <!-- 1. Linha Superior: Filtros Globais em Tempo Real -->
        <div class="control-header-row">
          <div class="filters-main-row">
            <!-- Plataforma -->
            <div class="filter-item">
              <label>{{ t('filters.platform', 'Plataforma:') }}</label>
              <div class="toggle-group">
                <button 
                  type="button" 
                  :class="['toggle-btn', { active: selectedPlatform === 'Todas' }]" 
                  @click="selectedPlatform = 'Todas'"
                >
                  🌐 {{ t('filters.both', 'Todas') }}
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
                  Mercado Livre
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
                  Shopee
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

            <!-- Vendas Mínimas -->
            <div class="filter-item sales-item">
              <label>{{ t('filters.min_sales', 'Vendas Mín:') }}</label>
              <input type="number" v-model="minSales" :placeholder="t('filters.min_sales_placeholder', 'Ex: 50')" class="glass-input sales-input" />
            </div>

            <!-- Checkbox Rápido 0 vendas -->
            <div class="filter-item checkboxes-item">
              <label class="checkbox-label">
                <input type="checkbox" v-model="hideZeroSales" />
                {{ t('filters.hide_zero', 'Ocultar 0 vendas') }}
              </label>
            </div>

            <!-- Botão Histograma -->
            <div class="filter-item">
              <button 
                type="button" 
                class="btn-toggle-histogram" 
                @click="showPriceHistogram = !showPriceHistogram"
              >
                📊 {{ showPriceHistogram ? t('filters.hide_price_range', 'Ocultar Faixa de Preços') : t('filters.filter_price_range', 'Filtrar Faixa de Preços') }}
              </button>
            </div>
          </div>
        </div>
        
        <!-- Histograma de Preços Expansível -->
        <transition name="slide-fade">
          <div v-if="showPriceHistogram" class="histogram-expand-wrapper">
            <PriceRangeHistogramFilter 
              :items="processedProducts" 
              @filter="(r) => { minPrice = r.min; maxPrice = r.max }" 
            />
          </div>
        </transition>

        <!-- 2. Linha Intermediária: Barra de Evolução Histórica (Data Inicial ➔ Data Final) -->
        <TimelineScrapeSelector 
          :rawItems="productsRaw" 
          @select-date="onTimelineSelectDate"
          @compare-dates="onTimelineCompareDates"
        />

        <!-- 3. Linha Inferior: Abas de Navegação das Visões -->
        <div class="control-bottom-row">
          <div class="view-tabs-group full-width">
            <button 
              :class="['view-tab-btn', { active: activeViewTab === 'overview' }]" 
              @click="activeViewTab = 'overview'"
            >
              {{ t('tabs.overview', '📊 Visão Geral de Mercado') }}
            </button>
            <button 
              :class="['view-tab-btn', { active: activeViewTab === 'trending' }]" 
              @click="activeViewTab = 'trending'"
            >
              {{ t('tabs.trending', '🚀 Produtos em Alta & Aceleração') }}
            </button>
            <button 
              :class="['view-tab-btn', { active: activeViewTab === 'pricing' }]" 
              @click="activeViewTab = 'pricing'"
            >
              {{ t('tabs.pricing', '🏷️ Estratégias de Preço & Oportunidades') }}
            </button>
          </div>
        </div>
      </div>

      <!-- VISÃO 1: Visão Geral de Mercado (Gráficos e Tabela) -->
      <div v-if="activeViewTab === 'overview'" class="overview-layout">
        <!-- SEÇÃO 2: Mapeamento Visual de Concorrência & Gráficos -->
        <section class="dashboard-section">
          <div class="section-header">
            <div class="section-title-box">
              <span class="section-badge blue">📊 {{ t('sections.badge_competition', 'Concorrência') }}</span>
              <h3>{{ t('sections.charts_title', 'Mapeamento Visual de Concorrência') }}</h3>
            </div>
            <p class="section-subtitle">{{ t('sections.charts_subtitle', 'Distribuição de lojas líderes, faixas de preço e categorias de mercado.') }}</p>
          </div>
          
          <div class="charts-container">
            <div class="charts-row">
              <TopProductsChart :items="filteredProducts" class="half-width" />
              <PriceVsSalesChart :items="filteredProducts" class="half-width" />
            </div>
            
            <div class="charts-row">
              <TopSellersChart :items="filteredProducts" class="full-width" />
            </div>

            <div class="charts-row">
              <CategoryVolumeChart :items="filteredProducts" class="half-width" />
              <PlatformMarketShareChart :items="filteredProducts" class="half-width" />
            </div>
          </div>
        </section>

        <!-- SEÇÃO 4: Catálogo Detalhado de Anúncios -->
        <section class="dashboard-section">
          <div class="section-header">
            <div class="section-title-box">
              <span class="section-badge purple">🔍 {{ t('sections.badge_products', 'Produtos') }}</span>
              <h3>{{ t('sections.table_title', 'Catálogo Completo de Anúncios') }}</h3>
            </div>
            <p class="section-subtitle">{{ t('sections.table_subtitle', 'Detalhamento de cada anúncio coletado com preço, vendedor e link oficial.') }}</p>
          </div>
          <DataTable :items="filteredProducts" class="full-width" />
        </section>
      </div>

      <!-- VISÃO 2: Ranking de Aceleração & Tendências -->
      <div v-else-if="activeViewTab === 'trending'">
        <TrendingProductsTab :products="filteredProducts" />
      </div>

      <!-- VISÃO 3: Monitor de Estratégias de Preço -->
      <div v-else-if="activeViewTab === 'pricing'">
        <PriceStrategyMonitor :products="filteredProducts" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import Navbar from '~/components/Navbar.vue'
import KpiCards from '~/components/KpiCards.vue'
import DataTable from '~/components/DataTable.vue'
import TopProductsChart from '~/components/TopProductsChart.client.vue'
import PriceVsSalesChart from '~/components/PriceVsSalesChart.client.vue'
import CategoryVolumeChart from '~/components/CategoryVolumeChart.client.vue'
import PlatformMarketShareChart from '~/components/PlatformMarketShareChart.client.vue'
import TopSellersChart from '~/components/TopSellersChart.client.vue'
import TimelineScrapeSelector from '~/components/TimelineScrapeSelector.vue'
import PriceRangeHistogramFilter from '~/components/PriceRangeHistogramFilter.vue'
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
const timelineSelectedDate = ref(null)
const timelineCompareRange = ref(null)

function onTimelineSelectDate(dateStr) {
  timelineCompareRange.value = null
  timelineSelectedDate.value = dateStr
}

function onTimelineCompareDates({ dateA, dateB }) {
  timelineSelectedDate.value = null
  timelineCompareRange.value = { dateA, dateB }
}

// Estado dos Filtros Globais
const selectedCategory = ref('Todas')
const selectedPlatform = ref('Todas')
const minPrice = ref(null)
const maxPrice = ref(null)
const minSales = ref(null)
const hideZeroSales = ref(false)
const showPriceHistogram = ref(false)

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
          link: p.link,
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
  if (productsRaw.value.length === 0) return t('global.loading_dates', 'Carregando datas...')
  
  if (timelineCompareRange.value) {
    const { dateA, dateB } = timelineCompareRange.value
    const dateLocale = locale.value === 'pt' ? 'pt-BR' : 'en-US'
    const formatStr = (dStr) => new Date(dStr + 'T00:00:00').toLocaleDateString(dateLocale, { day: '2-digit', month: '2-digit', year: 'numeric' })
    return `${formatStr(dateA)} ${t('global.until', 'até')} ${formatStr(dateB)}`
  }

  if (timelineSelectedDate.value) {
    const dateLocale = locale.value === 'pt' ? 'pt-BR' : 'en-US'
    return new Date(timelineSelectedDate.value + 'T00:00:00').toLocaleDateString(dateLocale, { day: '2-digit', month: '2-digit', year: 'numeric' })
  }

  return t('global.real_time_updates', 'Dados atualizados em tempo real')
})

// Processa métricas e variações com base no intervalo de datas selecionado
const processedProducts = computed(() => {
  return productsRaw.value
    .map(p => {
      let snapshot = p
      let hist = null
      let varInfo = null
      let salesDiff = null

      if (timelineCompareRange.value) {
        const { dateA, dateB } = timelineCompareRange.value
        const entryA = p.historico_coletas?.find(h => h.data_coleta && h.data_coleta.startsWith(dateA))
        const entryB = p.historico_coletas?.find(h => h.data_coleta && h.data_coleta.startsWith(dateB))
        
        const priceB = entryB ? entryB.preco : p.preco
        const salesB = entryB ? entryB.vendas_totais : p.vendas_totais
        const priceA = entryA ? entryA.preco : p.preco
        const salesA = entryA ? entryA.vendas_totais : 0

        snapshot = { ...p, preco: priceB, vendas_totais: salesB }
        hist = { preco: priceA, vendas_totais: salesA }
        salesDiff = Math.max(0, salesB - salesA)
        if (priceA > 0) {
          const diff = priceB - priceA
          if (Math.abs(diff) > 0.05) {
            varInfo = { diff, perc: (diff / priceA) * 100, isPositive: diff > 0, isNegative: diff < 0 }
          }
        }
      } else if (timelineSelectedDate.value) {
        const histEntry = p.historico_coletas?.find(h => h.data_coleta && h.data_coleta.startsWith(timelineSelectedDate.value))
        if (histEntry) {
          snapshot = { ...p, preco: histEntry.preco, vendas_totais: histEntry.vendas_totais }
        }
      }

      const createdDate = snapshot.criado_em ? new Date(snapshot.criado_em) : new Date()
      const isNew = (snapshot.historico_coletas && snapshot.historico_coletas.length === 1) || (new Date() - createdDate < 86400000)

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
.overview-layout {
  display: flex;
  flex-direction: column;
  gap: 1.4rem;
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

.section-badge {
  font-size: 0.75rem;
  font-weight: 800;
  padding: 0.2rem 0.55rem;
  border-radius: 99px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.section-badge.green {
  background: #ecfdf5;
  color: #059669;
  border: 1px solid #a7f3d0;
}

.section-badge.blue {
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
}

.section-badge.purple {
  background: #faf5ff;
  color: #7c3aed;
  border: 1px solid #ddd6fe;
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
  min-width: 400px;
}

.unified-control-panel {
  padding: 1.15rem 1.35rem;
  margin-bottom: 1.4rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 18px;
  box-shadow: 0 4px 15px -2px rgba(15, 23, 42, 0.04);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.control-header-row {
  width: 100%;
}

.filters-main-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 1.15rem 1.4rem;
  width: 100%;
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
  flex: 1 1 220px;
  min-width: 200px;
  max-width: 320px;
}

.category-item select {
  width: 100%;
}

.glass-input {
  background: #ffffff;
  border: 1.5px solid #cbd5e1;
  color: #0f172a;
  padding: 0.5rem 0.85rem;
  border-radius: 9px;
  outline: none;
  font-size: 0.88rem;
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
  width: 85px;
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

.btn-toggle-histogram {
  background: #f8fafc;
  border: 1.5px solid #cbd5e1;
  color: #334155;
  font-size: 0.84rem;
  font-weight: 700;
  padding: 0.5rem 0.95rem;
  border-radius: 9px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-toggle-histogram:hover {
  background: #e2e8f0;
  color: #0f172a;
  border-color: #94a3b8;
}

.histogram-expand-wrapper {
  padding-top: 0.5rem;
  border-top: 1px dashed #e2e8f0;
}

.control-bottom-row {
  padding-top: 0.85rem;
  border-top: 1px solid #f1f5f9;
}

.view-tabs-group {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  background: #f8fafc;
  padding: 0.35rem;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.view-tabs-group.full-width {
  width: 100%;
}

.view-tabs-group.full-width .view-tab-btn {
  flex: 1;
  justify-content: center;
  text-align: center;
  padding: 0.65rem 1rem;
}

.view-tab-btn {
  background: transparent;
  border: 1px solid transparent;
  color: #475569;
  padding: 0.55rem 1.1rem;
  border-radius: 9px;
  font-weight: 700;
  font-size: 0.88rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.view-tab-btn:hover {
  background: #ffffff;
  color: #0f172a;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}

.view-tab-btn.active {
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
    gap: 0.85rem;
  }
  .filters-main-row {
    gap: 0.85rem;
  }
  .filter-item {
    width: 100%;
    justify-content: space-between;
  }
  .category-item {
    max-width: 100%;
    width: 100%;
    flex: 1 1 100%;
  }
  .sales-item {
    width: 100%;
  }
  .sales-input {
    flex: 1;
    width: auto;
  }
  .btn-toggle-histogram {
    width: 100%;
    text-align: center;
  }
  .view-tabs-group.full-width {
    flex-direction: column;
    gap: 0.4rem;
  }
  .view-tabs-group.full-width .view-tab-btn {
    width: 100%;
    padding: 0.6rem 0.8rem;
    font-size: 0.84rem;
  }
}
</style>
