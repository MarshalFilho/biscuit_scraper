<template>
  <div class="strategy-container">
    <div class="glass-panel strategy-header animate-fade-in">
      <div class="header-content">
        <h2 class="title-with-icon">
          <Tag :size="22" class="text-indigo-600" />
          <span>{{ t('strategy.title', 'Monitor de Estratégias de Preço & Precificação') }}</span>
        </h2>
        <p v-html="t('strategy.subtitle', 'Análise comportamental dos concorrentes: identifique produtos com <strong>aumento de preço</strong> vs produtos com <strong>descontos e reduções</strong>.')"></p>
      </div>

      <div class="strategy-summary-pills">
        <div class="pill green">
          <span class="count">{{ priceIncreases.length }}</span>
          <span class="label">{{ t('strategy.price_increased', 'Aumentaram Preço') }}</span>
        </div>
        <div class="pill red">
          <span class="count">{{ priceDrops.length }}</span>
          <span class="label">{{ t('strategy.price_dropped', 'Reduziram Preço') }}</span>
        </div>
      </div>
    </div>

    <div class="strategy-grid">
      <!-- Card Aumento de Preço (Poder de Marca / Margem) -->
      <div class="glass-panel strategy-card animate-fade-in" style="animation-delay: 0.1s;">
        <div class="card-title-bar green">
          <div class="card-heading-flex">
            <TrendingUp :size="20" class="text-emerald-600" />
            <h3>{{ t('strategy.card1_title', 'Aumento de Preço & Margem') }}</h3>
          </div>
          <small>{{ t('strategy.card1_desc', 'Produtos que subiram o valor') }}</small>
        </div>

        <transition name="slide-up" mode="out-in">
          <div v-if="isLoading" class="p-4">
            <div v-for="i in 3" :key="'skel-up'+i" class="skeleton skeleton-text mb-2" style="height: 32px;"></div>
          </div>
          <div v-else class="table-wrapper">
            <table class="mini-table">
            <thead>
              <tr>
                <th>{{ t('strategy.col_product', 'Produto / Vendedor') }}</th>
                <th class="text-right">{{ t('strategy.col_before', 'Antes') }}</th>
                <th class="text-right">{{ t('strategy.col_now', 'Agora') }}</th>
                <th class="text-right">{{ t('strategy.col_variation', 'Variação') }}</th>
                <th class="text-right">{{ t('table.col_sales', 'Vendas') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in priceIncreases" :key="item.id">
                <td>
                  <a :href="item.link" target="_blank" class="prod-link">{{ item.titulo }}</a>
                  <small class="seller-name">{{ item.vendedor || t('strategy.seller', 'Vendedor') }}</small>
                </td>
                <td class="text-right">R$ {{ item.precoAnterior.toFixed(2).replace('.', ',') }}</td>
                <td class="text-right font-bold text-green">R$ {{ item.preco.toFixed(2).replace('.', ',') }}</td>
                <td class="text-right">
                  <span class="badge-price-up">
                    <ArrowUpRight :size="13" />
                    +R$ {{ item.diff.toFixed(2).replace('.', ',') }}
                  </span>
                </td>
                <td class="text-right font-medium sales-col">
                  {{ (item.vendas_totais || 0).toLocaleString(locale === 'pt' ? 'pt-BR' : 'en-US') }} un
                  <span v-if="item.salesDiff && item.salesDiff > 0" class="badge-growth-sm">+{{ item.salesDiff }}</span>
                </td>
              </tr>
              <tr v-if="priceIncreases.length === 0">
                <td colspan="5" class="empty">{{ t('strategy.no_increases', 'Nenhum aumento de preço registrado no período.') }}</td>
              </tr>
            </tbody>
            </table>
          </div>
        </transition>
      </div>

      <!-- Card Redução de Preço (Guerra de Preços / Promoção) -->
      <div class="glass-panel strategy-card animate-fade-in" style="animation-delay: 0.2s;">
        <div class="card-title-bar red">
          <div class="card-heading-flex">
            <TrendingDown :size="20" class="text-rose-600" />
            <h3>{{ t('strategy.card2_title', 'Guerra de Preço & Descontos') }}</h3>
          </div>
          <small>{{ t('strategy.card2_desc', 'Produtos que baixaram o valor') }}</small>
        </div>

        <transition name="slide-up" mode="out-in">
          <div v-if="isLoading" class="p-4">
            <div v-for="i in 3" :key="'skel-down'+i" class="skeleton skeleton-text mb-2" style="height: 32px;"></div>
          </div>
          <div v-else class="table-wrapper">
            <table class="mini-table">
            <thead>
              <tr>
                <th>{{ t('strategy.col_product', 'Produto / Vendedor') }}</th>
                <th class="text-right">{{ t('strategy.col_before', 'Antes') }}</th>
                <th class="text-right">{{ t('strategy.col_now', 'Agora') }}</th>
                <th class="text-right">{{ t('strategy.col_variation', 'Variação') }}</th>
                <th class="text-right">{{ t('table.col_sales', 'Vendas') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in priceDrops" :key="item.id">
                <td>
                  <a :href="item.link" target="_blank" class="prod-link">{{ item.titulo }}</a>
                  <small class="seller-name">{{ item.vendedor || t('strategy.seller', 'Vendedor') }}</small>
                </td>
                <td class="text-right">R$ {{ item.precoAnterior.toFixed(2).replace('.', ',') }}</td>
                <td class="text-right font-bold text-red">R$ {{ item.preco.toFixed(2).replace('.', ',') }}</td>
                <td class="text-right">
                  <span class="badge-price-down">
                    <ArrowDownRight :size="13" />
                    -R$ {{ Math.abs(item.diff).toFixed(2).replace('.', ',') }}
                  </span>
                </td>
                <td class="text-right font-medium sales-col">
                  {{ (item.vendas_totais || 0).toLocaleString(locale === 'pt' ? 'pt-BR' : 'en-US') }} un
                  <span v-if="item.salesDiff && item.salesDiff > 0" class="badge-growth-sm">+{{ item.salesDiff }}</span>
                </td>
              </tr>
              <tr v-if="priceDrops.length === 0">
                <td colspan="5" class="empty">{{ t('strategy.no_drops', 'Nenhuma redução de preço registrada no período.') }}</td>
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
import { Tag, TrendingUp, TrendingDown, ArrowUpRight, ArrowDownRight } from 'lucide-vue-next'
import { useAppI18n } from '~/composables/useAppI18n'

const { t, locale } = useAppI18n()

const props = defineProps({
  products: { type: Array, default: () => [] },
  isLoading: { type: Boolean, default: false }
})

const priceIncreases = computed(() => {
  const res = []
  for (const p of props.products) {
    const precoHoje = p.preco || 0
    let precoAntes = precoHoje
    let diff = 0

    if (p.varInfo) {
      diff = p.varInfo.diff
      precoAntes = p.hist ? p.hist.preco : (precoHoje - diff)
    } else if (p.hist) {
      precoAntes = p.hist.preco
      diff = precoHoje - precoAntes
    } else if (p.historico_coletas && p.historico_coletas.length >= 2) {
      precoAntes = p.historico_coletas[p.historico_coletas.length - 1].preco || 0
      diff = precoHoje - precoAntes
    }

    if (diff > 0.05) {
      res.push({ ...p, precoAnterior: precoAntes, diff })
    }
  }
  return res.sort((a, b) => b.diff - a.diff)
})

const priceDrops = computed(() => {
  const res = []
  for (const p of props.products) {
    const precoHoje = p.preco || 0
    let precoAntes = precoHoje
    let diff = 0

    if (p.varInfo) {
      diff = p.varInfo.diff
      precoAntes = p.hist ? p.hist.preco : (precoHoje - diff)
    } else if (p.hist) {
      precoAntes = p.hist.preco
      diff = precoHoje - precoAntes
    } else if (p.historico_coletas && p.historico_coletas.length >= 2) {
      precoAntes = p.historico_coletas[p.historico_coletas.length - 1].preco || 0
      diff = precoHoje - precoAntes
    }

    if (diff < -0.05) {
      res.push({ ...p, precoAnterior: precoAntes, diff })
    }
  }
  return res.sort((a, b) => a.diff - b.diff)
})
</script>

<style scoped>
.strategy-container { display: flex; flex-direction: column; gap: 1.4rem; margin-bottom: 2rem; }
.strategy-header { padding: 1.35rem 1.5rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; box-shadow: 0 4px 15px -2px rgba(15, 23, 42, 0.04); }
.title-with-icon { margin: 0 0 0.3rem 0; font-size: 1.25rem; color: #0f172a; display: flex; align-items: center; gap: 0.5rem; font-weight: 800; }
.header-content p { margin: 0; color: #64748b; font-size: 0.88rem; }

.strategy-summary-pills { display: flex; gap: 0.8rem; }
.pill { background: #f8fafc; border: 1px solid #cbd5e1; padding: 0.55rem 1.1rem; border-radius: 10px; display: flex; flex-direction: column; align-items: center; }
.pill.green { background: #f0fdf4; border-color: #bbf7d0; color: #166534; }
.pill.red { background: #fef2f2; border-color: #fecaca; color: #991b1b; }
.pill .count { font-weight: 800; font-size: 1.15rem; }
.pill .label { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; }

.strategy-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.4rem; }
@media (max-width: 900px) { .strategy-grid { grid-template-columns: 1fr; } }

.strategy-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 15px -2px rgba(15, 23, 42, 0.04); }
.card-title-bar { padding: 1.1rem 1.3rem; display: flex; flex-direction: column; gap: 0.2rem; border-bottom: 1px solid #e2e8f0; }
.card-title-bar.green { background: #f0fdf4; border-bottom-color: #bbf7d0; }
.card-title-bar.red { background: #fef2f2; border-bottom-color: #fecaca; }
.card-heading-flex { display: flex; align-items: center; gap: 0.5rem; }
.card-title-bar h3 { margin: 0; font-size: 1.05rem; font-weight: 800; color: #0f172a; }
.card-title-bar small { color: #64748b; font-size: 0.8rem; }

.table-wrapper { padding: 0.5rem; overflow-x: auto; }
.mini-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.mini-table th { padding: 0.6rem 0.8rem; color: #475569; font-weight: 700; border-bottom: 1px solid #e2e8f0; text-align: left; }
.mini-table td { padding: 0.75rem 0.8rem; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }

.prod-link { color: #0f172a; font-weight: 600; text-decoration: none; display: block; max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.prod-link:hover { color: #2563eb; text-decoration: underline; }
.seller-name { font-size: 0.72rem; color: #64748b; display: block; }

.sales-col { white-space: nowrap; }
.badge-growth-sm { background: #dcfce7; color: #15803d; font-size: 0.7rem; font-weight: 800; padding: 0.1rem 0.35rem; border-radius: 4px; margin-left: 0.3rem; }

.badge-price-up { display: inline-flex; align-items: center; gap: 0.2rem; background: #dcfce7; color: #15803d; font-weight: 700; padding: 0.15rem 0.45rem; border-radius: 4px; font-size: 0.78rem; }
.badge-price-down { display: inline-flex; align-items: center; gap: 0.2rem; background: #fee2e2; color: #991b1b; font-weight: 700; padding: 0.15rem 0.45rem; border-radius: 4px; font-size: 0.78rem; }
.text-green { color: #16a34a; }
.text-red { color: #dc2626; }
.empty { text-align: center; color: #94a3b8; padding: 1.5rem; }
</style>
