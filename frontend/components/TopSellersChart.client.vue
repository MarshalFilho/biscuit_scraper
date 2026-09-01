<template>
  <div class="glass-panel chart-container animate-fade-in" style="animation-delay: 0.6s;">
    <div class="chart-header-box">
      <div class="header-titles">
        <h3 class="header-title-flex">
          <Trophy :size="20" class="text-amber-500" />
          <span>{{ t('charts.top_sellers', 'Ranking de Vendedores Líderes por Faturamento') }}</span>
        </h3>
        <p class="chart-subtitle">{{ t('charts.top_sellers_desc', 'Lojas e vendedores com maior volume de vendas no mercado') }}</p>
      </div>
      <div class="view-toggle">
        <button 
          :class="['toggle-sm', { active: activeMode === 'table' }]" 
          @click="activeMode = 'table'"
          :title="t('charts.view_table_title', 'Ver como tabela detalhada')"
        >
          <Table :size="13" />
          {{ t('global.table', 'Tabela') }}
        </button>
        <button 
          :class="['toggle-sm', { active: activeMode === 'chart' }]" 
          @click="activeMode = 'chart'"
          :title="t('charts.view_chart_title', 'Ver como gráfico de barras')"
        >
          <BarChart2 :size="13" />
          {{ t('global.chart', 'Gráfico') }}
        </button>
      </div>
    </div>

    <!-- Banner informativo se a maioria for sem vendedor -->
    <div class="seller-notice-banner" v-if="hasUnregisteredSellers">
      <Info :size="16" class="notice-icon" />
      <span><strong>{{ t('charts.seller_note', 'Nota sobre Vendedores:') }}</strong> {{ t('charts.seller_note_desc', 'Os nomes oficiais dos vendedores serão sincronizados e preenchidos automaticamente na próxima execução do robô de raspagem.') }}</span>
    </div>

    <!-- Visão Gráfico -->
    <div class="chart-wrapper" v-if="activeMode === 'chart'">
      <apexchart 
        v-if="isMounted && topSellersList.length > 0" 
        :key="chartKey"
        type="bar" 
        height="320" 
        :options="chartOptions" 
        :series="series"
      ></apexchart>
      <div v-else class="empty-chart">
        <p>{{ t('charts.empty_sellers', 'Sem dados de vendedores para exibir no momento.') }}</p>
      </div>
    </div>

    <!-- Visão Tabela -->
    <div class="sellers-table-wrapper" v-else>
      <table class="sellers-table">
        <thead>
          <tr>
            <th>#</th>
            <th>{{ t('charts.col_seller', 'Vendedor / Loja') }}</th>
            <th>{{ t('table.col_platform', 'Plataforma') }}</th>
            <th>{{ t('charts.col_ads', 'Anúncios Ativos') }}</th>
            <th>{{ isComparing ? t('charts.new_sales', 'Novas Vendas') : t('kpis.sales', 'Vendas Totais') }}</th>
            <th>{{ t('kpis.revenue', 'Fat. Estimado') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(seller, index) in topSellersList" :key="seller.name" class="clickable-seller-row" @click="selectedSeller = seller">
            <td class="rank-td">#{{ index + 1 }}</td>
            <td class="seller-name-td">
              <span :class="{'text-unregistered': seller.isUnregistered}">{{ seller.name }}</span>
            </td>
            <td>
              <span :class="['badge-sm', seller.platform]">
                {{ seller.platform === 'meli' ? 'Mercado Livre' : 'Shopee' }}
              </span>
            </td>
            <td class="ads-count-td">
              <span class="ads-count-link" :title="t('seller_modal.inspect_tooltip', 'Clique para ver todos os anúncios deste vendedor')">
                {{ seller.productCount }} {{ seller.productCount === 1 ? t('charts.ad', 'anúncio') : t('charts.ads', 'anúncios') }}
              </span>
            </td>
            <td class="sales-td">
              <span v-if="isComparing && seller.totalSales > 0">+</span>{{ seller.totalSales.toLocaleString(locale === 'pt' ? 'pt-BR' : 'en-US') }} {{ isComparing ? t('charts.units_short', 'novas vendas') : t('report.sales_units', 'vendas') }}
            </td>
            <td class="revenue-td">R$ {{ seller.estimatedRevenue.toLocaleString(locale === 'pt' ? 'pt-BR' : 'en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</td>
          </tr>
          <tr v-if="topSellersList.length === 0">
            <td colspan="6" class="empty-state">{{ t('charts.empty_sellers', 'Sem dados de vendedores para exibir no momento.') }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal com os Anúncios do Vendedor -->
    <SellerProductsModal :seller="selectedSeller" @close="selectedSeller = null" />
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { Trophy, Table, BarChart2, Info } from 'lucide-vue-next'
import SellerProductsModal from './SellerProductsModal.vue'
import { useAppI18n } from '~/composables/useAppI18n'

const { t, locale } = useAppI18n()

const props = defineProps({
  items: { type: Array, default: () => [] },
  isComparing: { type: Boolean, default: false }
})

const isMounted = ref(false)
const activeMode = ref('table')
const selectedSeller = ref(null)

onMounted(() => { isMounted.value = true })

const hasUnregisteredSellers = computed(() => {
  return props.items.some(item => !item.vendedor)
})

// Agrupa produtos por vendedor/loja real
const topSellersList = computed(() => {
  const map = new Map()

  for (const item of props.items) {
    let name = item.vendedor
    let isUnregistered = false

    if (!name) {
      name = item.plataforma === 'meli' ? 'Loja Mercado Livre' : 'Loja Shopee'
      isUnregistered = true
    }

    const key = `${name}_${item.plataforma}`

    if (!map.has(key)) {
      map.set(key, {
        name,
        platform: item.plataforma,
        isUnregistered,
        productCount: 0,
        totalSales: 0,
        estimatedRevenue: 0,
        products: []
      })
    }

    const entry = map.get(key)
    entry.productCount += 1
    const sales = (props.isComparing && item.salesDiff !== null && item.salesDiff !== undefined) ? item.salesDiff : (item.vendas_totais || 0)
    entry.totalSales += sales
    entry.estimatedRevenue += ((item.preco || 0) * sales)
    entry.products.push(item)
  }

  return Array.from(map.values())
    .sort((a, b) => {
      const aIsGeneric = (a.name === 'Loja Shopee' || a.name === 'Loja Mercado Livre')
      const bIsGeneric = (b.name === 'Loja Shopee' || b.name === 'Loja Mercado Livre')
      if (aIsGeneric && !bIsGeneric) return 1
      if (!aIsGeneric && bIsGeneric) return -1
      return b.totalSales - a.totalSales
    })
    .slice(0, 10)
})

const series = computed(() => {
  return [
    {
      name: props.isComparing ? t('charts.new_sales', 'Novas Vendas') : t('kpis.sales', 'Vendas Totais'),
      data: topSellersList.value.map(s => s.totalSales)
    }
  ]
})

const chartKey = computed(() => {
  return `${props.isComparing}-${topSellersList.value.map(s => `${s.name}-${s.totalSales}`).join(',')}`
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
    formatter: (val) => val.toLocaleString(locale.value === 'pt' ? 'pt-BR' : 'en-US') + ' ' + t('charts.units_short', 'un'),
    style: { fontSize: '11px', fontWeight: 'bold', colors: ['#ffffff'] }
  },
  xaxis: {
    categories: topSellersList.value.map(s => s.name.length > 25 ? s.name.substring(0, 25) + '...' : s.name),
    labels: { style: { colors: '#475569' } }
  },
  yaxis: {
    labels: { style: { colors: '#0f172a', fontWeight: 600 } }
  },
  grid: { borderColor: '#e2e8f0', strokeDashArray: 4 },
  theme: { mode: 'light' },
  tooltip: {
    theme: 'light',
    y: { formatter: (val) => val.toLocaleString(locale.value === 'pt' ? 'pt-BR' : 'en-US') + ' ' + t('report.sales_units', 'vendas') }
  }
}))
</script>

<style scoped>
.chart-container { padding: 1.5rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; }
.chart-header-box { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.8rem; gap: 1rem; flex-wrap: wrap; }
.header-titles h3 { margin: 0 0 0.2rem 0; color: #0f172a; font-size: 1.15rem; }
.header-title-flex { display: flex; align-items: center; gap: 0.5rem; }
.chart-subtitle { color: #64748b; font-size: 0.85rem; margin: 0; }

.seller-notice-banner { background: #fefce8; border: 1px solid #fef08a; color: #854d0e; padding: 0.5rem 0.8rem; border-radius: 8px; font-size: 0.82rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }
.notice-icon { flex-shrink: 0; }

.view-toggle { display: flex; gap: 0.3rem; background: #f1f5f9; padding: 3px; border-radius: 8px; border: 1px solid #cbd5e1; }
.toggle-sm { padding: 0.35rem 0.7rem; font-size: 0.8rem; font-weight: 600; border: none; background: transparent; color: #475569; border-radius: 6px; cursor: pointer; transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 0.35rem; }
.toggle-sm.active { background: #ffffff; color: #2563eb; box-shadow: 0 2px 4px rgba(0,0,0,0.06); }

.chart-wrapper { height: 320px; max-height: 320px; }

.sellers-table-wrapper { height: 320px; max-height: 320px; overflow-y: auto; overflow-x: auto; border-radius: 10px; border: 1px solid #e2e8f0; }
.sellers-table { width: 100%; border-collapse: collapse; text-align: left; background: #ffffff; }
.sellers-table th, .sellers-table td { padding: 0.75rem 0.9rem; border-bottom: 1px solid #e2e8f0; font-size: 0.88rem; }
.sellers-table th { background: #f8fafc; color: #475569; font-weight: 700; text-transform: uppercase; font-size: 0.75rem; position: sticky; top: 0; z-index: 2; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.rank-td { font-weight: 700; color: #2563eb; width: 40px; }
.seller-name-td { font-weight: 600; color: #0f172a; }
.text-unregistered { color: #64748b; font-style: italic; }
.sales-td { font-weight: 700; color: #059669; }
.revenue-td { font-weight: 700; color: #2563eb; }

.badge-sm { display: inline-block; padding: 0.2rem 0.5rem; border-radius: 99px; font-size: 0.72rem; font-weight: 600; }
.badge-sm.meli { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
.badge-sm.shopee { background: #ffedd5; color: #c2410c; border: 1px solid #fdba74; }
.empty-state { text-align: center; padding: 2rem !important; color: #64748b; font-style: italic; }

.clickable-seller-row { cursor: pointer; transition: background 0.2s ease; }
.clickable-seller-row:hover { background: #f8fafc; }

.seller-name-td span { transition: color 0.2s ease; }
.clickable-seller-row:hover .seller-name-td span { color: #2563eb; text-decoration: underline; }

.ads-count-td { white-space: nowrap; }
.ads-count-link { font-weight: 600; color: #0f172a; transition: color 0.2s ease; white-space: nowrap; }
.clickable-seller-row:hover .ads-count-link, .ads-count-link:hover { color: #2563eb; text-decoration: underline; }
</style>
