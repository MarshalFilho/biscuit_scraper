<template>
  <div class="glass-panel chart-container animate-fade-in" style="animation-delay: 0.7s;">
    <h3>Market Share (Volume de Vendas)</h3>
    <div class="chart-wrapper donut-wrapper">
      <apexchart v-if="isMounted" type="donut" height="320" :options="chartOptions" :series="series"></apexchart>
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
  const meliSales = props.items.filter(i => i.plataforma === 'meli').reduce((acc, i) => acc + (i.vendas_totais || 0), 0)
  const shopeeSales = props.items.filter(i => i.plataforma === 'shopee').reduce((acc, i) => acc + (i.vendas_totais || 0), 0)
  return [meliSales, shopeeSales]
})

const chartOptions = {
  chart: { type: 'donut', background: 'transparent' },
  labels: ['Mercado Livre', 'Shopee'],
  colors: ['#ffe600', '#ff6b35'],
  stroke: { width: 0 },
  plotOptions: {
    pie: {
      donut: {
        size: '70%',
        labels: {
          show: true,
          name: { color: '#94a3b8' },
          value: { color: '#f8fafc', formatter: (val) => val.toLocaleString() + ' und.' },
          total: { show: true, showAlways: true, label: 'Vendas Totais', color: '#94a3b8' }
        }
      }
    }
  },
  legend: { position: 'bottom', labels: { colors: '#f8fafc' } },
  dataLabels: { enabled: false },
  theme: { mode: 'dark' },
  tooltip: { y: { formatter: (val) => val.toLocaleString() + " vendas" } }
}
</script>

<style scoped>
.chart-container { padding: 1.5rem; height: 100%; display: flex; flex-direction: column; }
.chart-container h3 { margin-bottom: 1rem; color: var(--text-main); font-size: 1.1rem; margin-top: 0; }
.chart-wrapper { min-height: 320px; flex: 1; display: flex; align-items: center; justify-content: center; }
.donut-wrapper { width: 100%; }
</style>
