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
  @apply bg-white rounded-lg overflow-hidden transition-all duration-200;
}

/* 尺寸变体 */
.card-sm {
  @apply text-sm;
}

.card-md {
  @apply text-base;
}

.card-lg {
  @apply text-lg;
}

/* 边框样式 */
.card-bordered {
  @apply border border-gray-200;
}

/* 悬停效果 */
.card-hoverable {
  @apply cursor-pointer;
}

.card-hoverable:hover {
  @apply shadow-lg transform -translate-y-1;
}

/* 加载状态 */
.card-loading {
  @apply relative overflow-hidden;
}

.card-loading::before {
  content: '';
  @apply absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30;
  animation: shimmer 1.5s infinite;
  transform: translateX(-100%);
}

/* 卡片头部 */
.card-header {
  @apply flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50;
}

.card-header-content {
  @apply flex-1;
}

.card-title {
  @apply text-lg font-semibold text-gray-900 m-0;
}

.card-extra {
  @apply flex items-center space-x-2;
}

/* 卡片内容 */
.card-body {
  @apply relative;
}

.card-body-padded {
  @apply p-6;
}

/* 卡片底部 */
.card-footer {
  @apply px-6 py-4 border-t border-gray-200 bg-gray-50;
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

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .card {
    @apply bg-gray-800 border-gray-700;
  }
  
  .card-header,
  .card-footer {
    @apply bg-gray-700 border-gray-600;
  }
  
  .card-title {
    @apply text-gray-100;
  }
  
  .card-loading::before {
    @apply via-gray-700;
  }
}

/* 响应式设计 */
@media (max-width: 640px) {
  .card-header,
  .card-body-padded,
  .card-footer {
    @apply px-4 py-3;
  }
  
  .card-title {
    @apply text-base;
  }
}
</style>