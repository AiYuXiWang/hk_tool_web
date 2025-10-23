import { ref, onMounted, onUnmounted, watch } from 'vue'

interface RefreshOptions {
  interval?: number
  immediate?: boolean
  enabled?: boolean
  onRefresh: () => Promise<void> | void
  onError?: (error: Error) => void
}

export function useDataRefresh(options: RefreshOptions) {
  const {
    interval = 30000,
    immediate = true,
    enabled = true,
    onRefresh,
    onError
  } = options

  const isRefreshing = ref(false)
  const lastRefreshTime = ref<Date | null>(null)
  const errorCount = ref(0)
  const isEnabled = ref(enabled)
  let timer: NodeJS.Timeout | null = null

  const refresh = async () => {
    if (isRefreshing.value) return
    
    isRefreshing.value = true
    try {
      await onRefresh()
      lastRefreshTime.value = new Date()
      errorCount.value = 0
    } catch (error) {
      errorCount.value++
      if (onError) {
        onError(error as Error)
      }
      console.error('Data refresh failed:', error)
    } finally {
      isRefreshing.value = false
    }
  }

  const startAutoRefresh = () => {
    if (timer) {
      clearInterval(timer)
    }
    timer = setInterval(() => {
      if (isEnabled.value && !isRefreshing.value) {
        refresh()
      }
    }, interval)
  }

  const stopAutoRefresh = () => {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  const enable = () => {
    isEnabled.value = true
    startAutoRefresh()
  }

  const disable = () => {
    isEnabled.value = false
    stopAutoRefresh()
  }

  const reset = () => {
    errorCount.value = 0
    lastRefreshTime.value = null
  }

  watch(() => isEnabled.value, (newValue) => {
    if (newValue) {
      startAutoRefresh()
    } else {
      stopAutoRefresh()
    }
  })

  onMounted(() => {
    if (immediate) {
      refresh()
    }
    if (isEnabled.value) {
      startAutoRefresh()
    }
  })

  onUnmounted(() => {
    stopAutoRefresh()
  })

  return {
    isRefreshing,
    lastRefreshTime,
    errorCount,
    isEnabled,
    refresh,
    enable,
    disable,
    reset
  }
}
