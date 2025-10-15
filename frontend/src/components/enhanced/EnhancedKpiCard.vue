<template>
  <div
    :class="cardClasses"
    @mouseenter="handleHover"
    @mouseleave="handleLeave"
    ref="cardRef"
  >
    <!-- 卡片背景装饰 -->
    <div class="kpi-card-bg">
      <div class="kpi-card-pattern"></div>
    </div>

    <!-- 卡片内容 -->
    <div class="kpi-card-content">
      <!-- 头部区域 -->
      <div class="kpi-card-header">
        <!-- 图标容器 -->
        <div class="kpi-icon-container">
          <div class="kpi-icon-wrapper" :class="iconClasses">
            <i :class="['kpi-icon', iconClass]"></i>
          </div>
          <!-- 装饰圆圈 -->
          <div class="kpi-icon-decoration"></div>
        </div>

        <!-- 趋势指示器 -->
        <div v-if="trend" class="kpi-trend" :class="trendClasses">
          <i :class="trendIconClass"></i>
          <span class="trend-value">{{ formattedTrendValue }}</span>
        </div>
      </div>

      <!-- 数值区域 -->
      <div class="kpi-card-body">
        <div class="kpi-title">{{ title }}</div>
        <div class="kpi-value-container">
          <span class="kpi-value" :class="valueClasses">
            {{ formattedValue }}
          </span>
          <span v-if="unit" class="kpi-unit">{{ unit }}</span>
        </div>
        <div v-if="subtitle" class="kpi-subtitle">{{ subtitle }}</div>
      </div>

      <!-- 底部区域 -->
      <div v-if="$slots.footer" class="kpi-card-footer">
        <slot name="footer"></slot>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="kpi-card-loading">
      <div class="loading-skeleton"></div>
    </div>

    <!-- 点击波纹效果 -->
    <div
      v-if="clickable && rippleEnabled"
      class="kpi-card-ripple"
      :style="rippleStyle"
    ></div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useAnimation, useAnimatedValue } from '@/composables/useAnimation'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    required: true
  },
  unit: String,
  subtitle: String,
  icon: {
    type: String,
    required: true
  },
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'success', 'warning', 'danger', 'info'].includes(value)
  },
  trend: {
    type: Object,
    default: null
    // shape: { type: 'up' | 'down' | 'stable', value: Number, icon: String }
  },
  loading: Boolean,
  clickable: Boolean,
  animated: {
    type: Boolean,
    default: true
  },
  rippleEnabled: {
    type: Boolean,
    default: true
  },
  formatOptions: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['click', 'hover', 'leave'])

const cardRef = ref(null)
const isHovered = ref(false)
const rippleStyle = ref({})
const previousValue = ref(props.value)

// 使用动画数值
const { animatedValue, animateTo } = useAnimatedValue(props.value)

// 计算属性
const cardClasses = computed(() => {
  return [
    'enhanced-kpi-card',
    `kpi-card--${props.variant}`,
    {
      'kpi-card--hovered': isHovered.value,
      'kpi-card--loading': props.loading,
      'kpi-card--clickable': props.clickable,
      'kpi-card--animated': props.animated
    }
  ]
})

const iconClasses = computed(() => {
  return [
    'icon-wrapper',
    `icon-wrapper--${props.variant}`
  ]
})

const iconClass = computed(() => {
  return props.icon.startsWith('icon-') ? props.icon : `icon-${props.icon}`
})

const trendClasses = computed(() => {
  if (!props.trend) return []

  return [
    'kpi-trend',
    `trend--${props.trend.type}`
  ]
})

const trendIconClass = computed(() => {
  if (!props.trend?.icon) return ''

  const iconMap = {
    up: 'icon-arrow-up',
    down: 'icon-arrow-down',
    stable: 'icon-minus'
  }

  return props.trend.icon.startsWith('icon-') ? props.trend.icon : iconMap[props.trend.type] || ''
})

const formattedValue = computed(() => {
  const numValue = Number(animatedValue.value)

  if (isNaN(numValue)) {
    return animatedValue.value
  }

  const options = {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
    ...props.formatOptions
  }

  return numValue.toLocaleString('zh-CN', options)
})

const formattedTrendValue = computed(() => {
  if (!props.trend?.value) return ''

  return `${Math.abs(props.trend.value).toFixed(1)}%`
})

const valueClasses = computed(() => {
  if (!props.trend) return []

  return [
    'kpi-value',
    `value--${props.trend.type}`
  ]
})

// 方法
const handleHover = () => {
  isHovered.value = true
  emit('hover')
}

const handleLeave = () => {
  isHovered.value = false
  emit('leave')
}

const handleClick = (event) => {
  if (!props.clickable) return

  if (props.rippleEnabled) {
    createRipple(event)
  }

  emit('click', event)
}

const createRipple = (event) => {
  if (!cardRef.value) return

  const card = cardRef.value
  const rect = card.getBoundingClientRect()

  const size = Math.max(rect.width, rect.height)
  const x = event.clientX - rect.left - size / 2
  const y = event.clientY - rect.top - size / 2

  rippleStyle.value = {
    width: `${size}px`,
    height: `${size}px`,
    left: `${x}px`,
    top: `${y}px`
  }

  // 重启动画
  setTimeout(() => {
    rippleStyle.value = { ...rippleStyle.value, animation: 'ripple-effect 0.6s ease-out' }
  }, 10)
}

// 监听数值变化，触发动画
watch(
  () => props.value,
  (newValue, oldValue) => {
    if (props.animated && typeof newValue === 'number' && typeof oldValue === 'number') {
      animateTo(newValue, 1000)
    } else {
      animatedValue.value = newValue
    }
  },
  { immediate: true }
)

onMounted(() => {
  if (props.animated && typeof props.value === 'number') {
    animateTo(props.value, 1000)
  }
})
</script>

<style scoped>
.enhanced-kpi-card {
  position: relative;
  background: var(--color-background-primary);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border-secondary);
  box-shadow: var(--shadow-light);
  overflow: hidden;
  transition: all var(--duration-base) var(--ease-out);
  cursor: default;
}

.enhanced-kpi-card.kpi-card--clickable {
  cursor: pointer;
}

.enhanced-kpi-card.kpi-card--hovered,
.enhanced-kpi-card.kpi-card--clickable:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-medium);
  border-color: var(--color-primary);
}

.enhanced-kpi-card.kpi-card--animated {
  transition: all var(--duration-slow) var(--ease-out-back);
}

/* 背景装饰 */
.kpi-card-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0.05;
  pointer-events: none;
}

.kpi-card-pattern {
  width: 100%;
  height: 100%;
  background-image:
    radial-gradient(circle at 20% 20%, var(--color-primary) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, var(--color-primary) 0%, transparent 50%);
}

/* 卡片内容 */
.kpi-card-content {
  position: relative;
  padding: var(--spacing-lg);
  z-index: 1;
}

/* 头部区域 */
.kpi-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-md);
}

.kpi-icon-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.kpi-icon-wrapper {
  position: relative;
  width: 48px;
  height: 48px;
  border-radius: var(--border-radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--duration-base) var(--ease-out);
}

.icon-wrapper--primary {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
  color: white;
}

.icon-wrapper--success {
  background: linear-gradient(135deg, var(--color-success), var(--color-success-light));
  color: white;
}

.icon-wrapper--warning {
  background: linear-gradient(135deg, var(--color-warning), var(--color-warning-light));
  color: white;
}

.icon-wrapper--danger {
  background: linear-gradient(135deg, var(--color-error), var(--color-error-light));
  color: white;
}

.icon-wrapper--info {
  background: linear-gradient(135deg, var(--color-info), var(--color-info-light));
  color: white;
}

.kpi-icon {
  font-size: 24px;
  z-index: 1;
}

.kpi-icon-decoration {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
}

/* 趋势指示器 */
.kpi-trend {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-lg);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  line-height: 1;
}

.trend--up {
  background: rgba(82, 196, 26, 0.1);
  color: var(--color-success);
}

.trend--down {
  background: rgba(255, 77, 79, 0.1);
  color: var(--color-error);
}

.trend--stable {
  background: rgba(140, 140, 140, 0.1);
  color: var(--color-text-tertiary);
}

.trend-value {
  font-weight: var(--font-weight-semibold);
}

/* 数值区域 */
.kpi-card-body {
  text-align: center;
}

.kpi-title {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-sm);
  font-weight: var(--font-weight-medium);
}

.kpi-value-container {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-xs);
}

.kpi-value {
  font-size: var(--font-size-xxl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  line-height: 1;
  transition: all var(--duration-base) var(--ease-out);
}

.value--up {
  color: var(--color-success);
}

.value--down {
  color: var(--color-error);
}

.value--stable {
  color: var(--color-text-primary);
}

.kpi-unit {
  font-size: var(--font-size-lg);
  color: var(--color-text-tertiary);
  font-weight: var(--font-weight-normal);
}

.kpi-subtitle {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  line-height: 1.4;
}

/* 底部区域 */
.kpi-card-footer {
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-light);
}

/* 加载状态 */
.kpi-card-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.loading-skeleton {
  width: 80%;
  height: 60%;
  background: linear-gradient(
    90deg,
    var(--color-background-tertiary) 25%,
    var(--color-background-quaternary) 50%,
    var(--color-background-tertiary) 75%
  );
  background-size: 200% 100%;
  animation: loading-skeleton 1.5s ease-in-out infinite;
  border-radius: var(--border-radius-base);
}

/* 波纹效果 */
.kpi-card-ripple {
  position: absolute;
  border-radius: 50%;
  background: rgba(24, 144, 255, 0.1);
  transform: scale(0);
  pointer-events: none;
  z-index: 0;
}

@keyframes ripple-effect {
  to {
    transform: scale(4);
    opacity: 0;
  }
}

@keyframes loading-skeleton {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .kpi-card-content {
    padding: var(--spacing-md);
  }

  .kpi-icon-wrapper {
    width: 40px;
    height: 40px;
  }

  .kpi-icon {
    font-size: 20px;
  }

  .kpi-value {
    font-size: var(--font-size-xl);
  }
}

/* 深色主题支持 */
@media (prefers-color-scheme: dark) {
  .enhanced-kpi-card {
    background: var(--color-background-secondary);
    border-color: var(--color-border-primary);
  }

  .kpi-card-loading {
    background: rgba(0, 0, 0, 0.8);
  }
}

/* 减少动画偏好支持 */
@media (prefers-reduced-motion: reduce) {
  .enhanced-kpi-card,
  .enhanced-kpi-card.kpi-card--animated,
  .kpi-icon-wrapper {
    transition: none;
  }

  .loading-skeleton {
    animation: none;
  }

  .kpi-card-ripple {
    animation: none;
  }
}
</style>