<template>
  <div class="glass-panel table-container animate-fade-in" style="animation-delay: 0.3s;">
    <div class="table-header">
      <div class="table-title">
        <h3>📦 Tabela de Produtos Monitorados</h3>
        <p class="subtitle">Clique nas colunas para ordenar os dados (▲ / ▼)</p>
      </div>
      <div class="table-actions">
        <button @click="exportToCSV" class="btn outline-btn ml-2" title="Baixar dados filtrados em CSV">⬇️ Exportar CSV</button>
        <input type="text" v-model="search" placeholder="Buscar por título..." class="search-input glass-panel ml-2" />
      </div>
    </div>
    
    <div class="table-scroll">
      <table class="data-table">
        <thead>
          <tr>
            <th @click="sortBy('plataforma')" class="sortable-header" title="Clique para ordenar por plataforma">
              Plataforma <span class="sort-icon">{{ sortKey === 'plataforma' ? (sortOrder === 'asc' ? '▲' : '▼') : '↕' }}</span>
            </th>
            <th @click="sortBy('categoria')" class="sortable-header" title="Clique para ordenar por categoria">
              Categoria <span class="sort-icon">{{ sortKey === 'categoria' ? (sortOrder === 'asc' ? '▲' : '▼') : '↕' }}</span>
            </th>
            <th @click="sortBy('titulo')" class="sortable-header" title="Clique para ordenar por título">
              Título Anúncio <span class="sort-icon">{{ sortKey === 'titulo' ? (sortOrder === 'asc' ? '▲' : '▼') : '↕' }}</span>
            </th>
            <th @click="sortBy('preco')" class="sortable-header" title="Clique para ordenar por preço">
              Preço Atual <span class="sort-icon">{{ sortKey === 'preco' ? (sortOrder === 'asc' ? '▲' : '▼') : '↕' }}</span>
            </th>
            <th @click="sortBy('hist_preco')" class="sortable-header" title="Clique para ordenar por preço anterior">
              Preço Ant. <span class="sort-icon">{{ sortKey === 'hist_preco' ? (sortOrder === 'asc' ? '▲' : '▼') : '↕' }}</span>
            </th>
            <th @click="sortBy('varInfo')" class="sortable-header" title="Clique para ordenar por variação R$">
              Variação <span class="sort-icon">{{ sortKey === 'varInfo' ? (sortOrder === 'asc' ? '▲' : '▼') : '↕' }}</span>
            </th>
            <th @click="sortBy('vendas_totais')" class="sortable-header" title="Clique para ordenar por vendas acumuladas">
              Vendas Totais <span class="sort-icon">{{ sortKey === 'vendas_totais' ? (sortOrder === 'asc' ? '▲' : '▼') : '↕' }}</span>
            </th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in paginatedData" :key="item.id">
            <td>
              <span :class="['badge', item.plataforma]">
                {{ item.plataforma === 'meli' ? 'Mercado Livre' : 'Shopee' }}
              </span>
            </td>
            <td>
              <span class="badge category">{{ item.categoria }}</span>
            </td>
            <td class="title-cell" :title="item.titulo">
              <span v-if="item.isNew" class="badge-new" title="Identificado recentemente">✨ Novo</span>
              {{ item.titulo }}
            </td>
            
            <!-- Preços -->
            <td class="price-cell">R$ {{ item.preco ? item.preco.toFixed(2).replace('.', ',') : '0,00' }}</td>
            
            <!-- Histórico -->
            <td class="old-price-cell text-muted">
              <span v-if="item.hist">R$ {{ item.hist.preco.toFixed(2).replace('.', ',') }}</span>
              <span v-else>-</span>
            </td>
            
            <td class="variation-cell">
              <span v-if="item.varInfo" :class="{'text-red': item.varInfo.isPositive, 'text-green': item.varInfo.isNegative}">
                {{ item.varInfo.isPositive ? '▲' : (item.varInfo.isNegative ? '▼' : '') }}
                R$ {{ Math.abs(item.varInfo.diff).toFixed(2).replace('.', ',') }}
                <small>({{ item.varInfo.perc > 0 ? '+' : '' }}{{ item.varInfo.perc.toFixed(1) }}%)</small>
              </span>
              <span v-else class="text-muted">-</span>
            </td>
            
            <td class="sales-diff-cell">
              <span class="sales-value">{{ item.vendas_totais || 0 }} un</span>
              <small v-if="item.salesDiff !== null && item.salesDiff > 0" class="text-green fw-bold block-diff">
                (+{{ item.salesDiff }} recentes)
              </small>
            </td>
            
            <td class="action-cell">
              <button @click="openModal(item)" class="action-btn" title="Ver histórico completo e métricas do anúncio">🔎 Detalhes</button>
              <a :href="item.link" target="_blank" class="link-btn" title="Abrir anúncio original na loja">Acessar ↗</a>
            </td>
          </tr>
          <tr v-if="filteredData.length === 0">
            <td colspan="8" class="empty-state">Nenhum produto encontrado com os filtros aplicados.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Paginação -->
    <div class="pagination" v-if="totalPages > 1">
      <button :disabled="currentPage === 1" @click="currentPage--" class="page-btn">Anterior</button>
      <span class="page-info">Página <strong>{{ currentPage }}</strong> de {{ totalPages }}</span>
      <button :disabled="currentPage === totalPages" @click="currentPage++" class="page-btn">Próxima</button>
    </div>

    <!-- Modal Analítico -->
    <ProductModal :product="selectedProduct" @close="selectedProduct = null" />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import ProductModal from './ProductModal.vue'

const props = defineProps({
  items: { type: Array, default: () => [] }
})

const search = ref('')
const currentPage = ref(1)
const itemsPerPage = 12
const selectedProduct = ref(null)

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

// Zera a página quando busca ou ordena
watch([search, sortKey, sortOrder], () => {
  currentPage.value = 1
})

function openModal(item) {
  selectedProduct.value = item
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

const totalPages = computed(() => Math.ceil(filteredData.value.length / itemsPerPage) || 1)

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredData.value.slice(start, end)
})

function exportToCSV() {
  if (filteredData.value.length === 0) return
  
  const headers = ['Plataforma', 'Categoria', 'Título', 'Preço Atual (R$)', 'Vendas Totais', 'Crescimento de Vendas', 'Variação Preço (R$)', 'Data Criação', 'Link']
  
  const rows = filteredData.value.map(item => {
    const varPreco = item.varInfo ? (item.varInfo.isPositive ? '+' : '-') + Math.abs(item.varInfo.diff).toFixed(2).replace('.', ',') : '0,00'
    const crescimento = item.salesDiff !== null ? `+${item.salesDiff}` : '0'
    const precoAtual = item.preco ? item.preco.toFixed(2).replace('.', ',') : '0,00'
    const criado = item.criado_em ? new Date(item.criado_em).toLocaleDateString('pt-BR') : ''
    
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

.btn { padding: 0.6rem 1rem; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s ease; border: none; font-size: 0.9rem; }
.outline-btn { background: #ffffff; border: 1px solid #cbd5e1; color: var(--text-main); }
.outline-btn:hover { background: #f1f5f9; border-color: var(--neon-blue); color: var(--neon-blue); }

.search-input { background: #ffffff; border: 1px solid #cbd5e1; color: var(--text-main); padding: 0.65rem 1rem; border-radius: 8px; width: 280px; outline: none; transition: border-color 0.3s ease; font-size: 0.9rem; }
.search-input:focus { border-color: var(--neon-blue); box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15); }

.table-scroll { overflow-x: auto; border-radius: 12px; border: 1px solid #e2e8f0; }
.data-table { width: 100%; border-collapse: collapse; text-align: left; background: #ffffff; }
.data-table th, .data-table td { padding: 0.9rem 1rem; border-bottom: 1px solid #e2e8f0; }
.data-table th { background: #f8fafc; color: #475569; font-weight: 700; text-transform: uppercase; font-size: 0.78rem; letter-spacing: 0.05em; white-space: nowrap; }

.sortable-header { cursor: pointer; user-select: none; transition: background 0.2s ease; }
.sortable-header:hover { background: #f1f5f9; color: var(--neon-blue); }
.sort-icon { display: inline-block; margin-left: 0.3rem; opacity: 0.6; font-size: 0.8rem; }
.sortable-header:hover .sort-icon { opacity: 1; }

.data-table tbody tr { transition: background 0.2s ease; }
.data-table tbody tr:hover { background: #f8fafc; }

.title-cell { max-width: 260px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 500; }
.price-cell, .old-price-cell, .variation-cell, .sales-diff-cell { white-space: nowrap; }
.price-cell { font-weight: 700; color: #0f172a; }

.text-muted { color: var(--text-muted); }
.text-red { color: #dc2626; font-weight: bold; }
.text-green { color: #16a34a; font-weight: bold; }
.sales-value { font-weight: 700; color: #0f172a; }
.block-diff { display: block; font-size: 0.75rem; }

.badge { padding: 0.3rem 0.7rem; border-radius: 99px; font-size: 0.75rem; font-weight: 600; white-space: nowrap; display: inline-block; }
.badge.meli { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
.badge.shopee { background: #ffedd5; color: #c2410c; border: 1px solid #fdba74; }
.badge.category { background: #f3e8ff; color: #6b21a8; border: 1px solid #d8b4fe; }

.badge-new { font-size: 0.65rem; background: linear-gradient(90deg, #d97706, #dc2626); color: white; padding: 0.2rem 0.5rem; border-radius: 99px; margin-right: 0.4rem; font-weight: bold; text-transform: uppercase; display: inline-block; vertical-align: middle; }

.action-cell { display: flex; gap: 0.5rem; align-items: center; }
.action-btn { display: inline-flex; align-items: center; gap: 0.3rem; padding: 0.45rem 0.8rem; background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; border-radius: 6px; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: all 0.2s ease; white-space: nowrap; }
.action-btn:hover { background: #dbeafe; border-color: #93c5fd; }
.link-btn { display: inline-flex; align-items: center; gap: 0.2rem; padding: 0.45rem 0.8rem; background: #f8fafc; color: #475569; text-decoration: none; border-radius: 6px; font-size: 0.85rem; font-weight: 600; transition: all 0.2s ease; white-space: nowrap; border: 1px solid #cbd5e1; }
.link-btn:hover { background: #f1f5f9; color: #0f172a; border-color: #94a3b8; }
.empty-state { text-align: center; padding: 3rem !important; color: var(--text-muted); font-style: italic; }

.pagination { display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 1.5rem; }
.page-btn { padding: 0.5rem 1rem; background: #ffffff; border: 1px solid #cbd5e1; color: var(--text-main); border-radius: 6px; cursor: pointer; font-weight: 600; transition: all 0.2s ease; font-size: 0.88rem; }
.page-btn:hover:not(:disabled) { background: #f1f5f9; border-color: var(--neon-blue); color: var(--neon-blue); }
.page-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.page-info { font-size: 0.9rem; color: var(--text-muted); }
</style>

