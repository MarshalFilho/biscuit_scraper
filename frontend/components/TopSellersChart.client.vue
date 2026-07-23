<template>
  <div class="glass-panel chart-container animate-fade-in" style="animation-delay: 0.6s;">
    <div class="chart-header-box">
      <div class="header-titles">
        <h3>🏪 Análise de Vendedores & Lojas em Destaque</h3>
        <p class="chart-subtitle">Lojas com maior volume de vendas e anúncios ativos no mercado</p>
      </div>
      <div class="view-toggle">
        <button 
          :class="['toggle-sm', { active: activeMode === 'chart' }]" 
          @click="activeMode = 'chart'"
          title="Ver como gráfico de barras"
        >
          📊 Gráfico
        </button>
        <button 
          :class="['toggle-sm', { active: activeMode === 'table' }]" 
          @click="activeMode = 'table'"
          title="Ver como tabela detalhada"
        >
          📋 Tabela
        </button>
      </div>
    </div>

    <!-- Visão Gráfico -->
    <div class="chart-wrapper" v-if="activeMode === 'chart'">
      <apexchart v-if="isMounted" type="bar" height="320" :options="chartOptions" :series="series"></apexchart>
    </div>

    <!-- Visão Tabela -->
    <div class="sellers-table-wrapper" v-else>
      <table class="sellers-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Vendedor / Loja</th>
            <th>Plataforma</th>
            <th>Anúncios Ativos</th>
            <th>Vendas Totais</th>
            <th>Fat. Estimado</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(seller, index) in topSellersList" :key="seller.name">
            <td class="rank-td">#{{ index + 1 }}</td>
            <td class="seller-name-td">{{ seller.name }}</td>
            <td>
              <span :class="['badge-sm', seller.platform]">
                {{ seller.platform === 'meli' ? 'Mercado Livre' : 'Shopee' }}
              </span>
            </td>
            <td>{{ seller.productCount }} anúncios</td>
            <td class="sales-td">{{ seller.totalSales.toLocaleString('pt-BR') }} un</td>
            <td class="revenue-td">R$ {{ seller.estimatedRevenue.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</td>
          </tr>
          <tr v-if="topSellersList.length === 0">
            <td colspan="6" class="empty-state">Sem dados de vendedores para exibir no momento.</td>
          </tr>
        </tbody>
      </table>
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
const activeMode = ref('chart')

onMounted(() => { isMounted.value = true })

// Agrupa produtos por vendedor/loja (ou fallback por vendedor derivado do título/anúncio)
const topSellersList = computed(() => {
  const map = new Map()

  for (const item of props.items) {
    // Se o item tiver vendedor explícito usa ele, senão agrupa por loja/termo
    const name = item.vendedor || item.loja || (item.plataforma === 'meli' ? 'Loja Oficial ML' : 'Vendedor Shopee')
    const key = `${name}_${item.plataforma}`

    if (!map.has(key)) {
      map.set(key, {
        name,
        platform: item.plataforma,
        productCount: 0,
        totalSales: 0,
        estimatedRevenue: 0
      })
    }

    const entry = map.get(key)
    entry.productCount += 1
    entry.totalSales += (item.vendas_totais || 0)
    entry.estimatedRevenue += ((item.preco || 0) * (item.vendas_totais || 0))
  }

  return Array.from(map.values())
    .sort((a, b) => b.totalSales - a.totalSales)
    .slice(0, 8)
})

const series = computed(() => {
  return [
    {
      name: 'Vendas Totais',
      data: topSellersList.value.map(s => s.totalSales)
    }
  ]
})

const chartOptions = computed(() => ({
  chart: {
    type: 'bar',
    toolbar: { show: false },
    background: 'transparent',
    fontFamily: 'Inter, sans-serif'
  },
  colors: ['#2563eb'],
  plotOptions: {
    bar: {
      horizontal: true,
      barHeight: '55%',
      borderRadius: 6
    }
  },
  dataLabels: {
    enabled: true,
    formatter: (val) => val.toLocaleString('pt-BR') + ' un',
    style: { fontSize: '11px', fontWeight: 'bold', colors: ['#ffffff'] }
  },
  xaxis: {
    categories: topSellersList.value.map(s => s.name.length > 22 ? s.name.substring(0, 22) + '...' : s.name),
    labels: { style: { colors: '#475569' } }
  },
  yaxis: {
    labels: { style: { colors: '#0f172a', fontWeight: 600 } }
  },
  grid: { borderColor: '#e2e8f0', strokeDashArray: 4 },
  theme: { mode: 'light' },
  tooltip: {
    theme: 'light',
    y: { formatter: (val) => val.toLocaleString('pt-BR') + ' vendas acumuladas' }
  }
}))
</script>

<style scoped>
.chart-container { padding: 1.5rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; }
.chart-header-box { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.2rem; gap: 1rem; flex-wrap: wrap; }
.header-titles h3 { margin: 0 0 0.2rem 0; color: #0f172a; font-size: 1.15rem; }
.chart-subtitle { color: #64748b; font-size: 0.85rem; margin: 0; }

.view-toggle { display: flex; gap: 0.3rem; background: #f1f5f9; padding: 3px; border-radius: 8px; border: 1px solid #cbd5e1; }
.toggle-sm { padding: 0.35rem 0.7rem; font-size: 0.8rem; font-weight: 600; border: none; background: transparent; color: #475569; border-radius: 6px; cursor: pointer; transition: all 0.2s ease; }
.toggle-sm.active { background: #ffffff; color: #2563eb; box-shadow: 0 2px 4px rgba(0,0,0,0.06); }

.chart-wrapper { min-height: 320px; }

.sellers-table-wrapper { overflow-x: auto; border-radius: 10px; border: 1px solid #e2e8f0; }
.sellers-table { width: 100%; border-collapse: collapse; text-align: left; background: #ffffff; }
.sellers-table th, .sellers-table td { padding: 0.75rem 0.9rem; border-bottom: 1px solid #e2e8f0; font-size: 0.88rem; }
.sellers-table th { background: #f8fafc; color: #475569; font-weight: 700; text-transform: uppercase; font-size: 0.75rem; }
.rank-td { font-weight: 700; color: #2563eb; width: 40px; }
.seller-name-td { font-weight: 600; color: #0f172a; }
.sales-td { font-weight: 700; color: #059669; }
.revenue-td { font-weight: 700; color: #2563eb; }

.badge-sm { display: inline-block; padding: 0.2rem 0.5rem; border-radius: 99px; font-size: 0.72rem; font-weight: 600; }
.badge-sm.meli { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
.badge-sm.shopee { background: #ffedd5; color: #c2410c; border: 1px solid #fdba74; }
.empty-state { text-align: center; padding: 2rem !important; color: #64748b; font-style: italic; }
</style>
