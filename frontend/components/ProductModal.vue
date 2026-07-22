<template>
  <div v-if="product" class="modal-overlay" @click.self="close">
    <div class="modal-content glass-panel animate-scale">
      <div class="modal-header">
        <h3>📊 Raio-X do Produto: <span class="text-neon">{{ product.titulo }}</span></h3>
        <button class="close-btn" @click="close">×</button>
      </div>
      
      <div class="modal-body">
        <ClientOnly>
          <apexchart type="line" height="350" :options="chartOptions" :series="chartSeries"></apexchart>
          <template #fallback>
            <div class="loading-chart">Montando inteligência visual...</div>
          </template>
        </ClientOnly>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  product: { type: Object, default: null }
})
const emit = defineEmits(['close'])

function close() {
  emit('close')
}

const chartSeries = computed(() => {
  if (!props.product || !props.product.historico_coletas) return []
  
  // Clona e reverte para ter o mais antigo no início (Esquerda para Direita no gráfico)
  const history = [...props.product.historico_coletas].reverse()
  
  return [
    {
      name: 'Vendas Totais',
      type: 'area',
      data: history.map(h => h.vendas_totais || 0)
    },
    {
      name: 'Preço (R$)',
      type: 'line',
      data: history.map(h => h.preco || 0)
    }
  ]
})

const chartOptions = computed(() => {
  if (!props.product || !props.product.historico_coletas) return {}
  
  const history = [...props.product.historico_coletas].reverse()
  const dates = history.map(h => new Date(h.data_coleta).toLocaleDateString('pt-BR'))
  
  return {
    chart: {
      type: 'line',
      background: 'transparent',
      toolbar: { show: false },
      fontFamily: 'Inter, sans-serif'
    },
    colors: ['#10b981', '#38bdf8'], // Verde para Vendas, Azul para Preço
    stroke: { curve: 'smooth', width: [0, 3] }, // Area sem borda grossa, linha do preço com 3px
    fill: { 
      type: ['gradient', 'solid'],
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.4,
        opacityTo: 0.05,
        stops: [0, 100]
      }
    },
    labels: dates,
    xaxis: {
      type: 'category',
      labels: { style: { colors: '#9ca3af' } }
    },
    yaxis: [
      {
        title: { text: 'Vendas', style: { color: '#10b981' } },
        labels: { style: { colors: '#10b981' } }
      },
      {
        opposite: true,
        title: { text: 'Preço (R$)', style: { color: '#38bdf8' } },
        labels: {
          style: { colors: '#38bdf8' },
          formatter: (value) => `R$ ${value.toFixed(2)}`
        }
      }
    ],
    theme: { mode: 'dark' },
    tooltip: { theme: 'dark' },
    legend: { labels: { colors: '#fff' } }
  }
})
</script>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: flex; justify-content: center; align-items: center; z-index: 1000; backdrop-filter: blur(8px); }
.modal-content { width: 95%; max-width: 900px; padding: 2rem; border-radius: 12px; position: relative; border: 1px solid rgba(255,255,255,0.1); }
.modal-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; }
.modal-header h3 { margin: 0; color: white; font-size: 1.3rem; max-width: 90%; }
.text-neon { color: var(--neon-blue); font-weight: bold; }
.close-btn { background: transparent; border: none; color: #9ca3af; font-size: 2.5rem; cursor: pointer; transition: color 0.2s; line-height: 0.8; }
.close-btn:hover { color: #ef4444; }
.loading-chart { height: 350px; display: flex; justify-content: center; align-items: center; color: var(--text-muted); font-weight: bold; letter-spacing: 0.1em; text-transform: uppercase; }
.animate-scale { animation: scaleIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
@keyframes scaleIn { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }
</style>
