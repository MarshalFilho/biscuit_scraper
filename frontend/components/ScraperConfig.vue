<template>
  <div class="glass-panel config-panel animate-fade-in" :class="{ 'is-collapsed': isCollapsed }">
    <div class="panel-header" @click="toggleCollapse">
      <h3>⚙️ Controle do Scraper <span class="badge">Nuvem Integrada</span></h3>
      <button class="btn-toggle">{{ isCollapsed ? '▼ Expandir' : '▲ Minimizar' }}</button>
    </div>
    
    <transition name="slide-fade">
      <div v-show="!isCollapsed" class="panel-content">
        <div class="form-group mt-3">
          <label>Nome do Projeto (Opcional):</label>
          <input type="text" v-model="nomeProjeto" placeholder="Ex: Monitoramento de Placas de Vídeo" class="glass-input full-width" :disabled="disparoPendente" />
        </div>

        <div class="form-group mt-3">
          <label>Termos de Busca Ativos (Para extração futura):</label>
          <div class="tag-input-container">
            <span v-for="tag in localSearchTerms" :key="tag" class="tag bg-blue">
              {{ tag }} <button class="close-btn" @click="removeSearchTag(tag)" :disabled="disparoPendente">x</button>
            </span>
            <input type="text" v-model="newSearchTag" @keydown.enter.prevent="addSearchTag" @paste="handlePasteSearch" placeholder="Cole uma lista ou digite (separados por vírgula)" class="glass-input inline" :disabled="disparoPendente" />
          </div>
        </div>

        <div class="form-group">
          <label>Blacklist (Se contiver no título, oculta/descarta automaticamente):</label>
          <div class="tag-input-container">
            <span v-for="tag in localBlacklist" :key="tag" class="tag bg-red">
              {{ tag }} <button class="close-btn" @click="removeBlacklistTag(tag)" :disabled="disparoPendente">x</button>
            </span>
            <input type="text" v-model="newBlacklistTag" @keydown.enter.prevent="addBlacklistTag" @paste="handlePasteBlacklist" placeholder="Cole uma lista ou digite (separados por vírgula)" class="glass-input inline" :disabled="disparoPendente" />
          </div>
        </div>

        <div class="actions">
          <button @click="saveConfigs" class="btn primary" :disabled="disparoPendente">💾 Salvar Preferências</button>
          
          <button @click="triggerScraper" class="btn danger" :disabled="disparoPendente || !props.user">
            <div v-if="disparoPendente" class="spinner-inline"></div>
            <span>{{ disparoPendente ? (statusScraper || '⏳ Iniciando nuvem...') : '▶️ Disparar Scraper Agora' }}</span>
          </button>
          
          <span v-if="statusMessage" class="status-msg">{{ statusMessage }}</span>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { createClient } from '@supabase/supabase-js'

const config = useRuntimeConfig()
const supabase = createClient(config.public.supabaseUrl, config.public.supabaseAnonKey)

const props = defineProps({
  user: { type: Object, default: null }
})

const emit = defineEmits(['update-blacklist', 'update-project-name'])

const nomeProjeto = ref('Meu Projeto Scraper')
const localBlacklist = ref([])
const localSearchTerms = ref([])
const newBlacklistTag = ref('')
const newSearchTag = ref('')
const statusMessage = ref('')
const isCollapsed = ref(true)

// Variáveis de Controle e Status Realtime
const disparoPendente = ref(false)
const statusScraper = ref('')
let realtimeChannel = null

watch(() => props.user?.id, (newId, oldId) => {
  if (newId !== oldId) {
    loadConfigs()
    if (newId) setupRealtime()
  }
})

onMounted(() => {
  const savedState = localStorage.getItem('scraper_panel_collapsed')
  if (savedState !== null) isCollapsed.value = JSON.parse(savedState)
  loadConfigs()
  if (props.user) setupRealtime()
})

onUnmounted(() => {
  if (realtimeChannel) supabase.removeChannel(realtimeChannel)
})

function setupRealtime() {
  if (realtimeChannel) supabase.removeChannel(realtimeChannel)
  
  realtimeChannel = supabase.channel('status_tracker')
    .on('postgres_changes', { 
      event: 'UPDATE', 
      schema: 'public', 
      table: 'configuracoes_scraper',
      filter: `user_id=eq.${props.user.id}`
    }, payload => {
      const novadata = payload.new
      if (novadata.disparo_pendente !== undefined) disparoPendente.value = novadata.disparo_pendente
      if (novadata.status_scraper !== undefined) statusScraper.value = novadata.status_scraper || ''
    })
    .subscribe()
}

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
  localStorage.setItem('scraper_panel_collapsed', JSON.stringify(isCollapsed.value))
}

async function loadConfigs() {
  if (props.user) {
    const { data, error } = await supabase
      .from('configuracoes_scraper')
      .select('nome_projeto, blacklist, termos_busca, disparo_pendente, status_scraper')
      .eq('user_id', props.user.id)
      .single()
      
    if (data) {
      if (data.nome_projeto) nomeProjeto.value = data.nome_projeto
      localBlacklist.value = data.blacklist || []
      localSearchTerms.value = data.termos_busca || []
      if (data.disparo_pendente !== undefined) disparoPendente.value = data.disparo_pendente
      if (data.status_scraper !== undefined) statusScraper.value = data.status_scraper || ''
      
      emit('update-blacklist', localBlacklist.value)
      emit('update-project-name', nomeProjeto.value)
      return
    }
  }

  // Simulação Local via LocalStorage (Fallback)
  const savedName = localStorage.getItem('scraper_nome_projeto')
  if (savedName) nomeProjeto.value = savedName
  
  const savedBL = localStorage.getItem('scraper_blacklist')
  if (savedBL) localBlacklist.value = JSON.parse(savedBL)
  else localBlacklist.value = ['termo_indesejado_1']

  const savedST = localStorage.getItem('scraper_search_terms')
  if (savedST) localSearchTerms.value = JSON.parse(savedST)
  else localSearchTerms.value = ['meu produto teste']
  
  emit('update-blacklist', localBlacklist.value)
  emit('update-project-name', nomeProjeto.value)
}

async function saveConfigs() {
  localStorage.setItem('scraper_nome_projeto', nomeProjeto.value)
  localStorage.setItem('scraper_blacklist', JSON.stringify(localBlacklist.value))
  localStorage.setItem('scraper_search_terms', JSON.stringify(localSearchTerms.value))
  
  if (props.user) {
    const { error } = await supabase.from('configuracoes_scraper').upsert(
      { 
        user_id: props.user.id, 
        nome_projeto: nomeProjeto.value,
        blacklist: localBlacklist.value, 
        termos_busca: localSearchTerms.value 
      },
      { onConflict: 'user_id' }
    )
    if (error) {
      showStatus('Erro ao salvar na nuvem!')
      console.error(error)
      return
    }
    showStatus('Preferências salvas na nuvem!')
  } else {
    showStatus('Salvo localmente (Logue para salvar na nuvem)')
  }
  emit('update-blacklist', localBlacklist.value)
  emit('update-project-name', nomeProjeto.value)
}

async function triggerScraper() {
  if (props.user) {
    disparoPendente.value = true
    statusScraper.value = "Agendado na Nuvem. Aguardando robô..."
    const { error } = await supabase.from('configuracoes_scraper').upsert(
      { user_id: props.user.id, disparo_pendente: true, status_scraper: statusScraper.value },
      { onConflict: 'user_id' }
    )
    if (error) {
      showStatus('Erro ao agendar disparo!')
      disparoPendente.value = false
      return
    }
  } else {
    showStatus('Apenas simulação. Faça login para disparar de verdade!')
  }
}

function showStatus(msg) {
  statusMessage.value = msg
  setTimeout(() => statusMessage.value = '', 3500)
}

function processTags(rawString, targetArray) {
  if (!rawString) return
  const tags = rawString.split(/[,;\n]+/).map(t => t.trim().toLowerCase()).filter(t => t)
  tags.forEach(t => {
    if (!targetArray.value.includes(t)) targetArray.value.push(t)
  })
}

function addBlacklistTag() {
  processTags(newBlacklistTag.value, localBlacklist)
  newBlacklistTag.value = ''
}

function removeBlacklistTag(tag) { 
  localBlacklist.value = localBlacklist.value.filter(t => t !== tag) 
}

function addSearchTag() {
  processTags(newSearchTag.value, localSearchTerms)
  newSearchTag.value = ''
}

function removeSearchTag(tag) { 
  localSearchTerms.value = localSearchTerms.value.filter(t => t !== tag) 
}

function handlePasteBlacklist(e) {
  e.preventDefault()
  const text = (e.clipboardData || window.clipboardData).getData('text')
  processTags(text, localBlacklist)
}

function handlePasteSearch(e) {
  e.preventDefault()
  const text = (e.clipboardData || window.clipboardData).getData('text')
  processTags(text, localSearchTerms)
}
</script>

<style scoped>
.config-panel { padding: 1.5rem; margin-bottom: 1rem; transition: padding 0.3s ease; }
.config-panel.is-collapsed { padding: 1rem 1.5rem; }
.panel-header { display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
.panel-header h3 { margin: 0; color: var(--text-main); font-size: 1.25rem; display: flex; align-items: center; gap: 0.8rem; }
.badge { font-size: 0.7rem; background: rgba(56, 189, 248, 0.2); color: var(--neon-blue); padding: 0.2rem 0.6rem; border-radius: 99px; border: 1px solid rgba(56, 189, 248, 0.4); text-transform: uppercase; letter-spacing: 0.05em; font-weight: bold; }
.btn-toggle { background: transparent; border: none; color: var(--text-muted); cursor: pointer; font-size: 0.9rem; font-weight: bold; transition: color 0.2s; outline: none; }
.btn-toggle:hover { color: var(--neon-blue); }

.mt-3 { margin-top: 1.5rem; }
.form-group { margin-bottom: 1.2rem; }
.form-group label { display: block; color: var(--text-muted); font-size: 0.9rem; margin-bottom: 0.5rem; font-weight: 500; }
.tag-input-container { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; background: rgba(0,0,0,0.1); padding: 0.8rem; border-radius: 8px; border: 1px solid var(--border-glass); }
.tag { padding: 0.3rem 0.6rem; border-radius: 6px; font-size: 0.85rem; font-weight: 600; display: flex; align-items: center; gap: 0.4rem; color: #fff; }
.bg-blue { background: rgba(56, 189, 248, 0.4); border: 1px solid rgba(56, 189, 248, 0.6); }
.bg-red { background: rgba(239, 68, 68, 0.4); border: 1px solid rgba(239, 68, 68, 0.6); }
.close-btn { background: none; border: none; color: white; cursor: pointer; font-size: 0.9rem; padding: 0; line-height: 1; opacity: 0.7; }
.close-btn:hover { opacity: 1; }
.glass-input { background: rgba(0,0,0,0.2); border: 1px solid var(--border-glass); color: white; padding: 0.6rem 1rem; border-radius: 8px; outline: none; }
.glass-input.inline { background: transparent; border: none; flex: 1; min-width: 200px; padding: 0; }
.glass-input.full-width { width: 100%; display: block; margin-bottom: 0.5rem; }
.glass-input:focus { border-color: var(--neon-blue); }
.glass-input:disabled { opacity: 0.5; cursor: not-allowed; }

.actions { display: flex; gap: 1rem; align-items: center; margin-top: 1.5rem; flex-wrap: wrap; }
.btn { padding: 0.6rem 1.2rem; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s ease; border: none; display: flex; align-items: center; gap: 0.5rem; }
.btn.primary { background: var(--neon-blue); color: #000; }
.btn.primary:hover:not(:disabled) { background: #1da4e3; box-shadow: 0 0 15px rgba(56, 189, 248, 0.4); }
.btn.danger { background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.4); }
.btn.danger:hover:not(:disabled) { background: rgba(239, 68, 68, 0.3); }
.btn:disabled { opacity: 0.6; cursor: not-allowed; filter: grayscale(1); border-color: transparent; }

.spinner-inline { width: 16px; height: 16px; border: 2px solid rgba(255, 255, 255, 0.3); border-top-color: currentColor; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.status-msg { color: #10b981; font-weight: 600; font-size: 0.9rem; }

/* Transição do Vue */
.slide-fade-enter-active, .slide-fade-leave-active { transition: all 0.3s ease; overflow: hidden; transform-origin: top; }
.slide-fade-enter-from, .slide-fade-leave-to { opacity: 0; max-height: 0; transform: translateY(-10px); }
.slide-fade-enter-to, .slide-fade-leave-from { opacity: 1; max-height: 1000px; transform: translateY(0); }
</style>
