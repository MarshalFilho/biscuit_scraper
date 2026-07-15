  <div class="container">
    <header class="header animate-fade-in">
      <div class="header-top">
        <h1 class="premium-title text-gradient">✨ Biscuit Scraper Pro</h1>
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
        <ScraperConfig :user="authUser" @update-blacklist="onUpdateBlacklist" />
        <CategoryManager :user="authUser" @update-categories="onUpdateCategories" />
      </div>

      <KpiCards 
        :totalProducts="totalProducts"
        :averagePrice="averagePrice"
        :topPlatform="topPlatform"
        :topProduct="topProduct"
        :estimatedRevenue="estimatedRevenue"
      />
      
      <!-- Super Filtros Globais -->
      <div class="glass-panel filters-panel animate-fade-in" style="animation-delay: 0.2s;">
        <h4 class="filters-title">🔍 Super Filtros (Reflete em todo o painel)</h4>
        
        <div class="filters-grid">
          <div class="filter-group">
            <label>Categoria:</label>
            <select v-model="selectedCategory" class="glass-input">
              <option value="Todas">Todas as Categorias</option>
              <option v-for="cat in dynamicCategories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>

          <div class="filter-group">
            <label>Plataforma:</label>
            <select v-model="selectedPlatform" class="glass-input">
              <option value="Todas">Ambos (ML + Shopee)</option>
              <option value="meli">Mercado Livre</option>
              <option value="shopee">Shopee</option>
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

// Configurações e Categorias dinâmicas
const blacklist = ref([])
const categoryRules = ref([])

function onUpdateBlacklist(list) { blacklist.value = list }
function onUpdateCategories(rules) { categoryRules.value = rules }

// Estado dos Super Filtros
const selectedCategory = ref('Todas')
const selectedPlatform = ref('Todas')
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

onMounted(async () => {
  try {
    loading.value = true
    const { data: prodData, error: prodErr } = await supabase
      .from('produtos')
      .select(`
        id, plataforma, titulo, link, id_externo,
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
          preco: latestHistory.preco || 0,
          vendas_totais: latestHistory.vendas_totais || 0,
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

// Mapeia regras e remove blacklist
const processedProducts = computed(() => {
  return productsRaw.value
    .map(p => ({
      ...p,
      categoria: getCategoryByRules(p.titulo)
    }))
    .filter(p => {
      const t = p.titulo.toLowerCase()
      if (blacklist.value.some(word => t.includes(word))) return false
      return true
    })
    .sort((a, b) => (b.vendas_totais || 0) - (a.vendas_totais || 0))
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

.glass-input { background: rgba(0,0,0,0.2); border: 1px solid var(--border-glass); color: var(--text-main); padding: 0.6rem 1rem; border-radius: 8px; outline: none; transition: border 0.3s; font-size: 0.95rem; }
.glass-input:focus { border-color: var(--neon-blue); }
.glass-input option { background: var(--bg-color); color: var(--text-main); }
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
