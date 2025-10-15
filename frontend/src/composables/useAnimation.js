import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import animationManager from '@/utils/animation'

/**
 * 动画组合式API
 */
export function useAnimation() {
  const isAnimating = ref(false)
  const animationElement = ref(null)

  /**
   * 触发进入动画
   */
  const triggerEnterAnimation = async (element, options) => {
    if (!element) return

    isAnimating.value = true

    await nextTick()

    const animation = animationManager.createEnterAnimation(element, options)

    animation.addEventListener('finish', () => {
      isAnimating.value = false
    })

    return animation
  }

  /**
   * 动画化数值变化
   */
  const animateValue = (fromValue, toValue, duration = 1000) => {
    const currentValue = ref(fromValue)

    animationManager.animateValue(
      (value) => {
        currentValue.value = value
      },
      fromValue,
      toValue,
      duration
    )

    return currentValue
  }

  /**
   * 滚动显示动画
   */
  const setupScrollAnimation = (elementRef, callback) => {
    if (!elementRef.value) return

    const observer = animationManager.createScrollObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          triggerEnterAnimation(entry.target)
          if (callback) callback(entry.target)
        }
      })
    })

    observer.observe(elementRef.value)

    onUnmounted(() => {
      observer.disconnect()
    })

    return observer
  }

  onUnmounted(() => {
    animationManager.cleanup()
  })

  return {
    isAnimating,
    animationElement,
    triggerEnterAnimation,
    animateValue,
    setupScrollAnimation
  }
}

/**
 * 数值动画Hook
 */
export function useAnimatedValue(initialValue = 0) {
  const animatedValue = ref(initialValue)

  const animateTo = (targetValue, duration = 1000) => {
    const currentValue = animatedValue.value

    animationManager.animateValue(
      (value) => {
        animatedValue.value = value
      },
      currentValue,
      targetValue,
      duration
    )
  }

  return {
    animatedValue,
    animateTo
  }
}