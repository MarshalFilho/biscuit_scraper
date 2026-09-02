<template>
  <div class="glass-panel chart-container animate-fade-in" style="animation-delay: 0.4s;">
    <div class="header">
      <div class="header-titles">
        <h3 class="chart-heading-inline">
          <Flame :size="18" class="text-amber-500" />
          <span>{{ metricMode === 'growth' ? t('charts.top_growing', 'Top 10 Produtos em Crescimento') : t('charts.top_products', 'Top 10 Produtos Mais Vendidos') }}</span>
        </h3>
        <p class="chart-subtitle">
          <span class="sub-highlight">{{ metricMode === 'growth' ? 'Novas Vendas: Unidades vendidas no período monitorado' : 'Vendas Totais: Total histórico acumulado do produto no marketplace' }}</span>
        </p>
      </div>

      <div class="controls-flex">
        <div class="metric-toggle-group">
          <button 
            type="button" 
            :class="['metric-btn', { active: metricMode === 'growth' }]" 
            @click="metricMode = 'growth'"
          >
            {{ t('charts.toggle_growth', 'Novas Vendas') }}
          </button>
          <button 
            type="button" 
            :class="['metric-btn', { active: metricMode === 'total' }]" 
            @click="metricMode = 'total'"
          >
            {{ t('charts.toggle_total', 'Vendas Totais') }}
          </button>
        </div>
      </div>
    </div>

    <div class="chart-wrapper">
      <apexchart 
        v-if="isMounted && series[0]?.data?.length > 0" 
        :key="chartKey"
        type="bar" 
        height="320" 
        :options="chartOptions" 
        :series="series"
      ></apexchart>
      <div v-else class="empty-chart">
        <p>{{ t('charts.waiting_data', 'Aguardando dados para calcular o ranking de produtos...') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { Flame } from 'lucide-vue-next'
import { useAppI18n } from '~/composables/useAppI18n'

const { t, locale } = useAppI18n()
const metricMode = ref('growth') // 'growth' ou 'total'

const props = defineProps({
  items: { type: Array, default: () => [] },
  isComparing: { type: Boolean, default: false }
})

const isMounted = ref(false)
onMounted(() => { isMounted.value = true })

const top10List = computed(() => {
  const useGrowth = metricMode.value === 'growth'
  return [...props.items]
    .sort((a, b) => {
      const valA = useGrowth ? (a.salesDiff || 0) : (a.vendas_totais || 0)
      const valB = useGrowth ? (b.salesDiff || 0) : (b.vendas_totais || 0)
      return valB - valA
    })
    .slice(0, 10)
})

const series = computed(() => {
  const useGrowth = metricMode.value === 'growth'
  return [{
    name: useGrowth ? t('charts.new_sales', 'Novas Vendas no Período') : t('kpis.sales', 'Vendas Totais'),
    data: top10List.value.map(i => useGrowth ? (i.salesDiff || 0) : (i.vendas_totais || 0))
  }]
})

const chartOptions = computed(() => {
  const useGrowth = metricMode.value === 'growth'
  return {
    chart: { 
      type: 'bar', 
      toolbar: { show: false }, 
      background: 'transparent', 
      fontFamily: 'Inter, sans-serif'
    },
    plotOptions: { 
      bar: { 
        horizontal: true, 
        borderRadius: 4, 
        distributed: false, 
        barHeight: '58%' 
      } 
    },
    colors: [useGrowth ? '#f59e0b' : '#3b82f6'],
    dataLabels: { 
      enabled: true, 
      formatter: (val) => (useGrowth && val > 0 ? '+' : '') + Number(val).toLocaleString(locale.value === 'pt' ? 'pt-BR' : 'en-US') + ' ' + t('charts.units_short', 'un'),
      style: { colors: ['#ffffff'], fontSize: '11px', fontWeight: 'bold' },
      offsetX: 4
    },
    xaxis: { 
      categories: top10List.value.map(i => {
        const title = i.titulo || ''
        return title.length > 70 ? title.substring(0, 70) + '...' : title
      }), 
      labels: { style: { colors: '#64748b', fontSize: '11px' } } 
    },
    yaxis: { 
      labels: { 
        style: { colors: '#1e293b', fontWeight: 600, fontSize: '12px' }, 
        maxWidth: 420
      } 
    },
    legend: { show: false },
    grid: { 
      borderColor: '#f1f5f9', 
      strokeDashArray: 4,
      padding: {
        left: 10,
        right: 25
      }
    },
    theme: { mode: 'light' },
    tooltip: { 
      y: { 
        formatter: (val) => (useGrowth && val > 0 ? '+' : '') + Number(val).toLocaleString(locale.value === 'pt' ? 'pt-BR' : 'en-US') + ' ' + (useGrowth ? t('charts.units_short', 'novas vendas') : t('report.sales_units', 'vendas'))
      } 
    }
  }
})

const chartKey = computed(() => {
  return `${metricMode.value}-${series.value[0]?.data?.join(',')}-${top10List.value.map(i => i.id).join(',')}`
})
</script>

<style scoped>
.chart-container { 
  padding: 1.35rem; 
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  box-shadow: 0 4px 15px -2px rgba(15, 23, 42, 0.04);
}

.header { 
  display: flex; 
  justify-content: space-between; 
  align-items: flex-start; 
  margin-bottom: 1.1rem; 
  padding-bottom: 0.8rem;
  border-bottom: 1px solid #f1f5f9;
  flex-wrap: wrap; 
  gap: 0.8rem; 
}

.header-titles {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.chart-heading-inline {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 800;
  color: #0f172a;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.chart-subtitle {
  margin: 0;
  font-size: 0.82rem;
  color: #64748b;
}

.sub-highlight {
  color: #475569;
  font-weight: 500;
}

.controls-flex { 
  display: flex; 
  align-items: center; 
  gap: 0.5rem; 
}

.metric-toggle-group {
  display: flex;
  background: #f1f5f9;
  padding: 0.25rem;
  border-radius: 9px;
  gap: 0.2rem;
  border: 1px solid #e2e8f0;
}

.metric-btn {
  background: transparent;
  border: none;
  font-size: 0.78rem;
  font-weight: 700;
  color: #64748b;
  padding: 0.35rem 0.75rem;
  border-radius: 7px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.metric-btn.active {
  background: #ffffff;
  color: #0f172a;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
}

.chart-wrapper { 
  min-height: 320px; 
}

.empty-chart { 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  height: 320px; 
  color: #94a3b8; 
  font-size: 0.9rem; 
}
</style>
