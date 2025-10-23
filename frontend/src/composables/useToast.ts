import { ElMessage, ElNotification } from 'element-plus'

type MessageType = 'success' | 'warning' | 'error' | 'info'

interface ToastOptions {
  message: string
  type?: MessageType
  duration?: number
  showClose?: boolean
}

interface NotificationOptions {
  title: string
  message: string
  type?: MessageType
  duration?: number
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left'
}

export function useToast() {
  const toast = (options: ToastOptions) => {
    ElMessage({
      message: options.message,
      type: options.type || 'info',
      duration: options.duration || 3000,
      showClose: options.showClose !== false,
      customClass: 'custom-message',
      grouping: true
    })
  }

  const success = (message: string, duration?: number) => {
    toast({ message, type: 'success', duration })
  }

  const error = (message: string, duration?: number) => {
    toast({ message, type: 'error', duration: duration || 4000 })
  }

  const warning = (message: string, duration?: number) => {
    toast({ message, type: 'warning', duration })
  }

  const info = (message: string, duration?: number) => {
    toast({ message, type: 'info', duration })
  }

  const notify = (options: NotificationOptions) => {
    ElNotification({
      title: options.title,
      message: options.message,
      type: options.type || 'info',
      duration: options.duration || 4500,
      position: options.position || 'top-right',
      customClass: 'custom-notification'
    })
  }

  const notifySuccess = (title: string, message: string) => {
    notify({ title, message, type: 'success' })
  }

  const notifyError = (title: string, message: string) => {
    notify({ title, message, type: 'error', duration: 6000 })
  }

  const notifyWarning = (title: string, message: string) => {
    notify({ title, message, type: 'warning' })
  }

  const notifyInfo = (title: string, message: string) => {
    notify({ title, message, type: 'info' })
  }

  return {
    toast,
    success,
    error,
    warning,
    info,
    notify,
    notifySuccess,
    notifyError,
    notifyWarning,
    notifyInfo
  }
}
