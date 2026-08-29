<template>
  <div class="glass-panel chart-container animate-fade-in" style="animation-delay: 0.5s;">
    <div class="chart-header-box">
      <div class="header-titles">
        <h3>{{ t('charts.platform_share', '🏪 Market Share por Marketplace') }}</h3>
        <p class="chart-subtitle">{{ t('charts.platform_share_desc', 'Comparativo de vendas, faturamento e ticket médio entre Mercado Livre e Shopee') }}</p>
      </div>
      <div class="view-toggle">
        <button 
          :class="['toggle-sm', { active: metricMode === 'sales' }]" 
          @click="metricMode = 'sales'"
          :title="t('charts.toggle_sales_vol', 'Volume de Vendas')"
        >
          📦 {{ t('charts.toggle_sales_vol', 'Volume de Vendas') }}
        </button>
        <button 
          :class="['toggle-sm', { active: metricMode === 'revenue' }]" 
          @click="metricMode = 'revenue'"
          :title="t('charts.toggle_revenue_vol', 'Faturamento (R$)')"
        >
          💰 {{ t('charts.toggle_revenue_vol', 'Faturamento (R$)') }}
        </button>
      </div>
    </div>

    <div class="chart-wrapper">
      <apexchart 
        v-if="isMounted && totalMetricCount > 0" 
        type="donut" 
        height="260" 
        :options="chartOptions" 
        :series="chartSeries"
      ></apexchart>
      <div v-else class="empty-chart">
        <p>{{ t('charts.waiting_data', 'Aguardando dados para calcular a distribuição...') }}</p>
      </div>
    </div>

    <!-- Mini Cards Comparativos de Cada Plataforma -->
    <div class="platform-stats-grid">
      <!-- Mercado Livre -->
      <div class="plat-stat-card meli-card">
        <div class="plat-stat-header">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" class="plat-svg">
            <circle cx="12" cy="12" r="11" fill="#FFE600"/>
            <path d="M7 12.5L10.5 15.5L17 8.5" stroke="#2D3277" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="plat-name">Mercado Livre</span>
          <span class="plat-share-pill meli-pill">{{ meliShare.toFixed(1) }}%</span>
        </div>
        <div class="plat-stat-body">
          <div class="stat-col">
            <span class="stat-lbl">{{ t('kpis.sales', 'Vendas') }}</span>
            <span class="stat-val">{{ meliData.sales.toLocaleString(locale === 'pt' ? 'pt-BR' : 'en-US') }} {{ t('charts.units_short', 'un') }}</span>
          </div>
          <div class="stat-col">
            <span class="stat-lbl">{{ t('kpis.revenue', 'Faturamento') }}</span>
            <span class="stat-val">R$ {{ formatNumberShort(meliData.revenue) }}</span>
          </div>
          <div class="stat-col">
            <span class="stat-lbl">{{ t('charts.avg_ticket', 'Ticket Médio') }}</span>
            <span class="stat-val">R$ {{ meliData.avgPrice.toFixed(2) }}</span>
          </div>
        </div>
      </div>

      <!-- Shopee -->
      <div class="plat-stat-card shopee-card">
        <div class="plat-stat-header">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" class="plat-svg">
            <rect width="24" height="24" rx="5" fill="#EE4D2D"/>
            <path d="M7 9V7C7 4.79086 8.79086 3 11 3H13C15.2091 3 17 4.79086 17 7V9M5 9H19L17.5 21H6.5L5 9Z" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 11V15M12 15C11 15 9.5 14.2 9.5 13C9.5 11.8 12 12.2 12 11M12 15C13 15 14.5 15.8 14.5 17" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round"/>
          </svg>
          <span class="plat-name">Shopee</span>
          <span class="plat-share-pill shopee-pill">{{ shopeeShare.toFixed(1) }}%</span>
        </div>
        <div class="plat-stat-body">
          <div class="stat-col">
            <span class="stat-lbl">{{ t('kpis.sales', 'Vendas') }}</span>
            <span class="stat-val">{{ shopeeData.sales.toLocaleString(locale === 'pt' ? 'pt-BR' : 'en-US') }} {{ t('charts.units_short', 'un') }}</span>
          </div>
          <div class="stat-col">
            <span class="stat-lbl">{{ t('kpis.revenue', 'Faturamento') }}</span>
            <span class="stat-val">R$ {{ formatNumberShort(shopeeData.revenue) }}</span>
          </div>
          <div class="stat-col">
            <span class="stat-lbl">{{ t('charts.avg_ticket', 'Ticket Médio') }}</span>
            <span class="stat-val">R$ {{ shopeeData.avgPrice.toFixed(2) }}</span>
          </div>
        </div>
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
const metricMode = ref('sales') // 'sales' ou 'revenue'

onMounted(() => {
  isMounted.value = true
})

const meliData = computed(() => {
  const meliItems = props.items.filter(i => i.plataforma === 'meli')
  const count = meliItems.length
  const sales = meliItems.reduce((acc, i) => acc + (i.vendas_totais || 0), 0)
  const revenue = meliItems.reduce((acc, i) => acc + ((i.preco || 0) * (i.vendas_totais || 0)), 0)
  const totalPrice = meliItems.reduce((acc, i) => acc + (i.preco || 0), 0)
  const avgPrice = count > 0 ? (totalPrice / count) : 0

  return { count, sales, revenue, avgPrice }
})

const shopeeData = computed(() => {
  const shopeeItems = props.items.filter(i => i.plataforma === 'shopee')
  const count = shopeeItems.length
  const sales = shopeeItems.reduce((acc, i) => acc + (i.vendas_totais || 0), 0)
  const revenue = shopeeItems.reduce((acc, i) => acc + ((i.preco || 0) * (i.vendas_totais || 0)), 0)
  const totalPrice = shopeeItems.reduce((acc, i) => acc + (i.preco || 0), 0)
  const avgPrice = count > 0 ? (totalPrice / count) : 0

  return { count, sales, revenue, avgPrice }
})

const chartSeries = computed(() => {
  if (metricMode.value === 'revenue') {
    return [Math.round(meliData.value.revenue), Math.round(shopeeData.value.revenue)]
  }
  return [meliData.value.sales, shopeeData.value.sales]
})

const totalMetricCount = computed(() => {
  return chartSeries.value.reduce((acc, v) => acc + v, 0)
})

const meliShare = computed(() => {
  if (totalMetricCount.value === 0) return 50
  return (chartSeries.value[0] / totalMetricCount.value) * 100
})

const shopeeShare = computed(() => {
  if (totalMetricCount.value === 0) return 50
  return (chartSeries.value[1] / totalMetricCount.value) * 100
})

function formatNumberShort(num) {
  if (!num) return '0,00'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + ' mi'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num.toLocaleString(locale.value === 'pt' ? 'pt-BR' : 'en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const chartOptions = computed(() => ({
  chart: {
    type: 'donut',
    background: 'transparent',
    fontFamily: 'Inter, sans-serif'
  },
  labels: ['Mercado Livre', 'Shopee'],
  colors: ['#eab308', '#ea580c'],
  plotOptions: {
    pie: {
      donut: {
        size: '65%',
        labels: {
          show: true,
          total: {
            show: true,
            label: metricMode.value === 'revenue' ? t('kpis.revenue', 'Faturamento') : t('kpis.sales', 'Total de Vendas'),
            fontSize: '12px',
            fontWeight: 600,
            color: '#64748b',
            formatter: () => {
              if (metricMode.value === 'revenue') {
                return 'R$ ' + formatNumberShort(totalMetricCount.value)
              }
              return totalMetricCount.value.toLocaleString(locale.value === 'pt' ? 'pt-BR' : 'en-US') + ' ' + t('charts.units_short', 'un')
            }
          },
          value: {
            fontSize: '18px',
            fontWeight: 800,
            color: '#0f172a',
            formatter: (val) => {
              if (metricMode.value === 'revenue') {
                return 'R$ ' + formatNumberShort(Number(val))
              }
              return Number(val).toLocaleString(locale.value === 'pt' ? 'pt-BR' : 'en-US') + ' ' + t('charts.units_short', 'un')
            }
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
    fontSize: '12px',
    fontWeight: 600,
    labels: { colors: '#334155' },
    markers: { radius: 12 }
  },
  tooltip: {
    theme: 'light',
    y: {
      formatter: (val) => {
        const perc = totalMetricCount.value > 0 ? ((val / totalMetricCount.value) * 100).toFixed(1) : 0
        if (metricMode.value === 'revenue') {
          return `R$ ${Number(val).toLocaleString('pt-BR', { minimumFractionDigits: 2 })} (${perc}%)`
        }
        return `${Number(val).toLocaleString('pt-BR')} ${t('charts.units_short', 'un')} (${perc}%)`
      }
    }
  },
  dataLabels: {
    enabled: true,
    formatter: (val) => Number(val).toFixed(1) + '%',
    style: {
      fontSize: '11px',
      fontWeight: 700,
      colors: ['#ffffff']
    },
    dropShadow: {
      enabled: true,
      blur: 2,
      opacity: 0.35
    }
  }
}))
</script>

<style scoped>
.chart-container {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.chart-header-box {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 0.85rem;
}

.header-titles h3 {
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.chart-subtitle {
  font-size: 0.78rem;
  color: #64748b;
  margin: 0.2rem 0 0 0;
}

.view-toggle {
  display: inline-flex;
  background: #f1f5f9;
  padding: 0.2rem;
  border-radius: 8px;
  gap: 0.2rem;
}

.toggle-sm {
  background: transparent;
  border: none;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  padding: 0.3rem 0.65rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-sm:hover {
  color: #0f172a;
}

.toggle-sm.active {
  background: #ffffff;
  color: #0f172a;
  font-weight: 700;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.chart-wrapper {
  min-height: 260px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-chart {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 240px;
  color: #94a3b8;
  font-size: 0.85rem;
}

.platform-stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin-top: 0.85rem;
  padding-top: 0.85rem;
  border-top: 1px dashed #e2e8f0;
}

.plat-stat-card {
  padding: 0.65rem 0.8rem;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.meli-card {
  background: #fefce8;
  border: 1px solid #fef08a;
}

.shopee-card {
  background: #fff7ed;
  border: 1px solid #fed7aa;
}

.plat-stat-header {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.plat-name {
  font-size: 0.82rem;
  font-weight: 800;
  color: #0f172a;
}

.plat-share-pill {
  margin-left: auto;
  font-size: 0.72rem;
  font-weight: 800;
  padding: 0.15rem 0.45rem;
  border-radius: 99px;
}

.meli-pill {
  background: #fde047;
  color: #713f12;
}

.shopee-pill {
  background: #fdba74;
  color: #9a3412;
}

.plat-stat-body {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
}

.stat-col {
  display: flex;
  flex-direction: column;
}

.stat-lbl {
  font-size: 0.68rem;
  color: #64748b;
  font-weight: 600;
}

.stat-val {
  font-size: 0.8rem;
  font-weight: 800;
  color: #0f172a;
}

@media (max-width: 640px) {
  .platform-stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
