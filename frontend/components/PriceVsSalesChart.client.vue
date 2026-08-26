<template>
  <div class="glass-panel chart-container animate-fade-in" style="animation-delay: 0.5s;">
    <div class="chart-header-box">
      <h3>{{ t('charts.price_vs_sales', '🎯 Distribuição de Vendas por Faixa de Preço') }}</h3>
      <p class="chart-subtitle">{{ t('charts.price_vs_sales_desc', 'Descubra em qual faixa de preço o mercado mais vende') }}</p>
    </div>
    <div class="chart-wrapper">
      <apexchart v-if="isMounted" type="bar" height="320" :options="chartOptions" :series="series"></apexchart>
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

const priceRanges = computed(() => [
  { label: t('charts.up_to', 'Até') + ' R$ 25', min: 0, max: 25 },
  { label: 'R$ 25 - R$ 50', min: 25.01, max: 50 },
  { label: 'R$ 50 - R$ 100', min: 50.01, max: 100 },
  { label: 'R$ 100 - R$ 200', min: 100.01, max: 200 },
  { label: t('charts.above', 'Acima') + ' R$ 200', min: 200.01, max: Infinity }
])

const series = computed(() => {
  const meliSales = priceRanges.value.map(r => {
    return props.items
      .filter(i => i.plataforma === 'meli' && i.preco >= r.min && i.preco <= r.max)
      .reduce((sum, i) => sum + (i.vendas_totais || 0), 0)
  })

  const shopeeSales = priceRanges.value.map(r => {
    return props.items
      .filter(i => i.plataforma === 'shopee' && i.preco >= r.min && i.preco <= r.max)
      .reduce((sum, i) => sum + (i.vendas_totais || 0), 0)
  })

  return [
    { name: 'Mercado Livre', data: meliSales },
    { name: 'Shopee', data: shopeeSales }
  ]
})

const chartOptions = computed(() => ({
  chart: {
    type: 'bar',
    toolbar: { show: false },
    background: 'transparent',
    fontFamily: 'Inter, sans-serif'
  },
  colors: ['#ca8a04', '#ea580c'], // Dourado para Mercado Livre, Laranja para Shopee
  plotOptions: {
    bar: {
      horizontal: false,
      columnWidth: '55%',
      borderRadius: 6
    }
  },
  dataLabels: {
    enabled: true,
    formatter: (val) => val > 0 ? val.toLocaleString(locale.value === 'pt' ? 'pt-BR' : 'en-US') : '',
    style: { fontSize: '11px', fontWeight: 'bold', colors: ['#ffffff'] }
  },
  stroke: { show: true, width: 2, colors: ['transparent'] },
  xaxis: {
    categories: priceRanges.value.map(r => r.label),
    labels: { style: { colors: '#475569', fontWeight: 600 } }
  },
  yaxis: {
    title: { text: t('kpis.sales', 'Vendas Totais') + ' (' + t('charts.units_short', 'un') + ')', style: { color: '#475569', fontWeight: 600 } },
    labels: { style: { colors: '#475569' } }
  },
  legend: { position: 'top', labels: { colors: '#0f172a' } },
  grid: { borderColor: '#e2e8f0', strokeDashArray: 4 },
  theme: { mode: 'light' },
  tooltip: {
    theme: 'light',
    y: { formatter: (val) => val.toLocaleString(locale.value === 'pt' ? 'pt-BR' : 'en-US') + " " + t('report.sales_units', 'vendas') }
  }
}))
</script>

<style scoped>
.chart-container { padding: 1.5rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; }
.chart-header-box { margin-bottom: 1rem; }
.chart-header-box h3 { margin: 0 0 0.2rem 0; color: #0f172a; font-size: 1.15rem; }
.chart-subtitle { color: #64748b; font-size: 0.85rem; margin: 0; }
.chart-wrapper { min-height: 320px; }
</style>
