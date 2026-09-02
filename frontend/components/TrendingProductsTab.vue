<template>
  <div class="trending-container">
    <!-- Header descritivo da aba -->
    <div class="glass-panel trending-header animate-fade-in">
      <div class="header-content">
        <h2 class="title-with-icon">
          <Flame :size="22" class="text-amber-500" />
          <span>{{ t('trending.title', 'Ranking de Aceleração & Tendências de Vendas') }}</span>
        </h2>
        <p v-html="t('trending.subtitle', 'Produtos que registraram o maior volume de <strong>novas vendas</strong> comparando o histórico de coletas.')"></p>
      </div>

      <!-- Métricas Resumidas -->
      <div class="trending-stats">
        <div class="stat-pill highlight">
          <span class="label">{{ t('trending.top_accelerator', 'Top Acelerador:') }}</span>
          <strong>{{ topTrendingProduct ? topTrendingProduct.titulo.substring(0, 25) + '...' : t('trending.na', 'N/A') }}</strong>
          <span class="value" v-if="topTrendingProduct">+{{ topTrendingProduct.deltaVendas }} {{ t('trending.units', 'un.') }}</span>
        </div>
        <div class="stat-pill">
          <span class="label">{{ t('trending.total_new_sales', 'Total Novas Vendas:') }}</span>
          <strong class="text-green">+{{ totalNewSales }} {{ t('trending.units', 'un.') }}</strong>
        </div>
      </div>
    </div>

    <!-- Tabela dos Produtos em Alta -->
    <div class="glass-panel trending-table-card animate-fade-in" style="animation-delay: 0.1s;">
      <transition name="slide-up" mode="out-in">
        <div v-if="isLoading" class="table-responsive p-4">
          <div v-for="i in 5" :key="'skel-trend'+i" class="skeleton skeleton-text mb-3" style="height: 48px; border-radius: 8px;"></div>
        </div>
        <div v-else class="table-responsive">
          <table class="trending-table">
            <thead>
              <tr>
                <th>{{ t('trending.col_position', 'Posição') }}</th>
                <th>{{ t('trending.col_platform_store', 'Plataforma / Loja') }}</th>
                <th>{{ t('trending.col_product', 'Produto') }}</th>
                <th class="text-right">{{ t('trending.col_current_price', 'Preço Atual') }}</th>
                <th class="text-right">{{ t('trending.col_total_sales', 'Vendas Totais') }}</th>
                <th class="text-center">{{ t('trending.col_velocity', 'Novas Vendas no Período') }}</th>
                <th class="text-right">{{ t('trending.col_action', 'Ação') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, idx) in paginatedTrendingList" :key="item.id">
                <!-- Posição Real Global -->
                <td class="text-center font-bold">
                  <span :class="['rank-badge', getRankClass((currentPage - 1) * itemsPerPage + idx + 1)]">
                    #{{ (currentPage - 1) * itemsPerPage + idx + 1 }}
                  </span>
                </td>

                <!-- Plataforma / Loja -->
                <td>
                  <div class="store-cell">
                    <span :class="['platform-badge', item.plataforma]">
                      {{ item.plataforma === 'meli' ? 'Mercado Livre' : 'Shopee' }}
                    </span>
                    <small class="store-name">{{ item.vendedor || t('trending.unknown_seller', 'Vendedor Desconhecido') }}</small>
                  </div>
                </td>

                <!-- Título do Produto -->
                <td>
                  <a :href="item.link" target="_blank" class="product-title-link" :title="t('trending.open_ad_title', 'Abrir produto no marketplace')">
                    {{ item.titulo }}
                  </a>
                </td>

                <!-- Preço Atual -->
                <td class="text-right font-medium">
                  R$ {{ item.preco.toFixed(2).replace('.', ',') }}
                </td>

                <!-- Vendas Totais -->
                <td class="text-right font-medium">
                  {{ (item.vendas_totais || 0).toLocaleString(locale === 'pt' ? 'pt-BR' : 'en-US') }} {{ t('trending.units', 'un.') }}
                </td>

                <!-- Novas Vendas (Delta) -->
                <td class="text-center">
                  <span class="delta-badge">+{{ item.deltaVendas.toLocaleString(locale === 'pt' ? 'pt-BR' : 'en-US') }} {{ t('trending.units', 'un.') }}</span>
                </td>

                <!-- Ação -->
                <td class="text-center">
                  <a 
                    :href="getAdLink(item)" 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    class="icon-btn link-btn"
                    :title="t('trending.view_ad', 'Abrir Produto no Marketplace')"
                  >
                    <ExternalLink :size="14" />
                  </a>
                </td>
              </tr>

              <tr v-if="trendingList.length === 0">
                <td colspan="7" class="empty-state">
                  <div class="empty-flex">
                    <Inbox :size="24" class="text-slate-400" />
                    <span>{{ t('trending.empty_state', 'Nenhum produto apresentou novas vendas no período selecionado.') }}</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </transition>

      <!-- Paginação de 15 itens por página -->
      <div v-if="!isLoading && trendingList.length > 0" class="pagination-footer">
        <div class="pagination-info">
          <span>Mostrando <strong>{{ (currentPage - 1) * itemsPerPage + 1 }}</strong> a <strong>{{ Math.min(currentPage * itemsPerPage, trendingList.length) }}</strong> de <strong>{{ trendingList.length }}</strong> produtos em alta</span>
        </div>

        <div class="pagination-controls" v-if="totalPages > 1">
          <button 
            :disabled="currentPage === 1" 
            @click="currentPage--" 
            class="page-btn" 
            title="Página Anterior"
          >
            <ChevronLeft :size="15" />
            <span>Anterior</span>
          </button>

          <span class="page-current">Pág. {{ currentPage }} de {{ totalPages }}</span>

          <button 
            :disabled="currentPage === totalPages" 
            @click="currentPage++" 
            class="page-btn" 
            title="Próxima Página"
          >
            <span>Próxima</span>
            <ChevronRight :size="15" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Flame, ExternalLink, Inbox, ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { useAppI18n } from '~/composables/useAppI18n'

const { t, locale } = useAppI18n()

const props = defineProps({
  products: {
    type: Array,
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

const currentPage = ref(1)
const itemsPerPage = ref(15)

// Processa a lista calculando o delta de vendas reais (apenas produtos com histórico real >= 2 coletas)
const trendingList = computed(() => {
  const list = []

  for (const item of props.products) {
    const vendasHoje = item.vendas_totais || 0
    let delta = 0
    let vendasAnterior = 0

    if (item.salesDiff !== null && item.salesDiff !== undefined) {
      delta = item.salesDiff
      vendasAnterior = item.hist ? item.hist.vendas_totais : Math.max(0, vendasHoje - delta)
    } else if (item.historico_coletas && item.historico_coletas.length >= 2) {
      const historicoAnterior = item.historico_coletas[item.historico_coletas.length - 1]
      vendasAnterior = historicoAnterior.vendas_totais || 0
      delta = Math.max(0, vendasHoje - vendasAnterior)
    }

    // Apenas produtos que tiveram aumento real verificado
    if (delta > 0) {
      list.push({
        ...item,
        deltaVendas: delta,
        vendasAnterior
      })
    }
  }

  return list.sort((a, b) => b.deltaVendas - a.deltaVendas)
})

const totalPages = computed(() => Math.ceil(trendingList.value.length / itemsPerPage.value) || 1)

watch(trendingList, () => {
  if (currentPage.value > totalPages.value) {
    currentPage.value = 1
  }
})

const paginatedTrendingList = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  return trendingList.value.slice(start, start + itemsPerPage.value)
})

const topTrendingProduct = computed(() => trendingList.value.length > 0 ? trendingList.value[0] : null)
const totalNewSales = computed(() => trendingList.value.reduce((acc, curr) => acc + curr.deltaVendas, 0))

function getRankClass(rank) {
  if (rank === 1) return 'rank-1'
  if (rank === 2) return 'rank-2'
  if (rank === 3) return 'rank-3'
  return 'rank-other'
}

function getAdLink(item) {
  if (item && item.link && typeof item.link === 'string' && item.link.startsWith('http')) {
    return item.link
  }
  const query = (item && item.titulo) || 'produto'
  if (item && item.plataforma === 'shopee') {
    return `https://shopee.com.br/search?keyword=${encodeURIComponent(query)}`
  }
  return `https://lista.mercadolivre.com.br/${encodeURIComponent(query)}`
}
</script>

<style scoped>
.trending-container { display: flex; flex-direction: column; gap: 1.4rem; margin-bottom: 2rem; }
.trending-header { padding: 1.35rem 1.5rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; box-shadow: 0 4px 15px -2px rgba(15, 23, 42, 0.04); }
.title-with-icon { margin: 0 0 0.3rem 0; font-size: 1.25rem; color: #0f172a; display: flex; align-items: center; gap: 0.5rem; font-weight: 800; }
.header-content p { margin: 0; color: #64748b; font-size: 0.88rem; }

.trending-stats { display: flex; gap: 0.8rem; }
.stat-pill { background: #f8fafc; border: 1px solid #cbd5e1; padding: 0.55rem 1rem; border-radius: 10px; display: flex; flex-direction: column; gap: 0.1rem; }
.stat-pill.highlight { background: #eff6ff; border-color: #bfdbfe; }
.stat-pill .label { font-size: 0.72rem; color: #64748b; font-weight: 700; text-transform: uppercase; }
.stat-pill .value { color: #2563eb; font-weight: 800; font-size: 0.95rem; }
.text-green { color: #16a34a; font-weight: 800; }

.trending-table-card { padding: 1.2rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; box-shadow: 0 4px 15px -2px rgba(15, 23, 42, 0.04); }
.table-responsive { overflow-x: auto; }
.trending-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.88rem; }
.trending-table th { background: #f8fafc; color: #475569; padding: 0.75rem 0.9rem; font-weight: 700; border-bottom: 2px solid #e2e8f0; }
.trending-table td { padding: 0.8rem 0.9rem; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }

.rank-badge { font-weight: 800; font-size: 0.88rem; color: #475569; background: #f1f5f9; padding: 0.2rem 0.5rem; border-radius: 6px; }
.rank-1 { color: #b45309; background: #fef3c7; border: 1px solid #fde68a; }
.rank-2 { color: #475569; background: #e2e8f0; border: 1px solid #cbd5e1; }
.rank-3 { color: #9a3412; background: #ffedd5; border: 1px solid #fed7aa; }
.store-cell { display: flex; flex-direction: column; gap: 0.2rem; min-width: 140px; }
.platform-badge { font-size: 0.7rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 4px; display: inline-block; width: max-content; }
.platform-badge.meli { background: #fff59d; color: #574c00; }
.platform-badge.shopee { background: #ffccbc; color: #bf360c; }
.store-name { color: #64748b; font-size: 0.78rem; }

.product-title-link { color: #0f172a; font-weight: 600; text-decoration: none; transition: color 0.2s ease; display: block; max-width: 380px; }
.product-title-link:hover { color: #2563eb; text-decoration: underline; }

.delta-badge { background: #dcfce7; color: #15803d; font-weight: 800; padding: 0.25rem 0.65rem; border-radius: 99px; font-size: 0.82rem; min-width: 68px; text-align: center; display: inline-block; white-space: nowrap; }

.empty-state { text-align: center; padding: 2.5rem; color: #64748b; font-size: 0.95rem; }
.empty-flex { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.6rem; }

.icon-btn.link-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  border: 1px solid #cbd5e1;
  background: #f8fafc;
  color: #475569;
}
.icon-btn.link-btn:hover {
  background: #eff6ff;
  color: #2563eb;
  border-color: #93c5fd;
  transform: translateY(-1px);
}

.pagination-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  padding-top: 1rem;
  margin-top: 0.8rem;
  border-top: 1px solid #e2e8f0;
}

.pagination-info {
  font-size: 0.84rem;
  color: #64748b;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.page-btn {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 7px;
  padding: 0.35rem 0.7rem;
  font-size: 0.82rem;
  font-weight: 700;
  color: #334155;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  transition: all 0.2s ease;
}

.page-btn:hover:not(:disabled) {
  background: #f1f5f9;
  border-color: #94a3b8;
  color: #0f172a;
}

.page-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.page-current {
  font-size: 0.82rem;
  font-weight: 700;
  color: #475569;
  padding: 0 0.4rem;
}
</style>
