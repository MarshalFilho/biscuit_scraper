<template>
  <div class="container">
    <Navbar :projectName="nomeProjeto" @auth-change="user => authUser = user" />

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Conectando à base de dados segura do Supabase...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>⚠️ Ocorreu um erro ao carregar os dados: {{ error }}</p>
    </div>

    <div v-else>
      <!-- Relatório de Inteligência Executiva por IA (Fase 4) -->
      <AiExecutiveReport :reportData="aiReportData" />

      <!-- Super Filtros Globais (Comanda a página) -->
      <div class="glass-panel filters-panel animate-fade-in" style="animation-delay: 0.1s;">
        <div class="filters-header">
          <h4>🔍 Super Filtros Globais</h4>
          <span class="filters-info">Altera em tempo real todos os KPIs, gráficos e tabelas do painel</span>
        </div>
        
        <div class="filters-grid">
          <!-- Plataforma -->
          <div class="filter-group">
            <label>Plataforma:</label>
            <div class="toggle-group">
              <button 
                type="button" 
                :class="['toggle-btn', { active: selectedPlatform === 'Todas' }]" 
                @click="selectedPlatform = 'Todas'"
              >
                🌐 Ambas
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

          <!-- Período de Análise -->
          <div class="filter-group">
            <label>Intervalo de Datas (Período):</label>
            <select v-model="selectedTimeframe" class="glass-input highlight-select">
              <option value="7">📅 Últimos 7 Dias</option>
              <option value="15">📅 Últimos 15 Dias</option>
              <option value="30">📅 Últimos 30 Dias</option>
              <option value="all">♾️ Todo o Histórico</option>
            </select>
          </div>

          <!-- Categoria -->
          <div class="filter-group">
            <label>Categoria:</label>
            <select v-model="selectedCategory" class="glass-input">
              <option value="Todas">Todas as Categorias</option>
              <option v-for="cat in dynamicCategories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>

          <!-- Faixa de Preço -->
          <div class="filter-group">
            <label>Faixa de Preço (R$):</label>
            <div class="range-inputs">
              <input type="number" v-model="minPrice" placeholder="Mín" class="glass-input tiny" />
              <span class="range-sep">até</span>
              <input type="number" v-model="maxPrice" placeholder="Máx" class="glass-input tiny" />
            </div>
          </div>

          <!-- Vendas Mínimas -->
          <div class="filter-group">
            <label>Vendas Mínimas:</label>
            <input type="number" v-model="minSales" placeholder="Ex: 50" class="glass-input" />
          </div>

          <!-- Ocultar Sem Vendas -->
          <div class="filter-group checkbox-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="hideZeroSales" />
              Ocultar produtos com 0 vendas
            </label>
          </div>
        </div>
      </div>

      <!-- Métricas Globais (KPIs) -->
      <KpiCards 
        :totalProducts="totalProducts"
        :averagePrice="averagePrice"
        :topPlatform="topPlatform"
        :topProduct="topProduct"
        :estimatedRevenue="estimatedRevenue"
        :dateRangeText="dateRangeText"
      />

      <div class="content-grid">
        <!-- Tabela Principal -->
        <DataTable :items="filteredProducts" class="full-width" />
        
        <!-- Linha 1 de Gráficos: Top Produtos + Barras de Faixa de Preço -->
        <div class="charts-row">
          <TopProductsChart :items="filteredProducts" class="half-width" />
          <PriceVsSalesChart :items="filteredProducts" class="half-width" />
        </div>
        
        <!-- Linha 2 de Gráficos: Vendedores em Destaque + Participação de Mercado -->
        <div class="charts-row">
          <TopSellersChart :items="filteredProducts" class="half-width" />
          <MarketShareChart :items="filteredProducts" class="half-width" />
        </div>

        <!-- Linha 3 de Gráficos: Distribuição de Preços -->
        <div class="charts-row">
          <PriceDistributionChart :items="filteredProducts" class="full-width" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { createClient } from '@supabase/supabase-js'
import Navbar from '~/components/Navbar.vue'
import KpiCards from '~/components/KpiCards.vue'
import DataTable from '~/components/DataTable.vue'
import TopProductsChart from '~/components/TopProductsChart.client.vue'
import PriceVsSalesChart from '~/components/PriceVsSalesChart.client.vue'
import MarketShareChart from '~/components/MarketShareChart.client.vue'
import PriceDistributionChart from '~/components/PriceDistributionChart.client.vue'
import TopSellersChart from '~/components/TopSellersChart.client.vue'

const config = useRuntimeConfig()
const supabase = createClient(config.public.supabaseUrl, config.public.supabaseAnonKey)

const productsRaw = ref([])
const loading = ref(true)
const error = ref(null)
const authUser = ref(null)
const nomeProjeto = ref('Scraper Pro')

// Configurações e Categorias dinâmicas
const blacklist = ref([])
const categoryRules = ref([])

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

const dynamicCategories = computed(() => {
  const cats = new Set(categoryRules.value.map(r => r.category))
  cats.add('Outros')
  return Array.from(cats)
})

function getCategoryByRules(title) {
  const t = title.toLowerCase()
  for (const rule of categoryRules.value) {
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

onMounted(async () => {
  try {
    loading.value = true
    
    // Tenta carregar o relatório de IA se houver no Supabase
    try {
      const { data: cfg } = await supabase.from('configuracoes_scraper').select('relatorio_insights').limit(1).single()
      if (cfg && cfg.relatorio_insights) {
        aiReportData.value = cfg.relatorio_insights
      }
    } catch (e) {
      // Usa o fallback mock padrão do componente AiExecutiveReport
    }

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
})

// Texto explicativo do período para os KPIs
const dateRangeText = computed(() => {
  if (productsRaw.value.length === 0) return 'Carregando datas...'
  
  const dates = []
  for (const p of productsRaw.value) {
    if (p.historico_coletas) {
      for (const h of p.historico_coletas) {
        if (h.data_coleta) dates.push(new Date(h.data_coleta))
      }
    }
  }

  if (dates.length === 0) return 'Dados atualizados em tempo real'
  
  const minDate = new Date(Math.min(...dates))
  const maxDate = new Date(Math.max(...dates))
  
  const formatStr = (d) => d.toLocaleDateString('pt-BR')
  const periodName = selectedTimeframe.value === 'all' ? 'Todo o Histórico' : `Últimos ${selectedTimeframe.value} Dias`

  return `${formatStr(minDate)} até ${formatStr(maxDate)} (${periodName})`
})

// Processa métricas e variações com base no período selecionado
const processedProducts = computed(() => {
  return productsRaw.value
    .map(p => {
      const createdDate = p.criado_em ? new Date(p.criado_em) : new Date()
      const isNew = (p.historico_coletas && p.historico_coletas.length === 1) || (new Date() - createdDate < 86400000)
      
      let hist = null
      let varInfo = null
      let salesDiff = null
      
      hist = getHistoricalData(p, selectedTimeframe.value)
      if (hist) {
        salesDiff = Math.max(0, p.vendas_totais - hist.vendas_totais)
        if (hist.preco > 0) {
          const diff = p.preco - hist.preco
          if (Math.abs(diff) > 0.05) {
            varInfo = { diff, perc: (diff / hist.preco) * 100, isPositive: diff > 0, isNegative: diff < 0 }
          }
        }
      }

      return {
        ...p,
        categoria: getCategoryByRules(p.titulo),
        isNew,
        hist,
        varInfo,
        salesDiff
      }
    })
    .filter(p => {
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
</style>
