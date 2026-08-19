<template>
  <div class="glass-panel config-panel animate-fade-in" :class="{ 'is-collapsed': isCollapsed }">
    <div class="panel-header" @click="toggleCollapse">
      <h3>⚙️ Controle & Disparo do Robô Scraper <span class="badge">Nuvem Serverless</span></h3>
      <button class="btn-toggle">{{ isCollapsed ? '▼ Expandir' : '▲ Minimizar' }}</button>
    </div>
    
    <transition name="slide-fade">
      <div v-show="!isCollapsed" class="panel-content">
        <!-- Banner Especial de Alerta de Captcha -->
        <div v-if="isCaptchaAlert" class="captcha-alert-banner">
          <div class="captcha-alert-content">
            <div class="alert-icon-box">🚨</div>
            <div class="alert-text-box">
              <strong>DESAFIO ANTI-ROBÔ / CAPTCHA DETECTADO!</strong>
              <p>A Shopee ou Mercado Livre exigiu uma validação rápida. Clique ao lado para abrir o Chrome na sua tela, resolver em 10s e liberar o robô.</p>
            </div>
          </div>
          <button @click="triggerWebLogin('todos')" class="btn-resolve-captcha" :disabled="isLoggingIn">
            <span v-if="isLoggingIn">⏳ Abrindo Chrome...</span>
            <span v-else>🔑 Resolver Captcha Agora</span>
          </button>
        </div>

        <!-- 1. Nome do Projeto -->
        <div class="form-group mt-3">
          <label>Nome do Projeto / Nicho:</label>
          <input type="text" v-model="nomeProjeto" placeholder="Ex: Monitoramento de Nicho / E-commerce" class="glass-input full-width" :disabled="disparoPendente" />
        </div>

        <!-- 2. Autenticação & Conexão de Contas das Lojas (1-Clique) -->
        <div class="form-group auth-box">
          <label class="section-label">🔒 Autenticação & Conexão das Lojas:</label>
          <div class="auth-card-web">
            <div class="auth-info-text">
              <strong>🔑 Conexão Direta das Lojas (Mercado Livre & Shopee)</strong>
              <p>Clique no botão abaixo para abrir o Chrome na sua tela, fazer o login de forma segura e salvar a sessão no robô sem precisar usar o terminal.</p>
            </div>
            <button 
              @click="triggerWebLogin('todos')" 
              class="btn-login-web" 
              :disabled="isLoggingIn || disparoPendente"
            >
              <span v-if="isLoggingIn">⏳ Abrindo Navegador Chrome...</span>
              <span v-else>🔑 Conectar Minhas Contas (1-Clique)</span>
            </button>
          </div>
          <div class="privacy-note">
            <span class="lock-icon">🔒</span>
            <span><strong>Garantia de Privacidade & Segurança:</strong> Nós <u>NÃO</u> salvamos sua senha nem seus dados pessoais. O robô utiliza apenas os cookies anônimos de sessão no seu próprio navegador para navegar sem travamentos.</span>
          </div>
          <div v-if="loginStatusMsg" class="login-status-banner">
            {{ loginStatusMsg }}
          </div>
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

        <!-- 5. Produtos Excluídos / Bloqueados Manualmente -->
        <div class="form-group">
          <label>🚫 Produtos Bloqueados Manualmente (Excluídos da tabela):</label>
          <div v-if="localBlockedProducts.length === 0" class="empty-blocked-box">
            <span>Nenhum produto bloqueado manualmente até o momento.</span>
          </div>
          <div v-else class="blocked-items-list">
            <div v-for="(item, idx) in localBlockedProducts" :key="idx" class="blocked-item-card">
              <div class="blocked-item-info">
                <strong>{{ typeof item === 'string' ? item : item.titulo }}</strong>
                <small v-if="typeof item === 'object' && item.link" class="text-muted block-link">{{ item.link }}</small>
              </div>
              <button @click="unblockProduct(item)" class="btn-unblock" title="Reativar / Desbloquear este produto">🔓 Reativar</button>
            </div>
          </div>
        </div>

        <!-- Painel de Progresso do Robô em Tempo Real -->
        <transition name="fade">
          <div v-if="disparoPendente || statusScraper" :class="['status-tracker-box', { 'pulse-active': disparoPendente }]">
            <div class="tracker-header">
              <div class="spinner-inline green"></div>
              <strong>Status do Robô na Nuvem:</strong>
            </div>
            <p class="tracker-msg">{{ statusScraper || '🤖 Inicializando robô de raspagem na nuvem...' }}</p>
          </div>
        </transition>

        <!-- Ações -->
        <div class="actions">
          <button @click="saveConfigs" class="btn primary" :disabled="disparoPendente">💾 Salvar Preferências</button>
          
          <button @click="triggerScraper" class="btn danger" :disabled="disparoPendente">
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
import { ref, onMounted, watch, onUnmounted, computed } from 'vue'
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
const localBlockedProducts = ref([])
const localSearchTerms = ref([])
const newBlacklistTag = ref('')
const newSearchTag = ref('')
const statusMessage = ref('')
const authFileStatus = ref('')
const isCollapsed = ref(false) // Aberto por padrão na página de config

const isLoggingIn = ref(false)
const loginStatusMsg = ref('')

const isCaptchaAlert = computed(() => {
  const status = (statusScraper.value || '').toLowerCase()
  return status.includes('captcha') || status.includes('desafio') || status.includes('bloqueio') || status.includes('autentica')
})

async function triggerWebLogin(plataforma) {
  isLoggingIn.value = true
  loginStatusMsg.value = `⏳ Abrindo navegador Chrome para login no Mercado Livre e Shopee... Faça o login normalmente e feche a janela.`

  try {
    const res = await $fetch('/api/login-session', {
      method: 'POST',
      body: { plataforma }
    })
    if (res && res.success) {
      loginStatusMsg.value = `✅ Conexão e sessão atualizadas com sucesso!`
      showStatus('Sessão de login atualizada!')
    } else {
      loginStatusMsg.value = `⚠️ Aviso no login: ${res?.error || 'Navegador encerrado.'}`
    }
  } catch (err) {
    loginStatusMsg.value = `❌ Erro ao abrir navegador de login: ${err.message}`
  } finally {
    isLoggingIn.value = false
  }
}

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
  // Carrega lista de bloqueados localmente
  const savedBlocked = localStorage.getItem('scraper_blocked_products')
  if (savedBlocked) {
    try { localBlockedProducts.value = JSON.parse(savedBlocked) } catch (e) { localBlockedProducts.value = [] }
  }

  if (props.user) {
    const { data, error } = await supabase
      .from('configuracoes_scraper')
      .select('nome_projeto, blacklist, termos_busca, disparo_pendente, status_scraper, modo_paginacao, auth_state_meli, blocked_products')
      .eq('user_id', props.user.id)
      .single()
      
    if (data) {
      if (data.nome_projeto) nomeProjeto.value = data.nome_projeto
      if (data.modo_paginacao) modoPaginacao.value = data.modo_paginacao
      if (data.auth_state_meli) authFileStatus.value = '✅ Sessão salva no Supabase'
      localBlacklist.value = data.blacklist || []
      localSearchTerms.value = data.termos_busca || []
      if (data.blocked_products && Array.isArray(data.blocked_products)) {
        localBlockedProducts.value = data.blocked_products
        localStorage.setItem('scraper_blocked_products', JSON.stringify(data.blocked_products))
      }
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

async function unblockProduct(item) {
  const targetId = typeof item === 'string' ? item : (item.link || item.id || item.titulo)
  localBlockedProducts.value = localBlockedProducts.value.filter(p => {
    if (typeof p === 'string') return p !== targetId
    return p.link !== targetId && p.id !== targetId && p.titulo !== targetId
  })
  localStorage.setItem('scraper_blocked_products', JSON.stringify(localBlockedProducts.value))
  await saveConfigs()
  showStatus('Produto reativado com sucesso!')
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
  localStorage.setItem('scraper_blocked_products', JSON.stringify(localBlockedProducts.value))
  
  if (props.user) {
    const { error } = await supabase.from('configuracoes_scraper').upsert(
      { 
        user_id: props.user.id, 
        nome_projeto: nomeProjeto.value,
        modo_paginacao: modoPaginacao.value,
        blacklist: localBlacklist.value, 
        termos_busca: localSearchTerms.value,
        blocked_products: localBlockedProducts.value
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
  disparoPendente.value = true
  statusScraper.value = "🚀 Robô acionado no backend local! Extraindo dados no terminal..."
  showStatus("Disparo acionado com sucesso!")
  
  try {
    const res = await $fetch('/api/trigger-local', {
      method: 'POST',
      body: { plataforma: 'todos' }
    })
    if (res?.message) {
      showStatus(res.message, 6000)
    }
  } catch (err) {
    console.error("Erro no disparo local:", err)
    showStatus("❌ Erro ao acionar o robô local.", 6000)
  } finally {
    setTimeout(() => {
      disparoPendente.value = false
    }, 5000)
  }

  if (props.user) {
    await supabase.from('configuracoes_scraper').upsert(
      { user_id: props.user.id, disparo_pendente: true, status_scraper: statusScraper.value },
      { onConflict: 'user_id' }
    ).catch(e => console.warn(e))
  }
}

function showStatus(msg, duration = 4000) {
  statusMessage.value = msg
  setTimeout(() => statusMessage.value = '', duration)
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

.empty-blocked-box { background: #f8fafc; border: 1px dashed #cbd5e1; padding: 0.8rem 1rem; border-radius: 8px; font-size: 0.85rem; color: #64748b; font-style: italic; }
.blocked-items-list { display: flex; flex-direction: column; gap: 0.5rem; max-height: 220px; overflow-y: auto; background: #f8fafc; padding: 0.6rem; border-radius: 8px; border: 1px solid #cbd5e1; }
.blocked-item-card { display: flex; justify-content: space-between; align-items: center; background: #ffffff; border: 1px solid #e2e8f0; padding: 0.6rem 0.8rem; border-radius: 8px; gap: 0.8rem; }
.blocked-item-info { display: flex; flex-direction: column; overflow: hidden; }
.blocked-item-info strong { font-size: 0.85rem; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.block-link { font-size: 0.72rem; color: #64748b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.btn-unblock { background: #f0fdf4; border: 1px solid #86efac; color: #166534; padding: 0.35rem 0.7rem; border-radius: 6px; font-size: 0.8rem; font-weight: 700; cursor: pointer; transition: all 0.2s ease; flex-shrink: 0; }
.btn-unblock:hover { background: #dcfce7; border-color: #4ade80; color: #15803d; }

.auth-card-web { background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border: 1px solid #7dd3fc; border-radius: 12px; padding: 1.2rem; display: flex; justify-content: space-between; align-items: center; gap: 1rem; margin-top: 0.5rem; }
.auth-info-text strong { display: block; color: #0369a1; font-size: 0.95rem; margin-bottom: 0.3rem; }
.auth-info-text p { margin: 0; font-size: 0.83rem; color: #0284c7; line-height: 1.4; }
.btn-login-web { background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; border: none; padding: 0.75rem 1.3rem; border-radius: 8px; font-weight: 700; cursor: pointer; transition: all 0.2s ease; white-space: nowrap; font-size: 0.9rem; box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.3); }
.btn-login-web:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 6px 12px -2px rgba(2, 132, 199, 0.4); }
.btn-login-web:disabled { opacity: 0.7; cursor: not-allowed; }
.login-status-banner { background: #e0f2fe; border-left: 4px solid #0284c7; color: #0369a1; font-weight: 600; padding: 0.8rem 1rem; border-radius: 6px; font-size: 0.88rem; margin-top: 0.8rem; }
.privacy-note { display: flex; align-items: flex-start; gap: 0.5rem; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.6rem 0.8rem; font-size: 0.8rem; color: #64748b; margin-top: 0.6rem; line-height: 1.4; }
.privacy-note u { text-decoration: underline; color: #0f172a; }

.captcha-alert-banner { background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); border: 2px solid #ef4444; border-radius: 12px; padding: 1rem 1.2rem; display: flex; justify-content: space-between; align-items: center; gap: 1rem; margin-bottom: 1.2rem; box-shadow: 0 4px 14px rgba(239, 68, 68, 0.25); animation: pulse-alert 2s infinite; }
.captcha-alert-content { display: flex; align-items: center; gap: 0.8rem; }
.alert-icon-box { font-size: 1.6rem; }
.alert-text-box strong { display: block; color: #991b1b; font-size: 0.95rem; }
.alert-text-box p { margin: 0.2rem 0 0 0; color: #b91c1c; font-size: 0.83rem; line-height: 1.3; }
.btn-resolve-captcha { background: #dc2626; color: #ffffff; border: none; padding: 0.7rem 1.2rem; border-radius: 8px; font-weight: 700; cursor: pointer; transition: all 0.2s ease; font-size: 0.88rem; white-space: nowrap; box-shadow: 0 4px 6px -1px rgba(220, 38, 38, 0.4); }
.btn-resolve-captcha:hover:not(:disabled) { background: #b91c1c; transform: scale(1.03); }

@keyframes pulse-alert {
  0% { border-color: #ef4444; box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
  70% { border-color: #f87171; box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
  100% { border-color: #ef4444; box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}

.slide-fade-enter-active, .slide-fade-leave-active { transition: all 0.3s ease; }
.slide-fade-enter-from, .slide-fade-leave-to { opacity: 0; transform: translateY(-10px); }
</style>
