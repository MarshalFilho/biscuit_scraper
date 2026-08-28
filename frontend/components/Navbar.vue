<template>
  <header class="app-header glass-panel animate-fade-in">
    <div class="header-main">
      <div class="brand-box">
        <h1 class="brand-title">📈 {{ projectName || 'MarketPulse AI' }}</h1>
        <span class="brand-badge">{{ t('navbar.badge', 'Inteligência Ativa') }}</span>
      </div>

      <div class="header-right">
        <!-- Botão de Disparo Imediato ao Worker Local -->
        <button 
          @click="triggerScrape" 
          :disabled="isTriggering"
          class="btn-trigger-scrape"
          :title="t('navbar.trigger_scrape_tooltip', 'Solicitar coleta imediata ao Worker Local')"
        >
          <span v-if="!isTriggering">⚡ {{ t('navbar.trigger_scrape', 'Disparar Nova Raspagem') }}</span>
          <span v-else class="loading-spin">⏳ {{ t('navbar.triggering', 'Solicitando ao Worker...') }}</span>
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAppI18n } from '~/composables/useAppI18n'
import { useSupabase } from '~/composables/useSupabase'

const props = defineProps({
  projectName: { type: String, default: 'MarketPulse AI' },
  user: { type: Object, default: null }
})

const emit = defineEmits(['auth-change'])

const { locale, toggleLanguage, t } = useAppI18n()
const router = useRouter()
const supabase = useSupabase()

const isTriggering = ref(false)

async function triggerScrape() {
  isTriggering.value = true
  try {
    const { data: { user: currentUser } } = await supabase.auth.getUser()
    const userId = currentUser?.id || props.user?.id

    if (userId) {
      const { error } = await supabase.table('configuracoes_scraper').update({
        disparo_pendente: true,
        status_scraper: '⚡ Disparo solicitado pelo Dashboard! Aguardando o Worker Local...'
      }).eq('user_id', userId)

      if (!error) {
        alert('🚀 Disparo solicitado com sucesso!\n\nSe o seu Worker Local (iniciar_worker.bat) estiver ligado, ele iniciará a coleta em poucos segundos.')
      } else {
        alert('⚠️ Aviso ao enviar comando: ' + error.message)
      }
    } else {
      // Caso não haja usuário autenticado
      await supabase.table('configuracoes_scraper').update({
        disparo_pendente: true,
        status_scraper: '⚡ Disparo solicitado!'
      }).neq('user_id', '00000000-0000-0000-0000-000000000000')
      alert('🚀 Disparo solicitado com sucesso!')
    }
  } catch (e) {
    console.error(e)
    alert('Erro ao comunicar com o banco de dados: ' + e.message)
  } finally {
    setTimeout(() => {
      isTriggering.value = false
    }, 4000)
  }
}

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
  flex-wrap: wrap;
}

.btn-trigger-scrape {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  color: #ffffff;
  border: none;
  padding: 0.45rem 1rem;
  border-radius: 99px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
  transition: all 0.2s ease;
}

.btn-trigger-scrape:hover:not(:disabled) {
  background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
}

.btn-trigger-scrape:disabled {
  opacity: 0.75;
  cursor: not-allowed;
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
