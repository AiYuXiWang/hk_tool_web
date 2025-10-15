/**
 * 响应式工具类 - 管理断点和响应式逻辑
 */
class ResponsiveManager {
  constructor() {
    this.breakpoints = {
      xs: 480,
      sm: 768,
      md: 1024,
      lg: 1440,
      xl: 1920
    }

    this.currentBreakpoint = this.getCurrentBreakpoint()
    this.listeners = []

    this.init()
  }

  /**
   * 初始化响应式监听
   */
  init() {
    if (typeof window !== 'undefined') {
      window.addEventListener('resize', this.handleResize.bind(this))
    }
  }

  /**
   * 获取当前断点
   */
  getCurrentBreakpoint() {
    if (typeof window === 'undefined') return 'lg'

    const width = window.innerWidth

    for (const [name, size] of Object.entries(this.breakpoints)) {
      if (width < size) {
        return name
      }
    }

    return 'xl'
  }

  /**
   * 处理窗口大小变化
   */
  handleResize() {
    const newBreakpoint = this.getCurrentBreakpoint()

    if (newBreakpoint !== this.currentBreakpoint) {
      this.currentBreakpoint = newBreakpoint
      this.notifyListeners()
    }
  }

  /**
   * 通知所有监听器
   */
  notifyListeners() {
    this.listeners.forEach(listener => {
      listener(this.currentBreakpoint)
    })
  }

  /**
   * 添加断点变化监听器
   */
  addListener(callback) {
    this.listeners.push(callback)
    return () => {
      const index = this.listeners.indexOf(callback)
      if (index > -1) {
        this.listeners.splice(index, 1)
      }
    }
  }

  /**
   * 检查是否匹配指定断点
   */
  isBreakpoint(breakpoint) {
    return this.currentBreakpoint === breakpoint
  }

  /**
   * 检查是否小于指定断点
   */
  isSmallerThan(breakpoint) {
    const breakpointOrder = Object.keys(this.breakpoints)
    const currentIndex = breakpointOrder.indexOf(this.currentBreakpoint)
    const targetIndex = breakpointOrder.indexOf(breakpoint)

    return currentIndex < targetIndex
  }

  /**
   * 检查是否大于指定断点
   */
  isLargerThan(breakpoint) {
    const breakpointOrder = Object.keys(this.breakpoints)
    const currentIndex = breakpointOrder.indexOf(this.currentBreakpoint)
    const targetIndex = breakpointOrder.indexOf(breakpoint)

    return currentIndex > targetIndex
  }

  /**
   * 获取响应式配置
   */
  getResponsiveConfig(configs) {
    // 从大到小查找匹配的配置
    const breakpointOrder = ['xl', 'lg', 'md', 'sm', 'xs']

    for (const breakpoint of breakpointOrder) {
      if (configs[breakpoint] && this.isLargerThan(breakpoint)) {
        return configs[breakpoint]
      }
    }

    return configs.default || configs.xs
  }

  /**
   * 清理资源
   */
  cleanup() {
    if (typeof window !== 'undefined') {
      window.removeEventListener('resize', this.handleResize)
    }
    this.listeners = []
  }
}

export const responsiveManager = new ResponsiveManager()
export default responsiveManager