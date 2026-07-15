<template>
  <div class="kpi-grid">
    <div class="glass-panel kpi-card animate-fade-in" style="animation-delay: 0.1s;">
      <div class="kpi-icon blue">📦</div>
      <div class="kpi-content">
        <h3 class="kpi-title">Total de Produtos</h3>
        <p class="kpi-value text-gradient">{{ totalProducts }}</p>
      </div>
    </div>
    
    <div class="glass-panel kpi-card animate-fade-in" style="animation-delay: 0.2s;">
      <div class="kpi-icon purple">💰</div>
      <div class="kpi-content">
        <h3 class="kpi-title">Preço Médio</h3>
        <p class="kpi-value text-gradient">R$ {{ averagePrice.toFixed(2).replace('.', ',') }}</p>
      </div>
    </div>
    
    <div class="glass-panel kpi-card animate-fade-in" style="animation-delay: 0.3s;">
      <div class="kpi-icon blue">🔥</div>
      <div class="kpi-content">
        <h3 class="kpi-title">Plataforma Ativa</h3>
        <p class="kpi-value text-gradient" style="text-transform: capitalize;">{{ topPlatform || 'N/A' }}</p>
      </div>
    </div>

    <div class="glass-panel kpi-card animate-fade-in" style="animation-delay: 0.4s;">
      <div class="kpi-icon purple">🏆</div>
      <div class="kpi-content">
        <h3 class="kpi-title">Produto Campeão</h3>
        <p class="kpi-value-small text-gradient" :title="topProduct?.titulo">
          {{ topProduct ? (topProduct.titulo.length > 25 ? topProduct.titulo.substring(0, 25) + '...' : topProduct.titulo) : 'N/A' }}
        </p>
        <small class="kpi-subtext" v-if="topProduct">{{ topProduct.vendas_totais }} vendas ({{ topProduct.plataforma }})</small>
      </div>
    </div>

    <div class="glass-panel kpi-card animate-fade-in" style="animation-delay: 0.5s;">
      <div class="kpi-icon blue">💎</div>
      <div class="kpi-content">
        <h3 class="kpi-title">Faturamento Estimado</h3>
        <p class="kpi-value text-gradient">R$ {{ estimatedRevenue.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</p>
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
  estimatedRevenue: { type: Number, default: 0 }
})
</script>

<style scoped>
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.kpi-card {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.kpi-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px 0 rgba(56, 189, 248, 0.2);
  border-color: rgba(56, 189, 248, 0.4);
}

.kpi-icon {
  font-size: 2rem;
  margin-right: 1.2rem;
  padding: 0.8rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
}

.kpi-title {
  font-size: 0.9rem;
  color: var(--text-muted);
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.kpi-value {
  font-size: 1.8rem;
  font-weight: 800;
  margin: 0;
}

.kpi-value-small {
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0;
  white-space: nowrap;
}
.kpi-subtext {
  font-size: 0.8rem;
  color: var(--text-muted);
}
</style>
