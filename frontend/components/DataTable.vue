<template>
  <div class="glass-panel table-container animate-fade-in" style="animation-delay: 0.3s;">
    <div class="table-header">
      <div class="table-title">
        <h3>📦 {{ t('table.title', 'Tabela de Produtos Monitorados') }}</h3>
        <p class="subtitle">{{ t('table.subtitle', 'Clique nas colunas para ordenar os dados (▲ / ▼)') }}</p>
      </div>
      <div class="table-actions">
        <button @click="exportToCSV" class="btn outline-btn ml-2" title="Export CSV">{{ t('table.export_csv', '⬇️ Exportar CSV') }}</button>
        <input type="text" v-model="search" :placeholder="t('table.search_placeholder', 'Buscar por título...')" class="search-input glass-panel ml-2" />
      </div>
    </div>
    
    <div class="table-scroll">
      <table class="data-table">
        <thead>
          <tr>
            <th @click="sortBy('plataforma')" class="sortable-header">
              {{ t('table.col_platform', 'Plataforma') }} <span class="sort-icon">{{ sortKey === 'plataforma' ? (sortOrder === 'asc' ? '▲' : '▼') : '↕' }}</span>
            </th>
            <th @click="sortBy('categoria')" class="sortable-header">
              {{ t('table.col_category', 'Categoria') }} <span class="sort-icon">{{ sortKey === 'categoria' ? (sortOrder === 'asc' ? '▲' : '▼') : '↕' }}</span>
            </th>
            <th @click="sortBy('titulo')" class="sortable-header">
              {{ t('table.col_product', 'Título Anúncio') }} <span class="sort-icon">{{ sortKey === 'titulo' ? (sortOrder === 'asc' ? '▲' : '▼') : '↕' }}</span>
            </th>
            <th @click="sortBy('preco')" class="sortable-header">
              {{ t('table.col_price', 'Preço Atual') }} <span class="sort-icon">{{ sortKey === 'preco' ? (sortOrder === 'asc' ? '▲' : '▼') : '↕' }}</span>
            </th>
            <th @click="sortBy('hist_preco')" class="sortable-header">
              {{ t('table.col_old_price', 'Preço Ant.') }} <span class="sort-icon">{{ sortKey === 'hist_preco' ? (sortOrder === 'asc' ? '▲' : '▼') : '↕' }}</span>
            </th>
            <th @click="sortBy('varInfo')" class="sortable-header">
              {{ t('table.col_variation', 'Variação') }} <span class="sort-icon">{{ sortKey === 'varInfo' ? (sortOrder === 'asc' ? '▲' : '▼') : '↕' }}</span>
            </th>
            <th @click="sortBy('vendas_totais')" class="sortable-header">
              {{ t('table.col_sales', 'Vendas Totais') }} <span class="sort-icon">{{ sortKey === 'vendas_totais' ? (sortOrder === 'asc' ? '▲' : '▼') : '↕' }}</span>
            </th>
            <th class="action-th">{{ t('table.col_actions', 'Ações') }}</th>
          </tr>
        </thead>
        <tbody v-if="isLoading">
          <tr v-for="i in 10" :key="'skel-dt'+i">
            <td colspan="8"><div class="skeleton skeleton-text" style="height: 36px"></div></td>
          </tr>
        </tbody>
        <tbody v-else>
          <tr v-for="item in visibleData" :key="item.id">
            <td>
              <span :class="['badge', item.plataforma]">
                <svg v-if="item.plataforma === 'meli'" width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="badge-icon">
                  <rect width="24" height="24" rx="12" fill="#FFE600"/>
                  <path d="M7 11.5L10 14.5L17 7.5" stroke="#2D3277" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="badge-icon">
                  <path d="M6 8V6C6 4.34315 7.34315 3 9 3H15C16.6569 3 18 4.34315 18 6V8M3 8H21L19.5 21H4.5L3 8Z" stroke="#EE4D2D" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M12 11V15M12 15C11 15 9.5 14.2 9.5 13C9.5 11.8 12 12.2 12 11M12 15C13 15 14.5 15.8 14.5 17" stroke="#EE4D2D" stroke-width="1.8" stroke-linecap="round"/>
                </svg>
                {{ item.plataforma === 'meli' ? 'Mercado Livre' : 'Shopee' }}
              </span>
            </td>
            <td>
              <span class="badge category">{{ item.categoria }}</span>
            </td>
            <td class="title-cell clickable-title" :title="item.titulo" @click="openModal(item)">
              <span v-if="item.isNew" class="badge-new" :title="t('table.new_badge_title', 'Identificado recentemente')">{{ t('table.new_badge', '✨ Novo') }}</span>
              <div class="title-text">{{ item.titulo }}</div>
              <small v-if="item.vendedor" class="seller-subtext" :title="'Vendedor / Loja: ' + item.vendedor">
                {{ item.vendedor.startsWith('Loja em') ? '📍' : '🏪' }} {{ item.vendedor }}
              </small>
            </td>
            
            <!-- Preços -->
            <td class="price-cell">R$ {{ item.preco ? item.preco.toFixed(2).replace('.', ',') : '0,00' }}</td>
            
            <!-- Histórico -->
            <td class="old-price-cell text-muted">
              <span v-if="item.hist">R$ {{ item.hist.preco.toFixed(2).replace('.', ',') }}</span>
              <span v-else class="text-muted">-</span>
            </td>
            
            <td class="variation-cell">
              <span v-if="item.varInfo" :class="{'badge-price-up': item.varInfo.isPositive, 'badge-price-down': item.varInfo.isNegative}">
                {{ item.varInfo.isPositive ? '▲' : '▼' }}
                R$ {{ Math.abs(item.varInfo.diff).toFixed(2).replace('.', ',') }}
                <small>({{ item.varInfo.perc > 0 ? '+' : '' }}{{ item.varInfo.perc.toFixed(1) }}%)</small>
              </span>
              <span v-else class="text-muted">-</span>
            </td>
            
            <td class="sales-diff-cell">
              <span class="sales-value">{{ item.vendas_totais || 0 }}</span>
              <span v-if="item.salesDiff !== null && item.salesDiff > 0" class="badge-growth" :title="t('table.sales_growth_title', 'Vendas novas registradas no período selecionado')">
                +{{ item.salesDiff }}
              </span>
              <span v-else-if="item.salesDiff === 0" class="badge-stable" :title="t('table.sales_stable_title', 'Sem novas vendas no período')">
                0
              </span>
            </td>
            
            <td class="action-cell">
              <div class="action-btns-wrap">
                <button @click="openModal(item)" class="icon-btn action-btn-icon" :title="t('table.view_details_title', 'Ver detalhes completos do anúncio')">🔎</button>
                <a :href="item.link" target="_blank" class="icon-btn link-btn-icon" :title="t('table.open_store_title', 'Abrir anúncio original na loja')">↗</a>
                <button @click="confirmDelete(item)" class="icon-btn delete-btn-icon" :title="item._isHidden ? t('table.restore_ad_title', 'Restaurar produto') : t('table.silence_ad_title', 'Ocultar / Silenciar este anúncio')">
                  {{ item._isHidden ? '👁️' : '🚫' }}
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="filteredData.length === 0 && !isLoading">
            <td colspan="8" class="empty-state">{{ t('table.empty', 'Nenhum produto encontrado com os filtros aplicados.') }}</td>
          </tr>
          <tr v-if="visibleLimit < filteredData.length">
            <td colspan="8" class="loading-more-row">
              <div ref="loadMoreTrigger" class="load-more-trigger">
                {{ t('table.loading_more', 'Carregando mais produtos...') }}
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Paginação removida em favor de Infinite Scrolling -->
    <div v-if="!isLoading && visibleLimit < filteredData.length" class="text-center mt-3 mb-2">
      <button @click="loadMore" class="btn outline-btn">{{ t('table.btn_load_more', 'Carregar mais produtos ↓') }}</button>
    </div>

    <!-- Modal Analítico -->
    <ProductModal :product="selectedProduct" @close="selectedProduct = null" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useAppI18n } from '~/composables/useAppI18n'
import ProductModal from './ProductModal.vue'

const { t, getRaw, locale } = useAppI18n()

const props = defineProps({
  items: { type: Array, default: () => [] },
  isLoading: { type: Boolean, default: false }
})

const emit = defineEmits(['delete-product'])

const search = ref('')
const visibleLimit = ref(50) // Começa com 50 itens
const selectedProduct = ref(null)
const loadMoreTrigger = ref(null)

let observer = null

onMounted(() => {
  observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && visibleLimit.value < filteredData.value.length) {
      loadMore()
    }
  }, { rootMargin: '100px' })
})

watch(loadMoreTrigger, (el) => {
  if (observer) {
    observer.disconnect()
    if (el) observer.observe(el)
  }
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})

// Ordenação interativa por coluna
const sortKey = ref('vendas_totais')
const sortOrder = ref('desc') // 'asc' ou 'desc'

function sortBy(key) {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'desc' // Padrão desc para métricas
  }
}

// Zera o limite visível quando busca ou ordena
watch([search, sortKey, sortOrder], () => {
  visibleLimit.value = 50
})

function openModal(item) {
  selectedProduct.value = item
}

function confirmDelete(item) {
  const isHidden = item._isHidden
  if (isHidden) {
    emit('delete-product', item) // A função pai deve cuidar do toggle
  } else {
    const msg = t('table.confirm_hide', 'Deseja silenciar/ocultar o anúncio:\n\n"{title}"\n\nVocê pode desfazer isso depois.').replace('{title}', item.titulo)
    if (confirm(msg)) {
      emit('delete-product', item)
    }
  }
}

const filteredData = computed(() => {
  let result = props.items
  
  if (search.value) {
    const lowerSearch = search.value.toLowerCase()
    result = result.filter(item => item.titulo.toLowerCase().includes(lowerSearch))
  }
  
  return [...result].sort((a, b) => {
    let valA = a[sortKey.value]
    let valB = b[sortKey.value]
    
    if (sortKey.value === 'hist_preco') {
      valA = a.hist ? a.hist.preco : 0
      valB = b.hist ? b.hist.preco : 0
    } else if (sortKey.value === 'varInfo') {
      valA = a.varInfo ? a.varInfo.diff : 0
      valB = b.varInfo ? b.varInfo.diff : 0
    }
    
    if (valA === undefined || valA === null) valA = ''
    if (valB === undefined || valB === null) valB = ''
    
    if (typeof valA === 'string') {
      const cmp = valA.localeCompare(valB)
      return sortOrder.value === 'asc' ? cmp : -cmp
    }
    
    return sortOrder.value === 'asc' ? valA - valB : valB - valA
  })
})

const visibleData = computed(() => {
  return filteredData.value.slice(0, visibleLimit.value)
})

function loadMore() {
  visibleLimit.value += 50
}

function exportToCSV() {
  if (filteredData.value.length === 0) return
  
  const headers = getRaw('table.csv_headers') || ['Plataforma', 'Categoria', 'Título', 'Preço Atual (R$)', 'Vendas Totais', 'Crescimento de Vendas', 'Variação Preço (R$)', 'Data Criação', 'Link']
  
  const rows = filteredData.value.map(item => {
    const varPreco = item.varInfo ? (item.varInfo.isPositive ? '+' : '-') + Math.abs(item.varInfo.diff).toFixed(2).replace('.', ',') : '0,00'
    const crescimento = item.salesDiff !== null ? `+${item.salesDiff}` : '0'
    const precoAtual = item.preco ? item.preco.toFixed(2).replace('.', ',') : '0,00'
    const criado = item.criado_em ? new Date(item.criado_em).toLocaleDateString(locale.value === 'pt' ? 'pt-BR' : 'en-US') : ''
    
    return [
      item.plataforma,
      item.categoria,
      `"${item.titulo.replace(/"/g, '""')}"`,
      precoAtual,
      item.vendas_totais || 0,
      crescimento,
      varPreco,
      criado,
      `"${item.link}"`
    ].join(';')
  })
  
  const csvContent = [headers.join(';'), ...rows].join('\n')
  const blob = new Blob(["\uFEFF" + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement("a")
  const url = URL.createObjectURL(blob)
  
  link.setAttribute("href", url)
  link.setAttribute("download", `relatorio_produtos_${new Date().toISOString().split('T')[0]}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<style scoped>
.table-container { padding: 1.5rem; margin-bottom: 2rem; }
.table-header { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem; }
.table-title h3 { font-size: 1.25rem; color: var(--text-main); margin: 0 0 0.2rem 0; }
.subtitle { color: var(--text-muted); font-size: 0.85rem; margin: 0; }
.table-actions { display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; }
.loading-more-row { text-align: center; color: var(--text-muted); font-size: 0.9rem; padding: 1.5rem 0 !important; }
.load-more-trigger { width: 100%; display: flex; justify-content: center; align-items: center; height: 30px; }

.btn { padding: 0.6rem 1rem; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s ease; border: none; font-size: 0.9rem; }
.outline-btn { background: #ffffff; border: 1px solid #cbd5e1; color: var(--text-main); }
.outline-btn:hover { background: #f1f5f9; border-color: var(--neon-blue); color: var(--neon-blue); }

.search-input { background: #ffffff; border: 1px solid #cbd5e1; color: var(--text-main); padding: 0.65rem 1rem; border-radius: 8px; width: 280px; outline: none; transition: border-color 0.3s ease; font-size: 0.9rem; }
.search-input:focus { border-color: var(--neon-blue); box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15); }

.table-scroll {
  overflow-x: auto;
  overflow-y: auto;
  max-height: 580px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.02);
}
.data-table { width: 100%; border-collapse: collapse; text-align: left; background: #ffffff; }
.data-table th, .data-table td { padding: 0.65rem 0.75rem; border-bottom: 1px solid #e2e8f0; vertical-align: middle; }
.data-table th {
  position: sticky;
  top: 0;
  z-index: 10;
  background: #f8fafc;
  color: #475569;
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.04em;
  white-space: nowrap;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}

.sortable-header { cursor: pointer; user-select: none; transition: background 0.2s ease; }
.sortable-header:hover { background: #f1f5f9; color: var(--neon-blue); }
.sort-icon { display: inline-block; margin-left: 0.3rem; opacity: 0.6; font-size: 0.8rem; }
.sortable-header:hover .sort-icon { opacity: 1; }

.data-table tbody tr { transition: background 0.2s ease; }
.data-table tbody tr:hover { background: #f8fafc; }

.title-cell { max-width: 240px; font-weight: 500; }
.clickable-title { cursor: pointer; transition: color 0.2s ease; }
.clickable-title:hover .title-text { color: #2563eb; text-decoration: underline; }
.title-text { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 0.88rem; }
.seller-subtext { display: block; font-size: 0.72rem; color: #64748b; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 0.1rem; }

.price-cell, .old-price-cell, .variation-cell, .sales-diff-cell { white-space: nowrap; font-size: 0.85rem; }
.price-cell { font-weight: 700; color: #0f172a; }

.text-muted { color: var(--text-muted); }
.text-red { color: #dc2626; font-weight: bold; }
.text-green { color: #16a34a; font-weight: bold; }
.sales-value { font-weight: 700; color: #0f172a; margin-right: 0.3rem; }

.badge-growth { display: inline-block; padding: 0.12rem 0.4rem; border-radius: 99px; font-size: 0.7rem; font-weight: 800; background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
.badge-stable { display: inline-block; padding: 0.12rem 0.4rem; border-radius: 99px; font-size: 0.7rem; font-weight: 600; background: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0; }
.badge-price-up { display: inline-block; padding: 0.12rem 0.4rem; border-radius: 6px; font-size: 0.72rem; font-weight: 700; background: #fef2f2; color: #dc2626; border: 1px solid #fca5a5; }
.badge-price-down { display: inline-block; padding: 0.12rem 0.4rem; border-radius: 6px; font-size: 0.72rem; font-weight: 700; background: #f0fdf4; color: #166534; border: 1px solid #86efac; }

.badge { padding: 0.25rem 0.55rem; border-radius: 99px; font-size: 0.72rem; font-weight: 600; white-space: nowrap; display: inline-flex; align-items: center; gap: 0.3rem; }
.badge.meli { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
.badge.shopee { background: #ffedd5; color: #c2410c; border: 1px solid #fdba74; }
.badge.category { background: #f3e8ff; color: #6b21a8; border: 1px solid #d8b4fe; }
.badge-icon { vertical-align: middle; flex-shrink: 0; }

.badge-new { font-size: 0.62rem; background: linear-gradient(90deg, #d97706, #dc2626); color: white; padding: 0.15rem 0.4rem; border-radius: 99px; margin-right: 0.3rem; font-weight: bold; text-transform: uppercase; display: inline-block; vertical-align: middle; }

.action-th { text-align: center; width: 110px; }
.action-cell { text-align: center; width: 110px; }
.action-btns-wrap { display: flex; gap: 0.35rem; justify-content: center; align-items: center; }
.icon-btn { display: inline-flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: 6px; font-size: 0.88rem; cursor: pointer; transition: all 0.2s ease; text-decoration: none; border: 1px solid #cbd5e1; }
.action-btn-icon { background: #eff6ff; color: #2563eb; border-color: #bfdbfe; }
.action-btn-icon:hover { background: #dbeafe; border-color: #93c5fd; transform: translateY(-1px); }
.link-btn-icon { background: #f8fafc; color: #475569; border-color: #cbd5e1; font-weight: bold; }
.link-btn-icon:hover { background: #f1f5f9; color: #0f172a; border-color: #94a3b8; transform: translateY(-1px); }
.delete-btn-icon { background: #fef2f2; color: #dc2626; border-color: #fca5a5; font-size: 0.82rem; }
.delete-btn-icon:hover { background: #fee2e2; border-color: #f87171; transform: translateY(-1px); }
.empty-state { text-align: center; padding: 3rem !important; color: var(--text-muted); font-style: italic; }
</style>

