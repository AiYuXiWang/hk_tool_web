<template>
  <div class="time-range-selector">
    <button
      v-for="range in ranges"
      :key="range.value"
      :class="['range-btn', { active: modelValue === range.value }]"
      @click="selectRange(range.value)"
    >
      <span class="range-label">{{ range.label }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface TimeRange {
  label: string
  value: string
}

interface Props {
  modelValue: string
  ranges?: TimeRange[]
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  ranges: () => [
    { label: '24小时', value: '24h' },
    { label: '7天', value: '7d' },
    { label: '30天', value: '30d' },
    { label: '90天', value: '90d' }
  ]
})

const emit = defineEmits<Emits>()

const selectRange = (value: string) => {
  if (value !== props.modelValue) {
    emit('update:modelValue', value)
    emit('change', value)
  }
}
</script>

<style scoped>
.time-range-selector {
  display: flex;
  gap: var(--spacing-sm, 12px);
  flex-wrap: wrap;
}

.range-btn {
  padding: var(--spacing-sm, 12px) var(--spacing-md, 16px);
  background: rgba(14, 23, 51, 0.65);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(0, 212, 255, 0.35);
  border-radius: var(--border-radius-md, 8px);
  color: var(--color-text-secondary, rgba(255, 255, 255, 0.8));
  font-size: var(--font-size-sm, 14px);
  font-weight: var(--font-weight-medium, 500);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.range-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 255, 204, 0.1));
  opacity: 0;
  transition: opacity 0.2s ease;
}

.range-btn:hover {
  border-color: rgba(0, 255, 204, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 212, 255, 0.25);
}

.range-btn:hover::before {
  opacity: 1;
}

.range-btn.active {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.25), rgba(0, 255, 204, 0.15));
  border-color: rgba(0, 255, 204, 0.85);
  color: var(--color-text-primary, #ffffff);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.4), inset 0 0 10px rgba(0, 255, 204, 0.2);
  animation: scaleIn 0.3s ease;
}

.range-btn.active::before {
  opacity: 1;
}

.range-label {
  position: relative;
  z-index: 1;
}

@keyframes scaleIn {
  0% {
    transform: scale(0.95);
  }
  50% {
    transform: scale(1.02);
  }
  100% {
    transform: scale(1);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .range-btn {
    flex: 1;
    min-width: 80px;
    padding: var(--spacing-xs, 8px) var(--spacing-sm, 12px);
    font-size: var(--font-size-xs, 12px);
  }
}
</style>
