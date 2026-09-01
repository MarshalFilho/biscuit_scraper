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
        height="260" 
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
import { DollarSign, BarChart2 } from 'lucide-vue-next'
import { useAppI18n } from '~/composables/useAppI18n'

const { t, locale } = useAppI18n()

const props = defineProps({
  items: { type: Array, default: () => [] },
  isComparing: { type: Boolean, default: false }
})

const isMounted = ref(false)
onMounted(() => { isMounted.value = true })

// Calcula faixas de preço limpas, inteligentes e perfeitamente arredondadas
const priceRanges = computed(() => {
  const validPrices = props.items
    .map(i => i.preco)
    .filter(p => typeof p === 'number' && p > 0)
    .sort((a, b) => a - b)

  if (validPrices.length === 0) {
    return [
      { label: t('charts.up_to', 'Até') + ' R$ 30', min: 0, max: 30 },
      { label: 'R$ 30 - R$ 60', min: 30.01, max: 60 },
      { label: 'R$ 60 - R$ 100', min: 60.01, max: 100 },
      { label: 'R$ 100 - R$ 200', min: 100.01, max: 200 },
      { label: t('charts.above', 'Acima') + ' R$ 200', min: 200.01, max: Infinity }
    ]
  }

  const p95Index = Math.min(Math.floor(validPrices.length * 0.95), validPrices.length - 1)
  const maxP = Math.max(validPrices[p95Index], 100)

  // Arredonda degraus de preço de forma harmoniosa para e-commerce
  let s1 = 30, s2 = 60, s3 = 100, s4 = 200
  if (maxP <= 80) {
    s1 = 15; s2 = 30; s3 = 50; s4 = 80
  } else if (maxP > 300) {
    s1 = 50; s2 = 100; s3 = 200; s4 = 400
  }

  return [
    { label: `${t('charts.up_to', 'Até')} R$ ${s1}`, min: 0, max: s1 },
    { label: `R$ ${s1} - R$ ${s2}`, min: s1 + 0.01, max: s2 },
    { label: `R$ ${s2} - R$ ${s3}`, min: s2 + 0.01, max: s3 },
    { label: `R$ ${s3} - R$ ${s4}`, min: s3 + 0.01, max: s4 },
    { label: `${t('charts.above', 'Acima')} R$ ${s4}`, min: s4 + 0.01, max: Infinity }
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
      columnWidth: '55%',
      borderRadius: 6,
      borderRadiusApplication: 'end'
    }
  },
  dataLabels: {
    enabled: false
  },
  stroke: { show: true, width: 2, colors: ['transparent'] },
  xaxis: {
    categories: priceRanges.value.map(r => r.label),
    labels: { 
      style: { colors: '#475569', fontWeight: 700, fontSize: '11px' } 
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
    xaxis: { lines: { show: false } }
  },
  theme: { mode: 'light' },
  tooltip: {
    theme: 'light',
    y: { 
      formatter: (val) => `${val.toLocaleString(locale.value === 'pt' ? 'pt-BR' : 'en-US')} ${t('report.sales_units', 'vendas')}` 
    }
  }
}))
</script>

<style scoped>
.chart-container { 
  padding: 1.25rem 1.4rem; 
  background: #ffffff; 
  border: 1px solid #e2e8f0; 
  border-radius: 16px; 
  box-shadow: 0 4px 15px -2px rgba(15, 23, 42, 0.04);
}

.chart-header-box { 
  margin-bottom: 0.8rem; 
}

.header-title-flex {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.8rem;
}

.chart-header-box h3 { 
  margin: 0 0 0.2rem 0; 
  color: #0f172a; 
  font-size: 1.05rem; 
  font-weight: 800;
}

.chart-subtitle { 
  color: #64748b; 
  font-size: 0.82rem; 
  margin: 0; 
}

.chart-badge {
  background: #f8fafc;
  color: #475569;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.chart-wrapper { 
  min-height: 260px; 
}
</style>
