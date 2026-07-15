<template>
  <div class="glass-panel chart-container animate-fade-in" style="animation-delay: 0.6s;">
    <h3>Média de Preço por Categoria</h3>
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

// Calcula média de preço agrupado por plataforma e categoria
const series = computed(() => {
  const categoriesList = ['Velas', 'Topos de Bolo', 'Chaveiros/Lembrancinhas', 'Outros']
  
  const getAvg = (plat, cat) => {
    const list = props.items.filter(i => i.plataforma === plat && i.categoria === cat && i.preco > 0)
    if (list.length === 0) return 0
    return list.reduce((acc, i) => acc + i.preco, 0) / list.length
  }

  return [
    {
      name: 'Mercado Livre',
      data: categoriesList.map(cat => getAvg('meli', cat).toFixed(2))
    },
    {
      name: 'Shopee',
      data: categoriesList.map(cat => getAvg('shopee', cat).toFixed(2))
    }
  ]
})

const chartOptions = {
  chart: { type: 'bar', toolbar: { show: false }, background: 'transparent' },
  plotOptions: { bar: { horizontal: false, columnWidth: '55%', borderRadius: 4, endingShape: 'rounded' } },
  dataLabels: { enabled: false },
  stroke: { show: true, width: 2, colors: ['transparent'] },
  colors: ['#ffe600', '#ff6b35'],
  xaxis: { 
    categories: ['Velas', 'Topos de Bolo', 'Chaveiros', 'Outros'], 
    labels: { style: { colors: '#94a3b8' } }
  },
  yaxis: { 
    title: { text: 'Preço Médio (R$)' }, 
    labels: { style: { colors: '#94a3b8' }, formatter: (val) => "R$ " + val }
  },
  legend: { position: 'top', labels: { colors: '#f8fafc' } },
  grid: { borderColor: 'rgba(255, 255, 255, 0.1)', strokeDashArray: 4 },
  theme: { mode: 'dark' },
  tooltip: { y: { formatter: (val) => "R$ " + val } }
}
</script>

<style scoped>
.chart-container { padding: 1.5rem; }
.chart-container h3 { margin-bottom: 1rem; color: var(--text-main); font-size: 1.1rem; margin-top: 0; }
.chart-wrapper { min-height: 350px; }
</style>
