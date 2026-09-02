<template>
  <Teleport to="body">
    <div v-if="product" class="modal-overlay" @click.self="close">
      <div class="modal-content glass-panel animate-scale">
        <div class="modal-header">
          <div class="modal-title-box">
            <span class="badge-category">{{ product.categoria || t('product_modal.general', 'Geral') }}</span>
            <h3 class="modal-heading-flex">
              <FileSearch :size="20" class="text-blue-600" />
              <span>{{ t('product_modal.title', 'Análise Detalhada:') }}</span>
              <span class="product-title-text">{{ product.titulo }}</span>
            </h3>
          </div>
          <button class="close-btn" @click="close" :title="t('product_modal.close_window', 'Fechar janela')">
            <X :size="18" />
          </button>
        </div>
        
        <div class="modal-body">
          <!-- Cards de Visão Geral do Produto -->
          <div class="product-summary-grid">
            <div class="summary-card">
              <span class="card-label">{{ t('product_modal.platform', 'Plataforma') }}</span>
              <span :class="['badge-platform', product.plataforma]">
                <ShoppingBag :size="14" />
                {{ product.plataforma === 'meli' ? 'Mercado Livre' : 'Shopee' }}
              </span>
            </div>

            <div class="summary-card">
              <span class="card-label">{{ t('product_modal.current_price', 'Preço Atual') }}</span>
              <span class="card-value price">R$ {{ product.preco ? product.preco.toFixed(2).replace('.', ',') : '0,00' }}</span>
            </div>

            <div class="summary-card">
              <span class="card-label">{{ t('product_modal.total_sales', 'Vendas Acumuladas') }}</span>
              <span class="card-value sales">{{ (product.vendas_totais || 0).toLocaleString(locale === 'pt' ? 'pt-BR' : 'en-US') }} {{ t('product_modal.units_label', 'unidades') }}</span>
            </div>

            <div class="summary-card" v-if="product.vendedor">
              <span class="card-label">{{ t('product_modal.seller_origin', 'Vendedor / Origem') }}</span>
              <span class="card-value seller inline-flex-seller">
                <MapPin v-if="product.vendedor.startsWith('Loja em')" :size="16" />
                <Store v-else :size="16" />
                {{ product.vendedor }}
              </span>
            </div>

            <div class="summary-card">
              <span class="card-label">{{ t('product_modal.original_ad', 'Produto Original') }}</span>
              <a :href="product.link" target="_blank" class="store-link-btn">
                {{ t('product_modal.view_in_store', 'Acessar na Loja') }}
                <ExternalLink :size="13" />
              </a>
            </div>
          </div>

          <!-- Tabela de Histórico Bruto -->
          <div class="history-table-section" v-if="product.historico_coletas && product.historico_coletas.length > 0">
            <h4 class="section-title-flex">
              <Calendar :size="17" />
              {{ t('product_modal.scrape_records', 'Registro de Coletas') }}
            </h4>
            <div class="history-table-wrapper">
              <table class="history-table">
                <thead>
                  <tr>
                    <th>{{ t('product_modal.col_date', 'Data da Coleta') }}</th>
                    <th>{{ t('table.col_price', 'Preço') }} (R$)</th>
                    <th>{{ t('table.col_sales', 'Vendas Totais') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(entry, index) in product.historico_coletas" :key="index">
                    <td>{{ formatDate(entry.data_coleta) }}</td>
                    <td class="fw-bold">R$ {{ entry.preco ? entry.preco.toFixed(2).replace('.', ',') : '0,00' }}</td>
                    <td>{{ (entry.vendas_totais || 0).toLocaleString(locale === 'pt' ? 'pt-BR' : 'en-US') }} {{ t('product_modal.unit_short', 'un') }}</td>
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
import { FileSearch, X, ShoppingBag, MapPin, Store, ExternalLink, Calendar } from 'lucide-vue-next'
import { useAppI18n } from '~/composables/useAppI18n'

const { t, locale } = useAppI18n()

const props = defineProps({
  product: { type: Object, default: null }
})
const emit = defineEmits(['close'])

function close() {
  emit('close')
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString(locale.value === 'pt' ? 'pt-BR' : 'en-US')
}
</script>

<style scoped>
.modal-overlay { position: fixed; inset: 0; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(15, 23, 42, 0.7); display: flex; justify-content: center; align-items: center; z-index: 99999; backdrop-filter: blur(6px); padding: 1.5rem; }
.modal-content { width: 100%; max-width: 780px; max-height: 88vh; overflow-y: auto; padding: 1.8rem; border-radius: 16px; position: relative; background: #ffffff; border: 1px solid #e2e8f0; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); margin: auto; }

.modal-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 1rem; }
.modal-title-box { flex: 1; padding-right: 1rem; }
.badge-category { font-size: 0.75rem; font-weight: 700; color: #6b21a8; background: #f3e8ff; padding: 0.2rem 0.6rem; border-radius: 99px; border: 1px solid #d8b4fe; text-transform: uppercase; margin-bottom: 0.4rem; display: inline-block; }
.modal-heading-flex { margin: 0; color: #0f172a; font-size: 1.2rem; line-height: 1.4; display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.product-title-text { color: #2563eb; font-weight: 700; }

.close-btn { background: #f1f5f9; border: 1px solid #cbd5e1; color: #64748b; width: 34px; height: 34px; border-radius: 50%; font-size: 1.3rem; cursor: pointer; transition: all 0.2s ease; display: flex; justify-content: center; align-items: center; line-height: 1; }
.close-btn:hover { background: #fee2e2; color: #dc2626; border-color: #fca5a5; }

.product-summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.summary-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.9rem; display: flex; flex-direction: column; gap: 0.3rem; }
.card-label { font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; }
.card-value { font-size: 1.1rem; font-weight: 700; color: #0f172a; }
.card-value.price { color: #2563eb; }
.card-value.sales { color: #059669; }
.inline-flex-seller { display: flex; align-items: center; gap: 0.4rem; }

.badge-platform { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.3rem 0.6rem; border-radius: 6px; font-size: 0.85rem; font-weight: 700; width: fit-content; }
.badge-platform.meli { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
.badge-platform.shopee { background: #ffedd5; color: #c2410c; border: 1px solid #fdba74; }

.store-link-btn { display: inline-flex; align-items: center; justify-content: center; gap: 0.35rem; padding: 0.45rem 0.8rem; background: #2563eb; color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 0.85rem; font-weight: 600; transition: background 0.2s ease; margin-top: 0.2rem; }
.store-link-btn:hover { background: #1d4ed8; }

.history-table-section { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.2rem; }
.history-table-section h4 { font-size: 1rem; color: #0f172a; margin-bottom: 0.8rem; }
.history-table-wrapper { overflow-x: auto; }
.history-table { width: 100%; border-collapse: collapse; text-align: left; }
.history-table th, .history-table td { padding: 0.6rem 0.8rem; border-bottom: 1px solid #e2e8f0; font-size: 0.88rem; }
.history-table th { background: #f1f5f9; color: #475569; font-weight: 700; }
.fw-bold { font-weight: 700; color: #0f172a; }

.animate-scale { animation: scaleIn 0.25s ease-out; }
@keyframes scaleIn { from { transform: scale(0.97); opacity: 0; } to { transform: scale(1); opacity: 1; } }
</style>
