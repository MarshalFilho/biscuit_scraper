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
        <div class="user-box">
          <LoginModal @auth-change="user => $emit('auth-change', user)" />
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useAppI18n } from '~/composables/useAppI18n'
import LoginModal from './LoginModal.vue'

defineProps({
  projectName: { type: String, default: 'Scraper Pro' }
})

defineEmits(['auth-change'])

const { locale, toggleLanguage, t } = useAppI18n()
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
</style>
