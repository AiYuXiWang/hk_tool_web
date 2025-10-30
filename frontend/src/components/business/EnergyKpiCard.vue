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
  background: 
    linear-gradient(135deg, rgba(14, 23, 51, 0.85) 0%, rgba(20, 35, 62, 0.75) 100%);
  backdrop-filter: blur(20px) saturate(200%);
  border: 1px solid rgba(0, 212, 255, 0.35);
  border-radius: var(--panel-radius, var(--border-radius-lg));
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  box-shadow: 
    0 4px 20px rgba(0, 0, 0, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  isolation: isolate;
}

/* 顶部渐变光效 */
.kpi-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(0, 212, 255, 0.8) 25%, 
    rgba(0, 255, 204, 1) 50%, 
    rgba(0, 212, 255, 0.8) 75%, 
    transparent 100%);
  opacity: 0;
  transition: opacity 0.4s ease;
  animation: shimmerFlow 3s ease-in-out infinite;
}

/* 发光边框效果 */
.kpi-card::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1px;
  background: linear-gradient(135deg, 
    rgba(0, 212, 255, 0.5), 
    rgba(138, 43, 226, 0.3), 
    rgba(0, 255, 204, 0.5));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 0.4s ease;
}

@keyframes shimmerFlow {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.kpi-card:hover::before {
  opacity: 1;
}

.kpi-card:hover::after {
  opacity: 0.6;
}

.kpi-card:hover {
  transform: translateY(-6px) scale(1.02);
  border-color: rgba(0, 212, 255, 0.7);
  box-shadow: 
    0 12px 40px rgba(0, 212, 255, 0.3),
    0 0 30px rgba(0, 212, 255, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.kpi-card-content {
  position: relative;
  padding: 12px 14px;
  z-index: 1;
}

/* 尺寸变体 */
.kpi-card-sm .kpi-card-content {
  padding: 8px 10px;
}

.kpi-card-lg .kpi-card-content {
  padding: 16px 18px;
}

/* 颜色变体 */
.kpi-card-primary {
  border-color: rgba(0, 212, 255, 0.55);
  box-shadow: 
    0 12px 36px rgba(0, 212, 255, 0.18),
    inset 0 1px 0 rgba(255, 255, 255, 0.18);
  background: linear-gradient(135deg, rgba(14, 23, 51, 0.85) 0%, rgba(24, 144, 255, 0.28) 40%, rgba(14, 23, 51, 0.75) 100%);
}

.kpi-card-success {
  border-color: rgba(82, 196, 26, 0.45);
  box-shadow: 
    0 12px 36px rgba(82, 196, 26, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
  background: linear-gradient(135deg, rgba(14, 23, 51, 0.85) 0%, rgba(82, 196, 26, 0.25) 40%, rgba(14, 23, 51, 0.75) 100%);
}

.kpi-card-warning {
  border-color: rgba(250, 173, 20, 0.45);
  box-shadow: 
    0 12px 36px rgba(250, 173, 20, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
  background: linear-gradient(135deg, rgba(14, 23, 51, 0.85) 0%, rgba(250, 173, 20, 0.25) 40%, rgba(14, 23, 51, 0.75) 100%);
}

.kpi-card-danger {
  border-color: rgba(255, 77, 79, 0.45);
  box-shadow: 
    0 12px 36px rgba(255, 77, 79, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
  background: linear-gradient(135deg, rgba(14, 23, 51, 0.85) 0%, rgba(255, 77, 79, 0.25) 40%, rgba(14, 23, 51, 0.75) 100%);
}

.kpi-card-info {
  border-color: rgba(0, 212, 255, 0.55);
  box-shadow: 
    0 12px 36px rgba(0, 212, 255, 0.18),
    inset 0 1px 0 rgba(255, 255, 255, 0.18);
  background: linear-gradient(135deg, rgba(14, 23, 51, 0.85) 0%, rgba(0, 212, 255, 0.28) 40%, rgba(14, 23, 51, 0.75) 100%);
}

/* KPI头部 */
.kpi-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 8px;
}

.kpi-title h3 {
  margin: 0;
  font-size: 14px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.kpi-subtitle {
  font-size: 11px;
  color: var(--color-text-secondary);
  margin-top: 3px;
}

.kpi-icon {
  flex-shrink: 0;
  padding: 8px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(0, 212, 255, 0.18) 100%);
  box-shadow: 0 10px 30px rgba(0, 212, 255, 0.2);
  backdrop-filter: blur(12px);
}

.kpi-icon svg {
  width: 18px;
  height: 18px;
}

.kpi-card-default .kpi-icon {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(15, 25, 45, 0.6) 100%);
  color: var(--color-text-secondary);
  box-shadow: none;
}

.kpi-card-primary .kpi-icon {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.3) 0%, rgba(24, 144, 255, 0.6) 100%);
  color: var(--color-primary-contrast, #0b2f40);
  box-shadow: 0 10px 30px rgba(24, 144, 255, 0.35);
}

.kpi-card-success .kpi-icon {
  background: linear-gradient(135deg, rgba(82, 196, 26, 0.3) 0%, rgba(111, 207, 151, 0.65) 100%);
  color: var(--color-success-contrast, #10351d);
  box-shadow: 0 10px 30px rgba(82, 196, 26, 0.3);
}

.kpi-card-warning .kpi-icon {
  background: linear-gradient(135deg, rgba(250, 173, 20, 0.3) 0%, rgba(255, 214, 102, 0.65) 100%);
  color: var(--color-warning-contrast, #402b04);
  box-shadow: 0 10px 30px rgba(250, 173, 20, 0.3);
}

.kpi-card-danger .kpi-icon {
  background: linear-gradient(135deg, rgba(255, 77, 79, 0.3) 0%, rgba(255, 138, 141, 0.65) 100%);
  color: var(--color-error-contrast, #3f0e11);
  box-shadow: 0 10px 30px rgba(255, 77, 79, 0.3);
}

/* KPI数值 */
.kpi-value {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-bottom: 6px;
}

.value {
  font-size: 22px;
  font-weight: var(--font-weight-bold);
  font-variant-numeric: tabular-nums;
  text-shadow: 
    0 0 14px rgba(0, 212, 255, 0.45),
    0 0 24px rgba(0, 212, 255, 0.28),
    0 1px 3px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
  filter: drop-shadow(0 0 6px rgba(0, 212, 255, 0.5));
}

.kpi-card:hover .value {
  text-shadow: 
    0 0 22px rgba(0, 212, 255, 0.7),
    0 0 32px rgba(0, 212, 255, 0.45),
    0 2px 6px rgba(0, 0, 0, 0.4);
  filter: drop-shadow(0 0 10px rgba(0, 255, 204, 0.7));
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
  font-size: 18px;
}

.kpi-card-lg .value {
  font-size: 26px;
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
  font-size: 13px;
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

.kpi-card-sm .unit {
  font-size: 12px;
}

.kpi-card-lg .unit {
  font-size: 15px;
}

/* KPI趋势 */
.kpi-trend {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
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