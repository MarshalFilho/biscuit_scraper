<template>
  <div class="glass-panel config-panel animate-fade-in" style="animation-delay: 0.1s;">
    <h3>🏷️ Gerenciador Dinâmico de Categorias</h3>
    <p class="subtitle">Associe palavras-chave aos nomes das categorias para organizar os produtos.</p>
    
    <div class="rules-list">
      <div v-for="(rule, index) in rules" :key="index" class="rule-item">
        <span class="text-muted">Se o título contiver:</span>
        <input type="text" v-model="rule.keyword" placeholder="ex: noivos" class="glass-input small" />
        <span class="text-muted">➔ Categoria:</span>
        <input type="text" v-model="rule.category" placeholder="ex: Casamento" class="glass-input small" />
        <button @click="removeRule(index)" class="btn-icon">✖</button>
      </div>
    </div>
    
    <div class="actions">
      <button @click="addRule" class="btn secondary">+ Adicionar Regra</button>
      <button @click="saveRules" class="btn primary">💾 Aplicar e Salvar Regras</button>
      <span v-if="statusMessage" class="status-msg">{{ statusMessage }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const emit = defineEmits(['update-categories'])

const rules = ref([])
const statusMessage = ref('')

onMounted(() => {
  const saved = localStorage.getItem('biscuit_category_rules')
  if (saved) {
    rules.value = JSON.parse(saved)
  } else {
    rules.value = [
      { keyword: 'vela', category: 'Velas' },
      { keyword: 'topo', category: 'Topos de Bolo' },
      { keyword: 'bolo', category: 'Topos de Bolo' },
      { keyword: 'chaveiro', category: 'Chaveiros/Lembrancinhas' },
      { keyword: 'lembrancinha', category: 'Chaveiros/Lembrancinhas' }
    ]
  }
  emit('update-categories', rules.value)
})

function addRule() {
  rules.value.push({ keyword: '', category: '' })
}
function removeRule(idx) {
  rules.value.splice(idx, 1)
}
function saveRules() {
  const validRules = rules.value.filter(r => r.keyword.trim() !== '' && r.category.trim() !== '')
  localStorage.setItem('biscuit_category_rules', JSON.stringify(validRules))
  emit('update-categories', validRules)
  showStatus('Regras aplicadas em tempo real!')
}

function showStatus(msg) {
  statusMessage.value = msg
  setTimeout(() => statusMessage.value = '', 3500)
}
</script>

<style scoped>
.config-panel { padding: 1.5rem; margin-bottom: 2rem; }
.config-panel h3 { margin-top: 0; color: var(--text-main); font-size: 1.25rem; margin-bottom: 0.3rem; }
.subtitle { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1.2rem; }
.rules-list { display: flex; flex-direction: column; gap: 0.8rem; margin-bottom: 1.2rem; }
.rule-item { display: flex; align-items: center; gap: 0.8rem; flex-wrap: wrap; background: rgba(0,0,0,0.1); padding: 0.6rem 1rem; border-radius: 8px; border: 1px solid var(--border-glass); }
.text-muted { color: var(--text-muted); font-size: 0.9rem; }
.glass-input.small { background: rgba(255,255,255,0.05); border: 1px solid var(--border-glass); color: var(--text-main); padding: 0.4rem 0.8rem; border-radius: 6px; outline: none; transition: border 0.3s; width: 180px; }
.glass-input.small:focus { border-color: var(--neon-purple); }
.btn-icon { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); color: #ef4444; cursor: pointer; padding: 0.3rem 0.6rem; border-radius: 6px; transition: 0.2s; }
.btn-icon:hover { background: rgba(239, 68, 68, 0.3); }
.actions { display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; }
.btn { padding: 0.6rem 1.2rem; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s ease; border: none; }
.btn.primary { background: var(--neon-purple); color: #000; }
.btn.primary:hover { background: #b062fb; box-shadow: 0 0 15px rgba(192, 132, 252, 0.4); }
.btn.secondary { background: rgba(255, 255, 255, 0.05); color: var(--text-main); border: 1px solid var(--border-glass); }
.btn.secondary:hover { background: rgba(255, 255, 255, 0.1); }
.status-msg { color: #10b981; font-weight: 600; font-size: 0.9rem; }
</style>
