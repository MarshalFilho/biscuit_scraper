<template>
  <div class="glass-panel chart-container animate-fade-in" style="animation-delay: 0.5s;">
    <h3>Relação Preço vs Vendas (Dispersão)</h3>
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

const series = computed(() => {
  const meliData = props.items.filter(i => i.plataforma === 'meli' && i.preco && i.vendas_totais).map(i => [i.preco, i.vendas_totais])
  const shopeeData = props.items.filter(i => i.plataforma === 'shopee' && i.preco && i.vendas_totais).map(i => [i.preco, i.vendas_totais])
  
  return [
    { name: 'Mercado Livre', data: meliData },
    { name: 'Shopee', data: shopeeData }
  ]
})

const chartOptions = {
  chart: { type: 'scatter', zoom: { enabled: true, type: 'xy' }, toolbar: { show: false }, background: 'transparent' },
  colors: ['#ffe600', '#ff6b35'],
  xaxis: { title: { text: 'Preço (R$)' }, labels: { style: { colors: '#94a3b8' } }, tickAmount: 10, type: 'numeric' },
  yaxis: { title: { text: 'Vendas Totais' }, labels: { style: { colors: '#94a3b8' } } },
  legend: { position: 'top', labels: { colors: '#f8fafc' } },
  grid: { borderColor: 'rgba(255, 255, 255, 0.1)', strokeDashArray: 4 },
  theme: { mode: 'dark' },
  markers: { size: 6, strokeWidth: 0, hover: { size: 8 } },
  tooltip: {
    y: { formatter: (val) => val + " vendas" }
  }
}
</script>

<style scoped>
.chart-container { padding: 1.5rem; }
.chart-container h3 { margin-bottom: 1rem; color: var(--text-main); font-size: 1.25rem; }
.chart-wrapper { min-height: 350px; }
</style>
