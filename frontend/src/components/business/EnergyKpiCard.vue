<template>
  <BaseCard
    :class="cardClasses"
    shadow="md"
    :hoverable="true"
  >
    <div class="kpi-card-content">
      <!-- KPI头部 -->
      <div class="kpi-header">
        <div class="kpi-title">
          <h3>{{ title }}</h3>
          <span v-if="subtitle" class="kpi-subtitle">{{ subtitle }}</span>
        </div>
        <div class="kpi-icon" :class="iconClass">
          <slot name="icon">
            <svg v-if="icon" :class="icon" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <!-- 默认图标 -->
              <path d="M12 2L2 7v10c0 5.55 3.84 9.05 9 9.93 5.16-.88 9-4.38 9-9.93V7l-10-5z"/>
            </svg>
          </slot>
        </div>
      </div>
      
      <!-- KPI数值 -->
      <div class="kpi-value">
        <span class="value" :class="valueClass">
          {{ formattedValue }}
        </span>
        <span v-if="unit" class="unit">{{ unit }}</span>
      </div>
      
      <!-- KPI趋势 -->
      <div v-if="trend" class="kpi-trend">
        <span class="trend-indicator" :class="trendClasses">
          <svg
            v-if="trend.direction === 'up'"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
          <svg
            v-else-if="trend.direction === 'down'"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline>
            <polyline points="17 18 23 18 23 12"></polyline>
          </svg>
          <svg
            v-else
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          {{ trend.percentage }}%
        </span>
        <span class="trend-text">{{ trend.text || '较昨日' }}</span>
      </div>
      
      <!-- 额外信息 -->
      <div v-if="$slots.extra" class="kpi-extra">
        <slot name="extra" />
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="kpi-loading">
        <svg class="animate-spin" width="20" height="20" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" opacity="0.25"/>
          <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" opacity="0.75"/>
        </svg>
      </div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BaseCard from '../common/BaseCard.vue'

interface Trend {
  direction: 'up' | 'down' | 'stable'
  percentage: number
  text?: string
}

interface Props {
  title: string
  subtitle?: string
  value: number | string
  unit?: string
  icon?: string
  iconClass?: string
  trend?: Trend
  loading?: boolean
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  formatter?: (value: number | string) => string
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  variant: 'default',
  size: 'md'
})

const cardClasses = computed(() => {
  const classes = ['kpi-card', `kpi-card-${props.variant}`, `kpi-card-${props.size}`]
  if (props.loading) classes.push('kpi-card-loading')
  return classes
})

const valueClass = computed(() => {
  const classes = ['kpi-value-text']
  if (props.variant !== 'default') {
    classes.push(`kpi-value-${props.variant}`)
  }
  return classes
})

const trendClasses = computed(() => {
  if (!props.trend) return []
  
  const classes = ['trend-icon']
  switch (props.trend.direction) {
    case 'up':
      classes.push('trend-up')
      break
    case 'down':
      classes.push('trend-down')
      break
    case 'stable':
      classes.push('trend-stable')
      break
  }
  return classes
})

const formattedValue = computed(() => {
  if (props.loading) return '--'
  
  if (props.formatter) {
    return props.formatter(props.value)
  }
  
  if (typeof props.value === 'number') {
    // 格式化数字，添加千分位分隔符
    return props.value.toLocaleString()
  }
  
  return props.value
})
</script>

<style scoped>
.kpi-card {
  @apply relative;
}

.kpi-card-content {
  @apply p-6;
}

/* 尺寸变体 */
.kpi-card-sm .kpi-card-content {
  @apply p-4;
}

.kpi-card-lg .kpi-card-content {
  @apply p-8;
}

/* 颜色变体 */
.kpi-card-primary {
  @apply border-l-4 border-blue-500;
}

.kpi-card-success {
  @apply border-l-4 border-green-500;
}

.kpi-card-warning {
  @apply border-l-4 border-yellow-500;
}

.kpi-card-danger {
  @apply border-l-4 border-red-500;
}

/* KPI头部 */
.kpi-header {
  @apply flex items-start justify-between mb-4;
}

.kpi-title h3 {
  @apply text-lg font-semibold text-gray-900 m-0;
}

.kpi-subtitle {
  @apply text-sm text-gray-500 mt-1;
}

.kpi-icon {
  @apply flex-shrink-0 p-2 rounded-lg;
}

.kpi-card-default .kpi-icon {
  @apply bg-gray-100 text-gray-600;
}

.kpi-card-primary .kpi-icon {
  @apply bg-blue-100 text-blue-600;
}

.kpi-card-success .kpi-icon {
  @apply bg-green-100 text-green-600;
}

.kpi-card-warning .kpi-icon {
  @apply bg-yellow-100 text-yellow-600;
}

.kpi-card-danger .kpi-icon {
  @apply bg-red-100 text-red-600;
}

/* KPI数值 */
.kpi-value {
  @apply flex items-baseline space-x-2 mb-3;
}

.value {
  @apply text-3xl font-bold;
}

.kpi-card-sm .value {
  @apply text-2xl;
}

.kpi-card-lg .value {
  @apply text-4xl;
}

.kpi-value-text {
  @apply text-gray-900;
}

.kpi-value-primary {
  @apply text-blue-600;
}

.kpi-value-success {
  @apply text-green-600;
}

.kpi-value-warning {
  @apply text-yellow-600;
}

.kpi-value-danger {
  @apply text-red-600;
}

.unit {
  @apply text-lg text-gray-500 font-medium;
}

.kpi-card-sm .unit {
  @apply text-base;
}

.kpi-card-lg .unit {
  @apply text-xl;
}

/* KPI趋势 */
.kpi-trend {
  @apply flex items-center space-x-2 text-sm;
}

.trend-indicator {
  @apply flex items-center space-x-1 px-2 py-1 rounded-full font-medium;
}

.trend-up {
  @apply bg-green-100 text-green-700;
}

.trend-down {
  @apply bg-red-100 text-red-700;
}

.trend-stable {
  @apply bg-gray-100 text-gray-700;
}

.trend-text {
  @apply text-gray-500;
}

/* 额外信息 */
.kpi-extra {
  @apply mt-4 pt-4 border-t border-gray-200;
}

/* 加载状态 */
.kpi-loading {
  @apply absolute inset-0 flex items-center justify-center bg-white bg-opacity-75;
}

.kpi-card-loading .kpi-card-content {
  @apply opacity-50;
}

/* 动画 */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .kpi-title h3 {
    @apply text-gray-100;
  }
  
  .kpi-subtitle {
    @apply text-gray-400;
  }
  
  .kpi-value-text {
    @apply text-gray-100;
  }
  
  .unit {
    @apply text-gray-400;
  }
  
  .trend-text {
    @apply text-gray-400;
  }
  
  .kpi-extra {
    @apply border-gray-700;
  }
  
  .kpi-loading {
    @apply bg-gray-800 bg-opacity-75;
  }
  
  .kpi-card-default .kpi-icon {
    @apply bg-gray-700 text-gray-300;
  }
}

/* 响应式设计 */
@media (max-width: 640px) {
  .kpi-card-content {
    @apply p-4;
  }
  
  .kpi-header {
    @apply mb-3;
  }
  
  .kpi-title h3 {
    @apply text-base;
  }
  
  .value {
    @apply text-2xl;
  }
  
  .unit {
    @apply text-base;
  }
  
  .kpi-trend {
    @apply text-xs;
  }
}
</style>