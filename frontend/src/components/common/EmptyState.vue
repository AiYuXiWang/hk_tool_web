<template>
  <div class="empty-state" :class="emptyClass">
    <div class="empty-icon">
      <slot name="icon">
        <svg
          v-if="type === 'no-data'"
          width="64"
          height="64"
          viewBox="0 0 64 64"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle cx="32" cy="32" r="30" stroke="currentColor" stroke-width="2" opacity="0.3"/>
          <path d="M20 32h24M32 20v24" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <svg
          v-else-if="type === 'error'"
          width="64"
          height="64"
          viewBox="0 0 64 64"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle cx="32" cy="32" r="30" stroke="currentColor" stroke-width="2" opacity="0.3"/>
          <path d="M32 20v16M32 44v4" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
        </svg>
        <svg
          v-else
          width="64"
          height="64"
          viewBox="0 0 64 64"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <rect x="16" y="12" width="32" height="40" rx="2" stroke="currentColor" stroke-width="2" opacity="0.3"/>
          <path d="M24 24h16M24 32h16M24 40h8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </slot>
    </div>
    
    <div class="empty-content">
      <h3 v-if="title" class="empty-title">{{ title }}</h3>
      <p v-if="description" class="empty-description">{{ description }}</p>
    </div>
    
    <div v-if="$slots.action || action" class="empty-action">
      <slot name="action">
        <button v-if="action" class="empty-button" @click="handleAction">
          {{ actionText }}
        </button>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'default' | 'no-data' | 'error' | 'empty'
  title?: string
  description?: string
  action?: boolean
  actionText?: string
  size?: 'sm' | 'md' | 'lg'
}

interface Emits {
  (e: 'action'): void
}

const props = withDefaults(defineProps<Props>(), {
  type: 'default',
  title: '暂无数据',
  description: '',
  action: false,
  actionText: '重新加载',
  size: 'md'
})

const emit = defineEmits<Emits>()

const emptyClass = computed(() => [
  `empty-state-${props.type}`,
  `empty-state-${props.size}`
])

const handleAction = () => {
  emit('action')
}
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl);
  text-align: center;
  color: var(--color-text-secondary);
  min-height: 300px;
}

.empty-icon {
  margin-bottom: var(--spacing-lg);
  color: var(--color-text-tertiary);
  opacity: 0.6;
  animation: fadeInScale 0.4s ease-out;
}

@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 0.6;
    transform: scale(1);
  }
}

.empty-content {
  margin-bottom: var(--spacing-lg);
}

.empty-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm) 0;
}

.empty-description {
  font-size: var(--font-size-base);
  color: var(--color-text-tertiary);
  margin: 0;
  max-width: 400px;
  line-height: 1.6;
}

.empty-action {
  margin-top: var(--spacing-md);
}

.empty-button {
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--duration-base) var(--ease-out);
}

.empty-button:hover {
  background: var(--color-primary-light);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

.empty-button:active {
  transform: translateY(0);
}

/* 尺寸变体 */
.empty-state-sm {
  min-height: 200px;
  padding: var(--spacing-lg);
}

.empty-state-sm .empty-icon svg {
  width: 48px;
  height: 48px;
}

.empty-state-sm .empty-title {
  font-size: var(--font-size-base);
}

.empty-state-sm .empty-description {
  font-size: var(--font-size-sm);
}

.empty-state-lg {
  min-height: 400px;
  padding: var(--spacing-xxl);
}

.empty-state-lg .empty-icon svg {
  width: 80px;
  height: 80px;
}

.empty-state-lg .empty-title {
  font-size: var(--font-size-xl);
}

/* 类型变体 */
.empty-state-error .empty-icon {
  color: var(--color-error);
}

.empty-state-error .empty-title {
  color: var(--color-error);
}

.empty-state-no-data .empty-icon {
  color: var(--color-warning);
}

/* 响应式 */
@media (max-width: 640px) {
  .empty-state {
    padding: var(--spacing-lg);
    min-height: 250px;
  }
  
  .empty-icon svg {
    width: 48px;
    height: 48px;
  }
  
  .empty-title {
    font-size: var(--font-size-base);
  }
  
  .empty-description {
    font-size: var(--font-size-sm);
  }
}
</style>
