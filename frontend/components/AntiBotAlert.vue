<template>
  <transition name="fade">
    <div v-if="alertaVisivel" class="antibot-alert glass-panel">
      <div class="alert-content">
        <div class="alert-icon">
          <AlertTriangle :size="20" />
        </div>
        <div class="alert-text">
          <strong>{{ t('alert.anti_bot_title', 'Alerta de Coleta Automática') }}</strong>
          <p>{{ customMensagem || t('alert.anti_bot_desc', 'O robô de coleta encontrou uma verificação de segurança na última execução.') }}</p>
        </div>
      </div>
      <button @click="dismiss" class="btn-dismiss" :title="t('alert.dismiss', 'Entendido')">
        <X :size="18" />
      </button>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { AlertTriangle, X } from 'lucide-vue-next'
import { useAppI18n } from '~/composables/useAppI18n'

const { t } = useAppI18n()

const props = defineProps({
  alerta: { type: [Object, String], default: null }
})

const dismissed = ref(false)

const customMensagem = computed(() => {
  if (!props.alerta) return ''
  if (typeof props.alerta === 'string') return props.alerta
  return props.alerta.mensagem || props.alerta.status || ''
})

const alertaVisivel = computed(() => {
  if (dismissed.value) return false
  if (!props.alerta) return false
  if (typeof props.alerta === 'object') {
    return !!props.alerta.tipo || !!props.alerta.mensagem
  }
  return typeof props.alerta === 'string' && props.alerta.length > 0 && props.alerta !== 'OK'
})

watch(() => props.alerta, () => {
  dismissed.value = false
})

function dismiss() {
  dismissed.value = true
}
</script>

<style scoped>
.antibot-alert {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.4rem;
  margin-bottom: 1.5rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-left: 5px solid #ef4444;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.08);
}

.alert-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.alert-icon {
  font-size: 1.5rem;
}

.alert-text strong {
  display: block;
  font-size: 0.95rem;
  color: #991b1b;
  margin-bottom: 0.2rem;
}

.alert-text p {
  margin: 0;
  font-size: 0.85rem;
  color: #b91c1c;
  line-height: 1.4;
}

.btn-dismiss {
  background: none;
  border: none;
  color: #991b1b;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 0.4rem;
  border-radius: 6px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-dismiss:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #7f1d1d;
}

.fade-enter-active, .fade-leave-active {
  transition: all 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
