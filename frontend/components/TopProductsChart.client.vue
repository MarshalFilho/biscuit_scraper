<template>
  <div class="glass-panel chart-container animate-fade-in" style="animation-delay: 0.4s;">
    <div class="header">
      <h3 class="chart-heading-inline">
        <Flame :size="18" class="text-amber-500" />
        <span>{{ isComparing && metricMode === 'growth' ? t('charts.top_growing', 'Top 10 Produtos em Crescimento') : t('charts.top_products', 'Top 10 Produtos Mais Vendidos') }}</span>
      </h3>
      <div class="controls-flex">
        <select v-if="isComparing" v-model="metricMode" class="glass-select small">
          <option value="growth">{{ t('charts.toggle_growth', 'Novas Vendas') }}</option>
          <option value="total">{{ t('charts.toggle_total', 'Vendas Totais') }}</option>
        </select>
        <select v-model="platformFilter" class="glass-select small">
          <option value="all">{{ t('filters.both', 'Geral') }}</option>
          <option value="meli">Mercado Livre</option>
          <option value="shopee">Shopee</option>
        </select>
      </div>
    </div>
    <div class="chart-wrapper">
      <apexchart 
        v-if="isMounted && series[0]?.data?.length > 0" 
        :key="chartKey"
        type="bar" 
        height="350" 
        :options="chartOptions" 
        :series="series"
      ></apexchart>
      <div v-else class="empty-chart">
        <p>{{ t('charts.waiting_data', 'Aguardando dados para calcular a distribuição...') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { Flame } from 'lucide-vue-next'
import { useAppI18n } from '~/composables/useAppI18n'

const { t, locale } = useAppI18n()
const platformFilter = ref('all')
const metricMode = ref('growth') // 'growth' ou 'total'

const props = defineProps({
  items: { type: Array, default: () => [] },
  isComparing: { type: Boolean, default: false }
})

const isMounted = ref(false)
onMounted(() => { isMounted.value = true })

const filteredItems = computed(() => {
  let list = props.items
  if (platformFilter.value !== 'all') {
    list = list.filter(i => i.plataforma === platformFilter.value)
  }
  return list
})

const top10List = computed(() => {
  const useGrowth = props.isComparing && metricMode.value === 'growth'
  return [...filteredItems.value]
    .sort((a, b) => {
      const valA = useGrowth ? (a.salesDiff || 0) : (a.vendas_totais || 0)
      const valB = useGrowth ? (b.salesDiff || 0) : (b.vendas_totais || 0)
      return valB - valA
    })
    .slice(0, 10)
})

const series = computed(() => {
  const useGrowth = props.isComparing && metricMode.value === 'growth'
  return [{
    name: useGrowth ? t('charts.new_sales', 'Novas Vendas no Período') : t('kpis.sales', 'Vendas Totais'),
    data: top10List.value.map(i => useGrowth ? (i.salesDiff || 0) : (i.vendas_totais || 0))
  }]
})

const chartOptions = computed(() => {
  const useGrowth = props.isComparing && metricMode.value === 'growth'
  return {
    chart: { type: 'bar', toolbar: { show: false }, background: 'transparent' },
    plotOptions: { bar: { horizontal: true, borderRadius: 4, distributed: false, columnWidth: '70%' } },
    colors: [useGrowth ? '#f59e0b' : '#38bdf8'],
    dataLabels: { 
      enabled: true, 
      formatter: (val) => (useGrowth && val > 0 ? '+' : '') + Number(val).toLocaleString(locale.value === 'pt' ? 'pt-BR' : 'en-US') + ' ' + t('charts.units_short', 'un'),
      style: { colors: ['#fff'] } 
    },
    xaxis: { 
      categories: top10List.value.map(i => i.titulo.length > 25 ? i.titulo.substring(0, 25) + '...' : i.titulo), 
      labels: { style: { colors: '#94a3b8' } } 
    },
    yaxis: { labels: { style: { colors: '#94a3b8' }, maxWidth: 200 } },
    legend: { show: false },
    grid: { borderColor: 'rgba(255, 255, 255, 0.1)', strokeDashArray: 4 },
    theme: { mode: 'light' },
    tooltip: { 
      y: { 
        formatter: (val) => (useGrowth && val > 0 ? '+' : '') + Number(val).toLocaleString(locale.value === 'pt' ? 'pt-BR' : 'en-US') + ' ' + (useGrowth ? t('charts.units_short', 'novas vendas') : t('report.sales_units', 'vendas'))
      } 
    }
  }
})

const chartKey = computed(() => {
  return `${props.isComparing}-${metricMode.value}-${platformFilter.value}-${series.value[0]?.data?.join(',')}-${top10List.value.map(i => i.id).join(',')}`
})
</script>

<style scoped>
.chart-container { padding: 1.5rem; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 1rem; }
.controls-flex { display: flex; align-items: center; gap: 0.5rem; }
.chart-container h3 { margin: 0; color: var(--text-main); font-size: 1.1rem; }
.chart-wrapper { min-height: 350px; }
.empty-chart { display: flex; align-items: center; justify-content: center; height: 350px; color: #94a3b8; font-size: 0.9rem; }
.glass-select.small { padding: 0.3rem 0.8rem; font-size: 0.85rem; background: rgba(255,255,255,0.05); border: 1px solid var(--border-glass); color: var(--text-main); border-radius: 6px; outline: none; }
.glass-select.small option { background: var(--bg-color); color: var(--text-main); }
</style>
