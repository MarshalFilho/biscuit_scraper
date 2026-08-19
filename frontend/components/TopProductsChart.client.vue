<template>
  <div class="glass-panel chart-container animate-fade-in" style="animation-delay: 0.4s;">
    <div class="header">
      <h3>Top 5 Produtos Mais Vendidos</h3>
      <select v-model="platformFilter" class="glass-select small">
        <option value="all">Geral</option>
        <option value="meli">Mercado Livre</option>
        <option value="shopee">Shopee</option>
      </select>
    </div>
    <div class="chart-wrapper">
      <apexchart v-if="isMounted" type="bar" height="350" :options="chartOptions" :series="series"></apexchart>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'

const platformFilter = ref('all')

const props = defineProps({
  items: { type: Array, default: () => [] }
})

const isMounted = ref(false)
onMounted(() => { isMounted.value = true })

const filteredItems = computed(() => {
  if (platformFilter.value === 'all') return props.items
  return props.items.filter(i => i.plataforma === platformFilter.value)
})

const series = computed(() => {
  const top5 = [...filteredItems.value].sort((a, b) => (b.vendas_totais || 0) - (a.vendas_totais || 0)).slice(0, 5)
  return [{
    name: 'Vendas Totais',
    data: top5.map(i => i.vendas_totais || 0)
  }]
})

const chartOptions = computed(() => {
  const top5 = [...filteredItems.value].sort((a, b) => (b.vendas_totais || 0) - (a.vendas_totais || 0)).slice(0, 5)
  return {
    chart: { type: 'bar', toolbar: { show: false }, background: 'transparent' },
    plotOptions: { bar: { horizontal: true, borderRadius: 4, distributed: true } },
    colors: ['#38bdf8', '#c084fc', '#ffe600', '#ff6b35', '#2dd4bf'],
    dataLabels: { enabled: true, style: { colors: ['#fff'] } },
    xaxis: { categories: top5.map(i => i.titulo.length > 25 ? i.titulo.substring(0, 25) + '...' : i.titulo), labels: { style: { colors: '#94a3b8' } } },
    yaxis: { labels: { style: { colors: '#94a3b8' }, maxWidth: 200 } },
    legend: { show: false },
    grid: { borderColor: 'rgba(255, 255, 255, 0.1)', strokeDashArray: 4 },
    theme: { mode: 'dark' },
    tooltip: { y: { formatter: (val) => val.toLocaleString() + " vendas" } }
  }
})
</script>

<style scoped>
.chart-container { padding: 1.5rem; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 1rem; }
.chart-container h3 { margin: 0; color: var(--text-main); font-size: 1.1rem; }
.chart-wrapper { min-height: 350px; }
.glass-select.small { padding: 0.3rem 0.8rem; font-size: 0.85rem; background: rgba(255,255,255,0.05); border: 1px solid var(--border-glass); color: var(--text-main); border-radius: 6px; outline: none; }
.glass-select.small option { background: var(--bg-color); color: var(--text-main); }
</style>
