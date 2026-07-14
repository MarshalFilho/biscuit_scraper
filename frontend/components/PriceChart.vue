<template>
  <div class="glass-panel chart-container animate-fade-in" style="animation-delay: 0.5s;">
    <h3>Distribuição de Preços por Plataforma</h3>
    <div class="chart-wrapper">
      <ClientOnly>
        <apexchart type="scatter" height="350" :options="chartOptions" :series="series"></apexchart>
      </ClientOnly>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] }
})

const series = computed(() => {
  const meliData = props.items.filter(i => i.plataforma === 'meli').map(i => [i.vendas_totais || 0, i.preco || 0])
  const shopeeData = props.items.filter(i => i.plataforma === 'shopee').map(i => [i.vendas_totais || 0, i.preco || 0])
  
  return [
    { name: 'Mercado Livre', data: meliData },
    { name: 'Shopee', data: shopeeData }
  ]
})

const chartOptions = {
  chart: {
    type: 'scatter',
    zoom: { enabled: true, type: 'xy' },
    toolbar: { show: false },
    background: 'transparent',
    foreColor: '#94a3b8'
  },
  colors: ['#ffe600', '#ff6b35'],
  xaxis: {
    title: { text: 'Quantidade de Vendas' },
    labels: { style: { colors: '#94a3b8' } },
    tickAmount: 10
  },
  yaxis: {
    title: { text: 'Preço (R$)' },
    labels: { style: { colors: '#94a3b8' } }
  },
  legend: {
    position: 'top',
    labels: { colors: '#f8fafc' }
  },
  grid: {
    borderColor: 'rgba(255, 255, 255, 0.1)',
    strokeDashArray: 4
  },
  theme: { mode: 'dark' },
  markers: { size: 6, strokeWidth: 0, hover: { size: 8 } }
}
</script>

<style scoped>
.chart-container {
  padding: 1.5rem;
  margin-bottom: 2rem;
}
.chart-container h3 {
  margin-bottom: 1rem;
  color: var(--text-main);
  font-size: 1.25rem;
}
.chart-wrapper {
  min-height: 350px;
}
</style>
