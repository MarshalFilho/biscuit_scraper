<template>
  <div class="glass-panel chart-container animate-fade-in" style="animation-delay: 0.3s;">
    <div class="chart-header-box">
      <div class="header-title-flex">
        <div>
          <h3 class="chart-heading-inline">
            <DollarSign :size="18" class="text-emerald-600" />
            <span>{{ t('charts.price_vs_sales', 'Distribuição de Vendas por Faixa de Preço') }}</span>
          </h3>
          <p class="chart-subtitle">{{ t('charts.price_vs_sales_desc', 'Volume total de unidades vendidas agrupadas por faixa de valor.') }}</p>
        </div>
      </div>
    </div>
    <div class="chart-wrapper">
      <apexchart 
        v-if="isMounted && (series[0]?.data?.some(v => v > 0) || series[1]?.data?.some(v => v > 0))" 
        :key="chartKey"
        type="bar" 
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
import { DollarSign } from 'lucide-vue-next'
import { useAppI18n } from '~/composables/useAppI18n'

const { t, locale } = useAppI18n()

const props = defineProps({
  items: { type: Array, default: () => [] },
  isComparing: { type: Boolean, default: false }
})

const isMounted = ref(false)
onMounted(() => { isMounted.value = true })

// Faixas de preço com +R$ 100 consolidado (juntando 100-200 e +200)
const priceRanges = computed(() => {
  return [
    { label: `${t('charts.up_to', 'Até')} R$ 30`, min: 0, max: 30 },
    { label: 'R$ 30 - R$ 60', min: 30.01, max: 60 },
    { label: 'R$ 60 - R$ 100', min: 60.01, max: 100 },
    { label: '+ R$ 100', min: 100.01, max: Infinity }
  ]
})

const series = computed(() => {
  const getItemSales = (i) => {
    if (props.isComparing && i.salesDiff !== null && i.salesDiff !== undefined) {
      return i.salesDiff
    }
    return i.vendas_totais || 0
  }

  const meliSales = priceRanges.value.map(r => {
    return props.items
      .filter(i => i.plataforma === 'meli' && i.preco >= r.min && i.preco <= r.max)
      .reduce((sum, i) => sum + getItemSales(i), 0)
  })

  const shopeeSales = priceRanges.value.map(r => {
    return props.items
      .filter(i => i.plataforma === 'shopee' && i.preco >= r.min && i.preco <= r.max)
      .reduce((sum, i) => sum + getItemSales(i), 0)
  })

  return [
    { name: 'Mercado Livre', data: meliSales },
    { name: 'Shopee', data: shopeeSales }
  ]
})

const chartKey = computed(() => {
  return `${props.isComparing}-${series.value[0]?.data?.join(',')}-${series.value[1]?.data?.join(',')}`
})

const chartOptions = computed(() => ({
  chart: {
    type: 'bar',
    toolbar: { show: false },
    background: 'transparent',
    fontFamily: 'Inter, -apple-system, sans-serif'
  },
  colors: ['#F59E0B', '#EE4D2D'],
  plotOptions: {
    bar: {
      horizontal: false,
      columnWidth: '50%',
      borderRadius: 6,
      borderRadiusApplication: 'end'
    }
  },
  dataLabels: {
    enabled: true,
    formatter: (val) => val > 0 ? Number(val).toLocaleString(locale.value === 'pt' ? 'pt-BR' : 'en-US') : '',
    style: {
      fontSize: '11px',
      fontWeight: 'bold',
      colors: ['#334155']
    },
    offsetY: -18
  },
  stroke: { show: true, width: 2, colors: ['transparent'] },
  xaxis: {
    categories: priceRanges.value.map(r => r.label),
    labels: { 
      style: { colors: '#475569', fontWeight: 700, fontSize: '12px' } 
    },
    axisBorder: { show: false },
    axisTicks: { show: false }
  },
  yaxis: {
    title: { 
      text: t('charts.units_short', 'Unidades Vendidas'), 
      style: { color: '#64748b', fontSize: '11px', fontWeight: 600 } 
    },
    labels: { 
      style: { colors: '#64748b', fontSize: '11px' },
      formatter: (val) => val >= 1000 ? `${(val / 1000).toFixed(1)}k` : val.toString()
    }
  },
  legend: { 
    position: 'top', 
    horizontalAlign: 'right',
    labels: { colors: '#1e293b' }, 
    fontSize: '12px',
    fontWeight: 700,
    markers: { radius: 4 }
  },
  grid: { 
    borderColor: '#f1f5f9', 
    strokeDashArray: 4,
    padding: {
      bottom: 0
    }
  },
  theme: { mode: 'light' },
  tooltip: {
    shared: true,
    intersect: false,
    y: {
      formatter: (val) => Number(val).toLocaleString(locale.value === 'pt' ? 'pt-BR' : 'en-US') + ' ' + t('report.sales_units', 'vendas')
    }
  }
}))
</script>

<style scoped>
.chart-container {
  padding: 1.35rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  box-shadow: 0 4px 15px -2px rgba(15, 23, 42, 0.04);
  display: flex;
  flex-direction: column;
}

.chart-header-box {
  margin-bottom: 0.8rem;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid #f1f5f9;
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
  margin: 0.2rem 0 0 0;
  font-size: 0.82rem;
  color: #64748b;
}

.chart-wrapper {
  flex: 1;
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
