<template>
  <Teleport to="body">
    <div v-if="isOpen" class="modal-overlay" @click.self="close">
      <div class="modal-content glass-panel animate-scale">
        <!-- Header -->
        <div class="modal-header">
          <div class="modal-title-box">
            <span class="badge-tag">⚙️ {{ t('keywords.badge', 'Configurações de Extração') }}</span>
            <h3>🎯 {{ t('keywords.title', 'Gerenciador de Palavras-Chave & Blacklist') }}</h3>
            <p class="subtitle">{{ t('keywords.subtitle', 'Defina quais termos o robô deve monitorar e quais palavras deve descartar automaticamente.') }}</p>
          </div>
          <button class="close-btn" @click="close" title="Fechar janela">×</button>
        </div>

        <div class="modal-body">
          <!-- Nicho do Negócio -->
          <div class="form-section">
            <div class="section-header-flex">
              <label class="section-label">
                🏷️ {{ t('keywords.niche_label', 'Seu Nicho de Mercado / Segmento:') }}
              </label>
              <span class="char-counter" :class="{ 'char-warn': niche.length >= 50 }">
                {{ niche.length }} / 60 {{ t('keywords.characters', 'caracteres') }}
              </span>
            </div>
            <div class="input-row">
              <input 
                v-model="niche" 
                type="text" 
                maxlength="60"
                class="input-field" 
                :placeholder="t('keywords.niche_placeholder', 'Ex: Bijuterias, Velas Decorativas, Artesanato...')" 
              />
              <button 
                type="button" 
                class="btn-ai-magic" 
                :disabled="isLoadingAi || !niche.trim() || terms.length >= MAX_TERMS || aiCooldown > 0" 
                @click="generateAiSuggestions"
              >
                <span v-if="isLoadingAi" class="loading-spin">⏳ {{ t('keywords.btn_ai_loading', 'Consultando IA...') }}</span>
                <span v-else-if="aiCooldown > 0">{{ t('keywords.cooldown_wait', '⏳ Aguarde {sec}s').replace('{sec}', aiCooldown) }}</span>
                <span v-else>✨ {{ t('keywords.btn_ai_suggest', 'Gerar Termos com IA') }}</span>
              </button>
            </div>
            <div class="quota-info-row">
              <small>⚡ {{ t('keywords.ai_security_limit', 'Limite da IA (Admin): 10 consultas por dia (restantes: {count})').replace('{count}', quotaRemaining ?? 10) }}</small>
            </div>
          </div>

          <!-- Solicitações de Novos Termos Enviadas por Clientes (Se houver) -->
          <div v-if="clientRequests.length > 0" class="client-requests-box animate-fade-in">
            <div class="requests-header">
              <div class="header-badge-row">
                <span class="requests-badge">📬 Solicitações de Clientes ({{ clientRequests.length }})</span>
                <small class="requests-sub">Termos pedidos pelos clientes para você aprovar e incluir no robô:</small>
              </div>
            </div>
            <div class="requests-grid">
              <div v-for="req in clientRequests" :key="req.id" class="request-item-card">
                <div class="req-left">
                  <div class="req-title-row">
                    <strong class="req-term">🔍 {{ req.termo }}</strong>
                    <span v-if="req.nicho" class="req-nicho-tag">{{ req.nicho }}</span>
                  </div>
                  <p class="req-reason" v-if="req.motivo">"{{ req.motivo }}"</p>
                  <small class="req-meta">👤 {{ req.solicitante_email || 'Cliente' }}</small>
                </div>
                <div class="req-actions">
                  <button 
                    type="button" 
                    class="btn-req-approve" 
                    :disabled="terms.length >= MAX_TERMS"
                    @click="approveClientRequest(req)" 
                    title="Aprovar e adicionar aos termos ativos"
                  >
                    ✓ Aprovar
                  </button>
                  <button 
                    type="button" 
                    class="btn-req-reject" 
                    @click="rejectClientRequest(req)" 
                    title="Recusar solicitação"
                  >
                    ✕
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Sugestões da IA (Se houver) -->
          <div v-if="aiSuggestions.length > 0" class="ai-suggestions-box animate-fade-in">
            <div class="ai-header">
              <span class="ai-badge">🤖 {{ t('keywords.ai_suggestions_title', 'Sugestões Estratégicas por IA') }}</span>
              <div class="ai-header-actions">
                <button 
                  type="button" 
                  class="btn-add-all-sug" 
                  :disabled="terms.length >= MAX_TERMS" 
                  @click="addAllSuggestions"
                >
                  {{ t('keywords.btn_add_all', '+ Adicionar Todas') }}
                </button>
                <button type="button" class="btn-clear-suggestions" @click="aiSuggestions = []">
                  {{ t('keywords.clear_suggestions', 'Limpar sugestões') }}
                </button>
              </div>
            </div>
            <div class="suggestions-grid">
              <div 
                v-for="(sug, index) in aiSuggestions" 
                :key="index" 
                class="suggestion-card"
              >
                <div class="sug-info">
                  <strong>{{ sug.termo }}</strong>
                  <small>{{ sug.motivo }}</small>
                </div>
                <button 
                  type="button" 
                  class="btn-add-sug" 
                  :disabled="terms.length >= MAX_TERMS || terms.includes(sug.termo)"
                  @click="addSuggestedTerm(sug.termo)"
                >
                  {{ terms.includes(sug.termo) ? t('keywords.already_added', '✓ Já Adicionado') : t('keywords.add', '+ Adicionar') }}
                </button>
              </div>
            </div>
          </div>

          <!-- Termos Ativos para Raspagem -->
          <div class="form-section">
            <div class="section-header-flex">
              <div class="header-left-flex">
                <label class="section-label">
                  🔎 {{ t('keywords.active_terms_label', 'Termos de Busca Ativos (Monitorados):') }}
                </label>
                <button 
                  v-if="terms.length > 0" 
                  type="button" 
                  class="btn-clear-inline" 
                  @click="clearAllTerms"
                  title="Remover todos os termos ativos"
                >
                  🗑️ {{ t('keywords.clear_terms', 'Limpar Todos') }}
                </button>
              </div>
              <div class="term-limit-counter" :class="{ 'limit-warn': terms.length >= 12, 'limit-danger': terms.length >= MAX_TERMS }">
                <span>{{ terms.length }} / {{ MAX_TERMS }} {{ t('keywords.terms_unit', 'termos') }}</span>
                <div class="progress-bar-bg">
                  <div class="progress-bar-fill" :style="{ width: `${(terms.length / MAX_TERMS) * 100}%` }"></div>
                </div>
              </div>
            </div>

            <!-- Tags Ativas -->
            <div class="tags-container">
              <span 
                v-for="(term, idx) in terms" 
                :key="idx" 
                class="tag-pill active-term"
              >
                {{ term }}
                <button type="button" class="btn-remove-tag" @click="removeTerm(idx)">×</button>
              </span>
              <span v-if="terms.length === 0" class="empty-tags-hint">
                {{ t('keywords.empty_terms_hint', 'Nenhum termo cadastrado. Digite termos abaixo ou use a IA acima para preencher.') }}
              </span>
            </div>

            <!-- Adicionar Novo Termo -->
            <div class="add-tag-row">
              <input 
                v-model="newTermInput" 
                type="text" 
                class="input-field" 
                :placeholder="t('keywords.new_term_placeholder', 'Digite um novo termo e pressione Enter...')"
                :disabled="terms.length >= MAX_TERMS"
                @keyup.enter="addTerm"
              />
              <button 
                type="button" 
                class="btn-add" 
                :disabled="!newTermInput.trim() || terms.length >= MAX_TERMS" 
                @click="addTerm"
              >
                + {{ t('keywords.btn_add_term', 'Adicionar') }}
              </button>
            </div>
            <small v-if="terms.length >= MAX_TERMS" class="limit-error-msg">
              {{ t('keywords.limit_error', '⚠️ Limite de segurança de {max} termos atingido. Remova um termo para adicionar novos.').replace('{max}', MAX_TERMS) }}
            </small>
          </div>

          <!-- Blacklist / Palavras Negativas -->
          <div class="form-section">
            <div class="section-header-flex">
              <label class="section-label">
                🚫 {{ t('keywords.blacklist_label', 'Palavras Negativas / Blacklist (Filtro de Descarte):') }}
                <span class="label-hint">{{ t('keywords.blacklist_hint', 'Anúncios contendo estas palavras serão automaticamente ignorados.') }}</span>
              </label>
              <button 
                v-if="blacklist.length > 0" 
                type="button" 
                class="btn-clear-inline btn-clear-danger" 
                @click="clearAllBlacklist"
                title="Remover todas as palavras negativas"
              >
                🗑️ {{ t('keywords.clear_blacklist', 'Limpar Blacklist') }}
              </button>
            </div>

            <!-- Tags Blacklist -->
            <div class="tags-container blacklist-container">
              <span 
                v-for="(item, idx) in blacklist" 
                :key="idx" 
                class="tag-pill blacklist-term"
              >
                {{ item }}
                <button type="button" class="btn-remove-tag" @click="removeBlacklist(idx)">×</button>
              </span>
              <span v-if="blacklist.length === 0" class="empty-tags-hint">
                {{ t('keywords.empty_blacklist_hint', 'Nenhuma palavra negativa cadastrada.') }}
              </span>
            </div>

            <!-- Adicionar Palavra Negativa -->
            <div class="add-tag-row">
              <input 
                v-model="newBlacklistInput" 
                type="text" 
                class="input-field" 
                :placeholder="t('keywords.new_blacklist_placeholder', 'Ex: racao, molde, silicone, papel...')"
                @keyup.enter="addBlacklist"
              />
              <button 
                type="button" 
                class="btn-add btn-add-blacklist" 
                :disabled="!newBlacklistInput.trim()" 
                @click="addBlacklist"
              >
                + {{ t('keywords.btn_add_blacklist', 'Bloquear Palavra') }}
              </button>
            </div>
          </div>
        </div>

        <!-- Footer com Botão Salvar -->
        <div class="modal-footer">
          <button type="button" class="btn-secondary" @click="close">
            {{ t('keywords.cancel', 'Cancelar') }}
          </button>
          <button 
            type="button" 
            class="btn-primary-save" 
            :disabled="isSaving || terms.length === 0" 
            @click="saveConfigurations"
          >
            <span v-if="!isSaving">💾 {{ t('keywords.btn_save', 'Salvar Configurações no Banco') }}</span>
            <span v-else>⏳ {{ t('keywords.btn_saving', 'Salvando...') }}</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useSupabase } from '~/composables/useSupabase'
import { useAppI18n } from '~/composables/useAppI18n'
import { useToast } from '~/composables/useToast'
import { useConfirmDialog } from '~/composables/useConfirmDialog'

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  user: { type: Object, default: null }
})

const emit = defineEmits(['close', 'saved'])

const { t } = useAppI18n()
const supabase = useSupabase()
const toast = useToast()
const { askConfirm } = useConfirmDialog()

const MAX_TERMS = 15

const niche = ref('')
const terms = ref([])
const blacklist = ref([])
const clientRequests = ref([])
const newTermInput = ref('')
const newBlacklistInput = ref('')
const aiSuggestions = ref([])

const isLoadingAi = ref(false)
const isSaving = ref(false)
const aiCooldown = ref(0)
const quotaRemaining = ref(null)
let cooldownTimer = null

function startCooldown(seconds = 10) {
  aiCooldown.value = seconds
  if (cooldownTimer) clearInterval(cooldownTimer)
  cooldownTimer = setInterval(() => {
    if (aiCooldown.value > 0) {
      aiCooldown.value -= 1
    } else {
      clearInterval(cooldownTimer)
    }
  }, 1000)
}

// Carrega configurações do usuário no Supabase
async function loadUserKeywords() {
  try {
    const { data: { user: currentUser } } = await supabase.auth.getUser()
    const userId = currentUser?.id || props.user?.id

    if (!userId) {
      terms.value = []
      blacklist.value = []
      clientRequests.value = []
      niche.value = ''
      return
    }

    const { data, error } = await supabase
      .from('configuracoes_scraper')
      .select('termos_busca, blacklist, solicitacoes_termos')
      .eq('user_id', userId)
      .limit(1)
      .maybeSingle()

    if (data && (data.termos_busca || data.blacklist || data.solicitacoes_termos)) {
      terms.value = Array.isArray(data.termos_busca) ? [...data.termos_busca] : []
      blacklist.value = Array.isArray(data.blacklist) ? [...data.blacklist] : []
      clientRequests.value = Array.isArray(data.solicitacoes_termos) ? [...data.solicitacoes_termos] : []
    } else {
      // Usuário novo: inicia completamente limpo
      terms.value = []
      blacklist.value = []
      clientRequests.value = []
      niche.value = ''
    }
  } catch (e) {
    console.warn('Erro ao carregar termos do usuário:', e)
    terms.value = []
    blacklist.value = []
    clientRequests.value = []
    niche.value = ''
  }
}

function approveClientRequest(req) {
  if (terms.value.length >= MAX_TERMS) {
    toast.warning(t('keywords.limit_error', '⚠️ Limite de segurança de {max} termos atingido.').replace('{max}', MAX_TERMS), t('keywords.limit_reached', 'Limite Atingido'))
    return
  }
  if (!terms.value.includes(req.termo)) {
    terms.value.push(req.termo)
  }
  clientRequests.value = clientRequests.value.filter(r => r.id !== req.id)
  toast.success(`Termo "${req.termo}" aprovado e adicionado à lista! Clique em Salvar para persistir.`)
}

function rejectClientRequest(req) {
  clientRequests.value = clientRequests.value.filter(r => r.id !== req.id)
  toast.info(`Solicitação do termo "${req.termo}" removida.`)
}

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    loadUserKeywords()
    aiSuggestions.value = []
  }
})

onMounted(() => {
  if (props.isOpen) {
    loadUserKeywords()
  }
})

function close() {
  emit('close')
}

async function clearAllTerms() {
  const ok = await askConfirm({
    title: t('keywords.confirm_clear_terms_title', 'Limpar todos os termos?'),
    message: t('keywords.confirm_clear_terms_msg', 'Deseja realmente remover todos os termos de busca da sua lista de monitoramento?'),
    confirmText: t('keywords.confirm_clear_terms_btn', 'Sim, limpar todos'),
    danger: true
  })
  if (ok) {
    terms.value = []
    toast.info(t('keywords.toast_terms_cleared', 'Lista de termos de busca esvaziada.'))
  }
}

async function clearAllBlacklist() {
  const ok = await askConfirm({
    title: t('keywords.confirm_clear_bl_title', 'Limpar palavras negativas?'),
    message: t('keywords.confirm_clear_bl_msg', 'Deseja realmente remover todas as palavras da sua blacklist?'),
    confirmText: t('keywords.confirm_clear_bl_btn', 'Sim, limpar blacklist'),
    danger: true
  })
  if (ok) {
    blacklist.value = []
    toast.info(t('keywords.toast_blacklist_cleared', 'Blacklist esvaziada.'))
  }
}

function addTerm() {
  const val = newTermInput.value.trim().toLowerCase()
  if (!val) return
  if (terms.value.length >= MAX_TERMS) {
    toast.warning(t('keywords.limit_error', '⚠️ Limite de segurança de {max} termos atingido.').replace('{max}', MAX_TERMS), t('keywords.limit_reached', 'Limite Atingido'))
    return
  }
  if (!terms.value.includes(val)) {
    terms.value.push(val)
  }
  newTermInput.value = ''
}

function removeTerm(idx) {
  terms.value.splice(idx, 1)
}

function addBlacklist() {
  const val = newBlacklistInput.value.trim().toLowerCase()
  if (!val) return
  if (!blacklist.value.includes(val)) {
    blacklist.value.push(val)
  }
  newBlacklistInput.value = ''
}

function removeBlacklist(idx) {
  blacklist.value.splice(idx, 1)
}

function addSuggestedTerm(termo) {
  if (terms.value.length >= MAX_TERMS) {
    toast.warning(t('keywords.limit_error', '⚠️ Limite de segurança de {max} termos atingido.').replace('{max}', MAX_TERMS), t('keywords.limit_reached', 'Limite Atingido'))
    return
  }
  if (!terms.value.includes(termo)) {
    terms.value.push(termo)
    toast.success(t('keywords.toast_term_added', 'Termo "{term}" adicionado ao monitoramento!').replace('{term}', termo))
  }
}

function addAllSuggestions() {
  if (terms.value.length >= MAX_TERMS) {
    toast.warning(t('keywords.limit_error', '⚠️ Limite de segurança de {max} termos atingido.').replace('{max}', MAX_TERMS), t('keywords.limit_reached', 'Limite Atingido'))
    return
  }
  let addedCount = 0
  for (const sug of aiSuggestions.value) {
    if (terms.value.length >= MAX_TERMS) break
    if (!terms.value.includes(sug.termo)) {
      terms.value.push(sug.termo)
      addedCount++
    }
  }
  if (addedCount > 0) {
    toast.success(t('keywords.toast_all_added', '{count} sugestões foram adicionadas!').replace('{count}', addedCount), t('keywords.toast_saved_title', 'Sucesso'))
  }
}

async function generateAiSuggestions() {
  if (aiCooldown.value > 0) return
  isLoadingAi.value = true
  try {
    const remainingSlots = Math.max(1, MAX_TERMS - terms.value.length)
    const { data: { session } } = await supabase.auth.getSession()
    const headers = {}
    if (session?.access_token) {
      headers.Authorization = `Bearer ${session.access_token}`
    }

    const res = await $fetch('/api/ai-keywords', {
      method: 'POST',
      headers,
      body: {
        niche: niche.value || 'Geral',
        currentTerms: terms.value,
        blacklist: blacklist.value,
        maxSuggestions: Math.min(8, remainingSlots)
      }
    })

    if (res?.remainingQuota !== undefined) {
      quotaRemaining.value = res.remainingQuota
    }

    if (res?.sugestoes && Array.isArray(res.sugestoes)) {
      aiSuggestions.value = res.sugestoes
      startCooldown(20)
      toast.success(t('keywords.toast_all_added', '{count} sugestões geradas!').replace('{count}', res.sugestoes.length), t('keywords.ai_suggestions_title', 'IA'))
    } else {
      toast.info(t('keywords.empty_terms_hint', 'Nenhuma nova sugestão retornada.'))
    }
  } catch (e) {
    console.error(e)
    const statusMsg = e?.data?.statusMessage || e?.message || ''
    if (statusMsg.startsWith('COOLDOWN:')) {
      const sec = statusMsg.split(':')[1]
      toast.warning(t('keywords.toast_cooldown_msg', 'Aguarde {sec}s').replace('{sec}', sec), t('keywords.toast_quota_title', 'Cota de IA'))
    } else if (statusMsg.startsWith('RATE_LIMIT:')) {
      const time = statusMsg.split(':')[1]
      toast.warning(t('keywords.toast_rate_limit_msg', 'Limite de segurança de IA atingido.').replace('{time}', time), t('keywords.toast_quota_title', 'Cota de IA'))
    } else {
      toast.warning(statusMsg || 'Erro ao consultar IA', t('keywords.toast_quota_title', 'Cota de IA'))
    }
  } finally {
    isLoadingAi.value = false
  }
}

async function saveConfigurations() {
  if (terms.value.length === 0) {
    toast.warning(t('keywords.empty_terms_hint', 'Por favor, mantenha pelo menos 1 termo ativo.'), t('keywords.limit_reached', 'Atenção'))
    return
  }
  isSaving.value = true
  try {
    const { data: { user: currentUser } } = await supabase.auth.getUser()
    const userId = currentUser?.id || props.user?.id

    if (!userId) {
      toast.error('Usuário não autenticado. Por favor, recarregue a página.')
      return
    }

    const { data: { session } } = await supabase.auth.getSession()
    const headers = {}
    if (session?.access_token) {
      headers.Authorization = `Bearer ${session.access_token}`
    }

    // Salva via API Server segura com validação de JWT Token
    const res = await $fetch('/api/save-keywords', {
      method: 'POST',
      headers,
      body: {
        userId,
        terms: terms.value,
        blacklist: blacklist.value,
        niche: niche.value,
        solicitacoes_termos: clientRequests.value
      }
    })

    if (!res?.success) {
      throw new Error('Falha na resposta do servidor.')
    }

    toast.success(t('keywords.toast_saved_success', 'Configurações e termos foram salvos com sucesso!'), t('keywords.toast_saved_title', 'Configurações Salvas'))
    emit('saved', { terms: terms.value, blacklist: blacklist.value, niche: niche.value, solicitacoes_termos: clientRequests.value })
    close()
  } catch (e) {
    console.error(e)
    const msg = e?.data?.statusMessage || e?.message || 'Erro desconhecido'
    toast.error('Erro ao salvar configurações no Supabase: ' + msg)
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(15, 23, 42, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 99999;
  backdrop-filter: blur(6px);
  padding: 1.5rem;
}

.modal-content {
  width: 100%;
  max-width: 820px;
  max-height: 88vh;
  overflow-y: auto;
  padding: 2rem;
  border-radius: 16px;
  position: relative;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  margin: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 1rem;
}

.modal-title-box {
  flex: 1;
  padding-right: 1rem;
}

.badge-tag {
  font-size: 0.75rem;
  font-weight: 700;
  color: #2563eb;
  background: #eff6ff;
  padding: 0.25rem 0.6rem;
  border-radius: 99px;
  border: 1px solid #bfdbfe;
  text-transform: uppercase;
  display: inline-block;
  margin-bottom: 0.4rem;
}

.modal-header h3 {
  margin: 0 0 0.3rem 0;
  color: #0f172a;
  font-size: 1.3rem;
  font-weight: 800;
}

.subtitle {
  margin: 0;
  font-size: 0.88rem;
  color: #64748b;
}

.close-btn {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #64748b;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  font-size: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  justify-content: center;
  align-items: center;
}

.close-btn:hover {
  background: #fee2e2;
  color: #dc2626;
}

.form-section {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.2rem;
  margin-bottom: 1.2rem;
}

.section-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.header-left-flex {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.btn-clear-inline {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #64748b;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 0.4rem;
}

.btn-clear-inline:hover {
  background: #fee2e2;
  color: #dc2626;
  border-color: #fca5a5;
}

.btn-clear-danger {
  margin-bottom: 0;
}

.char-counter {
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
}

.char-counter.char-warn {
  color: #d97706;
  font-weight: 700;
}

.quota-info-row {
  margin-top: 0.5rem;
  font-size: 0.78rem;
  color: #6d28d9;
  background: #f5f3ff;
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  display: inline-block;
}

.section-label {
  display: block;
  font-size: 0.95rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.label-hint {
  display: block;
  font-size: 0.8rem;
  color: #64748b;
  font-weight: 400;
  margin-top: 0.15rem;
}

.term-limit-counter {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.82rem;
  font-weight: 700;
  color: #059669;
}

.term-limit-counter.limit-warn {
  color: #d97706;
}

.term-limit-counter.limit-danger {
  color: #dc2626;
}

.progress-bar-bg {
  width: 70px;
  height: 8px;
  background: #e2e8f0;
  border-radius: 99px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: currentColor;
  border-radius: 99px;
  transition: width 0.3s ease;
}

.input-row {
  display: flex;
  gap: 0.6rem;
  align-items: center;
}

.input-field {
  flex: 1;
  padding: 0.6rem 0.9rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #0f172a;
  outline: none;
  background: #ffffff;
  transition: border-color 0.2s;
}

.input-field:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.btn-ai-magic {
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  color: #ffffff;
  border: none;
  padding: 0.6rem 1.1rem;
  border-radius: 8px;
  font-size: 0.88rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(109, 40, 217, 0.25);
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-ai-magic:hover:not(:disabled) {
  background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%);
  transform: translateY(-1px);
}

.btn-ai-magic:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.8rem;
  min-height: 40px;
  padding: 0.6rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.tag-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.75rem;
  border-radius: 99px;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.2s;
}

.active-term {
  background: #eff6ff;
  color: #1e40af;
  border: 1px solid #bfdbfe;
}

.blacklist-term {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.btn-remove-tag {
  background: none;
  border: none;
  color: inherit;
  font-size: 1.1rem;
  cursor: pointer;
  line-height: 1;
  padding: 0 0.15rem;
  opacity: 0.7;
}

.btn-remove-tag:hover {
  opacity: 1;
  font-weight: 800;
}

.empty-tags-hint {
  font-size: 0.85rem;
  color: #94a3b8;
  font-style: italic;
  display: flex;
  align-items: center;
}

.add-tag-row {
  display: flex;
  gap: 0.6rem;
}

.btn-add {
  background: #2563eb;
  color: #ffffff;
  border: none;
  padding: 0.6rem 1rem;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-add:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-add-blacklist {
  background: #dc2626;
}

.btn-add-blacklist:hover:not(:disabled) {
  background: #b91c1c;
}

.btn-add:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.limit-error-msg {
  color: #dc2626;
  font-weight: 600;
  margin-top: 0.4rem;
  display: block;
}

.ai-suggestions-box {
  background: #faf5ff;
  border: 1px solid #e9d5ff;
  border-radius: 12px;
  padding: 1.2rem;
  margin-bottom: 1.2rem;
}

.ai-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
}

.ai-badge {
  font-size: 0.85rem;
  font-weight: 700;
  color: #6b21a8;
}

.ai-header-actions {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.btn-add-all-sug {
  background: #7c3aed;
  color: #ffffff;
  border: none;
  font-size: 0.76rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-add-all-sug:hover:not(:disabled) {
  background: #6d28d9;
}

.btn-add-all-sug:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-clear-suggestions {
  background: none;
  border: none;
  color: #9333ea;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
}

.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.8rem;
}

.suggestion-card {
  background: #ffffff;
  border: 1px solid #d8b4fe;
  border-radius: 8px;
  padding: 0.8rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.6rem;
}

.sug-info {
  display: flex;
  flex-direction: column;
}

.sug-info strong {
  font-size: 0.88rem;
  color: #0f172a;
}

.sug-info small {
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.15rem;
}

.btn-add-sug {
  background: #f3e8ff;
  color: #7e22ce;
  border: 1px solid #d8b4fe;
  border-radius: 6px;
  padding: 0.35rem 0.6rem;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.btn-add-sug:hover:not(:disabled) {
  background: #7e22ce;
  color: #ffffff;
}

.btn-add-sug:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.8rem;
  border-top: 1px solid #e2e8f0;
  padding-top: 1.2rem;
  margin-top: 1rem;
}

.btn-secondary {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #475569;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-secondary:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.btn-primary-save {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  color: #ffffff;
  border: none;
  padding: 0.6rem 1.4rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.25);
  transition: all 0.2s;
}

.btn-primary-save:hover:not(:disabled) {
  background: linear-gradient(135deg, #047857 0%, #065f46 100%);
  transform: translateY(-1px);
}

.btn-primary-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.client-requests-box {
  background: #fdf4ff;
  border: 1px solid #f0abfc;
  border-radius: 12px;
  padding: 1.1rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  margin-bottom: 1.2rem;
}

.header-badge-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.requests-badge {
  background: #fae8ff;
  color: #a21caf;
  font-weight: 800;
  font-size: 0.82rem;
  padding: 0.25rem 0.6rem;
  border-radius: 99px;
  border: 1px solid #f5d0fe;
}

.requests-sub {
  color: #701a75;
  font-size: 0.8rem;
}

.requests-grid {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.request-item-card {
  background: #ffffff;
  border: 1px solid #f5d0fe;
  border-radius: 10px;
  padding: 0.75rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 5px rgba(162, 28, 175, 0.05);
}

.req-left {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  flex: 1;
}

.req-title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.req-term {
  color: #0f172a;
  font-size: 0.95rem;
}

.req-nicho-tag {
  font-size: 0.7rem;
  font-weight: 700;
  background: #f1f5f9;
  color: #475569;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.req-reason {
  margin: 0;
  font-size: 0.82rem;
  color: #475569;
  font-style: italic;
}

.req-meta {
  color: #94a3b8;
  font-size: 0.75rem;
}

.req-actions {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.btn-req-approve {
  background: #059669;
  color: #ffffff;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-req-approve:hover:not(:disabled) {
  background: #047857;
}

.btn-req-reject {
  background: #f1f5f9;
  color: #64748b;
  border: 1px solid #cbd5e1;
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-req-reject:hover {
  background: #fee2e2;
  color: #b91c1c;
  border-color: #fca5a5;
}

.animate-scale { animation: scaleIn 0.25s ease-out; }
@keyframes scaleIn { from { transform: scale(0.97); opacity: 0; } to { transform: scale(1); opacity: 1; } }
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>
