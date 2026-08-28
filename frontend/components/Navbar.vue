<template>
  <header class="app-header glass-panel animate-fade-in">
    <div class="header-main">
      <div class="brand-box">
        <div class="brand-logo-badge">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="24" height="24" rx="7" fill="url(#logo-grad)"/>
            <path d="M5 16.5L9.5 11.5L13.5 14.5L19 8" stroke="#FFFFFF" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="19" cy="8" r="2" fill="#93C5FD"/>
            <defs>
              <linearGradient id="logo-grad" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse">
                <stop stop-color="#2563EB"/>
                <stop offset="1" stop-color="#7C3AED"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <h1 class="brand-title">{{ projectName || 'MarketRadar AI' }}</h1>
        <span class="brand-badge">{{ t('navbar.badge', 'Inteligência Ativa') }}</span>
      </div>

      <div class="header-right">
        <!-- Indicador Informativo de Frequência Diária -->
        <div class="schedule-pill" :title="t('filters.daily_info', 'Rotina de raspagem executada automaticamente 1 vez por dia às 22h00')">
          <span class="pulse-dot"></span>
          <span class="schedule-text">{{ t('navbar.daily_schedule', '⏰ Coleta Diária às 22h00') }}</span>
        </div>

        <!-- 1. Botão para PRO: Gerenciar seus Termos e Palavras-Chave -->
        <button 
          v-if="isPro"
          type="button"
          class="btn-keywords"
          @click="$emit('open-keywords')"
          :title="t('keywords.pro_btn_title', 'Painel Pro: Gerenciar seus termos e IA')"
        >
          🎯 {{ t('keywords.badge_pro', 'Meus Termos & IA') }}
        </button>

        <!-- 2. Botão para BASIC: Solicitar Novo Termo -->
        <button 
          v-else-if="isBasic"
          type="button"
          class="btn-request-term"
          @click="$emit('open-request-term')"
          :title="t('request_term.client_btn_title', 'Solicitar ao administrador a inclusão de um novo termo/nicho')"
        >
          💡 {{ t('request_term.btn_label', 'Solicitar Termo') }}
        </button>

        <button 
          @click="toggleLanguage" 
          class="lang-btn" 
          :title="t('navbar.toggle_tooltip')"
        >
          <span class="lang-flag">{{ locale === 'pt' ? '🇧🇷 PT' : '🇺🇸 EN' }}</span>
        </button>

        <div class="user-box" v-if="user">
          <div class="user-pill">
            <span class="user-avatar">👤</span>
            <div class="user-details">
              <span class="user-email" :title="user.email">{{ user.email }}</span>
              <span :class="['role-pill', `role-${currentRole}`]">
                {{ currentRole.toUpperCase() }}
              </span>
            </div>
            <button @click="logout" class="btn-logout" :title="t('auth.logout', 'Sair')">
              🚪 {{ t('auth.logout', 'Sair') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAppI18n } from '~/composables/useAppI18n'
import { useSupabase } from '~/composables/useSupabase'

const props = defineProps({
  projectName: { type: String, default: 'SmartDashboard AI' },
  user: { type: Object, default: null }
})

const emit = defineEmits(['auth-change', 'open-keywords', 'open-request-term'])

const { locale, toggleLanguage, t } = useAppI18n()
const router = useRouter()
const supabase = useSupabase()

const currentRole = computed(() => {
  if (!props.user) return null
  const appRole = String(props.user.app_metadata?.role || '').toLowerCase()
  const userRole = String(props.user.user_metadata?.role || '').toLowerCase()
  const directRole = String(props.user.role || '').toLowerCase()
  const email = String(props.user.email || '').toLowerCase()

  if (appRole === 'admin' || userRole === 'admin' || directRole === 'admin' || email === 'adm@gmail.com') return 'admin'
  if (appRole === 'pro' || userRole === 'pro' || directRole === 'pro' || email === 'marshalfilho@gmail.com' || email === 'isadora@gmail.com') return 'pro'
  return 'basic'
})

const isAdmin = computed(() => currentRole.value === 'admin')
const isPro = computed(() => currentRole.value === 'pro')
const isBasic = computed(() => currentRole.value === 'basic')

async function logout() {
  await supabase.auth.signOut()
  emit('auth-change', null)
  router.push('/login')
}
</script>

<style scoped>
.app-header {
  padding: 0.85rem 1.25rem;
  margin-bottom: 1.25rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.brand-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.brand-logo-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 6px rgba(37, 99, 235, 0.12);
  flex-shrink: 0;
}

.brand-title {
  font-size: 1.45rem;
  font-weight: 800;
  margin: 0;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, #1d4ed8 0%, #6d28d9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-badge {
  font-size: 0.72rem;
  font-weight: 700;
  background: #eff6ff;
  color: #2563eb;
  padding: 0.25rem 0.6rem;
  border-radius: 99px;
  border: 1px solid #bfdbfe;
  text-transform: uppercase;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.btn-keywords {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: #ffffff;
  color: #4f46e5;
  border: 1.5px solid #c7d2fe;
  padding: 0.45rem 0.9rem;
  border-radius: 99px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.1);
  transition: all 0.2s ease;
}

.btn-keywords:hover {
  background: #eef2ff;
  border-color: #818cf8;
  color: #4338ca;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

.schedule-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 0.45rem 0.9rem;
  border-radius: 99px;
  font-size: 0.82rem;
  font-weight: 700;
  color: #334155;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  animation: pulse-green 2s infinite;
}

@keyframes pulse-green {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  }
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 6px rgba(16, 185, 129, 0);
  }
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
  }
}

.schedule-text {
  letter-spacing: -0.01em;
}

.lang-btn {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #0f172a;
  padding: 0.4rem 0.8rem;
  border-radius: 99px;
  font-size: 0.85rem;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.lang-btn:hover {
  background: #2563eb;
  color: #ffffff;
  border-color: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

.user-box {
  display: flex;
  align-items: center;
}

.user-pill {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 0.35rem 0.8rem;
  border-radius: 99px;
  font-size: 0.85rem;
}

.btn-request-term {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: #ffffff;
  color: #0284c7;
  border: 1.5px solid #bae6fd;
  padding: 0.45rem 0.9rem;
  border-radius: 99px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(2, 132, 199, 0.1);
  transition: all 0.2s ease;
}

.btn-request-term:hover {
  background: #f0f9ff;
  border-color: #38bdf8;
  color: #0369a1;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.2);
}

.user-details {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.role-pill {
  font-size: 0.65rem;
  font-weight: 800;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  letter-spacing: 0.03em;
}

.role-admin {
  background: #fef3c7;
  color: #92400e;
  border: 1px solid #fde68a;
}

.role-pro {
  background: #f3e8ff;
  color: #6b21a8;
  border: 1px solid #d8b4fe;
}

.role-basic, .role-light, .role-client {
  background: #e0f2fe;
  color: #0369a1;
  border: 1px solid #bae6fd;
}

.user-avatar {
  font-size: 1rem;
}

.user-email {
  font-weight: 600;
  color: #334155;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-logout {
  background: transparent;
  border: none;
  color: #64748b;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.btn-logout:hover {
  background: #fee2e2;
  color: #ef4444;
}
</style>
