import { ref, onMounted, onUnmounted, computed } from 'vue'
import responsiveManager from '@/utils/responsive'

/**
 * 响应式组合式API
 */
export function useResponsive() {
  const currentBreakpoint = ref(responsiveManager.currentBreakpoint)

  /**
   * 计算属性：是否为移动端
   */
  const isMobile = computed(() => {
    return ['xs', 'sm'].includes(currentBreakpoint.value)
  })

  /**
   * 计算属性：是否为平板端
   */
  const isTablet = computed(() => {
    return currentBreakpoint.value === 'md'
  })

  /**
   * 计算属性：是否为桌面端
   */
  const isDesktop = computed(() => {
    return ['lg', 'xl'].includes(currentBreakpoint.value)
  })

  /**
   * 获取响应式配置
   */
  const getResponsiveConfig = (configs) => {
    return responsiveManager.getResponsiveConfig(configs)
  }

  /**
   * 获取响应式值
   */
  const getResponsiveValue = (values) => {
    return values[currentBreakpoint.value] || values.default
  }

  /**
   * 监听断点变化
   */
  const onBreakpointChange = (callback) => {
    return responsiveManager.addListener((breakpoint) => {
      currentBreakpoint.value = breakpoint
      callback(breakpoint)
    })
  }

  onMounted(() => {
    onBreakpointChange((breakpoint) => {
      currentBreakpoint.value = breakpoint
    })
  })

  onUnmounted(() => {
    responsiveManager.cleanup()
  })

  return {
    currentBreakpoint,
    isMobile,
    isTablet,
    isDesktop,
    getResponsiveConfig,
    getResponsiveValue,
    onBreakpointChange
  }
}

/**
 * 响应式布局Hook
 */
export function useResponsiveLayout() {
  const { isMobile, isTablet, isDesktop } = useResponsive()

  /**
   * 获取网格列数
   */
  const getGridColumns = (config = {}) => {
    const defaultConfig = {
      xs: 1,
      sm: 2,
      md: 3,
      lg: 4,
      xl: 4
    }

    const finalConfig = { ...defaultConfig, ...config }

    if (isMobile.value) return finalConfig.xs
    if (isTablet.value) return finalConfig.md
    return finalConfig.lg
  }

  /**
   * 获取间距大小
   */
  const getSpacing = (config = {}) => {
    const defaultConfig = {
      xs: 'sm',
      sm: 'md',
      md: 'lg',
      lg: 'xl',
      xl: 'xl'
    }

    const finalConfig = { ...defaultConfig, ...config }
    return finalConfig[currentBreakpoint.value] || finalConfig.default
  }

  /**
   * 获取容器最大宽度
   */
  const getContainerMaxWidth = () => {
    if (isMobile.value) return '100%'
    if (isTablet.value) return '768px'
    return '1200px'
  }

  return {
    getGridColumns,
    getSpacing,
    getContainerMaxWidth
  }
}