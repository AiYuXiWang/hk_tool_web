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
  background: rgba(14, 23, 51, 0.65);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(0, 212, 255, 0.35);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.kpi-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.5), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.kpi-card:hover::before {
  opacity: 1;
}

.kpi-card:hover {
  transform: translateY(-4px);
  border-color: rgba(0, 212, 255, 0.6);
  box-shadow: 0 8px 24px rgba(0, 212, 255, 0.2);
}

.kpi-card-content {
  padding: var(--spacing-lg);
}

/* 尺寸变体 */
.kpi-card-sm .kpi-card-content {
  padding: var(--spacing-md);
}

.kpi-card-lg .kpi-card-content {
  padding: var(--spacing-xl);
}

/* 颜色变体 */
.kpi-card-primary {
  border-left: 4px solid var(--color-primary);
  background: linear-gradient(135deg, rgba(14, 23, 51, 0.65) 0%, rgba(24, 144, 255, 0.05) 100%);
}

.kpi-card-success {
  border-left: 4px solid var(--color-success);
  background: linear-gradient(135deg, rgba(14, 23, 51, 0.65) 0%, rgba(82, 196, 26, 0.05) 100%);
}

.kpi-card-warning {
  border-left: 4px solid var(--color-warning);
  background: linear-gradient(135deg, rgba(14, 23, 51, 0.65) 0%, rgba(250, 173, 20, 0.05) 100%);
}

.kpi-card-danger {
  border-left: 4px solid var(--color-error);
  background: linear-gradient(135deg, rgba(14, 23, 51, 0.65) 0%, rgba(255, 77, 79, 0.05) 100%);
}

.kpi-card-info {
  border-left: 4px solid var(--color-info);
  background: linear-gradient(135deg, rgba(14, 23, 51, 0.65) 0%, rgba(0, 212, 255, 0.05) 100%);
}

/* KPI头部 */
.kpi-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--spacing-md);
}

.kpi-title h3 {
  margin: 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.kpi-subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-top: var(--spacing-xs);
}

.kpi-icon {
  flex-shrink: 0;
  padding: var(--spacing-sm);
  border-radius: var(--border-radius-lg);
}

.kpi-card-default .kpi-icon {
  background: var(--color-background-tertiary);
  color: var(--color-text-secondary);
}

.kpi-card-primary .kpi-icon {
  background: rgba(24, 144, 255, 0.12);
  color: var(--color-primary);
}

.kpi-card-success .kpi-icon {
  background: rgba(82, 196, 26, 0.12);
  color: var(--color-success);
}

.kpi-card-warning .kpi-icon {
  background: rgba(250, 173, 20, 0.12);
  color: var(--color-warning);
}

.kpi-card-danger .kpi-icon {
  background: rgba(255, 77, 79, 0.12);
  color: var(--color-error);
}

/* KPI数值 */
.kpi-value {
  display: flex;
  align-items: baseline;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.value {
  font-size: var(--font-size-xxl);
  font-weight: var(--font-weight-bold);
  font-variant-numeric: tabular-nums;
  transition: all 0.3s ease;
}

@keyframes numberPulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.kpi-card-sm .value {
  font-size: var(--font-size-xl);
}

.kpi-card-lg .value {
  font-size: 28px;
}

.kpi-value-text {
  color: var(--color-text-primary);
}

.kpi-value-primary {
  color: var(--color-primary);
}

.kpi-value-success {
  color: var(--color-success);
}

.kpi-value-warning {
  color: var(--color-warning);
}

.kpi-value-danger {
  color: var(--color-error);
}

.unit {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

.kpi-card-sm .unit {
  font-size: var(--font-size-base);
}

.kpi-card-lg .unit {
  font-size: var(--font-size-xl);
}

/* KPI趋势 */
.kpi-trend {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.trend-indicator {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: 2px 8px;
  border-radius: 999px;
  font-weight: var(--font-weight-medium);
}

.trend-up {
  background: rgba(82, 196, 26, 0.12);
  color: var(--color-success-dark);
}

.trend-down {
  background: rgba(255, 77, 79, 0.12);
  color: var(--color-error-dark);
}

.trend-stable {
  background: var(--color-background-tertiary);
  color: var(--color-text-secondary);
}

.trend-text {
  color: var(--color-text-secondary);
}

/* 额外信息 */
.kpi-extra {
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-secondary);
}

/* 加载状态 */
.kpi-loading {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(14, 23, 51, 0.75);
  opacity: 0.75;
}

.kpi-card-loading .kpi-card-content {
  opacity: 0.5;
}

/* 深色模式支持（用设计令牌变量） */
@media (prefers-color-scheme: dark) {
  .kpi-title h3 {
    color: var(--color-text-primary);
  }
  
  .kpi-subtitle,
  .unit,
  .trend-text {
    color: var(--color-text-secondary);
  }
  
  .kpi-extra {
    border-color: var(--color-border-secondary);
  }
  
  .kpi-loading {
    background: rgba(14, 23, 51, 0.85);
  }
  
  .kpi-card {
    background: rgba(14, 23, 51, 0.65);
    border-color: rgba(0, 212, 255, 0.45);
  }
}

/* 响应式设计 */
@media (max-width: 640px) {
  .kpi-card-content {
    padding: var(--spacing-md);
  }
  
  .kpi-header {
    margin-bottom: var(--spacing-sm);
  }
  
  .kpi-title h3 {
    font-size: var(--font-size-base);
  }
  
  .value {
    font-size: var(--font-size-xl);
  }
  
  .unit {
    font-size: var(--font-size-base);
  }
  
  .kpi-trend {
    font-size: var(--font-size-xs);
  }
}
</style>