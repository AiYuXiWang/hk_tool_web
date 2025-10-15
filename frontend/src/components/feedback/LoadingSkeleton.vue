<template>
  <div :class="skeletonClasses" :style="skeletonStyle">
    <!-- 卡片骨架 -->
    <template v-if="type === 'card'">
      <div class="skeleton-card">
        <div class="skeleton-header">
          <div class="skeleton-avatar"></div>
          <div class="skeleton-header-content">
            <div class="skeleton-title"></div>
            <div class="skeleton-subtitle"></div>
          </div>
        </div>
        <div class="skeleton-content">
          <div v-for="n in contentLines" :key="n" class="skeleton-line" :style="{ width: getLineWidth(n) }"></div>
        </div>
      </div>
    </template>

    <!-- 表格骨架 -->
    <template v-else-if="type === 'table'">
      <div class="skeleton-table">
        <div class="skeleton-table-header">
          <div v-for="n in columns" :key="n" class="skeleton-header-cell"></div>
        </div>
        <div v-for="row in rows" :key="row" class="skeleton-table-row">
          <div v-for="n in columns" :key="n" class="skeleton-table-cell"></div>
        </div>
      </div>
    </template>

    <!-- KPI卡片骨架 -->
    <template v-else-if="type === 'kpi'">
      <div class="skeleton-kpi">
        <div class="skeleton-kpi-icon"></div>
        <div class="skeleton-kpi-content">
          <div class="skeleton-kpi-title"></div>
          <div class="skeleton-kpi-value"></div>
          <div class="skeleton-kpi-subtitle"></div>
        </div>
      </div>
    </template>

    <!-- 图表骨架 -->
    <template v-else-if="type === 'chart'">
      <div class="skeleton-chart">
        <div class="skeleton-chart-header">
          <div class="skeleton-chart-title"></div>
          <div class="skeleton-chart-controls">
            <div class="skeleton-control"></div>
            <div class="skeleton-control"></div>
          </div>
        </div>
        <div class="skeleton-chart-content">
          <div class="skeleton-chart-bars">
            <div v-for="n in 12" :key="n" class="skeleton-bar" :style="{ height: getBarHeight() }"></div>
          </div>
        </div>
      </div>
    </template>

    <!-- 列表骨架 -->
    <template v-else-if="type === 'list'">
      <div class="skeleton-list">
        <div v-for="n in items" :key="n" class="skeleton-list-item">
          <div class="skeleton-list-avatar"></div>
          <div class="skeleton-list-content">
            <div class="skeleton-list-title"></div>
            <div class="skeleton-list-subtitle"></div>
          </div>
          <div class="skeleton-list-action"></div>
        </div>
      </div>
    </template>

    <!-- 自定义骨架 -->
    <template v-else>
      <div class="skeleton-custom">
        <div class="skeleton-block" :style="customStyle"></div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'custom',
    validator: (value) => [
      'card', 'table', 'kpi', 'chart', 'list', 'custom'
    ].includes(value)
  },
  width: {
    type: [String, Number],
    default: '100%'
  },
  height: {
    type: [String, Number],
    default: 'auto'
  },
  animated: {
    type: Boolean,
    default: true
  },
  shimmer: {
    type: Boolean,
    default: true
  },
  // 卡片类型配置
  contentLines: {
    type: Number,
    default: 3
  },
  avatar: {
    type: Boolean,
    default: true
  },
  // 表格类型配置
  columns: {
    type: Number,
    default: 4
  },
  rows: {
    type: Number,
    default: 5
  },
  // 列表类型配置
  items: {
    type: Number,
    default: 4
  },
  // 自定义样式
  customStyle: {
    type: Object,
    default: () => ({})
  }
})

const skeletonClasses = computed(() => {
  return [
    'skeleton',
    `skeleton--${props.type}`,
    {
      'skeleton--animated': props.animated,
      'skeleton--shimmer': props.shimmer
    }
  ]
})

const skeletonStyle = computed(() => {
  const style = {}

  if (props.width) {
    style.width = typeof props.width === 'number' ? `${props.width}px` : props.width
  }

  if (props.height) {
    style.height = typeof props.height === 'number' ? `${props.height}px` : props.height
  }

  return style
})

// 生成随机宽度
const getLineWidth = (index) => {
  const widths = ['90%', '70%', '85%', '60%', '75%', '95%', '80%']
  return widths[index % widths.length]
}

// 生成随机柱状图高度
const getBarHeight = () => {
  return `${Math.floor(Math.random() * 60) + 20}%`
}
</script>

<style scoped>
.skeleton {
  position: relative;
  overflow: hidden;
}

.skeleton--animated {
  animation: skeleton-pulse 2s ease-in-out infinite;
}

.skeleton--shimmer::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.4) 50%,
    transparent 100%
  );
  animation: shimmer 1.5s ease-in-out infinite;
  transform: translateX(-100%);
}

/* 基础骨架元素 */
.skeleton-block,
.skeleton-title,
.skeleton-subtitle,
.skeleton-line,
.skeleton-avatar,
.skeleton-header-cell,
.skeleton-table-cell,
.skeleton-kpi-icon,
.skeleton-kpi-title,
.skeleton-kpi-value,
.skeleton-kpi-subtitle,
.skeleton-chart-title,
.skeleton-control,
.skeleton-bar,
.skeleton-list-avatar,
.skeleton-list-title,
.skeleton-list-subtitle,
.skeleton-list-action {
  background: var(--color-background-tertiary);
  border-radius: var(--border-radius-base);
}

/* 卡片骨架 */
.skeleton-card {
  padding: var(--spacing-lg);
  border: 1px solid var(--color-border-secondary);
  border-radius: var(--border-radius-lg);
  background: var(--color-background-primary);
}

.skeleton-header {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.skeleton-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  flex-shrink: 0;
}

.skeleton-header-content {
  flex: 1;
}

.skeleton-title {
  height: 16px;
  width: 120px;
  margin-bottom: var(--spacing-sm);
}

.skeleton-subtitle {
  height: 12px;
  width: 80px;
}

.skeleton-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.skeleton-line {
  height: 14px;
}

/* 表格骨架 */
.skeleton-table {
  border: 1px solid var(--color-border-secondary);
  border-radius: var(--border-radius-lg);
  background: var(--color-background-primary);
  overflow: hidden;
}

.skeleton-table-header {
  display: flex;
  padding: var(--spacing-md);
  background: var(--color-background-tertiary);
  border-bottom: 1px solid var(--color-border-secondary);
}

.skeleton-header-cell {
  height: 16px;
  flex: 1;
  margin-right: var(--spacing-sm);
}

.skeleton-header-cell:last-child {
  margin-right: 0;
}

.skeleton-table-row {
  display: flex;
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border-light);
}

.skeleton-table-row:last-child {
  border-bottom: none;
}

.skeleton-table-cell {
  height: 14px;
  flex: 1;
  margin-right: var(--spacing-sm);
}

.skeleton-table-cell:last-child {
  margin-right: 0;
}

/* KPI骨架 */
.skeleton-kpi {
  padding: var(--spacing-lg);
  border: 1px solid var(--color-border-secondary);
  border-radius: var(--border-radius-lg);
  background: var(--color-background-primary);
  text-align: center;
}

.skeleton-kpi-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto var(--spacing-md);
  border-radius: var(--border-radius-lg);
}

.skeleton-kpi-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.skeleton-kpi-title {
  height: 12px;
  width: 60px;
  margin: 0 auto;
}

.skeleton-kpi-value {
  height: 32px;
  width: 100px;
  margin: 0 auto;
}

.skeleton-kpi-subtitle {
  height: 12px;
  width: 80px;
  margin: 0 auto;
}

/* 图表骨架 */
.skeleton-chart {
  padding: var(--spacing-lg);
  border: 1px solid var(--color-border-secondary);
  border-radius: var(--border-radius-lg);
  background: var(--color-background-primary);
}

.skeleton-chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.skeleton-chart-title {
  height: 16px;
  width: 120px;
}

.skeleton-chart-controls {
  display: flex;
  gap: var(--spacing-sm);
}

.skeleton-control {
  height: 24px;
  width: 60px;
  border-radius: var(--border-radius-sm);
}

.skeleton-chart-content {
  height: 200px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding: var(--spacing-md);
}

.skeleton-chart-bars {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  width: 100%;
  height: 100%;
  gap: 4px;
}

.skeleton-bar {
  flex: 1;
  background: var(--color-background-tertiary);
  border-radius: var(--border-radius-sm) var(--border-radius-sm) 0 0;
  min-height: 20px;
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
  border: 1px solid var(--color-border-secondary);
  border-radius: var(--border-radius-base);
  background: var(--color-background-primary);
}

.skeleton-list-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  flex-shrink: 0;
}

.skeleton-list-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.skeleton-list-title {
  height: 14px;
  width: 120px;
}

.skeleton-list-subtitle {
  height: 12px;
  width: 80px;
}

.skeleton-list-action {
  height: 24px;
  width: 60px;
  border-radius: var(--border-radius-sm);
  flex-shrink: 0;
}

/* 自定义骨架 */
.skeleton-custom {
  display: flex;
  align-items: center;
  justify-content: center;
}

.skeleton-block {
  width: 100%;
  height: 100%;
}

/* 动画效果 */
@keyframes skeleton-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* 深色主题支持 */
@media (prefers-color-scheme: dark) {
  .skeleton-card,
  .skeleton-table,
  .skeleton-kpi,
  .skeleton-chart,
  .skeleton-list-item {
    background: var(--color-background-secondary);
    border-color: var(--color-border-primary);
  }

  .skeleton-table-header {
    background: var(--color-background-tertiary);
  }

  .skeleton--shimmer::after {
    background: linear-gradient(
      90deg,
      transparent 0%,
      rgba(255, 255, 255, 0.1) 50%,
      transparent 100%
    );
  }
}

/* 减少动画偏好支持 */
@media (prefers-reduced-motion: reduce) {
  .skeleton--animated {
    animation: none;
  }

  .skeleton--shimmer::after {
    animation: none;
  }
}
</style>