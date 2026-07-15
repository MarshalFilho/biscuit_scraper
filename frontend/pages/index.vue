<template>
  <div class="container">
    <header class="header animate-fade-in">
      <h1 class="premium-title text-gradient">✨ Biscuit Scraper Pro</h1>
      <p class="premium-subtitle">Plataforma de inteligência avançada para monitoramento de Biscuit.</p>
    </header>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Conectando à base de dados segura...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>⚠️ Ocorreu um erro: {{ error }}</p>
    </div>

    <div v-else>
      <KpiCards 
        :totalProducts="totalProducts"
        :averagePrice="averagePrice"
        :topPlatform="topPlatform"
        :topProduct="topProduct"
        :estimatedRevenue="estimatedRevenue"
      />
      
      <!-- Filtro Global de Categorias -->
      <div class="filter-section glass-panel animate-fade-in" style="animation-delay: 0.2s;">
        <label for="categoryFilter">Filtro de Categoria: </label>
        <select id="categoryFilter" v-model="selectedCategory" class="glass-select">
          <option value="Todas">Todas as Categorias</option>
          <option value="Velas">Velas</option>
          <option value="Topos de Bolo">Topos de Bolo</option>
          <option value="Chaveiros/Lembrancinhas">Chaveiros/Lembrancinhas</option>
          <option value="Outros">Outros</option>
        </select>
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
const selectedCategory = ref('Todas')

// Lógica de Categorização Dinâmica
function getCategory(title) {
  const t = title.toLowerCase()
  if (t.includes('vela')) return 'Velas'
  if (t.includes('topo') || t.includes('bolo')) return 'Topos de Bolo'
  if (t.includes('chaveiro') || t.includes('lembrancinha')) return 'Chaveiros/Lembrancinhas'
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
          categoria: getCategory(p.titulo),
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

// Processa a ordenação global
const processedProducts = computed(() => {
  return [...productsRaw.value].sort((a, b) => (b.vendas_totais || 0) - (a.vendas_totais || 0))
})

// Filtra pela categoria selecionada
const filteredProducts = computed(() => {
  if (selectedCategory.value === 'Todas') return processedProducts.value
  return processedProducts.value.filter(p => p.categoria === selectedCategory.value)
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

const topProduct = computed(() => {
  if (filteredProducts.value.length === 0) return null
  // Já estão ordenados descendentemente por vendas_totais
  return filteredProducts.value[0]
})

const estimatedRevenue = computed(() => {
  return filteredProducts.value.reduce((acc, p) => {
    return acc + ((p.preco || 0) * (p.vendas_totais || 0))
  }, 0)
})
</script>

<style scoped>
.header {
  margin-bottom: 2rem;
  text-align: center;
}
.premium-title {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}
.premium-subtitle {
  color: var(--text-muted);
  font-size: 1.1rem;
}

.filter-section {
  padding: 1rem 1.5rem;
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.glass-select {
  background: rgba(0,0,0,0.2);
  border: 1px solid var(--border-glass);
  color: var(--text-main);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  outline: none;
  font-size: 1rem;
}
.glass-select option {
  background: var(--bg-color);
  color: var(--text-main);
}

.content-grid {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.charts-row {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.full-width {
  width: 100%;
}

.half-width {
  flex: 1;
  min-width: 400px;
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 40vh;
  color: var(--text-muted);
  font-size: 1.2rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-left-color: var(--neon-blue);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
