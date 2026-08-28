<template>
  <Teleport to="body">
    <div class="toast-container" aria-live="polite">
      <TransitionGroup name="toast-slide">
        <div 
          v-for="toast in toasts" 
          :key="toast.id" 
          class="toast-item glass-toast"
          :class="toast.type"
        >
          <div class="toast-icon">
            <span v-if="toast.type === 'success'">✅</span>
            <span v-else-if="toast.type === 'error'">❌</span>
            <span v-else-if="toast.type === 'warning'">⚠️</span>
            <span v-else>ℹ️</span>
          </div>
          <div class="toast-body">
            <h5 v-if="toast.title" class="toast-title">{{ toast.title }}</h5>
            <p class="toast-message">{{ toast.message }}</p>
          </div>
          <button class="toast-close" @click="remove(toast.id)" title="Fechar">×</button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { useToast } from '~/composables/useToast'

const { toasts, remove } = useToast()
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 1.5rem;
  right: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  z-index: 999999;
  max-width: 420px;
  width: calc(100vw - 3rem);
  pointer-events: none;
}

.toast-item {
  pointer-events: auto;
  display: flex;
  align-items: flex-start;
  gap: 0.8rem;
  padding: 0.9rem 1.1rem;
  border-radius: 12px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 0, 0, 0.05);
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  overflow: hidden;
}

.toast-item.success {
  border-left: 5px solid #10b981;
}

.toast-item.error {
  border-left: 5px solid #ef4444;
}

.toast-item.warning {
  border-left: 5px solid #f59e0b;
}

.toast-item.info {
  border-left: 5px solid #3b82f6;
}

.toast-icon {
  font-size: 1.2rem;
  line-height: 1;
  flex-shrink: 0;
  margin-top: 0.1rem;
}

.toast-body {
  flex: 1;
}

.toast-title {
  margin: 0 0 0.2rem 0;
  font-size: 0.92rem;
  font-weight: 700;
  color: #0f172a;
}

.toast-message {
  margin: 0;
  font-size: 0.84rem;
  color: #475569;
  line-height: 1.4;
  white-space: pre-line;
}

.toast-close {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 1.3rem;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  margin-left: 0.3rem;
  transition: color 0.15s;
}

.toast-close:hover {
  color: #0f172a;
}

/* Animations */
.toast-slide-enter-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-slide-leave-active {
  transition: all 0.2s ease-in;
}

.toast-slide-enter-from {
  opacity: 0;
  transform: translateX(50px) scale(0.95);
}

.toast-slide-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>
