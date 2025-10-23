<template>
  <div v-if="visible" class="progress-bar" :class="progressClass">
    <div class="progress-bar-inner" :style="progressStyle"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Props {
  visible: boolean
  progress?: number
  color?: string
  height?: number
  animated?: boolean
  indeterminate?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  progress: 0,
  color: '#00d4ff',
  height: 3,
  animated: true,
  indeterminate: false
})

const progressClass = computed(() => ({
  'progress-bar-animated': props.animated,
  'progress-bar-indeterminate': props.indeterminate
}))

const progressStyle = computed(() => ({
  width: props.indeterminate ? '30%' : `${props.progress}%`,
  background: props.color,
  height: `${props.height}px`
}))
</script>

<style scoped>
.progress-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: var(--z-index-fixed);
  overflow: hidden;
}

.progress-bar-inner {
  height: 3px;
  transition: width 0.3s ease;
  box-shadow: 0 0 10px currentColor;
}

.progress-bar-animated .progress-bar-inner {
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.progress-bar-indeterminate .progress-bar-inner {
  animation: indeterminate 1.5s infinite;
}

@keyframes indeterminate {
  0% {
    left: -30%;
  }
  100% {
    left: 100%;
  }
}
</style>
