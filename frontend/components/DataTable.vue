<template>
  <div class="glass-panel table-container animate-fade-in" style="animation-delay: 0.3s;">
    <!-- Cabeçalho Principal da Tabela -->
    <div class="table-header">
      <div class="table-title">
        <h3>📦 {{ t('table.title', 'Catálogo Completo de Anúncios') }}</h3>
        <p class="subtitle">{{ t('table.subtitle', 'Filtre, pesquise e navegue pelas páginas diretamente por esta tabela.') }}</p>
      </div>
      <div class="table-actions">
        <button @click="exportToCSV" class="btn outline-btn" title="Exportar CSV">
          ⬇️ {{ t('table.export_csv', 'Exportar CSV') }}
        </button>
      </div>
    </div>

    <!-- Barra Integrada de Filtros e Busca da Tabela -->
    <div class="in-table-toolbar">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input 
          type="text" 
          v-model="search" 
          :placeholder="t('table.search_placeholder', 'Buscar por título ou loja...')" 
          class="table-search-input" 
        />
        <button v-if="search" @click="search = ''" class="clear-search-btn" title="Limpar busca">✕</button>
      </div>

      <div class="quick-filters-row">
        <!-- Pílulas de Plataforma com Ícones Oficiais -->
        <div class="platform-pills">
          <button 
            type="button"
            :class="['plat-pill', { active: localPlatform === 'Todas' }]" 
            @click="localPlatform = 'Todas'"
          >
            🌐 {{ t('filters.both', 'Todas') }}
          </button>
          <button 
            type="button"
            :class="['plat-pill meli-pill', { active: localPlatform === 'meli' }]" 
            @click="localPlatform = 'meli'"
          >
            <svg class="plat-svg" width="16" height="16" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="11" fill="#FFE600"/>
              <path d="M7 12.5L10.5 15.5L17 8.5" stroke="#2D3277" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Mercado Livre
          </button>
          <button 
            type="button"
            :class="['plat-pill shopee-pill', { active: localPlatform === 'shopee' }]" 
            @click="localPlatform = 'shopee'"
          >
            <svg class="plat-svg" width="16" height="16" viewBox="0 0 24 24" fill="none">
              <rect width="24" height="24" rx="6" fill="#EE4D2D"/>
              <path d="M7 9V7C7 4.79086 8.79086 3 11 3H13C15.2091 3 17 4.79086 17 7V9M5 9H19L17.5 21H6.5L5 9Z" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 11V15M12 15C11 15 9.5 14.2 9.5 13C9.5 11.8 12 12.2 12 11M12 15C13 15 14.5 15.8 14.5 17" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round"/>
            </svg>
            Shopee
          </button>
        </div>

        <!-- Categoria Dropdown -->
        <div class="category-select-wrap" v-if="tableCategories.length > 1">
          <select v-model="localCategory" class="table-select">
            <option value="Todas">📂 {{ t('filters.all_categories', 'Todas as Categorias') }}</option>
            <option v-for="cat in tableCategories" :key="cat" :value="cat">{{ cat }}</option>
          </select>
        </div>

        <!-- Contador de Registros -->
        <div class="table-counter-badge">
          <span>📊 <strong>{{ filteredData.length }}</strong> produtos</span>
        </div>
      </div>
    </div>
    
    <!-- Tabela Responsiva -->
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
          <tr v-for="item in paginatedData" :key="item.id">
            <td>
              <span :class="['badge', item.plataforma]">
                <svg v-if="item.plataforma === 'meli'" width="14" height="14" viewBox="0 0 24 24" fill="none" class="badge-icon">
                  <circle cx="12" cy="12" r="11" fill="#FFE600"/>
                  <path d="M7 12.5L10.5 15.5L17 8.5" stroke="#2D3277" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" class="badge-icon">
                  <rect width="24" height="24" rx="5" fill="#EE4D2D"/>
                  <path d="M7 9V7C7 4.79086 8.79086 3 11 3H13C15.2091 3 17 4.79086 17 7V9M5 9H19L17.5 21H6.5L5 9Z" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M12 11V15M12 15C11 15 9.5 14.2 9.5 13C9.5 11.8 12 12.2 12 11M12 15C13 15 14.5 15.8 14.5 17" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round"/>
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
        </tbody>
      </table>
    </div>

    <!-- Paginação Completa e Elegante -->
    <div v-if="!isLoading && filteredData.length > 0" class="pagination-footer">
      <div class="pagination-info">
        <span>Mostrando <strong>{{ (currentPage - 1) * itemsPerPage + 1 }}</strong> a <strong>{{ Math.min(currentPage * itemsPerPage, filteredData.length) }}</strong> de <strong>{{ filteredData.length }}</strong> produtos</span>
      </div>

      <div class="pagination-controls">
        <div class="items-per-page">
          <label>Por página:</label>
          <select v-model="itemsPerPage" class="per-page-select">
            <option :value="10">10</option>
            <option :value="25">25</option>
            <option :value="50">50</option>
            <option :value="100">100</option>
          </select>
        </div>

        <div class="page-buttons">
          <button 
            :disabled="currentPage === 1" 
            @click="currentPage = 1" 
            class="page-btn" 
            title="Primeira Página"
          >
            «
          </button>
          <button 
            :disabled="currentPage === 1" 
            @click="currentPage--" 
            class="page-btn" 
            title="Página Anterior"
          >
            ‹ Anterior
          </button>

          <span class="page-current">Pág. {{ currentPage }} de {{ totalPages }}</span>

          <button 
            :disabled="currentPage === totalPages" 
            @click="currentPage++" 
            class="page-btn" 
            title="Próxima Página"
          >
            Próxima ›
          </button>
          <button 
            :disabled="currentPage === totalPages" 
            @click="currentPage = totalPages" 
            class="page-btn" 
            title="Última Página"
          >
            »
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Analítico -->
    <ProductModal :product="selectedProduct" @close="selectedProduct = null" />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useAppI18n } from '~/composables/useAppI18n'
import ProductModal from './ProductModal.vue'

const { t, getRaw, locale } = useAppI18n()

const props = defineProps({
  items: { type: Array, default: () => [] },
  isLoading: { type: Boolean, default: false }
})

const emit = defineEmits(['delete-product'])

const search = ref('')
const localPlatform = ref('Todas')
const localCategory = ref('Todas')
const selectedProduct = ref(null)

// Paginação
const currentPage = ref(1)
const itemsPerPage = ref(25)

const tableCategories = computed(() => {
  const cats = new Set()
  props.items.forEach(p => {
    if (p.categoria) cats.add(p.categoria)
  })
  return Array.from(cats).sort()
})

// Ordenação interativa por coluna
const sortKey = ref('vendas_totais')
const sortOrder = ref('desc')

function sortBy(key) {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'desc'
  }
}

// Zera a página quando busca ou filtra
watch([search, localPlatform, localCategory, sortKey, sortOrder, itemsPerPage], () => {
  currentPage.value = 1
})

function openModal(item) {
  selectedProduct.value = item
}

function confirmDelete(item) {
  const isHidden = item._isHidden
  if (isHidden) {
    emit('delete-product', item)
  } else {
    const msg = t('table.confirm_hide', 'Deseja silenciar/ocultar o anúncio:\n\n"{title}"\n\nVocê pode desfazer isso depois.').replace('{title}', item.titulo)
    if (confirm(msg)) {
      emit('delete-product', item)
    }
  }
}

const filteredData = computed(() => {
  let result = props.items
  
  if (localPlatform.value !== 'Todas') {
    result = result.filter(item => item.plataforma === localPlatform.value)
  }

  if (localCategory.value !== 'Todas') {
    result = result.filter(item => item.categoria === localCategory.value)
  }

  if (search.value) {
    const lowerSearch = search.value.toLowerCase().trim()
    result = result.filter(item => 
      (item.titulo && item.titulo.toLowerCase().includes(lowerSearch)) || 
      (item.vendedor && item.vendedor.toLowerCase().includes(lowerSearch))
    )
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

const totalPages = computed(() => {
  return Math.ceil(filteredData.value.length / itemsPerPage.value) || 1
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  return filteredData.value.slice(start, start + itemsPerPage.value)
})

function exportToCSV() {
  if (filteredData.value.length === 0) return
  
  const headers = getRaw('table.csv_headers') || ['Plataforma', 'Categoria', 'Título', 'Preço Atual (R$)', 'Vendas Totais', 'Crescimento de Vendas', 'Variação Preço (R$)', 'Data Criação', 'Link']
  
  const rows = filteredData.value.map(item => {
    const varPreco = item.varInfo ? (item.varInfo.isPositive ? '+' : '-') + Math.abs(item.varInfo.diff).toFixed(2).replace('.', ',') : '0,00'
    const crescimento = item.salesDiff !== null ? `+${item.salesDiff}` : '0'
    const precoAtual = item.preco ? item.preco.toFixed(2).replace('.', ',') : '0,00'
    const criado = item.criado_em ? new Date(item.criado_em).toLocaleDateString(locale.value === 'pt' ? 'pt-BR' : 'en-US') : ''
    
    return [
      item.plataforma === 'meli' ? 'Mercado Livre' : 'Shopee',
      `"${(item.categoria || '').replace(/"/g, '""')}"`,
      `"${(item.titulo || '').replace(/"/g, '""')}"`,
      precoAtual,
      item.vendas_totais || 0,
      crescimento,
      varPreco,
      criado,
      `"${item.link || ''}"`
    ].join(';')
  })
  
  const csvContent = '\uFEFF' + [headers.join(';'), ...rows].join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', `biscuit_produtos_${new Date().toISOString().split('T')[0]}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<style scoped>
.table-container {
  padding: 1.5rem;
  margin-bottom: 2rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.2rem;
}

.table-title h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 800;
  color: #0f172a;
}

.subtitle {
  margin: 0.2rem 0 0;
  font-size: 0.85rem;
  color: #64748b;
}

.in-table-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
  padding: 0.9rem 1.1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  margin-bottom: 1.2rem;
}

.search-box {
  display: flex;
  align-items: center;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 0.4rem 0.8rem;
  min-width: 280px;
  flex: 1;
}

.search-icon {
  margin-right: 0.4rem;
  font-size: 0.9rem;
}

.table-search-input {
  border: none;
  background: none;
  outline: none;
  width: 100%;
  font-size: 0.88rem;
  color: #0f172a;
}

.clear-search-btn {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  font-size: 0.9rem;
  padding: 0 0.2rem;
}

.clear-search-btn:hover {
  color: #0f172a;
}

.quick-filters-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.platform-pills {
  display: flex;
  background: #e2e8f0;
  padding: 0.25rem;
  border-radius: 8px;
  gap: 0.25rem;
}

.plat-pill {
  border: none;
  background: none;
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 700;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.plat-svg {
  display: inline-block;
  flex-shrink: 0;
}

.plat-pill:hover {
  color: #0f172a;
}

.plat-pill.active {
  background: #ffffff;
  color: #0f172a;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}

.plat-pill.meli-pill.active {
  color: #854d0e;
  border: 1px solid #fde047;
}

.plat-pill.shopee-pill.active {
  color: #9a3412;
  border: 1px solid #fdba74;
}

.table-select {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #334155;
  outline: none;
}

.table-counter-badge {
  font-size: 0.82rem;
  color: #2563eb;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  white-space: nowrap;
}

.table-scroll {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}

.data-table th {
  background: #f8fafc;
  padding: 0.75rem 0.9rem;
  text-align: left;
  font-weight: 700;
  color: #475569;
  border-bottom: 2px solid #e2e8f0;
  white-space: nowrap;
}

.sortable-header {
  cursor: pointer;
  user-select: none;
}

.sortable-header:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.data-table td {
  padding: 0.75rem 0.9rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.data-table tr:hover td {
  background: #f8fafc;
}

.clickable-title {
  cursor: pointer;
}

.title-text {
  font-weight: 600;
  color: #1e293b;
}

.title-text:hover {
  color: #2563eb;
}

.seller-subtext {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.15rem;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
}

.badge.meli {
  background: #fef9c3;
  color: #854d0e;
  border: 1px solid #fde047;
}

.badge.shopee {
  background: #ffedd5;
  color: #9a3412;
  border: 1px solid #fdba74;
}

.badge.category {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
}

.badge-new {
  font-size: 0.68rem;
  background: #dcfce7;
  color: #15803d;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-weight: 800;
  margin-right: 0.4rem;
}

.price-cell {
  font-weight: 700;
  color: #0f172a;
}

.badge-price-up {
  color: #15803d;
  font-weight: 700;
}

.badge-price-down {
  color: #b91c1c;
  font-weight: 700;
}

.badge-growth {
  background: #dcfce7;
  color: #15803d;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 800;
  margin-left: 0.3rem;
}

.action-btns-wrap {
  display: flex;
  gap: 0.3rem;
}

.icon-btn {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 0.3rem 0.5rem;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.icon-btn:hover {
  background: #e2e8f0;
  transform: translateY(-1px);
}

.pagination-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  padding-top: 1.2rem;
  margin-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.pagination-info {
  font-size: 0.85rem;
  color: #64748b;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 1.2rem;
  flex-wrap: wrap;
}

.items-per-page {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.82rem;
  color: #475569;
}

.per-page-select {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #0f172a;
}

.page-buttons {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.page-btn {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 700;
  color: #334155;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-btn:hover:not(:disabled) {
  background: #eff6ff;
  border-color: #3b82f6;
  color: #1d4ed8;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-current {
  font-size: 0.85rem;
  font-weight: 700;
  color: #0f172a;
  padding: 0 0.4rem;
}
</style>
