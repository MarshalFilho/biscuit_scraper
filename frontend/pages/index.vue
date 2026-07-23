<template>
  <div class="container">
    <header class="header animate-fade-in">
      <div class="header-top">
        <h1 class="premium-title text-gradient">✨ {{ nomeProjeto || 'Scraper Pro' }}</h1>
        <LoginModal @auth-change="user => authUser = user" />
      </div>
      <p class="premium-subtitle">Plataforma de inteligência ativa para monitoramento e controle.</p>
    </header>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Conectando à base de dados segura...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>⚠️ Ocorreu um erro: {{ error }}</p>
    </div>

    <div v-else>
      <!-- Central de Controle -->
      <div class="admin-panels">
        <ScraperConfig :user="authUser" @update-blacklist="onUpdateBlacklist" @update-project-name="name => nomeProjeto = name" />
        <CategoryManager :user="authUser" @update-categories="onUpdateCategories" />
      </div>

      <!-- Super Filtros Globais (Acima das métricas para indicar que comanda o painel) -->
      <div class="glass-panel filters-panel animate-fade-in" style="animation-delay: 0.1s;">
        <h4 class="filters-title">🔍 Super Filtros Globais (Comanda todos os gráficos e métricas)</h4>
        
        <div class="filters-grid">
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
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="platform-svg">
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
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="platform-svg">
                  <path d="M6 8V6C6 4.34315 7.34315 3 9 3H15C16.6569 3 18 4.34315 18 6V8M3 8H21L19.5 21H4.5L3 8Z" stroke="#EE4D2D" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M12 11V15M12 15C11 15 9.5 14.2 9.5 13C9.5 11.8 12 12.2 12 11M12 15C13 15 14.5 15.8 14.5 17" stroke="#EE4D2D" stroke-width="1.8" stroke-linecap="round"/>
                </svg>
                Shopee
              </button>
            </div>
          </div>

          <div class="filter-group">
            <label>Ordenar por:</label>
            <select v-model="selectedSort" class="glass-input">
              <option value="sales">Vendas Totais</option>
              <option value="growth7">Maior Crescimento (Últimos 7d)</option>
              <option value="growth15">Maior Crescimento (Últimos 15d)</option>
              <option value="growth30">Maior Crescimento (Últimos 30d)</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Categoria:</label>
            <select v-model="selectedCategory" class="glass-input">
              <option value="Todas">Todas as Categorias</option>
              <option v-for="cat in dynamicCategories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Faixa de Preço (R$):</label>
            <div class="range-inputs">
              <input type="number" v-model="minPrice" placeholder="Mín" class="glass-input tiny" />
              <span class="range-sep">até</span>
              <input type="number" v-model="maxPrice" placeholder="Máx" class="glass-input tiny" />
            </div>
          </div>

          <div class="filter-group">
            <label>Vendas Mínimas:</label>
            <input type="number" v-model="minSales" placeholder="Ex: 50" class="glass-input" />
          </div>

          <div class="filter-group checkbox-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="hideZeroSales" />
              Ocultar produtos com 0 vendas
            </label>
          </div>
        </div>
      </div>

      <!-- Métricas / KPIs Globais -->
      <KpiCards 
        :totalProducts="totalProducts"
        :averagePrice="averagePrice"
        :topPlatform="topPlatform"
        :topProduct="topProduct"
        :estimatedRevenue="estimatedRevenue"
      />

      <div class="content-grid">
        <DataTable :items="filteredProducts" class="full-width" />
        
        <div class="charts-row">
          <TopProductsChart :items="filteredProducts" class="half-width" />
          <PriceVsSalesChart :items="filteredProducts" class="half-width" />
        </div>
        
        <div class="charts-row">
          <PriceDistributionChart :items="filteredProducts" class="half-width" />
          <MarketShareChart :items="filteredProducts" class="half-width" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { createClient } from '@supabase/supabase-js'

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
const selectedSort = ref('sales')
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
  const targetDate = new Date()
  targetDate.setDate(targetDate.getDate() - parseInt(daysAgo))
  
  let closest = null
  let minDiff = Infinity
  
  const historyToCheck = item.historico_coletas.slice(1)
  if (historyToCheck.length === 0) return null
  
  for (const entry of historyToCheck) {
    const entryDate = new Date(entry.data_coleta)
    const diff = Math.abs(entryDate - targetDate)
    
    // Tolerância de +- 2 dias (172800000 ms)
    if (diff < minDiff && diff <= 172800000) {
      minDiff = diff
      closest = entry
    }
  }
  return closest
}

onMounted(async () => {
  try {
    loading.value = true
    const { data: prodData, error: prodErr } = await supabase
      .from('produtos')
      .select(`
        id, plataforma, titulo, link, id_externo, criado_em,
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

// Mapeia regras, remove blacklist e calcula crescimento/novo
const processedProducts = computed(() => {
  return productsRaw.value
    .map(p => {
      // É novo se tiver apenas 1 registro no histórico ou se foi criado nas últimas 24h
      const createdDate = p.criado_em ? new Date(p.criado_em) : new Date()
      const isNew = (p.historico_coletas && p.historico_coletas.length === 1) || (new Date() - createdDate < 86400000)
      
      let hist = null
      let varInfo = null
      let salesDiff = null
      
      let daysAgo = 7
      if (selectedSort.value === 'growth15') daysAgo = 15
      if (selectedSort.value === 'growth30') daysAgo = 30
      
      hist = getHistoricalData(p, daysAgo)
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
    .sort((a, b) => {
      if (selectedSort.value.startsWith('growth')) {
        const diffA = a.salesDiff || 0
        const diffB = b.salesDiff || 0
        if (diffA !== diffB) return diffB - diffA
      }
      return (b.vendas_totais || 0) - (a.vendas_totais || 0)
    })
})

// Aplica os Super Filtros
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

// KPIs Baseados nos produtos filtrados
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
.header { margin-bottom: 2rem; }
.header-top { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }
.premium-title { font-size: 3rem; margin-bottom: 0.5rem; }
.premium-subtitle { color: var(--text-muted); font-size: 1.1rem; text-align: left; }
.admin-panels { display: flex; flex-direction: column; gap: 0rem; }

.filters-panel { padding: 1.5rem; margin-bottom: 2rem; }
.filters-title { margin-top: 0; color: var(--text-main); font-size: 1.1rem; margin-bottom: 1.2rem; }
.filters-grid { display: flex; flex-wrap: wrap; gap: 1.5rem; align-items: flex-end; }
.filter-group { display: flex; flex-direction: column; gap: 0.5rem; }
.filter-group label { color: var(--text-muted); font-size: 0.85rem; font-weight: 500; }

.glass-input { background: #ffffff; border: 1px solid #cbd5e1; color: var(--text-main); padding: 0.6rem 1rem; border-radius: 8px; outline: none; transition: border 0.3s, box-shadow 0.3s; font-size: 0.95rem; }
.glass-input:focus { border-color: var(--neon-blue); box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15); }
.glass-input option { background: #ffffff; color: var(--text-main); }
.glass-input.tiny { width: 80px; text-align: center; padding: 0.6rem 0.5rem; }
.glass-input.small { width: 120px; }

.range-inputs { display: flex; align-items: center; gap: 0.5rem; }
.range-sep { color: var(--text-muted); font-size: 0.85rem; }

.checkbox-group { justify-content: center; height: 100%; padding-bottom: 0.8rem; }
.checkbox-label { display: flex; align-items: center; gap: 0.5rem; cursor: pointer; color: var(--text-main) !important; font-size: 0.95rem !important; }

.content-grid { display: flex; flex-direction: column; gap: 2rem; }
.charts-row { display: flex; gap: 2rem; flex-wrap: wrap; }
.full-width { width: 100%; }
.half-width { flex: 1; min-width: 400px; }

.loading-state, .error-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 40vh; color: var(--text-muted); font-size: 1.2rem; }
.spinner { width: 40px; height: 40px; border: 4px solid rgba(255, 255, 255, 0.1); border-left-color: var(--neon-blue); border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 1rem; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
