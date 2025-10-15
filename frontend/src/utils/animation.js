/**
 * 动画工具类 - 提供统一的动画管理
 */
class AnimationManager {
  constructor() {
    this.animations = new Map()
    this.observer = null
  }

  /**
   * 创建进入动画
   * @param {Element} element - 目标元素
   * @param {Object} options - 动画选项
   */
  createEnterAnimation(element, options = {}) {
    const defaults = {
      duration: 300,
      easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
      fill: 'forwards'
    }

    const config = { ...defaults, ...options }
    const animation = element.animate([
      { opacity: 0, transform: 'translateY(20px)' },
      { opacity: 1, transform: 'translateY(0)' }
    ], config)

    this.animations.set(element, animation)
    return animation
  }

  /**
   * 创建数值变化动画
   * @param {Function} callback - 数值更新回调
   * @param {number} fromValue - 起始值
   * @param {number} toValue - 结束值
   * @param {number} duration - 动画时长
   */
  animateValue(callback, fromValue, toValue, duration = 1000) {
    const startTime = performance.now()

    const updateValue = (currentTime) => {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / duration, 1)

      // 使用缓动函数
      const easedProgress = this.easeOutCubic(progress)
      const currentValue = fromValue + (toValue - fromValue) * easedProgress

      callback(currentValue)

      if (progress < 1) {
        requestAnimationFrame(updateValue)
      }
    }

    requestAnimationFrame(updateValue)
  }

  /**
   * 缓动函数
   */
  easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3)
  }

  /**
   * 创建Intersection Observer用于滚动动画
   */
  createScrollObserver(callback, options = {}) {
    const defaults = {
      threshold: 0.1,
      rootMargin: '50px'
    }

    this.observer = new IntersectionObserver(callback, { ...defaults, ...options })
    return this.observer
  }

  /**
   * 清理动画
   */
  cleanup() {
    this.animations.forEach(animation => {
      animation.cancel()
    })
    this.animations.clear()

    if (this.observer) {
      this.observer.disconnect()
    }
  }
}

export const animationManager = new AnimationManager()
export default animationManager