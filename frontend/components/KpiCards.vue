<template>
  <div class="kpi-container">
    <div class="kpi-grid">
      <div class="glass-panel kpi-card animate-fade-in" style="animation-delay: 0.1s;">
        <div class="kpi-icon blue">📦</div>
        <div class="kpi-content">
          <h3 class="kpi-title">Total de Produtos</h3>
          <p class="kpi-value text-gradient">{{ formatLargeNumber(totalProducts) }}</p>
        </div>
      </div>
      
      <div class="glass-panel kpi-card animate-fade-in" style="animation-delay: 0.2s;">
        <div class="kpi-icon purple">💰</div>
        <div class="kpi-content">
          <h3 class="kpi-title">Preço Médio</h3>
          <p class="kpi-value text-gradient">{{ formatCurrency(averagePrice, false) }}</p>
        </div>
      </div>
      
      <div class="glass-panel kpi-card animate-fade-in" style="animation-delay: 0.3s;">
        <div class="kpi-icon blue">🔥</div>
        <div class="kpi-content">
          <h3 class="kpi-title">Top Plataforma</h3>
          <p class="kpi-value text-gradient" style="text-transform: capitalize;">
            {{ topPlatform === 'meli' ? 'Mercado Livre' : (topPlatform === 'shopee' ? 'Shopee' : 'Ambas') }}
          </p>
        </div>
      </div>

      <div class="glass-panel kpi-card animate-fade-in" style="animation-delay: 0.4s;">
        <div class="kpi-icon purple">🏆</div>
        <div class="kpi-content">
          <h3 class="kpi-title">Produto Campeão</h3>
          <p class="kpi-value-small text-gradient" :title="topProduct?.titulo">
            {{ topProduct ? (topProduct.titulo.length > 20 ? topProduct.titulo.substring(0, 20) + '...' : topProduct.titulo) : 'N/A' }}
          </p>
          <small class="kpi-subtext" v-if="topProduct">{{ formatLargeNumber(topProduct.vendas_totais) }} vendas</small>
        </div>
      </div>

      <div class="glass-panel kpi-card animate-fade-in" style="animation-delay: 0.5s;">
        <div class="kpi-icon blue">💎</div>
        <div class="kpi-content">
          <h3 class="kpi-title">Faturamento Est.</h3>
          <p class="kpi-value text-gradient">{{ formatCurrency(estimatedRevenue, true) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
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
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num.toString()
}

function formatCurrency(num, shorten = false) {
  if (!num) return 'R$ 0,00'
  if (shorten) {
    if (num >= 1000000) return 'R$ ' + (num / 1000000).toFixed(2).replace('.', ',') + 'M'
    if (num >= 10000) return 'R$ ' + (num / 1000).toFixed(1).replace('.', ',') + 'k'
  }
  return 'R$ ' + num.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
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
  font-size: 1.6rem;
  margin-right: 0.8rem;
  padding: 0.7rem;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  flex-shrink: 0;
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
</style>
