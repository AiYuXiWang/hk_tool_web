import { ref, watch, onMounted } from 'vue'

interface CountUpOptions {
  duration?: number
  decimals?: number
  useEasing?: boolean
  autoStart?: boolean
}

export function useCountUp(target: number | (() => number), options: CountUpOptions = {}) {
  const {
    duration = 1000,
    decimals = 0,
    useEasing = true,
    autoStart = true
  } = options

  const displayValue = ref(0)
  const startValue = ref(0)
  const endValue = ref(typeof target === 'function' ? target() : target)
  const startTime = ref<number | null>(null)
  const animationFrame = ref<number | null>(null)

  const easeOutExpo = (t: number): number => {
    return t === 1 ? 1 : 1 - Math.pow(2, -10 * t)
  }

  const updateValue = (timestamp: number) => {
    if (!startTime.value) {
      startTime.value = timestamp
    }

    const elapsed = timestamp - startTime.value
    const progress = Math.min(elapsed / duration, 1)

    const easedProgress = useEasing ? easeOutExpo(progress) : progress
    const current = startValue.value + (endValue.value - startValue.value) * easedProgress

    displayValue.value = Number(current.toFixed(decimals))

    if (progress < 1) {
      animationFrame.value = requestAnimationFrame(updateValue)
    } else {
      displayValue.value = Number(endValue.value.toFixed(decimals))
      startTime.value = null
    }
  }

  const start = (newTarget?: number) => {
    if (animationFrame.value) {
      cancelAnimationFrame(animationFrame.value)
    }

    startValue.value = displayValue.value
    endValue.value = newTarget !== undefined ? newTarget : (typeof target === 'function' ? target() : target)
    startTime.value = null
    
    animationFrame.value = requestAnimationFrame(updateValue)
  }

  const reset = () => {
    if (animationFrame.value) {
      cancelAnimationFrame(animationFrame.value)
    }
    displayValue.value = 0
    startValue.value = 0
    startTime.value = null
  }

  const stop = () => {
    if (animationFrame.value) {
      cancelAnimationFrame(animationFrame.value)
      animationFrame.value = null
    }
  }

  if (typeof target === 'function') {
    watch(target, (newValue) => {
      start(newValue)
    })
  } else {
    watch(() => target, (newValue) => {
      start(newValue)
    })
  }

  onMounted(() => {
    if (autoStart) {
      start()
    }
  })

  return {
    displayValue,
    start,
    reset,
    stop
  }
}
