<template>
  <div v-if="seller" class="modal-overlay" @click.self="close">
    <div class="modal-content glass-panel animate-scale">
      <div class="modal-header">
        <div class="modal-title-box">
          <span :class="['badge-platform', seller.platform]">
            {{ seller.platform === 'meli' ? '🛒 Mercado Livre' : '🧡 Shopee' }}
          </span>
          <h3>
            {{ seller.name.startsWith('Loja em') ? '📍' : '🏪' }} 
            {{ t('seller_modal.store_ads', 'Anúncios da Loja:') }} <span class="seller-title-text">{{ seller.name }}</span>
          </h3>
        </div>
        <button class="close-btn" @click="close" :title="t('seller_modal.close_window', 'Fechar janela')">×</button>
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
          <h4>{{ t('seller_modal.ads_list', '📦 Lista de Anúncios deste Vendedor') }}</h4>
          <div class="products-table-wrapper">
            <table class="products-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>{{ t('seller_modal.col_title', 'Título do Anúncio') }}</th>
                  <th>{{ t('seller_modal.col_price', 'Preço Atual') }}</th>
                  <th>{{ t('seller_modal.col_sales', 'Vendas Totais') }}</th>
                  <th class="text-center">{{ t('seller_modal.col_actions', 'Ações') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in seller.products" :key="item.id || index">
                  <td class="rank-td">{{ index + 1 }}</td>
                  <td class="title-td" :title="item.titulo">
                    <span class="product-title">{{ item.titulo }}</span>
                  </td>
                  <td class="price-td">R$ {{ item.preco ? item.preco.toFixed(2).replace('.', ',') : '0,00' }}</td>
                  <td class="sales-td"><strong>{{ item.vendas_totais || 0 }}</strong> {{ t('charts.units_short', 'un') }}</td>
                  <td class="action-td">
                    <button @click="inspectProduct(item)" class="icon-btn action-btn" :title="t('seller_modal.inspect_tooltip', 'Ver gráfico e histórico do anúncio')">🔎</button>
                    <a :href="item.link" target="_blank" class="icon-btn link-btn" :title="t('seller_modal.store_tooltip', 'Abrir anúncio na loja original')">↗</a>
                  </td>
                </tr>
                <tr v-if="!seller.products || seller.products.length === 0">
                  <td colspan="5" class="empty-state">{{ t('seller_modal.empty', 'Nenhum anúncio encontrado para este vendedor.') }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal do Produto Individual (Sub-modal) -->
    <ProductModal v-if="selectedProduct" :product="selectedProduct" @close="selectedProduct = null" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ProductModal from './ProductModal.vue'
import { useAppI18n } from '~/composables/useAppI18n'

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
</script>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 23, 42, 0.65); display: flex; justify-content: center; align-items: center; z-index: 1100; backdrop-filter: blur(4px); padding: 1rem; }
.modal-content { width: 100%; max-width: 900px; max-height: 90vh; overflow-y: auto; padding: 2rem; border-radius: 16px; position: relative; background: #ffffff; border: 1px solid #e2e8f0; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); }

.modal-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 1rem; }
.modal-title-box { flex: 1; padding-right: 1rem; }
.badge-platform { display: inline-block; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: 700; margin-bottom: 0.4rem; }
.badge-platform.meli { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
.badge-platform.shopee { background: #ffedd5; color: #c2410c; border: 1px solid #fdba74; }
.modal-header h3 { margin: 0; color: #0f172a; font-size: 1.25rem; }
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
.products-table-section h4 { font-size: 1rem; color: #0f172a; margin-bottom: 0.8rem; }
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
