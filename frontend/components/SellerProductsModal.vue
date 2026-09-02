<template>
  <Teleport to="body">
    <div v-if="seller" class="modal-overlay" @click.self="close">
      <div class="modal-content glass-panel animate-scale">
        <div class="modal-header">
          <div class="modal-title-box">
            <span :class="['badge-platform', seller.platform]">
              <ShoppingBag :size="14" />
              {{ seller.platform === 'meli' ? 'Mercado Livre' : 'Shopee' }}
            </span>
            <h3 class="modal-heading-flex">
              <MapPin v-if="seller.name.startsWith('Loja em')" :size="20" class="text-blue-600" />
              <Store v-else :size="20" class="text-blue-600" />
              <span>{{ t('seller_modal.store_ads', 'Produtos da Loja:') }}</span>
              <span class="seller-title-text">{{ seller.name }}</span>
            </h3>
          </div>
          <button class="close-btn" @click="close" :title="t('seller_modal.close_window', 'Fechar janela')">
            <X :size="18" />
          </button>
        </div>

        <div class="modal-body">
          <!-- Resumo da Loja -->
          <div class="seller-summary-grid">
            <div class="summary-card">
              <span class="card-label">{{ t('seller_modal.mapped_ads', 'Produtos Mapeados') }}</span>
              <span class="card-value">{{ seller.products.length }} {{ t('seller_modal.products_count', 'produtos') }}</span>
            </div>

            <div class="summary-card">
              <span class="card-label">{{ t('seller_modal.total_sales', 'Vendas Totais') }}</span>
              <span class="card-value sales">{{ seller.totalSales.toLocaleString(locale === 'pt' ? 'pt-BR' : 'en-US') }} {{ t('charts.units_short', 'un') }}</span>
            </div>

            <div class="summary-card">
              <span class="card-label">{{ t('seller_modal.estimated_revenue', 'Faturamento Estimado') }}</span>
              <span class="card-value revenue">R$ {{ seller.estimatedRevenue.toLocaleString(locale === 'pt' ? 'pt-BR' : 'en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
            </div>
          </div>

          <!-- Lista de Produtos da Loja -->
          <div class="products-table-section">
            <h4 class="section-title-flex">
              <Package :size="17" />
              {{ t('seller_modal.ads_list', 'Lista de Produtos deste Vendedor') }}
            </h4>
            <div class="products-table-wrapper">
              <table class="products-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>{{ t('seller_modal.col_title', 'Título do Produto') }}</th>
                    <th>{{ t('seller_modal.col_price', 'Preço Atual') }}</th>
                    <th>{{ t('seller_modal.col_sales', 'Vendas Acumuladas') }}</th>
                    <th>{{ t('table.col_revenue', 'Faturamento Est.') }}</th>
                    <th class="text-center">{{ t('global.actions', 'Ações') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(p, index) in seller.products" :key="p.id || index">
                    <td class="rank-td">{{ index + 1 }}</td>
                    <td class="title-td" :title="p.titulo">
                      <span class="product-title">{{ p.titulo }}</span>
                    </td>
                    <td class="price-td">R$ {{ p.preco ? p.preco.toFixed(2).replace('.', ',') : '0,00' }}</td>
                    <td class="sales-td">{{ p.vendas_totais || 0 }} {{ t('charts.units_short', 'un') }}</td>
                    <td class="sales-td">R$ {{ ((p.preco || 0) * (p.vendas_totais || 0)).toLocaleString(locale === 'pt' ? 'pt-BR' : 'en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</td>
                    <td class="action-td text-center">
                      <a 
                        :href="getProductLink(p)" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        class="icon-btn link-btn" 
                        :title="t('table.view_ad_btn', 'Abrir Produto')"
                      >
                        <ExternalLink :size="15" />
                      </a>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ShoppingBag, MapPin, Store, X, Package, ExternalLink } from 'lucide-vue-next'
import { useAppI18n } from '~/composables/useAppI18n'

const { t, locale } = useAppI18n()

const props = defineProps({
  seller: { type: Object, default: null }
})
const emit = defineEmits(['close'])

function close() {
  emit('close')
}

function getProductLink(p) {
  if (p && p.link && typeof p.link === 'string' && p.link.startsWith('http')) {
    return p.link
  }
  const query = (p && p.titulo) || (props.seller && props.seller.name) || 'produto'
  if (props.seller && props.seller.platform === 'shopee') {
    return `https://shopee.com.br/search?keyword=${encodeURIComponent(query)}`
  }
  return `https://lista.mercadolivre.com.br/${encodeURIComponent(query)}`
}
</script>

<style scoped>
.modal-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 999; padding: 1rem; }
.modal-content { background: #ffffff; border-radius: 16px; width: 100%; max-width: 850px; max-height: 85vh; display: flex; flex-direction: column; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); border: 1px solid #cbd5e1; }
.modal-header { padding: 1.25rem 1.5rem; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.modal-title-box { display: flex; flex-direction: column; gap: 0.35rem; }
.modal-heading-flex { margin: 0; font-size: 1.25rem; font-weight: 800; color: #0f172a; display: flex; align-items: center; gap: 0.5rem; }
.seller-title-text { color: #2563eb; }
.badge-platform { font-size: 0.72rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 4px; display: inline-flex; align-items: center; gap: 0.3rem; width: fit-content; }
.badge-platform.meli { background: #fff59d; color: #574c00; }
.badge-platform.shopee { background: #ffccbc; color: #bf360c; }
.close-btn { background: transparent; border: none; color: #64748b; cursor: pointer; padding: 0.4rem; border-radius: 6px; display: flex; align-items: center; justify-content: center; }
.close-btn:hover { background: #f1f5f9; color: #0f172a; }

.modal-body { padding: 1.5rem; overflow-y: auto; display: flex; flex-direction: column; gap: 1.5rem; }
.seller-summary-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.summary-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1rem; display: flex; flex-direction: column; gap: 0.25rem; }
.card-label { font-size: 0.75rem; color: #64748b; font-weight: 700; text-transform: uppercase; }
.card-value { font-size: 1.1rem; font-weight: 800; color: #0f172a; }
.card-value.sales { color: #2563eb; }
.card-value.revenue { color: #16a34a; }

.products-table-section { display: flex; flex-direction: column; gap: 0.75rem; }
.section-title-flex { margin: 0; font-size: 1rem; color: #0f172a; display: flex; align-items: center; gap: 0.4rem; font-weight: 700; }
.products-table-wrapper { border: 1px solid #e2e8f0; border-radius: 10px; overflow-x: auto; }
.products-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.88rem; }
.products-table th { background: #f8fafc; color: #475569; padding: 0.75rem 0.9rem; font-weight: 700; border-bottom: 1px solid #e2e8f0; }
.products-table td { padding: 0.75rem 0.9rem; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }

.rank-td { font-weight: 700; color: #64748b; width: 40px; }
.title-td { max-width: 320px; }
.product-title { font-weight: 600; color: #0f172a; display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.price-td { font-weight: 700; color: #0f172a; white-space: nowrap; }
.sales-td { font-weight: 600; color: #475569; white-space: nowrap; }

.action-td { white-space: nowrap; }
.icon-btn.link-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  background: #f8fafc;
  color: #475569;
  text-decoration: none;
  transition: all 0.2s ease;
}
.icon-btn.link-btn:hover {
  background: #eff6ff;
  color: #2563eb;
  border-color: #93c5fd;
  transform: translateY(-1px);
}
</style>
