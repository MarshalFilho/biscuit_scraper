<template>
  <div class="login-page">
    <!-- Barra Superior com Alternador de Idioma -->
    <header class="login-header">
      <div class="brand">
        <span class="logo-icon">📈</span>
        <span class="logo-text">PulseMarket AI</span>
      </div>
      <button @click="toggleLanguage" class="lang-toggle-btn" :title="t('navbar.toggle_tooltip')">
        {{ locale === 'pt' ? '🇧🇷 PT' : '🇺🇸 EN' }}
      </button>
    </header>

    <!-- Card Central de Login -->
    <div class="login-container animate-fade-in">
      <div class="glass-panel login-card">
        <div class="card-header">
          <div class="icon-circle">🔐</div>
          <h2>{{ t('auth.login_title', 'Acesso à Plataforma') }}</h2>
          <p class="subtitle">{{ t('auth.login_subtitle', 'Painel de Inteligência Competitiva e Análise de Mercado') }}</p>
        </div>

        <!-- Mensagem de Erro -->
        <div v-if="errorMessage" class="error-banner animate-shake">
          <span>⚠️ {{ errorMessage }}</span>
        </div>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="email">{{ t('auth.email_label', 'E-mail de Acesso') }}</label>
            <input 
              id="email" 
              type="email" 
              v-model="email" 
              :placeholder="t('auth.email_placeholder', 'seu@email.com')"
              required 
              class="glass-input"
              :disabled="loading"
              autofocus
            />
          </div>

          <div class="form-group">
            <label for="password">{{ t('auth.password_label', 'Sua Senha') }}</label>
            <input 
              id="password" 
              type="password" 
              v-model="password" 
              :placeholder="t('auth.password_placeholder', '••••••••')"
              required 
              class="glass-input"
              :disabled="loading"
            />
          </div>

          <button type="submit" class="btn-submit" :disabled="loading || !email || !password">
            <span v-if="loading" class="spinner">⏳ {{ t('auth.btn_logging_in', 'Autenticando...') }}</span>
            <span v-else>{{ t('auth.btn_login', 'Entrar no Dashboard 🚀') }}</span>
          </button>
        </form>

        <div class="card-footer">
          <span class="security-tag">🛡️ {{ t('auth.secure_access', 'Acesso Seguro & Criptografado') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { createClient } from '@supabase/supabase-js'
import { useAppI18n } from '~/composables/useAppI18n'

definePageMeta({
  layout: false
})

const { t, locale, toggleLanguage } = useAppI18n()
const router = useRouter()
const supabase = useSupabase()

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  if (!email.value || !password.value) return
  loading.value = true
  errorMessage.value = ''

  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email: email.value.trim(),
      password: password.value
    })

    if (error) {
      console.warn("Supabase Auth Error:", error)
      if (error.message.includes('Invalid login credentials')) {
        errorMessage.value = t('auth.login_failed', 'Credenciais inválidas. Verifique seu e-mail e senha.')
      } else if (error.message.includes('Email not confirmed')) {
        errorMessage.value = '⚠️ E-mail não confirmado. Desmarque "Confirm email" no Supabase Auth.'
      } else {
        errorMessage.value = error.message
      }
      return
    }

    if (data?.session) {
      // Redireciona com reload completo para carregar os dados autenticados
      window.location.href = '/'
    }
  } catch (err) {
    errorMessage.value = err.message || t('auth.login_failed', 'Erro ao conectar ao servidor de autenticação.')
    console.error('Login error:', err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
  font-family: 'Inter', sans-serif;
  color: #0f172a;
}

.login-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2.5rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.logo-icon { font-size: 1.4rem; }
.logo-text {
  font-size: 1.3rem;
  font-weight: 800;
  background: linear-gradient(135deg, #1d4ed8, #6d28d9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.lang-toggle-btn {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #0f172a;
  padding: 0.4rem 0.8rem;
  border-radius: 99px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}
.lang-toggle-btn:hover {
  background: #2563eb;
  color: #ffffff;
  border-color: #2563eb;
}

.login-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1.5rem;
}

.login-card {
  width: 100%;
  max-width: 440px;
  padding: 2.5rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02);
}

.card-header {
  text-align: center;
  margin-bottom: 2rem;
}

.icon-circle {
  width: 56px;
  height: 56px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.6rem;
  margin: 0 auto 1rem auto;
}

.card-header h2 {
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 0.4rem 0;
}

.subtitle {
  font-size: 0.88rem;
  color: #64748b;
  margin: 0;
  line-height: 1.4;
}

.error-banner {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: 0.8rem 1rem;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 700;
  color: #334155;
}

.glass-input {
  width: 100%;
  padding: 0.8rem 1rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  font-size: 0.95rem;
  color: #0f172a;
  outline: none;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.glass-input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}

.btn-submit {
  margin-top: 0.8rem;
  padding: 0.9rem 1.2rem;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #ffffff;
  border: none;
  border-radius: 10px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.card-footer {
  margin-top: 2rem;
  text-align: center;
  border-top: 1px solid #f1f5f9;
  padding-top: 1.2rem;
}

.security-tag {
  font-size: 0.78rem;
  color: #94a3b8;
  font-weight: 600;
}

.animate-fade-in {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
