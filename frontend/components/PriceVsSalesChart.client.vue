<template>
  <div class="glass-panel chart-container animate-fade-in" style="animation-delay: 0.3s;">
    <div class="chart-header-box">
      <h3>{{ t('charts.price_vs_sales', '🎯 Distribuição de Vendas por Faixa de Preço') }}</h3>
      <p class="chart-subtitle">{{ t('charts.price_vs_sales_desc', 'Descubra em qual faixa de preço o mercado mais vende') }}</p>
    </div>
    <div class="chart-wrapper">
      <apexchart v-if="isMounted" type="bar" height="210" :options="chartOptions" :series="series"></apexchart>
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

// Calcula faixas de preço dinâmicas e inteligentes baseadas no nicho monitorado
const priceRanges = computed(() => {
  const validPrices = props.items
    .map(i => i.preco)
    .filter(p => typeof p === 'number' && p > 0)
    .sort((a, b) => a - b)

  if (validPrices.length === 0) {
    return [
      { label: t('charts.up_to', 'Até') + ' R$ 25', min: 0, max: 25 },
      { label: 'R$ 25 - R$ 50', min: 25.01, max: 50 },
      { label: 'R$ 50 - R$ 100', min: 50.01, max: 100 },
      { label: 'R$ 100 - R$ 200', min: 100.01, max: 200 },
      { label: t('charts.above', 'Acima') + ' R$ 200', min: 200.01, max: Infinity }
    ]
  }

  const minP = validPrices[0]
  // 95º percentil para evitar que um item fora da curva distorça o gráfico
  const p95Index = Math.min(Math.floor(validPrices.length * 0.95), validPrices.length - 1)
  const maxP = Math.max(validPrices[p95Index], minP + 10)

  const rawStep = (maxP - minP) / 4
  let niceStep = 10
  if (rawStep <= 15) niceStep = 10
  else if (rawStep <= 35) niceStep = 25
  else if (rawStep <= 75) niceStep = 50
  else if (rawStep <= 150) niceStep = 100
  else if (rawStep <= 300) niceStep = 200
  else niceStep = Math.ceil(rawStep / 100) * 100

  const baseMin = Math.floor(minP / niceStep) * niceStep
  const b1 = baseMin + niceStep
  const b2 = b1 + niceStep
  const b3 = b2 + niceStep
  const b4 = b3 + niceStep

  return [
    { label: t('charts.up_to', 'Até') + ` R$ ${b1}`, min: 0, max: b1 },
    { label: `R$ ${b1} - R$ ${b2}`, min: b1 + 0.01, max: b2 },
    { label: `R$ ${b2} - R$ ${b3}`, min: b2 + 0.01, max: b3 },
    { label: `R$ ${b3} - R$ ${b4}`, min: b3 + 0.01, max: b4 },
    { label: t('charts.above', 'Acima') + ` R$ ${b4}`, min: b4 + 0.01, max: Infinity }
  ]
})

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
  colors: ['#ca8a04', '#ea580c'],
  plotOptions: {
    bar: {
      horizontal: false,
      columnWidth: '50%',
      borderRadius: 4
    }
  },
  dataLabels: {
    enabled: true,
    formatter: (val) => val > 0 ? (val > 999 ? (val / 1000).toFixed(1) + 'k' : val.toString()) : '',
    style: { fontSize: '10px', fontWeight: 'bold', colors: ['#ffffff'] }
  },
  stroke: { show: true, width: 2, colors: ['transparent'] },
  xaxis: {
    categories: priceRanges.value.map(r => r.label),
    labels: { style: { colors: '#475569', fontWeight: 600, fontSize: '11px' } }
  },
  yaxis: {
    title: { text: t('charts.units_short', 'un'), style: { color: '#64748b', fontSize: '11px' } },
    labels: { style: { colors: '#64748b', fontSize: '10px' } }
  },
  legend: { position: 'top', labels: { colors: '#0f172a' }, fontSize: '11px' },
  grid: { borderColor: '#e2e8f0', strokeDashArray: 3 },
  theme: { mode: 'light' },
  tooltip: {
    theme: 'light',
    y: { formatter: (val) => val.toLocaleString(locale.value === 'pt' ? 'pt-BR' : 'en-US') + " " + t('report.sales_units', 'vendas') }
  }
}))
</script>

<style scoped>
.chart-container { padding: 1rem 1.2rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; }
.chart-header-box { margin-bottom: 0.4rem; }
.chart-header-box h3 { margin: 0 0 0.15rem 0; color: #0f172a; font-size: 1.05rem; }
.chart-subtitle { color: #64748b; font-size: 0.8rem; margin: 0; }
.chart-wrapper { min-height: 210px; }
</style>
