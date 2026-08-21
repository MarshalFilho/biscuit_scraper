<template>
  <header class="app-header glass-panel animate-fade-in">
    <div class="header-main">
      <div class="brand-box">
        <h1 class="brand-title">✨ {{ projectName || 'Scraper Pro' }}</h1>
        <span class="brand-badge">{{ $t('navbar.badge') }}</span>
      </div>

      <div class="header-right">
        <!-- Language Switcher -->
        <button 
          @click="toggleLanguage" 
          class="lang-btn" 
          :title="locale === 'pt' ? 'Mudar para Inglês' : 'Switch to Portuguese'"
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
import { useRoute } from 'vue-router'
import LoginModal from './LoginModal.vue'

defineProps({
  projectName: { type: String, default: 'Scraper Pro' }
})

defineEmits(['auth-change'])

const route = useRoute()
const { locale, setLocale } = useI18n()

function toggleLanguage() {
  setLocale(locale.value === 'pt' ? 'en' : 'pt')
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
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  color: #334155;
  padding: 0.45rem 0.85rem;
  border-radius: 99px;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.lang-btn:hover {
  background: #eff6ff;
  border-color: #3b82f6;
  color: #1d4ed8;
  transform: translateY(-1px);
}

.user-box {
  display: flex;
  align-items: center;
}
</style>
