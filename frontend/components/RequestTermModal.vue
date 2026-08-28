<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-card glass-panel animate-scale-up">
      <!-- Header do Modal -->
      <div class="modal-header">
        <div class="header-left">
          <div class="icon-badge">{{ existingRequest ? '✏️' : '💡' }}</div>
          <div>
            <h3>{{ existingRequest ? t('request_term.title_edit', 'Editar Solicitação de Termo') : t('request_term.title', 'Solicitar Novo Termo / Nicho') }}</h3>
            <p class="subtitle">{{ existingRequest ? t('request_term.subtitle_edit', 'Você já possui uma solicitação enviada. Você pode editar os detalhes ou cancelar seu pedido.') : t('request_term.subtitle', 'Peça ao administrador para incluir novos termos ou produtos no monitoramento do robô.') }}</p>
          </div>
        </div>
        <button class="close-btn" @click="$emit('close')" title="Fechar">✕</button>
      </div>

      <!-- Banner de Solicitação Existente -->
      <div v-if="existingRequest" class="pending-notice-banner">
        <span>🕒 <strong>Status:</strong> Aguardando análise do Administrador (enviada em {{ formatDate(existingRequest.data_solicitacao) }})</span>
      </div>

      <!-- Formulário de Solicitação -->
      <form @submit.prevent="submitRequest" class="modal-body">
        <div class="form-group">
          <label class="form-label">
            {{ t('request_term.term_label', 'Palavra-chave ou Produto Desejado:') }} <span class="required">*</span>
          </label>
          <input 
            type="text" 
            v-model="term" 
            :placeholder="t('request_term.term_placeholder', 'Ex: topo de bolo formatura medicina')" 
            class="glass-input" 
            required 
            maxlength="60"
          />
          <small class="hint-text">{{ t('request_term.term_hint', 'Termo que será buscado no Mercado Livre e Shopee.') }}</small>
        </div>

        <div class="form-group">
          <label class="form-label">
            {{ t('request_term.niche_label', 'Nicho / Categoria (Opcional):') }}
          </label>
          <input 
            type="text" 
            v-model="niche" 
            :placeholder="t('request_term.niche_placeholder', 'Ex: Biscuit, Velas, Lembrancinhas...')" 
            class="glass-input" 
            maxlength="50"
          />
        </div>

        <div class="form-group">
          <label class="form-label">
            {{ t('request_term.reason_label', 'Motivo ou Observação (Opcional):') }}
          </label>
          <textarea 
            v-model="reason" 
            :placeholder="t('request_term.reason_placeholder', 'Ex: Estamos notando alta demanda de clientes para esse tema...')" 
            class="glass-textarea" 
            rows="3"
            maxlength="200"
          ></textarea>
        </div>

        <!-- Banner Informativo -->
        <div class="info-alert">
          <span class="info-icon">ℹ️</span>
          <span>{{ t('request_term.info_note', 'Sua solicitação será analisada pelo administrador. Assim que aprovada, os anúncios começarão a ser monitorados diariamente.') }}</span>
        </div>

        <!-- Ações -->
        <div class="modal-footer">
          <button 
            v-if="existingRequest" 
            type="button" 
            class="btn-delete-request" 
            :disabled="isCancelling || isSubmitting"
            @click="cancelRequest"
          >
            <span v-if="isCancelling">⏳ Cancelando...</span>
            <span v-else>🗑️ Cancelar Pedido</span>
          </button>
          
          <button type="button" class="btn-cancel" @click="$emit('close')">
            {{ t('request_term.cancel', 'Fechar') }}
          </button>
          
          <button type="submit" class="btn-submit" :disabled="isSubmitting || isCancelling || !term.trim()">
            <span v-if="isSubmitting">⏳ {{ t('request_term.sending', 'Enviando...') }}</span>
            <span v-else>{{ existingRequest ? '💾 Atualizar Solicitação' : '🚀 ' + t('request_term.send', 'Enviar Solicitação') }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAppI18n } from '~/composables/useAppI18n'
import { useSupabase } from '~/composables/useSupabase'

const { t, locale } = useAppI18n()
const supabase = useSupabase()

const props = defineProps({
  user: { type: Object, default: null }
})

const emit = defineEmits(['close', 'toast'])

const term = ref('')
const niche = ref('')
const reason = ref('')
const existingRequest = ref(null)
const isSubmitting = ref(false)
const isCancelling = ref(false)

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString(locale.value === 'pt' ? 'pt-BR' : 'en-US', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

async function loadExistingRequest() {
  const userId = props.user?.id
  if (!userId) return

  try {
    const { data: cfg } = await supabase
      .from('configuracoes_scraper')
      .select('regras_categoria')
      .eq('user_id', userId)
      .limit(1)
      .maybeSingle()

    if (cfg?.regras_categoria && typeof cfg.regras_categoria === 'object' && cfg.regras_categoria.solicitacao_pendente) {
      const req = cfg.regras_categoria.solicitacao_pendente
      existingRequest.value = req
      term.value = req.termo || ''
      niche.value = req.nicho || ''
      reason.value = req.motivo || ''
    }
  } catch (e) {
    console.warn('Erro ao verificar solicitacao existente:', e)
  }
}

async function submitRequest() {
  if (!term.value.trim() || isSubmitting.value) return

  isSubmitting.value = true
  try {
    const { data: { session } } = await supabase.auth.getSession()
    const token = session?.access_token || ''

    const headers = {}
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const res = await $fetch('/api/request-term', {
      method: 'POST',
      headers,
      body: {
        userId: props.user?.id,
        termo: term.value.trim(),
        nicho: niche.value.trim(),
        motivo: reason.value.trim()
      }
    })

    emit('toast', {
      type: 'success',
      title: t('request_term.toast_success_title', 'Solicitação Enviada!'),
      message: res?.message || t('request_term.toast_success_msg', 'Seu pedido de novo termo foi enviado com sucesso ao administrador.')
    })
    emit('close')
  } catch (err) {
    emit('toast', {
      type: 'error',
      title: t('request_term.toast_error_title', 'Erro ao Solicitar'),
      message: err?.data?.statusMessage || err?.message || 'Falha ao enviar solicitação.'
    })
  } finally {
    isSubmitting.value = false
  }
}

async function cancelRequest() {
  if (!confirm('Deseja realmente cancelar sua solicitação de termo?') || isCancelling.value) return

  isCancelling.value = true
  try {
    const { data: { session } } = await supabase.auth.getSession()
    const token = session?.access_token || ''

    const headers = {}
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    await $fetch('/api/request-term', {
      method: 'POST',
      headers,
      body: {
        userId: props.user?.id,
        action: 'cancel'
      }
    })

    emit('toast', {
      type: 'info',
      title: 'Solicitação Cancelada',
      message: 'Seu pedido de novo termo foi cancelado.'
    })
    emit('close')
  } catch (err) {
    emit('toast', {
      type: 'error',
      title: 'Erro',
      message: err?.data?.statusMessage || err?.message || 'Falha ao cancelar solicitação.'
    })
  } finally {
    isCancelling.value = false
  }
}

onMounted(() => {
  loadExistingRequest()
})
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(6px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.modal-card {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 20px;
  width: 100%;
  max-width: 520px;
  box-shadow: 0 20px 40px -10px rgba(15, 23, 42, 0.25);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 1.2rem 1.5rem;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.icon-badge {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  flex-shrink: 0;
}

.modal-header h3 {
  margin: 0 0 0.2rem 0;
  font-size: 1.15rem;
  color: #0f172a;
}

.subtitle {
  margin: 0;
  font-size: 0.82rem;
  color: #64748b;
  line-height: 1.35;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 1.2rem;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.close-btn:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.modal-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-label {
  font-size: 0.84rem;
  font-weight: 700;
  color: #334155;
}

.required {
  color: #ef4444;
}

.glass-input, .glass-textarea {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  padding: 0.65rem 0.9rem;
  font-size: 0.9rem;
  color: #0f172a;
  outline: none;
  transition: all 0.2s ease;
  font-family: inherit;
}

.glass-input:focus, .glass-textarea:focus {
  border-color: #2563eb;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}

.hint-text {
  font-size: 0.75rem;
  color: #64748b;
}

.info-alert {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 10px;
  padding: 0.65rem 0.9rem;
  display: flex;
  gap: 0.6rem;
  align-items: flex-start;
  font-size: 0.8rem;
  color: #166534;
  line-height: 1.35;
}

.info-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.8rem;
  margin-top: 0.5rem;
}

.btn-cancel {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #475569;
  padding: 0.6rem 1.1rem;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.btn-submit {
  background: #2563eb;
  border: 1px solid #1d4ed8;
  color: #ffffff;
  padding: 0.6rem 1.3rem;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
}

.btn-submit:hover:not(:disabled) {
  background: #1d4ed8;
  transform: translateY(-1px);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.pending-notice-banner {
  background: #fef3c7;
  border-bottom: 1px solid #fde68a;
  padding: 0.6rem 1.5rem;
  font-size: 0.82rem;
  color: #92400e;
}

.btn-delete-request {
  background: #fff1f2;
  border: 1px solid #fecdd3;
  color: #e11d48;
  padding: 0.6rem 1rem;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-right: auto;
}

.btn-delete-request:hover:not(:disabled) {
  background: #ffe4e6;
  border-color: #fda4af;
  color: #be123c;
}

@keyframes scaleUp {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.animate-scale-up {
  animation: scaleUp 0.2s ease forwards;
}
</style>
