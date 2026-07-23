<template>
  <header class="app-header glass-panel animate-fade-in">
    <div class="header-main">
      <div class="brand-box">
        <h1 class="brand-title">✨ {{ projectName || 'Scraper Pro' }}</h1>
        <span class="brand-badge">Inteligência Ativa</span>
      </div>

      <nav class="app-nav">
        <NuxtLink to="/" :class="['nav-link', { active: route.path === '/' }]">
          📊 Painel Analítico
        </NuxtLink>
        <NuxtLink to="/config" :class="['nav-link', { active: route.path === '/config' }]">
          ⚙️ Configurações & Robô
        </NuxtLink>
      </nav>

      <div class="user-box">
        <LoginModal @auth-change="user => $emit('auth-change', user)" />
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

.app-nav {
  display: flex;
  gap: 0.5rem;
  background: #f1f5f9;
  padding: 4px;
  border-radius: 10px;
  border: 1px solid #cbd5e1;
}

.nav-link {
  padding: 0.6rem 1.2rem;
  font-size: 0.92rem;
  font-weight: 700;
  color: #475569;
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.nav-link:hover {
  color: #0f172a;
}

.nav-link.active {
  background: #ffffff;
  color: #2563eb;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.user-box {
  display: flex;
  align-items: center;
}
</style>
