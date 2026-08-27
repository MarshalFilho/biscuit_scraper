<template>
  <header class="app-header glass-panel animate-fade-in">
    <div class="header-main">
      <div class="brand-box">
        <h1 class="brand-title">✨ {{ projectName || 'Scraper Pro' }}</h1>
        <span class="brand-badge">{{ t('navbar.badge', 'Inteligência Ativa') }}</span>
      </div>

      <div class="header-right">
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
            <span class="user-email" :title="user.email">{{ user.email }}</span>
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
import { useRouter } from 'vue-router'
import { createClient } from '@supabase/supabase-js'
import { useAppI18n } from '~/composables/useAppI18n'

const props = defineProps({
  projectName: { type: String, default: 'Scraper Pro' },
  user: { type: Object, default: null }
})

const emit = defineEmits(['auth-change'])

const { locale, toggleLanguage, t } = useAppI18n()
const router = useRouter()

const config = useRuntimeConfig()
const supabase = createClient(config.public.supabaseUrl, config.public.supabaseAnonKey)

async function logout() {
  await supabase.auth.signOut()
  emit('auth-change', null)
  router.push('/login')
}
</script>

<style scoped>
.app-header {
  padding: 1rem 1.5rem;
  margin-bottom: 2rem;
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
  gap: 0.8rem;
}

.brand-title {
  font-size: 1.6rem;
  font-weight: 800;
  margin: 0;
  background: linear-gradient(135deg, #1d4ed8, #6d28d9);
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

.user-avatar {
  font-size: 0.9rem;
}

.user-email {
  font-weight: 600;
  color: #334155;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-logout {
  background: none;
  border: none;
  color: #ef4444;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  padding: 0.2rem 0.4rem;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.btn-logout:hover {
  background: #fee2e2;
}
</style>
