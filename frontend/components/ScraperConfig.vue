<template>
  <div class="glass-panel config-panel animate-fade-in" :class="{ 'is-collapsed': isCollapsed }">
    <div class="panel-header" @click="toggleCollapse">
      <h3>⚙️ Controle & Disparo do Robô Scraper <span class="badge">Nuvem Serverless</span></h3>
      <button class="btn-toggle">{{ isCollapsed ? '▼ Expandir' : '▲ Minimizar' }}</button>
    </div>
    
    <transition name="slide-fade">
      <div v-show="!isCollapsed" class="panel-content">
        <!-- 1. Nome do Projeto -->
        <div class="form-group mt-3">
          <label>Nome do Projeto / Nicho:</label>
          <input type="text" v-model="nomeProjeto" placeholder="Ex: Monitoramento de Biscuit & Artesanato" class="glass-input full-width" :disabled="disparoPendente" />
        </div>

        <!-- 2. Modo de Paginação & Autenticação -->
        <div class="form-group mode-box">
          <label class="section-label">🔒 Modo de Execução & Autenticação:</label>
          <div class="mode-options">
            <label :class="['mode-card', { active: modoPaginacao === 'anonimo' }]">
              <input type="radio" v-model="modoPaginacao" value="anonimo" :disabled="disparoPendente" />
              <div class="mode-info">
                <strong>⚡ Modo Rápido / Anônimo (1 Página por busca)</strong>
                <p>Não exige login. Coleta os top produtos principais da 1ª página sem risco de bloqueio.</p>
              </div>
            </label>

            <label :class="['mode-card', { active: modoPaginacao === 'logado' }]">
              <input type="radio" v-model="modoPaginacao" value="logado" :disabled="disparoPendente" />
              <div class="mode-info">
                <strong>🔑 Modo Profundo / Logado (Múltiplas Páginas)</strong>
                <p>Coleta até 5+ páginas por busca injetando a sessão autenticada (`auth.json`) salva no Supabase.</p>
              </div>
            </label>
          </div>
        </div>

        <!-- Upload de Sessão se modo logado -->
        <div v-if="modoPaginacao === 'logado'" class="form-group auth-upload-box">
          <label>🔑 Importar / Atualizar Arquivo de Sessão (`auth.json`):</label>
          <div class="file-upload-row">
            <input type="file" ref="fileInput" accept=".json" @change="handleFileUpload" class="file-input" :disabled="disparoPendente" />
            <span v-if="authFileStatus" class="auth-file-status">{{ authFileStatus }}</span>
          </div>
          <small class="help-text">Gere o arquivo `auth.json` usando o script local `py src/main.py --login` e faça o upload aqui para salvar no Supabase.</small>
        </div>

        <!-- 3. Termos de Busca -->
        <div class="form-group mt-3">
          <label>Termos de Busca Ativos (Palavras que o robô vai pesquisar):</label>
          <div class="tag-input-container">
            <span v-for="tag in localSearchTerms" :key="tag" class="tag bg-blue">
              {{ tag }} <button class="close-btn" @click="removeSearchTag(tag)" :disabled="disparoPendente">x</button>
            </span>
            <input type="text" v-model="newSearchTag" @keydown.enter.prevent="addSearchTag" @paste="handlePasteSearch" placeholder="Cole uma lista ou digite (separados por vírgula)" class="glass-input inline" :disabled="disparoPendente" />
          </div>
        </div>

        <!-- 4. Blacklist / Palavras Negativas -->
        <div class="form-group">
          <label>Blacklist (Se o produto contiver no título, descarta automaticamente):</label>
          <div class="tag-input-container">
            <span v-for="tag in localBlacklist" :key="tag" class="tag bg-red">
              {{ tag }} <button class="close-btn" @click="removeBlacklistTag(tag)" :disabled="disparoPendente">x</button>
            </span>
            <input type="text" v-model="newBlacklistTag" @keydown.enter.prevent="addBlacklistTag" @paste="handlePasteBlacklist" placeholder="Cole uma lista ou digite (separados por vírgula)" class="glass-input inline" :disabled="disparoPendente" />
          </div>
        </div>

        <!-- Painel de Progresso do Robô em Tempo Real -->
        <div v-if="disparoPendente || statusScraper" class="status-tracker-box">
          <div class="tracker-header">
            <div class="spinner-inline green"></div>
            <strong>Status do Robô na Nuvem:</strong>
          </div>
          <p class="tracker-msg">{{ statusScraper || '🤖 Inicializando robô de raspagem na nuvem...' }}</p>
        </div>

        <!-- Ações -->
        <div class="actions">
          <button @click="saveConfigs" class="btn primary" :disabled="disparoPendente">💾 Salvar Preferências</button>
          
          <button @click="triggerScraper" class="btn danger" :disabled="disparoPendente || !props.user">
            <div v-if="disparoPendente" class="spinner-inline"></div>
            <span>{{ disparoPendente ? '⏳ Robô Rodando...' : '▶️ Disparar Scraper Agora' }}</span>
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
const modoPaginacao = ref('anonimo') // 'anonimo' ou 'logado'
const localBlacklist = ref([])
const localSearchTerms = ref([])
const newBlacklistTag = ref('')
const newSearchTag = ref('')
const statusMessage = ref('')
const authFileStatus = ref('')
const isCollapsed = ref(false) // Aberto por padrão na página de config

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
}

async function loadConfigs() {
  if (props.user) {
    const { data, error } = await supabase
      .from('configuracoes_scraper')
      .select('nome_projeto, blacklist, termos_busca, disparo_pendente, status_scraper, modo_paginacao, auth_state_meli')
      .eq('user_id', props.user.id)
      .single()
      
    if (data) {
      if (data.nome_projeto) nomeProjeto.value = data.nome_projeto
      if (data.modo_paginacao) modoPaginacao.value = data.modo_paginacao
      if (data.auth_state_meli) authFileStatus.value = '✅ Sessão salva no Supabase'
      localBlacklist.value = data.blacklist || []
      localSearchTerms.value = data.termos_busca || []
      if (data.disparo_pendente !== undefined) disparoPendente.value = data.disparo_pendente
      if (data.status_scraper !== undefined) statusScraper.value = data.status_scraper || ''
      
      emit('update-blacklist', localBlacklist.value)
      emit('update-project-name', nomeProjeto.value)
      return
    }
  }

  // Fallback local
  const savedName = localStorage.getItem('scraper_nome_projeto')
  if (savedName) nomeProjeto.value = savedName
  
  const savedBL = localStorage.getItem('scraper_blacklist')
  if (savedBL) localBlacklist.value = JSON.parse(savedBL)
  else localBlacklist.value = ['molde', 'ferramenta']

  const savedST = localStorage.getItem('scraper_search_terms')
  if (savedST) localSearchTerms.value = JSON.parse(savedST)
  else localSearchTerms.value = ['biscuit', 'lembrancinha biscuit']
  
  emit('update-blacklist', localBlacklist.value)
  emit('update-project-name', nomeProjeto.value)
}

function handleFileUpload(event) {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = async (e) => {
    try {
      const jsonContent = JSON.parse(e.target.result)
      if (props.user) {
        const { error } = await supabase.from('configuracoes_scraper').upsert(
          { user_id: props.user.id, auth_state_meli: jsonContent },
          { onConflict: 'user_id' }
        )
        if (error) throw error
        authFileStatus.value = '✅ Sessão salva com sucesso no Supabase!'
        showStatus('Sessão auth.json enviada!')
      } else {
        showStatus('Faça login para salvar a sessão na nuvem.')
      }
    } catch (err) {
      console.error(err)
      authFileStatus.value = '❌ Erro ao ler arquivo JSON.'
    }
  }
  reader.readAsText(file)
}

function applyAiGeneratedFilters(aiData) {
  if (aiData.termos) {
    aiData.termos.forEach(t => {
      if (!localSearchTerms.value.includes(t)) localSearchTerms.value.push(t)
    })
  }
  if (aiData.blacklist) {
    aiData.blacklist.forEach(b => {
      if (!localBlacklist.value.includes(b)) localBlacklist.value.push(b)
    })
  }
  saveConfigs()
  showStatus('Filtros gerados pela IA foram aplicados com sucesso!')
}

defineExpose({
  applyAiGeneratedFilters
})

async function saveConfigs() {
  localStorage.setItem('scraper_nome_projeto', nomeProjeto.value)
  localStorage.setItem('scraper_blacklist', JSON.stringify(localBlacklist.value))
  localStorage.setItem('scraper_search_terms', JSON.stringify(localSearchTerms.value))
  
  if (props.user) {
    const { error } = await supabase.from('configuracoes_scraper').upsert(
      { 
        user_id: props.user.id, 
        nome_projeto: nomeProjeto.value,
        modo_paginacao: modoPaginacao.value,
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

    try {
      const { data, error: fnError } = await supabase.functions.invoke('trigger-github')
      if (fnError) throw fnError
      showStatus('Sinal enviado! Robô ativado no GitHub Actions.')
    } catch (apiErr) {
      console.error('Erro ao acionar o GitHub Actions via Edge Function:', apiErr)
      showStatus('Sinal gravado no Supabase. Aguardando escuta do robô.')
    }
  } else {
    showStatus('Faça login para disparar o robô!')
  }
}

function showStatus(msg) {
  statusMessage.value = msg
  setTimeout(() => statusMessage.value = '', 4000)
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
.config-panel { padding: 1.5rem; margin-bottom: 1.5rem; background: #ffffff; border: 1px solid #cbd5e1; border-radius: 16px; box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.06); }
.panel-header { display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
.panel-header h3 { margin: 0; color: #0f172a; font-size: 1.25rem; display: flex; align-items: center; gap: 0.8rem; }
.badge { font-size: 0.7rem; background: #eff6ff; color: #2563eb; padding: 0.2rem 0.6rem; border-radius: 99px; border: 1px solid #bfdbfe; font-weight: bold; }
.btn-toggle { background: transparent; border: none; color: #64748b; cursor: pointer; font-size: 0.9rem; font-weight: bold; }

.mt-3 { margin-top: 1.2rem; }
.form-group { margin-bottom: 1.4rem; }
.form-group label { display: block; color: #334155; font-size: 0.9rem; margin-bottom: 0.5rem; font-weight: 600; }
.section-label { font-size: 0.95rem !important; color: #0f172a !important; font-weight: 700 !important; }

.mode-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem; }
.mode-options { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-top: 0.5rem; }
.mode-card { display: flex; align-items: flex-start; gap: 0.8rem; background: #ffffff; border: 2px solid #e2e8f0; padding: 1rem; border-radius: 10px; cursor: pointer; transition: all 0.2s ease; }
.mode-card:hover { border-color: #93c5fd; }
.mode-card.active { border-color: #2563eb; background: #eff6ff; }
.mode-info strong { display: block; font-size: 0.9rem; color: #0f172a; margin-bottom: 0.2rem; }
.mode-info p { font-size: 0.8rem; color: #64748b; margin: 0; line-height: 1.3; }

.auth-upload-box { background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 10px; padding: 1rem; }
.file-upload-row { display: flex; align-items: center; gap: 1rem; margin-bottom: 0.4rem; }
.file-input { font-size: 0.85rem; color: #334155; }
.auth-file-status { font-weight: 700; color: #059669; font-size: 0.85rem; }
.help-text { font-size: 0.78rem; color: #64748b; display: block; }

.tag-input-container { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; background: #f8fafc; padding: 0.8rem; border-radius: 8px; border: 1px solid #cbd5e1; }
.tag { padding: 0.3rem 0.6rem; border-radius: 6px; font-size: 0.85rem; font-weight: 600; display: flex; align-items: center; gap: 0.4rem; color: #fff; }
.bg-blue { background: #2563eb; }
.bg-red { background: #dc2626; }
.close-btn { background: none; border: none; color: white; cursor: pointer; font-size: 0.9rem; padding: 0; opacity: 0.8; }
.close-btn:hover { opacity: 1; }

.glass-input { background: #ffffff; border: 1px solid #cbd5e1; color: #0f172a; padding: 0.6rem 1rem; border-radius: 8px; outline: none; }
.glass-input.inline { background: transparent; border: none; flex: 1; min-width: 200px; padding: 0; }
.glass-input.full-width { width: 100%; display: block; }
.glass-input:focus { border-color: #2563eb; }

.status-tracker-box { background: #f0fdf4; border: 1px solid #bbf7d0; padding: 1rem; border-radius: 10px; margin-top: 1rem; }
.tracker-header { display: flex; align-items: center; gap: 0.5rem; color: #166534; font-size: 0.9rem; margin-bottom: 0.3rem; }
.tracker-msg { margin: 0; font-size: 0.88rem; color: #15803d; font-weight: 600; }

.actions { display: flex; gap: 1rem; align-items: center; margin-top: 1.5rem; flex-wrap: wrap; }
.btn { padding: 0.65rem 1.2rem; border-radius: 8px; font-weight: 700; cursor: pointer; transition: all 0.2s ease; border: none; display: flex; align-items: center; gap: 0.5rem; font-size: 0.9rem; }
.btn.primary { background: #2563eb; color: #ffffff; }
.btn.primary:hover:not(:disabled) { background: #1d4ed8; }
.btn.danger { background: #dc2626; color: #ffffff; }
.btn.danger:hover:not(:disabled) { background: #b91c1c; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }

.spinner-inline { width: 16px; height: 16px; border: 2px solid rgba(255, 255, 255, 0.4); border-top-color: #ffffff; border-radius: 50%; animation: spin 1s linear infinite; }
.spinner-inline.green { border-color: rgba(22, 101, 52, 0.3); border-top-color: #166534; }
@keyframes spin { to { transform: rotate(360deg); } }

.status-msg { color: #059669; font-weight: 700; font-size: 0.9rem; }

.slide-fade-enter-active, .slide-fade-leave-active { transition: all 0.3s ease; }
.slide-fade-enter-from, .slide-fade-leave-to { opacity: 0; transform: translateY(-10px); }
</style>
