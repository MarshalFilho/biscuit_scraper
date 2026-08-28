import { ref } from 'vue'

export interface ToastItem {
  id: string
  title?: string
  message: string
  type: 'success' | 'error' | 'warning' | 'info'
  duration?: number
}

const toasts = ref<ToastItem[]>([])

export function useToast() {
  function show(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info', title?: string, duration: number = 4500) {
    const id = Math.random().toString(36).substring(2, 9)
    const item: ToastItem = { id, title, message, type, duration }
    toasts.value.push(item)

    if (duration > 0) {
      setTimeout(() => {
        remove(id)
      }, duration)
    }
  }

  function success(message: string, title?: string, duration?: number) {
    show(message, 'success', title || 'Sucesso!', duration)
  }

  function error(message: string, title?: string, duration?: number) {
    show(message, 'error', title || 'Ops, algo deu errado', duration || 5500)
  }

  function warning(message: string, title?: string, duration?: number) {
    show(message, 'warning', title || 'Atenção', duration)
  }

  function info(message: string, title?: string, duration?: number) {
    show(message, 'info', title || 'Informação', duration)
  }

  function remove(id: string) {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index !== -1) {
      toasts.value.splice(index, 1)
    }
  }

  return {
    toasts,
    show,
    success,
    error,
    warning,
    info,
    remove
  }
}
