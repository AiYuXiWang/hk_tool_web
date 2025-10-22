<template>
  <div :class="['stat-card', `stat-card-${variant}`]">
    <div class="stat-header">
      <div :class="['stat-icon', `icon-${variant}`]">
        <i :class="icon"></i>
      </div>
      <div class="stat-title-group">
        <h3 class="stat-title">{{ title }}</h3>
        <p v-if="subtitle" class="stat-subtitle">{{ subtitle }}</p>
      </div>
    </div>
    
    <div class="stat-content">
      <div class="stat-value">
        <span class="value-number">{{ formattedValue }}</span>
        <span class="value-unit">{{ unit }}</span>
      </div>
      
      <div v-if="trend" class="stat-trend" :class="`trend-${trend.direction || 'stable'}`">
        <i :class="getTrendIcon(trend.direction)"></i>
        <span v-if="trend.percentage !== undefined">{{ trend.percentage }}%</span>
        <span v-if="trend.text" class="trend-text">{{ trend.text }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

export interface StatTrend {
  direction?: 'up' | 'down' | 'stable'
  percentage?: number
  text?: string
}

interface Props {
  title: string
  subtitle?: string
  value: number | string
  unit?: string
  icon?: string
  variant?: 'primary' | 'success' | 'warning' | 'info' | 'danger'
  trend?: StatTrend
  formatter?: (value: number | string) => string
}

const props = withDefaults(defineProps<Props>(), {
  unit: '',
  icon: 'icon-activity',
  variant: 'primary',
  formatter: undefined
})

const formattedValue = computed(() => {
  if (props.formatter) {
    return props.formatter(props.value)
  }
  
  if (typeof props.value === 'number') {
    // 格式化数字：大于1000添加千分位
    if (props.value >= 1000) {
      return props.value.toLocaleString('zh-CN', { 
        minimumFractionDigits: 0,
        maximumFractionDigits: 1
      })
    }
    return props.value.toFixed(1)
  }
  
  return String(props.value)
})

const getTrendIcon = (direction?: string): string => {
  switch (direction) {
    case 'up':
      return 'icon-trending-up'
    case 'down':
      return 'icon-trending-down'
    case 'stable':
    default:
      return 'icon-minus'
  }
}
</script>

<style scoped>
.stat-card {
  padding: var(--spacing-md, 16px);
  background: rgba(14, 23, 51, 0.65);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(0, 212, 255, 0.35);
  border-radius: var(--border-radius-lg, 12px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(0, 255, 204, 0.05));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 212, 255, 0.25);
  border-color: rgba(0, 255, 204, 0.5);
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm, 12px);
  margin-bottom: var(--spacing-md, 16px);
  position: relative;
  z-index: 1;
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius-md, 8px);
  font-size: 24px;
  transition: transform 0.3s ease;
}

.stat-card:hover .stat-icon {
  transform: scale(1.1) rotate(5deg);
}

.icon-primary {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 255, 204, 0.2));
  color: var(--color-primary, #00D4FF);
}

.icon-success {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(52, 211, 153, 0.2));
  color: #10b981;
}

.icon-warning {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(251, 191, 36, 0.2));
  color: #f59e0b;
}

.icon-info {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(96, 165, 250, 0.2));
  color: #3b82f6;
}

.icon-danger {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(248, 113, 113, 0.2));
  color: #ef4444;
}

.stat-title-group {
  flex: 1;
}

.stat-title {
  margin: 0;
  font-size: var(--font-size-md, 16px);
  font-weight: var(--font-weight-semibold, 600);
  color: var(--color-text-primary, #ffffff);
}

.stat-subtitle {
  margin: 4px 0 0 0;
  font-size: var(--font-size-xs, 12px);
  color: var(--color-text-tertiary, rgba(255, 255, 255, 0.6));
}

.stat-content {
  position: relative;
  z-index: 1;
}

.stat-value {
  display: flex;
  align-items: baseline;
  gap: var(--spacing-xs, 8px);
  margin-bottom: var(--spacing-sm, 12px);
}

.value-number {
  font-size: 32px;
  font-weight: var(--font-weight-bold, 700);
  color: var(--color-text-primary, #ffffff);
  line-height: 1;
  animation: numberSlideIn 0.6s ease;
}

@keyframes numberSlideIn {
  0% {
    opacity: 0;
    transform: translateY(10px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.value-unit {
  font-size: var(--font-size-md, 16px);
  font-weight: var(--font-weight-medium, 500);
  color: var(--color-text-secondary, rgba(255, 255, 255, 0.8));
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs, 6px);
  font-size: var(--font-size-sm, 14px);
  font-weight: var(--font-weight-medium, 500);
}

.trend-up {
  color: #10b981;
}

.trend-down {
  color: #ef4444;
}

.trend-stable {
  color: var(--color-text-tertiary, rgba(255, 255, 255, 0.6));
}

.trend-text {
  font-size: var(--font-size-xs, 12px);
  color: var(--color-text-tertiary, rgba(255, 255, 255, 0.6));
}

/* 变体边框颜色 */
.stat-card-primary {
  border-color: rgba(0, 212, 255, 0.35);
}

.stat-card-success {
  border-color: rgba(16, 185, 129, 0.35);
}

.stat-card-warning {
  border-color: rgba(245, 158, 11, 0.35);
}

.stat-card-info {
  border-color: rgba(59, 130, 246, 0.35);
}

.stat-card-danger {
  border-color: rgba(239, 68, 68, 0.35);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stat-card {
    padding: var(--spacing-sm, 12px);
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
  
  .value-number {
    font-size: 24px;
  }
  
  .value-unit {
    font-size: var(--font-size-sm, 14px);
  }
}
</style>
