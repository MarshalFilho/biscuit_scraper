<template>
  <header class="app-header glass-panel animate-fade-in">
    <div class="header-main">
      <div class="brand-box">
        <div class="brand-logo-badge">
          <Palette :size="20" class="brand-icon" />
        </div>
        <div class="brand-text-col">
          <h1 class="brand-title">{{ projectName || 'BiscuitInsights' }}</h1>
          <span class="brand-subtitle">{{ t('navbar.tagline', 'Inteligência de Mercado em Biscuit') }}</span>
        </div>
      </div>

      <div class="header-right">
        <button 
          @click="toggleLanguage" 
          class="lang-btn" 
          :title="t('navbar.toggle_tooltip', 'Alternar idioma')"
        >
          <Globe :size="15" />
          <span class="lang-flag">{{ locale === 'pt' ? 'PT' : 'EN' }}</span>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { Palette, Globe } from 'lucide-vue-next'
import { useAppI18n } from '~/composables/useAppI18n'

const props = defineProps({
  projectName: { type: String, default: 'BiscuitInsights' }
})

const { locale, toggleLanguage, t } = useAppI18n()
</script>

<style scoped>
.app-header {
  padding: 0.85rem 1.4rem;
  margin-bottom: 1.4rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
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
  gap: 0.85rem;
}

.brand-logo-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #fef3c7 0%, #fed7aa 100%);
  border: 1px solid #fde68a;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.15);
  flex-shrink: 0;
}

.brand-icon {
  color: #d97706;
}

.brand-text-col {
  display: flex;
  flex-direction: column;
}

.brand-title {
  font-size: 1.45rem;
  font-weight: 900;
  margin: 0;
  line-height: 1.1;
  letter-spacing: -0.03em;
  background: linear-gradient(135deg, #b45309 0%, #d97706 40%, #7c3aed 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-subtitle {
  font-size: 0.72rem;
  font-weight: 600;
  color: #64748b;
  letter-spacing: -0.01em;
}

.brand-badge {
  font-size: 0.7rem;
  font-weight: 800;
  background: #f0fdf4;
  color: #16a34a;
  padding: 0.25rem 0.65rem;
  border-radius: 99px;
  border: 1px solid #bbf7d0;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex-wrap: wrap;
}

.schedule-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 0.45rem 0.95rem;
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
  padding: 0.42rem 0.85rem;
  border-radius: 99px;
  font-size: 0.85rem;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.25s ease;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.lang-btn:hover {
  background: #d97706;
  color: #ffffff;
  border-color: #d97706;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(217, 119, 6, 0.25);
}
</style>
