<template>
  <div class="glass-panel table-container animate-fade-in" style="animation-delay: 0.4s;">
    <div class="table-header">
      <h3>Base de Dados de Produtos</h3>
      <input type="text" v-model="search" placeholder="Buscar por título..." class="search-input glass-panel" />
    </div>
    
    <div class="table-scroll">
      <table class="data-table">
        <thead>
          <tr>
            <th>Plataforma</th>
            <th>Título</th>
            <th>Preço Atual</th>
            <th>Vendas Totais</th>
            <th>Link</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredData" :key="item.id">
            <td>
              <span :class="['badge', item.plataforma]">
                {{ item.plataforma === 'meli' ? 'Mercado Livre' : 'Shopee' }}
              </span>
            </td>
            <td class="title-cell">{{ item.titulo }}</td>
            <td class="price-cell">R$ {{ item.preco ? item.preco.toFixed(2).replace('.', ',') : '0,00' }}</td>
            <td class="sales-cell">{{ item.vendas_totais || 0 }}</td>
            <td>
              <a :href="item.link" target="_blank" class="link-btn">Acessar ↗</a>
            </td>
          </tr>
          <tr v-if="filteredData.length === 0">
            <td colspan="5" class="empty-state">Nenhum produto encontrado.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] }
})

const search = ref('')

const filteredData = computed(() => {
  if (!search.value) return props.items
  const lowerSearch = search.value.toLowerCase()
  return props.items.filter(item => item.titulo.toLowerCase().includes(lowerSearch))
})
</script>

<style scoped>
.table-container {
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.table-header h3 {
  font-size: 1.25rem;
  color: var(--text-main);
}

.search-input {
  background: rgba(0,0,0,0.2);
  border: 1px solid var(--border-glass);
  color: var(--text-main);
  padding: 0.75rem 1rem;
  border-radius: 8px;
  width: 300px;
  outline: none;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  border-color: var(--neon-blue);
}

.table-scroll {
  overflow-x: auto;
  border-radius: 8px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.data-table th, .data-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--border-glass);
}

.data-table th {
  background: rgba(255,255,255,0.02);
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
}

.data-table tbody tr {
  transition: background 0.2s ease;
}

.data-table tbody tr:hover {
  background: rgba(255,255,255,0.03);
}

.title-cell {
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.price-cell, .sales-cell {
  font-weight: 600;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 99px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge.meli {
  background: rgba(255, 230, 0, 0.15);
  color: #ffe600;
  border: 1px solid rgba(255, 230, 0, 0.3);
}

.badge.shopee {
  background: rgba(255, 107, 53, 0.15);
  color: #ff6b35;
  border: 1px solid rgba(255, 107, 53, 0.3);
}

.link-btn {
  display: inline-block;
  padding: 0.4rem 0.8rem;
  background: rgba(56, 189, 248, 0.1);
  color: var(--neon-blue);
  text-decoration: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  transition: background 0.3s ease;
}

.link-btn:hover {
  background: rgba(56, 189, 248, 0.2);
}

.empty-state {
  text-align: center;
  padding: 3rem !important;
  color: var(--text-muted);
  font-style: italic;
}
</style>
