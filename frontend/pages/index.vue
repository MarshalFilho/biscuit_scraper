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
      />
      
      <div class="content-grid">
        <DataTable :items="products" class="full-width" />
        <PriceChart :items="products" class="full-width" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { createClient } from '@supabase/supabase-js'

const config = useRuntimeConfig()
const supabase = createClient(config.public.supabaseUrl, config.public.supabaseAnonKey)

const products = ref([])
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    loading.value = true
    
    // Busca produtos com os dados mais recentes de histórico
    const { data: prodData, error: prodErr } = await supabase
      .from('produtos')
      .select(`
        id, plataforma, titulo, link, id_externo,
        historico_coletas ( preco, vendas_totais, data_coleta )
      `)
      
    if (prodErr) throw prodErr
    
    // Tratamento dos dados para deixar flat e amigável para a UI
    if (prodData) {
      products.value = prodData.map(p => {
        // Pega o último histórico de coletas ordenando por data (do mais recente)
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

// Computeds para os KPIs
const totalProducts = computed(() => products.value.length)

const averagePrice = computed(() => {
  if (products.value.length === 0) return 0
  const validPrices = products.value.filter(p => p.preco > 0)
  if (validPrices.length === 0) return 0
  const sum = validPrices.reduce((acc, p) => acc + p.preco, 0)
  return sum / validPrices.length
})

const topPlatform = computed(() => {
  if (products.value.length === 0) return ''
  const counts = products.value.reduce((acc, p) => {
    acc[p.plataforma] = (acc[p.plataforma] || 0) + 1
    return acc
  }, {})
  return Object.keys(counts).reduce((a, b) => counts[a] > counts[b] ? a : b)
})
</script>

<style scoped>
.header {
  margin-bottom: 3rem;
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

.content-grid {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.full-width {
  width: 100%;
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
