<template>
  <div class="strategy-container">
    <div class="glass-panel strategy-header animate-fade-in">
      <div class="header-content">
        <h2>🏷️ Monitor de Estratégias de Preço & Precificação</h2>
        <p>Análise comportamental dos concorrentes: identifique produtos com <strong>aumento de margem</strong> vs produtos em <strong>guerra de preço/desconto</strong>.</p>
      </div>

      <div class="strategy-summary-pills">
        <div class="pill green">
          <span class="count">{{ priceIncreases.length }}</span>
          <span class="label">Aumentaram Preço</span>
        </div>
        <div class="pill red">
          <span class="count">{{ priceDrops.length }}</span>
          <span class="label">Reduziram Preço</span>
        </div>
      </div>
    </div>

    <div class="strategy-grid">
      <!-- Card Aumento de Preço (Poder de Marca / Margem) -->
      <div class="glass-panel strategy-card animate-fade-in" style="animation-delay: 0.1s;">
        <div class="card-title-bar green">
          <span class="icon">📈</span>
          <h3>Aumento de Preço & Margem</h3>
          <small>Produtos que subiram o valor sem estagnar vendas</small>
        </div>

        <transition name="slide-up" mode="out-in">
          <div v-if="isLoading" class="p-4">
            <div v-for="i in 3" :key="'skel-up'+i" class="skeleton skeleton-text mb-2" style="height: 32px;"></div>
          </div>
          <div v-else class="table-wrapper">
            <table class="mini-table">
            <thead>
              <tr>
                <th>Produto / Vendedor</th>
                <th class="text-right">Antes</th>
                <th class="text-right">Agora</th>
                <th class="text-right">Variação</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in priceIncreases" :key="item.id">
                <td>
                  <a :href="item.link" target="_blank" class="prod-link">{{ item.titulo }}</a>
                  <small class="seller-name">{{ item.vendedor || 'Vendedor' }}</small>
                </td>
                <td class="text-right">R$ {{ item.precoAnterior.toFixed(2) }}</td>
                <td class="text-right font-bold text-green">R$ {{ item.preco.toFixed(2) }}</td>
                <td class="text-right">
                  <span class="badge-price-up">▲ +R$ {{ item.diff.toFixed(2) }}</span>
                </td>
              </tr>
              <tr v-if="priceIncreases.length === 0">
                <td colspan="4" class="empty">Nenhum aumento de preço registrado no período.</td>
              </tr>
            </tbody>
            </table>
          </div>
        </transition>
      </div>

      <!-- Card Redução de Preço (Guerra de Preços / Promoção) -->
      <div class="glass-panel strategy-card animate-fade-in" style="animation-delay: 0.2s;">
        <div class="card-title-bar red">
          <span class="icon">📉</span>
          <h3>Guerra de Preço & Descontos</h3>
          <small>Produtos que baixaram o valor para ganhar volume</small>
        </div>

        <transition name="slide-up" mode="out-in">
          <div v-if="isLoading" class="p-4">
            <div v-for="i in 3" :key="'skel-down'+i" class="skeleton skeleton-text mb-2" style="height: 32px;"></div>
          </div>
          <div v-else class="table-wrapper">
            <table class="mini-table">
            <thead>
              <tr>
                <th>Produto / Vendedor</th>
                <th class="text-right">Antes</th>
                <th class="text-right">Agora</th>
                <th class="text-right">Variação</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in priceDrops" :key="item.id">
                <td>
                  <a :href="item.link" target="_blank" class="prod-link">{{ item.titulo }}</a>
                  <small class="seller-name">{{ item.vendedor || 'Vendedor' }}</small>
                </td>
                <td class="text-right">R$ {{ item.precoAnterior.toFixed(2) }}</td>
                <td class="text-right font-bold text-red">R$ {{ item.preco.toFixed(2) }}</td>
                <td class="text-right">
                  <span class="badge-price-down">▼ -R$ {{ Math.abs(item.diff).toFixed(2) }}</span>
                </td>
              </tr>
              <tr v-if="priceDrops.length === 0">
                <td colspan="4" class="empty">Nenhuma redução de preço registrada no período.</td>
              </tr>
            </tbody>
            </table>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  products: { type: Array, default: () => [] },
  isLoading: { type: Boolean, default: false }
})

const priceIncreases = computed(() => {
  const res = []
  for (const p of props.products) {
    if (!p.historico_coletas || p.historico_coletas.length < 2) continue
    const precoHoje = p.preco || 0
    const precoAntes = p.historico_coletas[1].preco || 0
    const diff = precoHoje - precoAntes

    if (diff > 0.5) { // Aumento relevante (> R$ 0.50)
      res.push({ ...p, precoAnterior: precoAntes, diff })
    }
  }
  return res.sort((a, b) => b.diff - a.diff)
})

const priceDrops = computed(() => {
  const res = []
  for (const p of props.products) {
    if (!p.historico_coletas || p.historico_coletas.length < 2) continue
    const precoHoje = p.preco || 0
    const precoAntes = p.historico_coletas[1].preco || 0
    const diff = precoHoje - precoAntes

    if (diff < -0.5) { // Redução relevante (< -R$ 0.50)
      res.push({ ...p, precoAnterior: precoAntes, diff })
    }
  }
  return res.sort((a, b) => a.diff - b.diff)
})
</script>

<style scoped>
.strategy-container { display: flex; flex-direction: column; gap: 1.5rem; margin-bottom: 2rem; }
.strategy-header { padding: 1.5rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
.header-content h2 { margin: 0 0 0.3rem 0; font-size: 1.3rem; color: #0f172a; }
.header-content p { margin: 0; color: #64748b; font-size: 0.9rem; }

.strategy-summary-pills { display: flex; gap: 0.8rem; }
.pill { background: #f8fafc; border: 1px solid #cbd5e1; padding: 0.6rem 1.2rem; border-radius: 10px; display: flex; flex-direction: column; align-items: center; }
.pill.green { background: #f0fdf4; border-color: #bbf7d0; color: #166534; }
.pill.red { background: #fef2f2; border-color: #fecaca; color: #991b1b; }
.pill .count { font-weight: 800; font-size: 1.2rem; }
.pill .label { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; }

.strategy-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
@media (max-width: 900px) { .strategy-grid { grid-template-columns: 1fr; } }

.strategy-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
.card-title-bar { padding: 1.2rem; display: flex; flex-direction: column; gap: 0.2rem; border-bottom: 1px solid #e2e8f0; }
.card-title-bar.green { background: #f0fdf4; border-bottom-color: #bbf7d0; }
.card-title-bar.red { background: #fef2f2; border-bottom-color: #fecaca; }
.card-title-bar h3 { margin: 0; font-size: 1.1rem; color: #0f172a; display: flex; align-items: center; gap: 0.5rem; }
.card-title-bar small { color: #64748b; font-size: 0.8rem; }

.table-wrapper { padding: 0.5rem; overflow-x: auto; }
.mini-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.mini-table th { padding: 0.6rem 0.8rem; color: #64748b; font-weight: 700; border-bottom: 1px solid #e2e8f0; text-align: left; }
.mini-table td { padding: 0.75rem 0.8rem; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }

.prod-link { color: #0f172a; font-weight: 600; text-decoration: none; display: block; max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.prod-link:hover { color: #2563eb; text-decoration: underline; }
.seller-name { font-size: 0.72rem; color: #64748b; display: block; }

.badge-price-up { background: #dcfce7; color: #15803d; font-weight: 700; padding: 0.15rem 0.45rem; border-radius: 4px; font-size: 0.78rem; }
.badge-price-down { background: #fee2e2; color: #991b1b; font-weight: 700; padding: 0.15rem 0.45rem; border-radius: 4px; font-size: 0.78rem; }
.text-green { color: #16a34a; }
.text-red { color: #dc2626; }
.empty { text-align: center; color: #94a3b8; padding: 1.5rem; }
</style>
