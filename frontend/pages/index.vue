<template>
  <div class="container">
    <Navbar :projectName="nomeProjeto" :user="authUser" @auth-change="handleAuthChange" />

    <AntiBotAlert :alerta="statusAlerta" />

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ t('global.connecting_db', 'Conectando à base de dados segura do Supabase...') }}</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>{{ t('global.error_loading', '⚠️ Ocorreu um erro ao carregar os dados:') }} {{ error }}</p>
    </div>

    <div v-else>
      <!-- Relatório de Inteligência Executiva por IA (Fase 4) -->
      <AiExecutiveReport 
        :isLoading="loading || isFetchingNewData" 
        :reportData="aiReportData"
        :products="processedProducts"
      />

      <!-- Banner da Data e Horário da Última Atualização -->
      <div class="last-update-banner animate-fade-in">
        <span>🕒 <strong>{{ t('filters.latest_scrape', 'Última atualização:') }}</strong> {{ lastScrapeFormatted }}</span>
      </div>

      <!-- Super Filtros Globais (Comanda a página) -->
      <div class="glass-panel filters-panel animate-fade-in" style="animation-delay: 0.1s;">
        <div class="filters-header">
          <div>
            <h4>🔍 {{ t('filters.title', 'Super Filtros Globais') }}</h4>
            <span class="filters-info">{{ t('filters.subtitle', 'Altera em tempo real todos os KPIs, gráficos e tabelas do painel') }}</span>
          </div>
        </div>
        
        <div class="filters-grid">
          <!-- Plataforma -->
          <div class="filter-group">
            <label>{{ t('filters.platform', 'Plataforma:') }}</label>
            <div class="toggle-group">
              <button 
                type="button" 
                :class="['toggle-btn', { active: selectedPlatform === 'Todas' }]" 
                @click="selectedPlatform = 'Todas'"
              >
                {{ t('filters.both', '🌐 Ambas') }}
              </button>
              <button 
                type="button" 
                :class="['toggle-btn meli-btn', { active: selectedPlatform === 'meli' }]" 
                @click="selectedPlatform = 'meli'"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="platform-svg">
                  <rect width="24" height="24" rx="12" fill="#FFE600"/>
                  <path d="M7 11.5L10 14.5L17 7.5" stroke="#2D3277" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Mercado Livre
              </button>
              <button 
                type="button" 
                :class="['toggle-btn shopee-btn', { active: selectedPlatform === 'shopee' }]" 
                @click="selectedPlatform = 'shopee'"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="platform-svg">
                  <path d="M6 8V6C6 4.34315 7.34315 3 9 3H15C16.6569 3 18 4.34315 18 6V8M3 8H21L19.5 21H4.5L3 8Z" stroke="#EE4D2D" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M12 11V15M12 15C11 15 9.5 14.2 9.5 13C9.5 11.8 12 12.2 12 11M12 15C13 15 14.5 15.8 14.5 17" stroke="#EE4D2D" stroke-width="1.8" stroke-linecap="round"/>
                </svg>
                Shopee
              </button>
            </div>
          </div>

          <!-- Categoria -->
          <div class="filter-group">
            <label>{{ t('filters.category', 'Categoria:') }}</label>
            <select v-model="selectedCategory" class="glass-input">
              <option value="Todas">{{ t('filters.all_categories', 'Todas as Categorias') }}</option>
              <option v-for="cat in dynamicCategories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>

          <!-- Vendas Mínimas -->
          <div class="filter-group">
            <label>{{ t('filters.min_sales', 'Vendas Mínimas:') }}</label>
            <input type="number" v-model="minSales" :placeholder="t('filters.min_sales_placeholder', 'Ex: 50')" class="glass-input" />
          </div>

          <!-- Ocultar Sem Vendas e Ocultados -->
          <div class="filter-group checkbox-group" style="display: flex; gap: 1rem; flex-wrap: wrap;">
            <label class="checkbox-label">
              <input type="checkbox" v-model="hideZeroSales" />
              {{ t('filters.hide_zero', 'Ocultar produtos com 0 vendas') }}
            </label>
            <label class="checkbox-label text-muted">
              <input type="checkbox" v-model="showHiddenProducts" />
              {{ t('filters.show_hidden', 'Mostrar anúncios silenciados') }}
            </label>
          </div>
        </div>
        
        <!-- Filtro Estilo Upwork: Histograma Interativo de Preços -->
        <div style="margin-top: 1.5rem;">
          <PriceRangeHistogramFilter 
            :items="processedProducts" 
            @filter="(r) => { minPrice = r.min; maxPrice = r.max }" 
          />
        </div>
      </div>

      <!-- Linha do Tempo Interativa de Coletas (Timeline & Date Picker) -->
      <TimelineScrapeSelector 
        :rawItems="productsRaw" 
        @select-date="onTimelineSelectDate"
        @compare-dates="onTimelineCompareDates"
      />

      <!-- Barra de Navegação entre Visões de Inteligência de Mercado -->
      <div class="view-tabs-bar glass-panel animate-fade-in">
        <button 
          :class="['tab-btn', { active: activeViewTab === 'overview' }]" 
          @click="activeViewTab = 'overview'"
        >
          {{ t('tabs.overview', '📊 Visão Geral de Mercado') }}
        </button>
        <button 
          :class="['tab-btn', { active: activeViewTab === 'trending' }]" 
          @click="activeViewTab = 'trending'"
        >
          {{ t('tabs.trending', '🚀 Produtos em Alta & Aceleração') }}
        </button>
        <button 
          :class="['tab-btn', { active: activeViewTab === 'pricing' }]" 
          @click="activeViewTab = 'pricing'"
        >
          {{ t('tabs.pricing', '🏷️ Estratégias de Preço & Oportunidades') }}
        </button>
      </div>

      <!-- VISÃO 1: Visão Geral de Mercado (KPIs, Gráficos e Tabela) -->
      <div v-if="activeViewTab === 'overview'" class="overview-layout">
        <!-- SEÇÃO 2: Métricas Financeiras & KPIs -->
        <section class="dashboard-section">
          <div class="section-header">
            <div class="section-title-box">
              <span class="section-badge green">💰 Métricas</span>
              <h3>{{ t('sections.kpi_title', 'Resultados & Métricas Consolidadas') }}</h3>
            </div>
            <p class="section-subtitle">{{ t('sections.kpi_subtitle', 'Resumo dos valores, preços e volume capturados no nicho monitorado.') }}</p>
          </div>
          <KpiCards 
            :totalProducts="totalProducts"
            :averagePrice="averagePrice"
            :topPlatform="topPlatform"
            :topProduct="topProduct"
            :estimatedRevenue="estimatedRevenue"
            :dateRangeText="dateRangeText"
          />
        </section>

        <!-- SEÇÃO 3: Mapeamento Visual de Concorrência & Gráficos -->
        <section class="dashboard-section">
          <div class="section-header">
            <div class="section-title-box">
              <span class="section-badge blue">📊 Concorrência</span>
              <h3>{{ t('sections.charts_title', 'Mapeamento Visual de Concorrência') }}</h3>
            </div>
            <p class="section-subtitle">{{ t('sections.charts_subtitle', 'Distribuição de lojas líderes, faixas de preço e categorias de mercado.') }}</p>
          </div>
          
          <div class="charts-container">
            <!-- Linha 1 de Gráficos: Top Produtos + Barras de Faixa de Preço -->
            <div class="charts-row">
              <TopProductsChart :items="filteredProducts" class="half-width" />
              <PriceVsSalesChart :items="filteredProducts" class="half-width" />
            </div>
            
            <!-- Linha 2 de Gráficos: Vendedores em Destaque (Expandido) -->
            <div class="charts-row">
              <TopSellersChart :items="filteredProducts" class="full-width" />
            </div>

            <!-- Linha 3 de Gráficos: Share de Volume por Categoria -->
            <div class="charts-row">
              <CategoryVolumeChart :items="filteredProducts" class="full-width" />
            </div>
          </div>
        </section>

        <!-- SEÇÃO 4: Catálogo Detalhado de Anúncios -->
        <section class="dashboard-section">
          <div class="section-header">
            <div class="section-title-box">
              <span class="section-badge purple">🔍 Produtos</span>
              <h3>{{ t('sections.table_title', 'Catálogo Completo de Anúncios') }}</h3>
            </div>
            <p class="section-subtitle">{{ t('sections.table_subtitle', 'Detalhamento de cada anúncio coletado com preço, vendedor e link oficial.') }}</p>
          </div>
          <DataTable :items="filteredProducts" @delete-product="onDeleteProduct" class="full-width" />
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
import { createClient } from '@supabase/supabase-js'
import Navbar from '~/components/Navbar.vue'
import AntiBotAlert from '~/components/AntiBotAlert.vue'
import KpiCards from '~/components/KpiCards.vue'
import DataTable from '~/components/DataTable.vue'
import TopProductsChart from '~/components/TopProductsChart.client.vue'
import PriceVsSalesChart from '~/components/PriceVsSalesChart.client.vue'
import CategoryVolumeChart from '~/components/CategoryVolumeChart.client.vue'
import TopSellersChart from '~/components/TopSellersChart.client.vue'

import TimelineScrapeSelector from '~/components/TimelineScrapeSelector.vue'
import PriceRangeHistogramFilter from '~/components/PriceRangeHistogramFilter.vue'
import TrendingProductsTab from '~/components/TrendingProductsTab.vue'
import PriceStrategyMonitor from '~/components/PriceStrategyMonitor.vue'

const supabase = useSupabase()

const { t, locale } = useAppI18n()

const productsRaw = ref([])
const loading = ref(true)
const error = ref(null)
const authUser = ref(null)
const nomeProjeto = ref('Scraper Pro')
const statusAlerta = ref(null)

// Estado das Visões da Dashboard
const activeViewTab = ref('overview') // 'overview', 'trending', 'pricing'
const timelineSelectedDate = ref(null)

function onTimelineSelectDate(dateStr) {
  timelineSelectedDate.value = dateStr
}

function onTimelineCompareDates({ dateA, dateB }) {
  console.log("Comparando datas:", dateA, dateB)
}

// Configurações e Categorias dinâmicas
const blacklist = ref([])
const blockedProducts = ref([]) // Lista de objetos/links de produtos excluídos manualmente
const categoryRules = ref([])

function loadBlockedProducts() {
  const savedBlocked = localStorage.getItem('scraper_blocked_products')
  if (savedBlocked) {
    try {
      blockedProducts.value = JSON.parse(savedBlocked)
    } catch (e) {
      blockedProducts.value = []
    }
  }
}

async function onDeleteProduct(product) {
  const identifier = product.link || product.id || product.titulo
  const existsIndex = blockedProducts.value.findIndex(p => (typeof p === 'string' ? p === identifier : (p.link === product.link || p.id === product.id)))
  
  if (existsIndex === -1) {
    const itemToBlock = {
      id: product.id,
      titulo: product.titulo,
      link: product.link,
      plataforma: product.plataforma,
      preco: product.preco,
      bloqueado_em: new Date().toISOString()
    }
    blockedProducts.value.push(itemToBlock)
  } else {
    blockedProducts.value.splice(existsIndex, 1) // Remove do bloqueio (Restaura)
  }
  
  localStorage.setItem('scraper_blocked_products', JSON.stringify(blockedProducts.value))
  
  // Tenta salvar na nuvem se autenticado
  if (authUser.value) {
    try {
      await supabase.from('configuracoes_scraper').upsert({
        user_id: authUser.value.id,
        blocked_products: blockedProducts.value
      }, { onConflict: 'user_id' })
    } catch (e) {
      console.warn("Erro ao salvar blocked_products no Supabase:", e)
    }
  }
}

function onUpdateBlacklist(list) { blacklist.value = list }
function onUpdateCategories(rules) { categoryRules.value = rules }

// Estado dos Super Filtros
const selectedCategory = ref('Todas')
const selectedPlatform = ref('Todas')
const selectedTimeframe = ref('7') // '7', '15', '30', 'all'
const minPrice = ref(null)
const maxPrice = ref(null)
const minSales = ref(null)
const hideZeroSales = ref(false)
const showHiddenProducts = ref(false)

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
  { keyword: 'escultura', category: 'Bonecos & Esculturas' }
]

const activeCategoryRules = computed(() => {
  return categoryRules.value && categoryRules.value.length > 0 ? categoryRules.value : defaultCategoryRules
})

const dynamicCategories = computed(() => {
  const cats = new Set(activeCategoryRules.value.map(r => r.category))
  cats.add('Outros')
  return Array.from(cats)
})

function getCategoryByRules(title) {
  const t = (title || '').toLowerCase()
  for (const rule of activeCategoryRules.value) {
    if (t.includes(rule.keyword.toLowerCase())) return rule.category
  }
  return 'Outros'
}

function getHistoricalData(item, daysAgo) {
  if (!item.historico_coletas || item.historico_coletas.length === 0) return null
  if (daysAgo === 'all') {
    return item.historico_coletas[item.historico_coletas.length - 1]
  }

  const targetDate = new Date()
  targetDate.setDate(targetDate.getDate() - parseInt(daysAgo))
  
  let closest = null
  let minDiff = Infinity
  
  const historyToCheck = item.historico_coletas.slice(1)
  if (historyToCheck.length === 0) return null
  
  for (const entry of historyToCheck) {
    const entryDate = new Date(entry.data_coleta)
    const diff = Math.abs(entryDate - targetDate)
    
    if (diff < minDiff && diff <= (parseInt(daysAgo) * 86400000 + 172800000)) {
      minDiff = diff
      closest = entry
    }
  }
  return closest
}

const aiReportData = ref(null)

const lastScrapeFormatted = computed(() => {
  if (!productsRaw.value || productsRaw.value.length === 0) return t('global.no_scrapes', 'Sem registros de raspagem')
  let maxDate = null
  for (const p of productsRaw.value) {
    if (p.criado_em) {
      const d = new Date(p.criado_em)
      if (!maxDate || d > maxDate) maxDate = d
    }
    if (p.historico_coletas && Array.isArray(p.historico_coletas)) {
      for (const h of p.historico_coletas) {
        if (h.data_coleta) {
          const d = new Date(h.data_coleta)
          if (!maxDate || d > maxDate) maxDate = d
        }
      }
    }
  }
  if (!maxDate) return t('global.no_scrapes', 'Sem registros de raspagem')
  const dateLocale = locale.value === 'pt' ? 'pt-BR' : 'en-US'
  const dateFormatted = maxDate.toLocaleDateString(dateLocale, { day: '2-digit', month: '2-digit', year: 'numeric' })
  const hours = String(maxDate.getHours()).padStart(2, '0')
  const minutes = String(maxDate.getMinutes()).padStart(2, '0')
  const atWord = t('global.at', 'às')
  return `${dateFormatted} ${atWord} ${hours}:${minutes}`
})

async function loadDashboardData() {
  try {
    loading.value = true
    error.value = null
    loadBlockedProducts()
    
    // 1. Obtém sessão do usuário logado
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.user) {
      authUser.value = session.user
    }

    // 2. Carrega configurações do tenant
    try {
      let cfgQuery = supabase.from('configuracoes_scraper').select('blocked_products, relatorio_insights, nome_projeto, status_alerta')
      if (authUser.value) {
        cfgQuery = cfgQuery.eq('user_id', authUser.value.id)
      }
      const { data: cfg } = await cfgQuery.limit(1).maybeSingle()
      
      if (cfg) {
        if (cfg.status_alerta) {
          statusAlerta.value = cfg.status_alerta
        }
        if (cfg.relatorio_insights) {
          aiReportData.value = cfg.relatorio_insights
        }
        if (cfg.nome_projeto) {
          nomeProjeto.value = cfg.nome_projeto
        }
        if (cfg.blocked_products && Array.isArray(cfg.blocked_products)) {
          blockedProducts.value = cfg.blocked_products
          localStorage.setItem('scraper_blocked_products', JSON.stringify(cfg.blocked_products))
        }
      }
    } catch (e) {
      console.warn("Nao foi possivel carregar configuracoes do Supabase:", e)
    }

    // 3. Carrega produtos filtrados pelo user_id
    let prodQuery = supabase
      .from('produtos')
      .select(`
        id, plataforma, titulo, link, id_externo, vendedor, criado_em,
        historico_coletas ( preco, vendas_totais, data_coleta )
      `)

    if (authUser.value) {
      prodQuery = prodQuery.eq('user_id', authUser.value.id)
    }
      
    const { data: prodData, error: prodErr } = await prodQuery
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

function handleAuthChange(user) {
  authUser.value = user
  loadDashboardData()
}

onMounted(() => {
  loadDashboardData()
})

// Texto explicativo do período para os KPIs
const dateRangeText = computed(() => {
  if (productsRaw.value.length === 0) return t('global.loading_dates', 'Carregando datas...')
  
  const dates = []
  for (const p of productsRaw.value) {
    if (p.historico_coletas) {
      for (const h of p.historico_coletas) {
        if (h.data_coleta) dates.push(new Date(h.data_coleta))
      }
    }
  }

  if (dates.length === 0) return t('global.real_time_updates', 'Dados atualizados em tempo real')
  
  const minDate = new Date(Math.min(...dates))
  const maxDate = new Date(Math.max(...dates))
  
  const dateLocale = locale.value === 'pt' ? 'pt-BR' : 'en-US'
  const formatStr = (d) => d.toLocaleDateString(dateLocale)
  const periodName = selectedTimeframe.value === 'all' ? t('global.all_history', 'Todo o Histórico') : t('global.last_days', 'Últimos {days} Dias').replace('{days}', selectedTimeframe.value)

  return `${formatStr(minDate)} ${t('global.until', 'até')} ${formatStr(maxDate)} (${periodName})`
})

// Processa métricas e variações com base no período selecionado
const processedProducts = computed(() => {
  return productsRaw.value
    .map(p => {
      let snapshot = p
      if (timelineSelectedDate.value && timelineSelectedDate.value !== 'latest') {
        const histEntry = p.historico_coletas?.find(h => h.data_coleta && h.data_coleta.startsWith(timelineSelectedDate.value))
        if (histEntry) {
          snapshot = { ...p, preco: histEntry.preco, vendas_totais: histEntry.vendas_totais }
        } else {
          snapshot = { ...p, _hiddenByTimeline: true }
        }
      }
      
      const pData = snapshot
      const createdDate = pData.criado_em ? new Date(pData.criado_em) : new Date()
      const isNew = (pData.historico_coletas && pData.historico_coletas.length === 1) || (new Date() - createdDate < 86400000)
      
      let hist = null
      let varInfo = null
      let salesDiff = null
      
      hist = getHistoricalData(pData, selectedTimeframe.value)
      if (hist) {
        salesDiff = Math.max(0, pData.vendas_totais - hist.vendas_totais)
        if (hist.preco > 0) {
          const diff = pData.preco - hist.preco
          if (Math.abs(diff) > 0.05) {
            varInfo = { diff, perc: (diff / hist.preco) * 100, isPositive: diff > 0, isNegative: diff < 0 }
          }
        }
      }

      return {
        ...pData,
        categoria: getCategoryByRules(pData.titulo),
        isNew,
        hist,
        varInfo,
        salesDiff
      }
    })
    .map(p => {
      const isBlocked = blockedProducts.value.some(b => {
        if (!b) return false
        if (typeof b === 'string') return b === p.link || b === p.id || b === p.titulo
        return (b.link && b.link === p.link) || (b.id && b.id === p.id) || (b.titulo && b.titulo === p.titulo)
      })
      if (isBlocked) {
        p._isHidden = true
      }
      return p
    })
    .filter(p => {
      if (p._hiddenByTimeline) return false
      if (p._isHidden && !showHiddenProducts.value) return false
      
      const t = p.titulo.toLowerCase()
      if (blacklist.value.some(word => t.includes(word))) return false
      
      return true
    })
    .sort((a, b) => (b.vendas_totais || 0) - (a.vendas_totais || 0))
})

// Aplica os Super Filtros Globais
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
.filters-panel { padding: 1.5rem; margin-bottom: 2rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05); }
.filters-header { margin-bottom: 1.2rem; }
.filters-header h4 { margin: 0 0 0.2rem 0; color: #0f172a; font-size: 1.15rem; }
.filters-info { color: #64748b; font-size: 0.85rem; }

.filters-grid { display: flex; flex-wrap: wrap; gap: 1.5rem; align-items: flex-end; }
.filter-group { display: flex; flex-direction: column; gap: 0.5rem; }
.filter-group label { color: #475569; font-size: 0.85rem; font-weight: 600; }

.glass-input { background: #ffffff; border: 1px solid #cbd5e1; color: #0f172a; padding: 0.6rem 1rem; border-radius: 8px; outline: none; transition: border 0.3s; font-size: 0.95rem; }
.glass-input:focus { border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15); }
.highlight-select { border-color: #93c5fd; background: #eff6ff; font-weight: 600; color: #1e40af; }
.glass-input.tiny { width: 80px; text-align: center; padding: 0.6rem 0.5rem; }

.range-inputs { display: flex; align-items: center; gap: 0.5rem; }
.range-sep { color: #64748b; font-size: 0.85rem; }

.checkbox-group { justify-content: center; height: 100%; padding-bottom: 0.8rem; }
.checkbox-label { display: flex; align-items: center; gap: 0.5rem; cursor: pointer; color: #0f172a !important; font-size: 0.92rem !important; font-weight: 600; }

.content-grid { display: flex; flex-direction: column; gap: 2rem; }
.charts-row { display: flex; gap: 2rem; flex-wrap: wrap; }
.full-width { width: 100%; }
.half-width { flex: 1; min-width: 400px; }

.loading-state, .error-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 40vh; color: #64748b; font-size: 1.2rem; }
.spinner { width: 40px; height: 40px; border: 4px solid #cbd5e1; border-left-color: #2563eb; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 1rem; }
@keyframes spin { to { transform: rotate(360deg); } }

.last-update-banner {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1e40af;
  padding: 0.65rem 1.1rem;
  border-radius: 12px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.view-tabs-bar {
  display: flex;
  gap: 0.75rem;
  background: #ffffff;
  padding: 0.6rem;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
}

.tab-btn {
  flex: 1;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #475569;
  padding: 0.75rem 1.2rem;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.92rem;
  cursor: pointer;
  transition: all 0.25 ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.tab-btn:hover {
  background: #f1f5f9;
  color: #0f172a;
  transform: translateY(-1px);
}

.tab-btn.active {
  background: #2563eb;
  color: #ffffff;
  border-color: #2563eb;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}

.overview-layout {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.dashboard-section {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.04);
}

.section-header {
  margin-bottom: 1.25rem;
  padding-bottom: 0.85rem;
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
  font-size: 1.2rem;
  font-weight: 800;
  color: #0f172a;
}

.section-subtitle {
  margin: 0;
  font-size: 0.85rem;
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
  gap: 1.5rem;
}
</style>
