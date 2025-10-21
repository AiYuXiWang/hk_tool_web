<template>
  <div :class="cardClasses">
    <!-- 卡片头部 -->
    <div v-if="$slots.header || title || $slots.extra" class="card-header">
      <div class="card-header-content">
        <slot name="header">
          <h3 v-if="title" class="card-title">{{ title }}</h3>
        </slot>
      </div>
      <div v-if="$slots.extra" class="card-extra">
        <slot name="extra" />
      </div>
    </div>
    
    <!-- 卡片内容 -->
    <div :class="bodyClasses">
      <slot />
    </div>
    
    <!-- 卡片底部 -->
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title?: string
  shadow?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
  border?: boolean
  hoverable?: boolean
  loading?: boolean
  size?: 'sm' | 'md' | 'lg'
  bodyPadding?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  shadow: 'md',
  border: true,
  hoverable: false,
  loading: false,
  size: 'md',
  bodyPadding: true
})

const cardClasses = computed(() => {
  const classes = ['card', `card-${props.size}`]
  
  if (props.shadow !== 'none') classes.push(`shadow-${props.shadow}`)
  if (props.border) classes.push('card-bordered')
  if (props.hoverable) classes.push('card-hoverable')
  if (props.loading) classes.push('card-loading')
  
  return classes
})

const bodyClasses = computed(() => {
  const classes = ['card-body']
  if (props.bodyPadding) classes.push('card-body-padded')
  return classes
})
</script>

<style scoped>
.card {
  background: var(--color-background-primary);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-light);
  transition: all var(--duration-base) var(--ease-out);
}

/* 边框样式 */
.card-bordered {
  border: 1px solid var(--color-border-secondary);
}

/* 悬停效果 */
.card-hoverable {
  cursor: pointer;
}

.card-hoverable:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-2px);
}

/* 加载状态 */
.card-loading {
  position: relative;
  overflow: hidden;
}

.card-loading::before {
  content: '';
  background: linear-gradient(90deg, transparent 25%, var(--color-background-quaternary) 50%, transparent 75%);
  opacity: 0.3;
  animation: shimmer 1.5s infinite;
  transform: translateX(-100%);
  position: absolute;
  inset: 0;
}

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-secondary);
  background: var(--color-background-secondary);
}

.card-header-content {
  flex: 1;
}

.card-title {
  margin: 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.card-extra {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

/* 卡片内容 */
.card-body {
  position: relative;
}

.card-body-padded {
  padding: var(--spacing-lg);
}

/* 卡片底部 */
.card-footer {
  padding: var(--spacing-md) var(--spacing-lg);
  border-top: 1px solid var(--color-border-secondary);
  background: var(--color-background-secondary);
}

/* 动画 */
@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* 深色模式支持（使用设计令牌变量） */
@media (prefers-color-scheme: dark) {
  .card {
    background: var(--color-background-primary);
    border-color: var(--color-border-secondary);
  }
  .card-header,
  .card-footer {
    background: var(--color-background-secondary);
    border-color: var(--color-border-secondary);
  }
  .card-title {
    color: var(--color-text-primary);
  }
}

/* 响应式设计 */
@media (max-width: 640px) {
  .card-header,
  .card-body-padded,
  .card-footer {
    padding: var(--spacing-sm) var(--spacing-md);
  }
  .card-title {
    font-size: var(--font-size-base);
  }
}
</style>