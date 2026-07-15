<template>
  <div class="glass-panel config-panel animate-fade-in">
    <h3>⚙️ Controle do Scraper (Simulação Local)</h3>
    
    <div class="form-group">
      <label>Termos de Busca Ativos (Para extração futura):</label>
      <div class="tag-input-container">
        <span v-for="tag in localSearchTerms" :key="tag" class="tag bg-blue">
          {{ tag }} <button class="close-btn" @click="removeSearchTag(tag)">x</button>
        </span>
        <input type="text" v-model="newSearchTag" @keydown.enter.prevent="addSearchTag" placeholder="Pressione Enter para adicionar (ex: topo de bolo)" class="glass-input inline" />
      </div>
    </div>

    <div class="form-group">
      <label>Blacklist (Se contiver no título, oculta/descarta automaticamente):</label>
      <div class="tag-input-container">
        <span v-for="tag in localBlacklist" :key="tag" class="tag bg-red">
          {{ tag }} <button class="close-btn" @click="removeBlacklistTag(tag)">x</button>
        </span>
        <input type="text" v-model="newBlacklistTag" @keydown.enter.prevent="addBlacklistTag" placeholder="Pressione Enter para adicionar (ex: chocolate)" class="glass-input inline" />
      </div>
    </div>

    <div class="actions">
      <button @click="saveSettings" class="btn primary">💾 Salvar Preferências</button>
      <button @click="triggerScraper" class="btn danger">▶️ Disparar Scraper Agora</button>
      <span v-if="statusMessage" class="status-msg">{{ statusMessage }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const emit = defineEmits(['update-blacklist'])

const localBlacklist = ref([])
const localSearchTerms = ref([])
const newBlacklistTag = ref('')
const newSearchTag = ref('')
const statusMessage = ref('')

onMounted(() => {
  const savedBL = localStorage.getItem('biscuit_blacklist')
  if (savedBL) localBlacklist.value = JSON.parse(savedBL)
  else localBlacklist.value = ['chocolate', 'nestle', 'choco', 'filtro', 'purificadora', 'bolacha']

  const savedST = localStorage.getItem('biscuit_search_terms')
  if (savedST) localSearchTerms.value = JSON.parse(savedST)
  else localSearchTerms.value = ['topo de bolo biscuit', 'vela biscuit personalizada']
  
  emit('update-blacklist', localBlacklist.value)
})

function addBlacklistTag() {
  const t = newBlacklistTag.value.trim().toLowerCase()
  if (t && !localBlacklist.value.includes(t)) localBlacklist.value.push(t)
  newBlacklistTag.value = ''
}
function removeBlacklistTag(tag) {
  localBlacklist.value = localBlacklist.value.filter(t => t !== tag)
}

function addSearchTag() {
  const t = newSearchTag.value.trim().toLowerCase()
  if (t && !localSearchTerms.value.includes(t)) localSearchTerms.value.push(t)
  newSearchTag.value = ''
}
function removeSearchTag(tag) {
  localSearchTerms.value = localSearchTerms.value.filter(t => t !== tag)
}

function saveSettings() {
  localStorage.setItem('biscuit_blacklist', JSON.stringify(localBlacklist.value))
  localStorage.setItem('biscuit_search_terms', JSON.stringify(localSearchTerms.value))
  emit('update-blacklist', localBlacklist.value)
  showStatus('Preferências salvas localmente!')
}

function triggerScraper() {
  showStatus('Comando enviado! (Status: Pendente para o Python)')
}

function showStatus(msg) {
  statusMessage.value = msg
  setTimeout(() => statusMessage.value = '', 3500)
}
</script>

<style scoped>
.config-panel { padding: 1.5rem; margin-bottom: 1.5rem; }
.config-panel h3 { margin-top: 0; color: var(--text-main); font-size: 1.25rem; margin-bottom: 1.2rem; }
.form-group { margin-bottom: 1.2rem; }
.form-group label { display: block; color: var(--text-muted); font-size: 0.9rem; margin-bottom: 0.5rem; font-weight: 500; }
.tag-input-container { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; background: rgba(0,0,0,0.1); padding: 0.8rem; border-radius: 8px; border: 1px solid var(--border-glass); }
.tag { padding: 0.3rem 0.6rem; border-radius: 6px; font-size: 0.85rem; font-weight: 600; display: flex; align-items: center; gap: 0.4rem; color: #fff; }
.bg-blue { background: rgba(56, 189, 248, 0.4); border: 1px solid rgba(56, 189, 248, 0.6); }
.bg-red { background: rgba(239, 68, 68, 0.4); border: 1px solid rgba(239, 68, 68, 0.6); }
.close-btn { background: none; border: none; color: white; cursor: pointer; font-size: 0.9rem; padding: 0; line-height: 1; opacity: 0.7; }
.close-btn:hover { opacity: 1; }
.glass-input.inline { background: transparent; border: none; color: var(--text-main); flex: 1; min-width: 200px; outline: none; }
.actions { display: flex; gap: 1rem; align-items: center; margin-top: 1.5rem; }
.btn { padding: 0.6rem 1.2rem; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s ease; border: none; }
.btn.primary { background: var(--neon-blue); color: #000; }
.btn.primary:hover { background: #1da4e3; box-shadow: 0 0 15px rgba(56, 189, 248, 0.4); }
.btn.danger { background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.4); }
.btn.danger:hover { background: rgba(239, 68, 68, 0.3); }
.status-msg { color: #10b981; font-weight: 600; font-size: 0.9rem; }
</style>
