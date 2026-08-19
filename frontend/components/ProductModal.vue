<template>
  <div v-if="product" class="modal-overlay" @click.self="close">
    <div class="modal-content glass-panel animate-scale">
      <div class="modal-header">
        <div class="modal-title-box">
          <span class="badge-category">{{ product.categoria || 'Geral' }}</span>
          <h3>🔎 Análise Detalhada: <span class="product-title-text">{{ product.titulo }}</span></h3>
        </div>
        <button class="close-btn" @click="close" title="Fechar janela">×</button>
      </div>
      
      <div class="modal-body">
        <!-- Cards de Visão Geral do Produto -->
        <div class="product-summary-grid">
          <div class="summary-card">
            <span class="card-label">Plataforma</span>
            <span :class="['badge-platform', product.plataforma]">
              {{ product.plataforma === 'meli' ? '🛒 Mercado Livre' : '🧡 Shopee' }}
            </span>
          </div>

          <div class="summary-card">
            <span class="card-label">Preço Atual</span>
            <span class="card-value price">R$ {{ product.preco ? product.preco.toFixed(2).replace('.', ',') : '0,00' }}</span>
          </div>

          <div class="summary-card">
            <span class="card-label">Vendas Acumuladas</span>
            <span class="card-value sales">{{ product.vendas_totais || 0 }} unidades</span>
          </div>

          <div class="summary-card" v-if="product.vendedor">
            <span class="card-label">Vendedor / Origem</span>
            <span class="card-value seller">
              {{ product.vendedor.startsWith('Loja em') ? '📍' : '🏪' }} {{ product.vendedor }}
            </span>
          </div>

          <div class="summary-card">
            <span class="card-label">Anúncio Original</span>
            <a :href="product.link" target="_blank" class="store-link-btn">Acessar na Loja ↗</a>
          </div>
        </div>

        <!-- Gráfico do Histórico -->
        <div class="chart-section">
          <h4>📈 Histórico de Evolução (Preço x Vendas)</h4>
          <ClientOnly>
            <apexchart type="line" height="300" :options="chartOptions" :series="chartSeries"></apexchart>
            <template #fallback>
              <div class="loading-chart">Carregando dados históricos do anúncio...</div>
            </template>
          </ClientOnly>
        </div>

        <!-- Tabela de Histórico Bruto -->
        <div class="history-table-section" v-if="product.historico_coletas && product.historico_coletas.length > 0">
          <h4>📅 Registro de Coletas</h4>
          <div class="history-table-wrapper">
            <table class="history-table">
              <thead>
                <tr>
                  <th>Data da Coleta</th>
                  <th>Preço (R$)</th>
                  <th>Vendas Totais</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(entry, index) in product.historico_coletas" :key="index">
                  <td>{{ formatDate(entry.data_coleta) }}</td>
                  <td class="fw-bold">R$ {{ entry.preco ? entry.preco.toFixed(2).replace('.', ',') : '0,00' }}</td>
                  <td>{{ entry.vendas_totais || 0 }} un</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

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
  return d.toLocaleDateString('pt-BR')
}

const chartSeries = computed(() => {
  if (!props.product || !props.product.historico_coletas) return []
  
  const history = [...props.product.historico_coletas].reverse()
  
  return [
    {
      name: 'Vendas Totais',
      type: 'area',
      data: history.map(h => h.vendas_totais || 0)
    },
    {
      name: 'Preço (R$)',
      type: 'line',
      data: history.map(h => h.preco || 0)
    }
  ]
})

const chartOptions = computed(() => {
  if (!props.product || !props.product.historico_coletas) return {}
  
  const history = [...props.product.historico_coletas].reverse()
  const dates = history.map(h => formatDate(h.data_coleta))
  
  return {
    chart: {
      type: 'line',
      background: 'transparent',
      toolbar: { show: false },
      fontFamily: 'Inter, sans-serif'
    },
    colors: ['#059669', '#2563eb'], // Verde para Vendas, Azul para Preço
    stroke: { curve: 'smooth', width: [0, 3] },
    fill: { 
      type: ['gradient', 'solid'],
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.3,
        opacityTo: 0.05,
        stops: [0, 100]
      }
    },
    labels: dates,
    xaxis: {
      type: 'category',
      labels: { style: { colors: '#475569', fontWeight: 600 } }
    },
    yaxis: [
      {
        title: { text: 'Vendas (unidades)', style: { color: '#059669', fontWeight: 600 } },
        labels: { style: { colors: '#059669' } }
      },
      {
        opposite: true,
        title: { text: 'Preço (R$)', style: { color: '#2563eb', fontWeight: 600 } },
        labels: {
          style: { colors: '#2563eb' },
          formatter: (value) => `R$ ${value.toFixed(2)}`
        }
      }
    ],
    theme: { mode: 'light' },
    tooltip: { theme: 'light' },
    legend: { position: 'top', labels: { colors: '#0f172a' } }
  }
})
</script>

<style scoped>
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 23, 42, 0.6); display: flex; justify-content: center; align-items: center; z-index: 1000; backdrop-filter: blur(4px); padding: 1rem; }
.modal-content { width: 100%; max-width: 920px; max-height: 90vh; overflow-y: auto; padding: 2rem; border-radius: 16px; position: relative; background: #ffffff; border: 1px solid #e2e8f0; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); }

.modal-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 1rem; }
.modal-title-box { flex: 1; padding-right: 1rem; }
.badge-category { font-size: 0.75rem; font-weight: 700; color: #6b21a8; background: #f3e8ff; padding: 0.2rem 0.6rem; border-radius: 99px; border: 1px solid #d8b4fe; text-transform: uppercase; margin-bottom: 0.4rem; display: inline-block; }
.modal-header h3 { margin: 0; color: #0f172a; font-size: 1.25rem; line-height: 1.4; }
.product-title-text { color: #2563eb; font-weight: 700; }

.close-btn { background: #f1f5f9; border: 1px solid #cbd5e1; color: #64748b; width: 36px; height: 36px; border-radius: 50%; font-size: 1.5rem; cursor: pointer; transition: all 0.2s ease; display: flex; justify-content: center; align-items: center; line-height: 1; }
.close-btn:hover { background: #fee2e2; color: #dc2626; border-color: #fca5a5; }

.product-summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.summary-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.9rem; display: flex; flex-direction: column; gap: 0.3rem; }
.card-label { font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; }
.card-value { font-size: 1.1rem; font-weight: 700; color: #0f172a; }
.card-value.price { color: #2563eb; }
.card-value.sales { color: #059669; }

.badge-platform { display: inline-block; padding: 0.3rem 0.6rem; border-radius: 6px; font-size: 0.85rem; font-weight: 700; width: fit-content; }
.badge-platform.meli { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
.badge-platform.shopee { background: #ffedd5; color: #c2410c; border: 1px solid #fdba74; }

.store-link-btn { display: inline-flex; align-items: center; justify-content: center; padding: 0.45rem 0.8rem; background: #2563eb; color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 0.85rem; font-weight: 600; transition: background 0.2s ease; margin-top: 0.2rem; }
.store-link-btn:hover { background: #1d4ed8; }

.chart-section { margin-bottom: 1.5rem; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.2rem; }
.chart-section h4 { font-size: 1rem; color: #0f172a; margin-bottom: 0.8rem; }
.loading-chart { height: 300px; display: flex; justify-content: center; align-items: center; color: #64748b; font-weight: 600; }

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
