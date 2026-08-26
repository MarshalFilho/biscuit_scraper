<template>
  <div class="glass-panel chart-container animate-fade-in" style="animation-delay: 0.4s;">
    <div class="chart-header">
      <div>
        <h3>🥧 {{ t('charts.category_share', 'Share de Volume de Vendas por Categoria') }}</h3>
        <p class="chart-subtitle">{{ t('charts.category_share_desc', 'Fatia de mercado e total de unidades vendidas em cada segmento') }}</p>
      </div>
      <div class="total-badge" v-if="totalSalesCount > 0">
        {{ totalSalesCount.toLocaleString('pt-BR') }} {{ t('charts.sales_analyzed', 'vendas analisadas') }}
      </div>
    </div>
    
    <div class="chart-wrapper">
      <apexchart 
        v-if="isMounted && series.length > 0 && totalSalesCount > 0" 
        type="donut" 
        height="320" 
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
import { useAppI18n } from '~/composables/useAppI18n'

const { t, locale } = useAppI18n()

const props = defineProps({
  items: { type: Array, default: () => [] }
})

const isMounted = ref(false)
onMounted(() => { isMounted.value = true })

const categoryData = computed(() => {
  const map = {}
  for (const item of props.items) {
    const cat = item.categoria || 'Outros'
    const sales = item.vendas_totais || 0
    map[cat] = (map[cat] || 0) + sales
  }
  
  // Ordena por volume decrescente
  const sorted = Object.entries(map)
    .filter(([_, sales]) => sales > 0)
    .sort((a, b) => b[1] - a[1])

  return {
    labels: sorted.map(([cat]) => cat),
    series: sorted.map(([_, sales]) => sales)
  }
})

const labels = computed(() => categoryData.value.labels)
const series = computed(() => categoryData.value.series)
const totalSalesCount = computed(() => series.value.reduce((acc, v) => acc + v, 0))

const chartOptions = computed(() => ({
  chart: {
    type: 'donut',
    background: 'transparent',
    fontFamily: 'inherit'
  },
  labels: labels.value,
  colors: ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ec4899', '#64748b'],
  plotOptions: {
    pie: {
      donut: {
        size: '65%',
        labels: {
          show: true,
          total: {
            show: true,
            label: t('kpis.sales', 'Total de Vendas'),
            fontSize: '13px',
            fontWeight: 600,
            color: '#64748b',
            formatter: () => totalSalesCount.value.toLocaleString(locale.value === 'pt' ? 'pt-BR' : 'en-US') + ' ' + t('charts.units_short', 'un')
          },
          value: {
            fontSize: '20px',
            fontWeight: 800,
            color: '#0f172a',
            formatter: (val) => Number(val).toLocaleString(locale.value === 'pt' ? 'pt-BR' : 'en-US') + ' ' + t('charts.units_short', 'un')
          }
        }
      }
    }
  },
  stroke: {
    show: true,
    colors: ['#ffffff'],
    width: 2
  },
  legend: {
    position: 'bottom',
    labels: { colors: '#334155' },
    fontSize: '13px',
    markers: { radius: 12 }
  },
  dataLabels: {
    enabled: true,
    formatter: (val) => `${val.toFixed(1)}%`,
    style: { fontSize: '11px', fontWeight: 'bold' },
    dropShadow: { enabled: false }
  },
  tooltip: {
    theme: 'light',
    y: {
      formatter: (val) => `${Number(val).toLocaleString(locale.value === 'pt' ? 'pt-BR' : 'en-US')} ` + t('charts.units_sold', 'unidades vendidas')
    }
  }
}))
</script>

<style scoped>
.chart-container {
  padding: 1.5rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 16px;
  box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.06);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0.8rem;
  margin-bottom: 1rem;
}

.chart-header h3 {
  margin: 0 0 0.2rem 0;
  color: #0f172a;
  font-size: 1.15rem;
  font-weight: 700;
}

.chart-subtitle {
  margin: 0;
  color: #64748b;
  font-size: 0.84rem;
}

.total-badge {
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
  padding: 0.25rem 0.65rem;
  border-radius: 99px;
  font-size: 0.78rem;
  font-weight: 700;
}

.chart-wrapper {
  min-height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-chart {
  color: #94a3b8;
  font-size: 0.9rem;
  font-style: italic;
}
</style>
