<template>
  <Teleport to="body">
    <div v-if="isOpen" class="modal-overlay" @click.self="handleCancel">
      <div class="confirm-dialog glass-panel animate-scale">
        <div class="confirm-icon-box" :class="{ 'is-danger': dialogOptions.danger }">
          <span>{{ dialogOptions.danger ? '⚠️' : '❓' }}</span>
        </div>

        <h3 class="confirm-title">{{ dialogOptions.title }}</h3>
        <p class="confirm-message">{{ dialogOptions.message }}</p>

        <div class="confirm-actions">
          <button type="button" class="btn-cancel" @click="handleCancel">
            {{ dialogOptions.cancelText || 'Cancelar' }}
          </button>
          <button 
            type="button" 
            class="btn-confirm" 
            :class="{ 'btn-danger': dialogOptions.danger }" 
            @click="handleConfirm"
          >
            {{ dialogOptions.confirmText || 'Confirmar' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { useConfirmDialog } from '~/composables/useConfirmDialog'

const { isOpen, dialogOptions, handleConfirm, handleCancel } = useConfirmDialog()
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(15, 23, 42, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999999;
  backdrop-filter: blur(6px);
  padding: 1.5rem;
}

.confirm-dialog {
  max-width: 440px;
  width: 100%;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 1.8rem 1.6rem;
  text-align: center;
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.25);
  margin: auto;
}

.confirm-icon-box {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  font-size: 1.6rem;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 auto 1rem auto;
}

.confirm-icon-box.is-danger {
  background: #fef2f2;
  border-color: #fecaca;
}

.confirm-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
  font-weight: 800;
  color: #0f172a;
}

.confirm-message {
  margin: 0 0 1.5rem 0;
  font-size: 0.9rem;
  color: #64748b;
  line-height: 1.5;
  white-space: pre-line;
}

.confirm-actions {
  display: flex;
  justify-content: center;
  gap: 0.8rem;
}

.btn-cancel {
  flex: 1;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #475569;
  padding: 0.65rem 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.btn-confirm {
  flex: 1;
  background: #2563eb;
  color: #ffffff;
  border: none;
  padding: 0.65rem 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}

.btn-confirm:hover {
  background: #1d4ed8;
}

.btn-confirm.btn-danger {
  background: #dc2626;
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.25);
}

.btn-confirm.btn-danger:hover {
  background: #b91c1c;
}

.animate-scale { animation: scaleIn 0.2s ease-out; }
@keyframes scaleIn { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }
</style>
