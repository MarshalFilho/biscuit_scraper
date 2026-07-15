<template>
  <div class="glass-panel chart-container animate-fade-in" style="animation-delay: 0.6s;">
    <h3>Distribuição de Preços (Dispersão Unidimensional)</h3>
    <div class="chart-wrapper">
      <apexchart v-if="isMounted" type="scatter" height="350" :options="chartOptions" :series="series"></apexchart>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import VueApexCharts from 'vue3-apexcharts'

const apexchart = VueApexCharts

const props = defineProps({
  items: { type: Array, default: () => [] }
})

const isMounted = ref(false)
onMounted(() => { isMounted.value = true })

// Boxplot requires specific data formats that might not render well without high volume, 
// using 1D Scatter for price distribution on platforms.
const series = computed(() => {
  const meliData = props.items.filter(i => i.plataforma === 'meli' && i.preco).map((i, idx) => [1, i.preco])
  const shopeeData = props.items.filter(i => i.plataforma === 'shopee' && i.preco).map((i, idx) => [2, i.preco])
  
  return [
    { name: 'Mercado Livre', data: meliData },
    { name: 'Shopee', data: shopeeData }
  ]
})

const chartOptions = {
  chart: { type: 'scatter', toolbar: { show: false }, background: 'transparent' },
  colors: ['#ffe600', '#ff6b35'],
  xaxis: { 
    categories: ['', 'Mercado Livre', 'Shopee', ''],
    min: 0,
    max: 3,
    tickAmount: 3,
    labels: { style: { colors: '#94a3b8' }, formatter: (val) => val === 1 ? 'M. Livre' : val === 2 ? 'Shopee' : '' }
  },
  yaxis: { title: { text: 'Preço (R$)' }, labels: { style: { colors: '#94a3b8' } } },
  legend: { show: false },
  grid: { borderColor: 'rgba(255, 255, 255, 0.1)', strokeDashArray: 4, xaxis: { lines: { show: true } } },
  theme: { mode: 'dark' },
  markers: { size: 5, strokeWidth: 0, hover: { size: 7 }, fillOpacity: 0.5 },
  tooltip: {
    x: { formatter: (val) => val === 1 ? 'Mercado Livre' : 'Shopee' },
    y: { formatter: (val) => "R$ " + val.toFixed(2) }
  }
}
</script>

<style scoped>
.chart-container { padding: 1.5rem; }
.chart-container h3 { margin-bottom: 1rem; color: var(--text-main); font-size: 1.25rem; }
.chart-wrapper { min-height: 350px; }
</style>
