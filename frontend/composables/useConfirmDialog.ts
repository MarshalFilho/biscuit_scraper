import { ref } from 'vue'

export interface ConfirmDialogOptions {
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  danger?: boolean
}

const isOpen = ref(false)
const dialogOptions = ref<ConfirmDialogOptions>({
  title: 'Confirmação',
  message: '',
  confirmText: 'Confirmar',
  cancelText: 'Cancelar',
  danger: false
})

let resolvePromise: ((value: boolean) => void) | null = null

export function useConfirmDialog() {
  function askConfirm(options: ConfirmDialogOptions | string): Promise<boolean> {
    if (typeof options === 'string') {
      dialogOptions.value = {
        title: 'Confirmação',
        message: options,
        confirmText: 'Confirmar',
        cancelText: 'Cancelar',
        danger: false
      }
    } else {
      dialogOptions.value = {
        title: options.title || 'Confirmação',
        message: options.message,
        confirmText: options.confirmText || 'Confirmar',
        cancelText: options.cancelText || 'Cancelar',
        danger: options.danger || false
      }
    }

    isOpen.value = true

    return new Promise((resolve) => {
      resolvePromise = resolve
    })
  }

  function handleConfirm() {
    isOpen.value = false
    if (resolvePromise) resolvePromise(true)
  }

  function handleCancel() {
    isOpen.value = false
    if (resolvePromise) resolvePromise(false)
  }

  return {
    isOpen,
    dialogOptions,
    askConfirm,
    handleConfirm,
    handleCancel
  }
}
