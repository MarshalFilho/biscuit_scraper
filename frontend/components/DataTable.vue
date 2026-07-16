<template>
  <div class="glass-panel table-container animate-fade-in" style="animation-delay: 0.3s;">
    <div class="table-header">
      <h3>Base de Dados de Produtos</h3>
      <div class="table-actions">
        <select v-model="periodoComparacao" class="glass-input inline-select">
          <option value="last">Comparar com: Último Registro</option>
          <option value="7">Comparar com: 1 Semana atrás</option>
          <option value="15">Comparar com: 15 Dias atrás</option>
          <option value="30">Comparar com: 30 Dias atrás</option>
        </select>
        <input type="text" v-model="search" placeholder="Buscar por título..." class="search-input glass-panel ml-2" />
      </div>
    </div>
    
    <div class="table-scroll">
      <table class="data-table">
        <thead>
          <tr>
            <th>Plataforma</th>
            <th>Categoria</th>
            <th>Título</th>
            <th>Preço Atual</th>
            <th>Preço Anterior</th>
            <th>Variação R$</th>
            <th>Vendas (Período)</th>
            <th>Ação</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in processedPaginatedData" :key="item.id">
            <td>
              <span :class="['badge', item.plataforma]">
                {{ item.plataforma === 'meli' ? 'Mercado Livre' : 'Shopee' }}
              </span>
            </td>
            <td>
              <span class="badge category">{{ item.categoria }}</span>
            </td>
            <td class="title-cell" :title="item.titulo">{{ item.titulo }}</td>
            
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
              <span v-if="item.salesDiff !== null" class="text-green fw-bold">
                +{{ item.salesDiff }} un
              </span>
              <span v-else class="text-muted">-</span>
            </td>
            
            <td>
              <a :href="item.link" target="_blank" class="link-btn">Acessar ↗</a>
            </td>
          </tr>
          <tr v-if="filteredData.length === 0">
            <td colspan="8" class="empty-state">Nenhum produto encontrado.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Paginação -->
    <div class="pagination" v-if="totalPages > 1">
      <button :disabled="currentPage === 1" @click="currentPage--" class="page-btn glass-panel">Anterior</button>
      <span class="page-info">Página {{ currentPage }} de {{ totalPages }}</span>
      <button :disabled="currentPage === totalPages" @click="currentPage++" class="page-btn glass-panel">Próxima</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] }
})

const search = ref('')
const periodoComparacao = ref('7') // default 1 week
const currentPage = ref(1)
const itemsPerPage = 12

// Zera a página quando busca
watch(search, () => {
  currentPage.value = 1
})

const filteredData = computed(() => {
  let result = props.items
  
  if (search.value) {
    const lowerSearch = search.value.toLowerCase()
    result = result.filter(item => item.titulo.toLowerCase().includes(lowerSearch))
  }
  
  return result
})

const totalPages = computed(() => Math.ceil(filteredData.value.length / itemsPerPage) || 1)

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredData.value.slice(start, end)
})

function getHistoricalData(item, daysAgo) {
  if (!item.historico_coletas || item.historico_coletas.length === 0) return null
  
  if (daysAgo === 'last') {
    return item.historico_coletas.length > 1 ? item.historico_coletas[1] : null
  }
  
  const targetDate = new Date()
  targetDate.setDate(targetDate.getDate() - parseInt(daysAgo))
  
  let closest = null
  let minDiff = Infinity
  
  const historyToCheck = item.historico_coletas.slice(1)
  if (historyToCheck.length === 0) return null
  
  for (const entry of historyToCheck) {
    const entryDate = new Date(entry.data_coleta)
    const diff = Math.abs(entryDate - targetDate)
    
    // Tolerância de +- 2 dias (172800000 ms)
    if (diff < minDiff && diff <= 172800000) {
      minDiff = diff
      closest = entry
    }
  }
  
  return closest
}

const processedPaginatedData = computed(() => {
  return paginatedData.value.map(item => {
    const hist = getHistoricalData(item, periodoComparacao.value)
    let varInfo = null
    let salesDiff = null
    
    if (hist) {
      if (hist.preco > 0) {
        const diff = item.preco - hist.preco
        const perc = (diff / hist.preco) * 100
        // Ignora pequenas oscilações de centavos
        if (Math.abs(diff) > 0.05) {
          varInfo = {
            diff,
            perc,
            isPositive: diff > 0,
            isNegative: diff < 0
          }
        }
      }
      salesDiff = Math.max(0, item.vendas_totais - hist.vendas_totais)
    }
    
    return {
      ...item,
      hist,
      varInfo,
      salesDiff
    }
  })
})
</script>

<style scoped>
.table-container { padding: 1.5rem; margin-bottom: 2rem; }
.table-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem; }
.table-header h3 { font-size: 1.25rem; color: var(--text-main); margin: 0; }
.table-actions { display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; }

.search-input { background: rgba(0,0,0,0.2); border: 1px solid var(--border-glass); color: var(--text-main); padding: 0.75rem 1rem; border-radius: 8px; width: 300px; outline: none; transition: border-color 0.3s ease; }
.search-input:focus { border-color: var(--neon-blue); }
.inline-select { background: rgba(0,0,0,0.2); border: 1px solid var(--border-glass); color: white; padding: 0.75rem 1rem; border-radius: 8px; outline: none; cursor: pointer; }
.inline-select:focus { border-color: var(--neon-blue); }
.inline-select option { background: #1a1a1a; color: white; }

.table-scroll { overflow-x: auto; border-radius: 8px; }
.data-table { width: 100%; border-collapse: collapse; text-align: left; }
.data-table th, .data-table td { padding: 1rem; border-bottom: 1px solid var(--border-glass); }
.data-table th { background: rgba(255,255,255,0.02); color: var(--text-muted); font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; white-space: nowrap; }
.data-table tbody tr { transition: background 0.2s ease; }
.data-table tbody tr:hover { background: rgba(255,255,255,0.03); }

.title-cell { max-width: 250px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.price-cell, .old-price-cell, .variation-cell, .sales-diff-cell { white-space: nowrap; }
.price-cell { font-weight: bold; }

.text-muted { color: var(--text-muted); }
.text-red { color: #ef4444; font-weight: bold; }
.text-green { color: #10b981; font-weight: bold; }
.fw-bold { font-weight: bold; }

.badge { padding: 0.25rem 0.6rem; border-radius: 99px; font-size: 0.7rem; font-weight: 600; white-space: nowrap; }
.badge.meli { background: rgba(255, 230, 0, 0.15); color: #ffe600; border: 1px solid rgba(255, 230, 0, 0.3); }
.badge.shopee { background: rgba(255, 107, 53, 0.15); color: #ff6b35; border: 1px solid rgba(255, 107, 53, 0.3); }
.badge.category { background: rgba(192, 132, 252, 0.15); color: var(--neon-purple); border: 1px solid rgba(192, 132, 252, 0.3); }

.link-btn { display: inline-block; padding: 0.4rem 0.8rem; background: rgba(56, 189, 248, 0.1); color: var(--neon-blue); text-decoration: none; border-radius: 6px; font-size: 0.85rem; font-weight: 600; transition: background 0.3s ease; white-space: nowrap; }
.link-btn:hover { background: rgba(56, 189, 248, 0.2); }
.empty-state { text-align: center; padding: 3rem !important; color: var(--text-muted); font-style: italic; }

.pagination { display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 1.5rem; }
.page-btn { padding: 0.5rem 1rem; background: rgba(255,255,255,0.05); border: 1px solid var(--border-glass); color: var(--text-main); border-radius: 6px; cursor: pointer; transition: all 0.2s ease; }
.page-btn:hover:not(:disabled) { background: rgba(56, 189, 248, 0.2); border-color: var(--neon-blue); }
.page-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.page-info { font-size: 0.9rem; color: var(--text-muted); }
</style>
