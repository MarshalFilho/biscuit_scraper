<template>
  <div class="glass-panel marketplace-panel animate-fade-in">
    <div class="panel-header">
      <div class="title-group">
        <h3 class="header-heading-flex">
          <Layers :size="20" class="text-amber-500" />
          <span>{{ t('report.tab_platforms', 'Comparativo de Marketplaces') }}</span>
        </h3>
        <p class="subtitle">{{ t('report.mod4_desc', 'Participação consolidada entre Mercado Livre e Shopee em volume de vendas e faturamento.') }}</p>
      </div>
    </div>

    <div class="platforms-grid mt-3">
      <div 
        v-for="(plat, index) in platformsList" 
        :key="index" 
        class="platform-card"
        :class="(plat.nome || '').toLowerCase().includes('shopee') ? 'shopee-card' : 'meli-card'"
      >
        <div class="card-header-row">
          <div class="plat-brand">
            <svg v-if="plat.nome.includes('Livre')" width="20" height="20" viewBox="0 0 24 24" fill="none" class="plat-logo">
              <circle cx="12" cy="12" r="11" fill="#FFE600"/>
              <path d="M7 12.5L10.5 15.5L17 8.5" stroke="#2D3277" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" class="plat-logo">
              <rect width="24" height="24" rx="5" fill="#EE4D2D"/>
              <path d="M7 9V7C7 4.79086 8.79086 3 11 3H13C15.2091 3 17 4.79086 17 7V9M5 9H19L17.5 21H6.5L5 9Z" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 11V15M12 15C11 15 9.5 14.2 9.5 13C9.5 11.8 12 12.2 12 11M12 15C13 15 14.5 15.8 14.5 17" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round"/>
            </svg>
            <strong>{{ plat.nome }}</strong>
          </div>
          <span :class="['share-badge', (plat.nome || '').toLowerCase().includes('shopee') ? 'shopee' : 'meli']">
            {{ plat.share }}% Share
          </span>
        </div>

        <div class="metrics-list">
          <div class="metric-row">
            <span class="metric-label">{{ t('report.sales_volume', 'Volume de Vendas:') }}</span>
            <strong class="metric-val">{{ (plat.vendas || 0).toLocaleString(locale === 'pt' ? 'pt-BR' : 'en-US') }} un</strong>
          </div>
          <div class="metric-row">
            <span class="metric-label">{{ t('report.est_revenue', 'Faturamento Estimado:') }}</span>
            <span class="revenue-tag">R$ {{ (plat.receita || 0).toLocaleString(locale === 'pt' ? 'pt-BR' : 'en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
          </div>
          <div class="metric-row" v-if="plat.totalProdutos">
            <span class="metric-label">{{ t('table.products_count', 'Produtos Cadastrados:') }}</span>
            <strong class="metric-val">{{ plat.totalProdutos }} produtos</strong>
          </div>
          <div class="metric-row border-top-row" v-if="plat.vendedores_unicos">
            <span class="metric-label">{{ t('report.active_stores', 'Lojas / Vendedores Ativos:') }}</span>
            <span class="stores-count-flex">
              <Store :size="14" />
              <strong>{{ plat.vendedores_unicos }}</strong>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Layers, Store } from 'lucide-vue-next'
import { useAppI18n } from '~/composables/useAppI18n'

const props = defineProps({
  products: {
    type: Array,
    default: () => []
  }
})

const { t, locale } = useAppI18n()

const platformsList = computed(() => {
  const prods = props.products || []
  if (prods.length === 0) {
    return [
      { nome: 'Mercado Livre', share: 50, vendas: 0, receita: 0, totalProdutos: 0, vendedores_unicos: 0 },
      { nome: 'Shopee', share: 50, vendas: 0, receita: 0, totalProdutos: 0, vendedores_unicos: 0 }
    ]
  }

  let meliSales = 0
  let meliRevenue = 0
  let meliCount = 0
  const meliSellers = new Set()

  let shopeeSales = 0
  let shopeeRevenue = 0
  let shopeeCount = 0
  const shopeeSellers = new Set()

  for (const p of prods) {
    const sName = (p.vendedor && p.vendedor.trim()) || null
    const sales = p.vendas_totais || 0
    const price = p.preco || 0
    const rev = price * sales

    if (p.plataforma === 'shopee') {
      shopeeSales += sales
      shopeeRevenue += rev
      shopeeCount += 1
      if (sName) shopeeSellers.add(sName)
    } else {
      meliSales += sales
      meliRevenue += rev
      meliCount += 1
      if (sName) meliSellers.add(sName)
    }
  }

  const totalRev = meliRevenue + shopeeRevenue || 1
  let meliShare = Math.round((meliRevenue / totalRev) * 100)
  if (meliRevenue > 0 && shopeeRevenue === 0) meliShare = 100
  if (shopeeRevenue > 0 && meliRevenue === 0) meliShare = 0
  const shopeeShare = 100 - meliShare

  return [
    {
      nome: 'Mercado Livre',
      share: meliShare,
      vendas: meliSales,
      receita: meliRevenue,
      totalProdutos: meliCount,
      vendedores_unicos: meliSellers.size || 1
    },
    {
      nome: 'Shopee',
      share: shopeeShare,
      vendas: shopeeSales,
      receita: shopeeRevenue,
      totalProdutos: shopeeCount,
      vendedores_unicos: shopeeSellers.size || 1
    }
  ]
})
</script>

<style scoped>
.marketplace-panel {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 1.35rem;
  box-shadow: 0 4px 15px -2px rgba(15, 23, 42, 0.04);
}

.panel-header {
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 0.75rem;
}

.title-group h3 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 800;
  color: #0f172a;
}

.header-heading-flex {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.subtitle {
  margin: 0.25rem 0 0 0;
  font-size: 0.82rem;
  color: #64748b;
}

.platforms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.25rem;
}

.platform-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.2rem;
  transition: all 0.2s ease;
}

.platform-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.04);
}

.meli-card {
  border-left: 4px solid #FFE600;
}

.shopee-card {
  border-left: 4px solid #EE4D2D;
}

.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid #e2e8f0;
}

.plat-brand {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  font-size: 1.05rem;
  color: #0f172a;
}

.share-badge {
  font-size: 0.78rem;
  font-weight: 800;
  padding: 0.25rem 0.6rem;
  border-radius: 99px;
  letter-spacing: 0.02em;
}

.share-badge.meli {
  background: #fef08a;
  color: #713f12;
  border: 1px solid #fde047;
}

.share-badge.shopee {
  background: #ffedd5;
  color: #9a3412;
  border: 1px solid #fed7aa;
}

.metrics-list {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.88rem;
}

.metric-label {
  color: #64748b;
  font-weight: 600;
}

.metric-val {
  color: #0f172a;
  font-weight: 700;
}

.revenue-tag {
  color: #059669;
  font-weight: 800;
  background: #ecfdf5;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  border: 1px solid #a7f3d0;
  font-size: 0.85rem;
}

.border-top-row {
  border-top: 1px solid #e2e8f0;
  padding-top: 0.65rem;
  margin-top: 0.2rem;
}

.stores-count-flex {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: #3b82f6;
  font-weight: 700;
}
</style>
