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
              <span>{{ t('seller_modal.store_ads', 'Anúncios da Loja:') }}</span>
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
              <span class="card-label">{{ t('seller_modal.mapped_ads', 'Anúncios Mapeados') }}</span>
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

          <!-- Lista de Produtos/Anúncios da Loja -->
          <div class="products-table-section">
            <h4 class="section-title-flex">
              <Package :size="17" />
              {{ t('seller_modal.ads_list', 'Lista de Anúncios deste Vendedor') }}
            </h4>
            <div class="products-table-wrapper">
              <table class="products-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>{{ t('seller_modal.col_title', 'Título do Anúncio') }}</th>
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
                    <td class="action-td">
                      <button 
                        @click="inspectProduct(p)" 
                        class="icon-btn action-btn" 
                        :title="t('table.analyze_btn', 'Ver Histórico Completo')"
                      >
                        <LineChart :size="15" />
                      </button>
                      <a 
                        :href="getProductLink(p)" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        class="icon-btn link-btn" 
                        :title="t('table.view_ad_btn', 'Abrir Anúncio')"
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

      <!-- Modal de Detalhes do Produto Selecionado -->
      <ProductModal v-if="selectedProduct" :product="selectedProduct" @close="selectedProduct = null" />
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { ShoppingBag, MapPin, Store, X, Package, LineChart, ExternalLink } from 'lucide-vue-next'
import { useAppI18n } from '~/composables/useAppI18n'
import ProductModal from './ProductModal.vue'

const { t, locale } = useAppI18n()

const props = defineProps({
  seller: { type: Object, default: null }
})
const emit = defineEmits(['close'])
const selectedProduct = ref(null)

function close() {
  emit('close')
}

function inspectProduct(product) {
  selectedProduct.value = product
}

function getProductLink(product) {
  if (product && product.link && typeof product.link === 'string' && product.link.startsWith('http')) {
    return product.link
  }
  const query = (product && product.titulo) || (props.seller && props.seller.name) || 'biscuit'
  const plat = (product && product.plataforma) || (props.seller && props.seller.platform) || 'meli'
  if (plat === 'shopee') {
    return `https://shopee.com.br/search?keyword=${encodeURIComponent(query)}`
  }
  return `https://lista.mercadolivre.com.br/${encodeURIComponent(query)}`
}
</script>

<style scoped>
.modal-overlay { position: fixed; inset: 0; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(15, 23, 42, 0.7); display: flex; justify-content: center; align-items: center; z-index: 99999; backdrop-filter: blur(6px); padding: 1.5rem; }
.modal-content { width: 100%; max-width: 900px; max-height: 88vh; overflow-y: auto; padding: 2rem; border-radius: 16px; position: relative; background: #ffffff; border: 1px solid #e2e8f0; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); margin: auto; }

.modal-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 1rem; }
.modal-title-box { flex: 1; padding-right: 1rem; }
.badge-platform { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: 700; margin-bottom: 0.4rem; }
.badge-platform.meli { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
.badge-platform.shopee { background: #ffedd5; color: #c2410c; border: 1px solid #fdba74; }
.modal-heading-flex { margin: 0; color: #0f172a; font-size: 1.25rem; display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.seller-title-text { color: #2563eb; font-weight: 700; }

.close-btn { background: #f1f5f9; border: 1px solid #cbd5e1; color: #64748b; width: 36px; height: 36px; border-radius: 50%; font-size: 1.5rem; cursor: pointer; transition: all 0.2s ease; display: flex; justify-content: center; align-items: center; line-height: 1; }
.close-btn:hover { background: #fee2e2; color: #dc2626; border-color: #fca5a5; }

.seller-summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.summary-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.9rem; display: flex; flex-direction: column; gap: 0.3rem; }
.card-label { font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; }
.card-value { font-size: 1.15rem; font-weight: 700; color: #0f172a; }
.card-value.sales { color: #059669; }
.card-value.revenue { color: #2563eb; }

.products-table-section { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.2rem; }
.section-title-flex { font-size: 1rem; color: #0f172a; margin-bottom: 0.8rem; display: flex; align-items: center; gap: 0.45rem; }
.products-table-wrapper { overflow-x: auto; max-height: 380px; }
.products-table { width: 100%; border-collapse: collapse; text-align: left; background: #ffffff; }
.products-table th, .products-table td { padding: 0.75rem 0.9rem; border-bottom: 1px solid #e2e8f0; font-size: 0.88rem; }
.products-table th { background: #f1f5f9; color: #475569; font-weight: 700; position: sticky; top: 0; z-index: 2; }

.rank-td { width: 40px; color: #64748b; font-weight: 700; }
.title-td { max-width: 320px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 500; }
.product-title { color: #0f172a; }
.price-td { font-weight: 700; color: #2563eb; white-space: nowrap; }
.sales-td { white-space: nowrap; color: #059669; }
.text-center { text-align: center; }

.action-td { display: flex; gap: 0.4rem; justify-content: center; align-items: center; white-space: nowrap; }
.icon-btn { display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; border-radius: 6px; font-size: 0.9rem; cursor: pointer; transition: all 0.2s ease; text-decoration: none; border: 1px solid #cbd5e1; }
.action-btn { background: #eff6ff; color: #2563eb; border-color: #bfdbfe; }
.action-btn:hover { background: #dbeafe; transform: translateY(-1px); }
.link-btn { background: #f8fafc; color: #475569; border-color: #cbd5e1; font-weight: bold; }
.link-btn:hover { background: #f1f5f9; color: #0f172a; transform: translateY(-1px); }

.animate-scale { animation: scaleIn 0.25s ease-out; }
@keyframes scaleIn { from { transform: scale(0.97); opacity: 0; } to { transform: scale(1); opacity: 1; } }
</style>
