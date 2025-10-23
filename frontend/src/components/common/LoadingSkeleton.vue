<template>
  <div class="loading-skeleton" :class="skeletonClass">
    <div v-if="variant === 'card'" class="skeleton-card">
      <div class="skeleton-header">
        <div class="skeleton-line" style="width: 40%"></div>
        <div class="skeleton-circle"></div>
      </div>
      <div class="skeleton-body">
        <div class="skeleton-line" style="width: 60%; height: 40px"></div>
        <div class="skeleton-line" style="width: 30%; margin-top: 8px"></div>
      </div>
    </div>
    
    <div v-else-if="variant === 'chart'" class="skeleton-chart">
      <div class="skeleton-line" style="width: 30%; margin-bottom: 16px"></div>
      <div class="skeleton-chart-area">
        <div class="skeleton-bars">
          <div class="skeleton-bar" v-for="i in 6" :key="i" :style="{ height: `${Math.random() * 60 + 40}%` }"></div>
        </div>
      </div>
    </div>
    
    <div v-else-if="variant === 'list'" class="skeleton-list">
      <div class="skeleton-list-item" v-for="i in count" :key="i">
        <div class="skeleton-circle"></div>
        <div class="skeleton-content">
          <div class="skeleton-line" style="width: 60%"></div>
          <div class="skeleton-line" style="width: 40%; margin-top: 8px"></div>
        </div>
      </div>
    </div>
    
    <div v-else class="skeleton-default">
      <div class="skeleton-line" v-for="i in count" :key="i" :style="lineStyle"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'default' | 'card' | 'chart' | 'list'
  count?: number
  animated?: boolean
  width?: string
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  count: 3,
  animated: true
})

const skeletonClass = computed(() => ({
  'skeleton-animated': props.animated
}))

const lineStyle = computed(() => ({
  width: props.width || '100%',
  height: props.height || '16px'
}))
</script>

<style scoped>
.loading-skeleton {
  width: 100%;
}

.skeleton-animated .skeleton-line,
.skeleton-animated .skeleton-circle,
.skeleton-animated .skeleton-bar {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.08) 25%,
    rgba(255, 255, 255, 0.15) 50%,
    rgba(255, 255, 255, 0.08) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* 基础元素 */
.skeleton-line {
  height: 16px;
  border-radius: var(--border-radius-sm);
  background: rgba(255, 255, 255, 0.1);
  margin-bottom: 8px;
}

.skeleton-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
}

/* 卡片骨架 */
.skeleton-card {
  padding: var(--spacing-lg);
}

.skeleton-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.skeleton-body {
  display: flex;
  flex-direction: column;
}

/* 图表骨架 */
.skeleton-chart {
  padding: var(--spacing-lg);
}

.skeleton-chart-area {
  height: 300px;
  display: flex;
  align-items: flex-end;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--border-radius-md);
}

.skeleton-bars {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  width: 100%;
  height: 100%;
  gap: 8px;
}

.skeleton-bar {
  flex: 1;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--border-radius-sm) var(--border-radius-sm) 0 0;
  min-height: 20%;
}

/* 列表骨架 */
.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.skeleton-list-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--border-radius-md);
}

.skeleton-content {
  flex: 1;
}

/* 默认骨架 */
.skeleton-default {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}
</style>
