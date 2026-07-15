<template>
  <div class="glass-panel chart-container animate-fade-in" style="animation-delay: 0.4s;">
    <h3>Top 5 Produtos Mais Vendidos</h3>
    <div class="chart-wrapper">
      <apexchart v-if="isMounted" type="bar" height="350" :options="chartOptions" :series="series"></apexchart>
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
  const top5 = [...props.items].sort((a, b) => (b.vendas_totais || 0) - (a.vendas_totais || 0)).slice(0, 5)
  return [{
    name: 'Vendas Totais',
    data: top5.map(i => i.vendas_totais || 0)
  }]
})

const chartOptions = computed(() => {
  const top5 = [...props.items].sort((a, b) => (b.vendas_totais || 0) - (a.vendas_totais || 0)).slice(0, 5)
  return {
    chart: { type: 'bar', toolbar: { show: false }, background: 'transparent' },
    plotOptions: { bar: { horizontal: true, borderRadius: 4, distributed: true } },
    colors: ['#38bdf8', '#c084fc', '#ffe600', '#ff6b35', '#2dd4bf'],
    dataLabels: { enabled: true, style: { colors: ['#fff'] } },
    xaxis: { categories: top5.map(i => i.titulo.length > 30 ? i.titulo.substring(0, 30) + '...' : i.titulo), labels: { style: { colors: '#94a3b8' } } },
    yaxis: { labels: { style: { colors: '#94a3b8' }, maxWidth: 200 } },
    legend: { show: false },
    grid: { borderColor: 'rgba(255, 255, 255, 0.1)', strokeDashArray: 4 },
    theme: { mode: 'dark' }
  }
})
</script>

<style scoped>
.chart-container { padding: 1.5rem; }
.chart-container h3 { margin-bottom: 1rem; color: var(--text-main); font-size: 1.25rem; }
.chart-wrapper { min-height: 350px; }
</style>
