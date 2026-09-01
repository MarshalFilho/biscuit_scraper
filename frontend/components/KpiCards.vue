<template>
  <div class="kpi-container">
    <div class="kpi-grid">
      <div class="glass-panel kpi-card animate-fade-in" style="animation-delay: 0.1s;">
        <div class="kpi-icon icon-blue">
          <Package :size="22" />
        </div>
        <div class="kpi-content">
          <h3 class="kpi-title">{{ t('kpis.total_items', 'Total de Produtos') }}</h3>
          <p class="kpi-value text-gradient">{{ formatLargeNumber(totalProducts) }}</p>
          <span class="kpi-subtext">{{ t('kpis.total_items_sub', 'Anúncios monitorados') }}</span>
        </div>
      </div>
      
      <div class="glass-panel kpi-card animate-fade-in" style="animation-delay: 0.2s;">
        <div class="kpi-icon icon-emerald">
          <DollarSign :size="22" />
        </div>
        <div class="kpi-content">
          <h3 class="kpi-title">{{ t('kpis.avg_price', 'Preço Médio') }}</h3>
          <p class="kpi-value text-gradient">{{ formatCurrency(averagePrice, false) }}</p>
          <span class="kpi-subtext">{{ t('kpis.avg_price_sub', 'Média de valor ativo') }}</span>
        </div>
      </div>
      
      <div class="glass-panel kpi-card animate-fade-in" style="animation-delay: 0.3s;">
        <div class="kpi-icon icon-amber">
          <ShoppingBag :size="22" />
        </div>
        <div class="kpi-content">
          <h3 class="kpi-title">{{ t('kpis.top_platform', 'Top Plataforma') }}</h3>
          <p class="kpi-value text-gradient" style="text-transform: capitalize;">
            {{ topPlatform === 'meli' ? 'Mercado Livre' : (topPlatform === 'shopee' ? 'Shopee' : t('global.both', 'Ambas')) }}
          </p>
          <span class="kpi-subtext">{{ t('kpis.top_platform_sub', 'Canal com maior oferta') }}</span>
        </div>
      </div>

      <div class="glass-panel kpi-card animate-fade-in" style="animation-delay: 0.4s;">
        <div class="kpi-icon icon-purple">
          <Trophy :size="22" />
        </div>
        <div class="kpi-content">
          <h3 class="kpi-title">{{ t('kpis.champion_product', 'Produto Campeão') }}</h3>
          <p class="kpi-value-small text-gradient" :title="topProduct?.titulo">
            {{ topProduct ? (topProduct.titulo.length > 20 ? topProduct.titulo.substring(0, 20) + '...' : topProduct.titulo) : 'N/A' }}
          </p>
          <span class="kpi-subtext" v-if="topProduct">{{ formatLargeNumber(topProduct.vendas_totais) }} {{ t('kpis.sales_suffix', 'vendas') }}</span>
          <span class="kpi-subtext" v-else>{{ t('kpis.champion_product_sub', 'Líder em vendas') }}</span>
        </div>
      </div>

      <div class="glass-panel kpi-card animate-fade-in" style="animation-delay: 0.5s;">
        <div class="kpi-icon icon-indigo">
          <TrendingUp :size="22" />
        </div>
        <div class="kpi-content">
          <h3 class="kpi-title">{{ t('kpis.revenue', 'Faturamento Est.') }}</h3>
          <p class="kpi-value text-gradient">{{ formatCurrency(estimatedRevenue, true) }}</p>
          <span class="kpi-subtext">{{ t('kpis.revenue_sub', 'Estimativa (Preço × Vendas)') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Package, DollarSign, ShoppingBag, Trophy, TrendingUp } from 'lucide-vue-next'
import { useAppI18n } from '~/composables/useAppI18n'

const { t, locale } = useAppI18n()

defineProps({
  totalProducts: { type: Number, default: 0 },
  averagePrice: { type: Number, default: 0 },
  topPlatform: { type: String, default: '' },
  topProduct: { type: Object, default: null },
  estimatedRevenue: { type: Number, default: 0 },
  dateRangeText: { type: String, default: 'Dados atualizados em tempo real' }
})

function formatLargeNumber(num) {
  if (!num) return '0'
  const unitMillion = t('kpis.unit_million', 'mi')
  const unitThousand = t('kpis.unit_thousand', 'mil')
  if (num >= 1000000) return (num / 1000000).toFixed(1) + ' ' + unitMillion
  if (num >= 1000) return (num / 1000).toFixed(1) + ' ' + unitThousand
  return num.toString()
}

function formatCurrency(num, shorten = false) {
  if (!num) return 'R$ 0,00'
  const unitMillion = t('kpis.unit_million', 'mi')
  const unitThousand = t('kpis.unit_thousand', 'mil')
  const isPt = locale.value === 'pt'
  if (shorten) {
    if (num >= 1000000) return 'R$ ' + (isPt ? (num / 1000000).toFixed(2).replace('.', ',') : (num / 1000000).toFixed(2)) + ' ' + unitMillion
    if (num >= 10000) return 'R$ ' + (isPt ? (num / 1000).toFixed(1).replace('.', ',') : (num / 1000).toFixed(1)) + ' ' + unitThousand
  }
  return 'R$ ' + num.toLocaleString(isPt ? 'pt-BR' : 'en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
</script>

<style scoped>
.kpi-container {
  margin-bottom: 2rem;
}

.kpi-date-banner {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1e40af;
  padding: 0.6rem 1.2rem;
  border-radius: 10px;
  margin-bottom: 1.2rem;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.banner-icon {
  font-size: 1.1rem;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.2rem;
}

.kpi-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem;
  min-height: 105px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.05);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  overflow: hidden;
}

.kpi-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px -4px rgba(37, 99, 235, 0.12);
  border-color: #bfdbfe;
}

.kpi-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  margin-right: 0.8rem;
  border-radius: 12px;
  flex-shrink: 0;
}

.icon-blue {
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
}

.icon-emerald {
  background: #ecfdf5;
  color: #059669;
  border: 1px solid #a7f3d0;
}

.icon-amber {
  background: #fffbeb;
  color: #d97706;
  border: 1px solid #fde68a;
}

.icon-purple {
  background: #faf5ff;
  color: #7c3aed;
  border: 1px solid #ddd6fe;
}

.icon-indigo {
  background: #eef2ff;
  color: #4f46e5;
  border: 1px solid #c7d2fe;
}

.kpi-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-end;
  flex: 1;
  text-align: right;
  min-width: 0;
}

.kpi-title {
  font-size: 0.78rem;
  color: #64748b;
  font-weight: 700;
  margin-bottom: 0.3rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.kpi-value {
  font-size: 1.45rem;
  font-weight: 800;
  margin: 0;
  white-space: nowrap;
  color: #0f172a;
}

.kpi-value-small {
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  color: #0f172a;
}

.kpi-subtext {
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.2rem;
}

@media (max-width: 640px) {
  .kpi-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  .kpi-card {
    padding: 1rem;
    min-height: auto;
  }
  .kpi-value {
    font-size: 1.25rem;
  }
}
</style>
