<template>
  <div class="login-wrapper">
    <div v-if="user" class="user-info">
      <span class="user-badge">🟢 Conectado</span>
      <span class="user-email">{{ user.email }}</span>
      <button @click="logout" class="btn-text">Sair</button>
    </div>
    <div v-else class="login-form">
      <input type="email" v-model="email" placeholder="E-mail admin" class="glass-input tiny" @keyup.enter="login" />
      <input type="password" v-model="password" placeholder="Senha" class="glass-input tiny" @keyup.enter="login" />
      <button @click="login" :disabled="loading" class="btn small primary">{{ loading ? '⏳' : 'Entrar' }}</button>
      <span v-if="errorMsg" class="error-text">{{ errorMsg }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { createClient } from '@supabase/supabase-js'

const config = useRuntimeConfig()
const supabase = createClient(config.public.supabaseUrl, config.public.supabaseAnonKey)

const emit = defineEmits(['auth-change'])

const user = ref(null)
const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

onMounted(async () => {
  const { data: { session } } = await supabase.auth.getSession()
  user.value = session?.user || null
  emit('auth-change', user.value)

  supabase.auth.onAuthStateChange((_event, session) => {
    user.value = session?.user || null
    emit('auth-change', user.value)
  })
})

async function login() {
  if (!email.value || !password.value) return
  loading.value = true
  errorMsg.value = ''
  
  const { error } = await supabase.auth.signInWithPassword({
    email: email.value,
    password: password.value
  })

  if (error) {
    errorMsg.value = 'Falha no login'
    console.error(error)
  }
  loading.value = false
}

async function logout() {
  await supabase.auth.signOut()
  user.value = null
}
</script>

<style scoped>
.login-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(16, 185, 129, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.user-badge {
  font-size: 0.8rem;
  font-weight: bold;
  color: #10b981;
}

.user-email {
  color: var(--text-main);
  font-size: 0.9rem;
}

.btn-text {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.9rem;
}
.btn-text:hover { color: #ef4444; }

.login-form {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.glass-input.tiny {
  padding: 0.4rem 0.8rem;
  width: 150px;
  background: rgba(0,0,0,0.2);
  border: 1px solid var(--border-glass);
  color: white;
  border-radius: 6px;
  outline: none;
}
.glass-input.tiny:focus {
  border-color: var(--neon-blue);
}

.btn.small {
  padding: 0.4rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  border: none;
}
.btn.primary { background: var(--neon-blue); color: #000; }
.btn.primary:hover { background: #1da4e3; }

.error-text {
  color: #ef4444;
  font-size: 0.8rem;
  margin-left: 0.5rem;
}
</style>
