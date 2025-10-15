<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    @click="handleClick"
    @mouseenter="handleHover"
    @mouseleave="handleLeave"
    ref="buttonRef"
  >
    <!-- 加载状态 -->
    <span v-if="loading" class="button-loading">
      <i class="icon-loading icon-spin"></i>
    </span>

    <!-- 按钮图标 -->
    <span v-if="icon && !loading" class="button-icon">
      <i :class="icon"></i>
    </span>

    <!-- 按钮内容 -->
    <span class="button-text">
      <slot>{{ text }}</slot>
    </span>

    <!-- 波纹效果 -->
    <span
      v-if="rippleEnabled"
      class="button-ripple"
      :style="rippleStyle"
      ref="rippleRef"
    ></span>
  </button>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useAnimation } from '@/composables/useAnimation'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => [
      'primary', 'secondary', 'success', 'warning', 'danger', 'info', 'ghost'
    ].includes(value)
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg', 'xl'].includes(value)
  },
  icon: String,
  loading: Boolean,
  disabled: Boolean,
  text: String,
  rounded: {
    type: Boolean,
    default: false
  },
  rippleEnabled: {
    type: Boolean,
    default: true
  },
  animated: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['click', 'hover', 'leave'])

const buttonRef = ref(null)
const rippleRef = ref(null)
const isHovered = ref(false)
const rippleStyle = ref({})

const buttonClasses = computed(() => {
  return [
    'enhanced-button',
    `enhanced-button--${props.variant}`,
    `enhanced-button--${props.size}`,
    {
      'enhanced-button--loading': props.loading,
      'enhanced-button--disabled': props.disabled,
      'enhanced-button--rounded': props.rounded,
      'enhanced-button--hovered': isHovered.value,
      'enhanced-button--has-icon': props.icon,
      'enhanced-button--animated': props.animated
    }
  ]
})

const handleClick = (event) => {
  if (props.disabled || props.loading) return

  if (props.rippleEnabled) {
    createRipple(event)
  }

  emit('click', event)
}

const handleHover = () => {
  isHovered.value = true
  emit('hover')
}

const handleLeave = () => {
  isHovered.value = false
  emit('leave')
}

const createRipple = (event) => {
  if (!buttonRef.value || !rippleRef.value) return

  const button = buttonRef.value
  const ripple = rippleRef.value
  const rect = button.getBoundingClientRect()

  const size = Math.max(rect.width, rect.height)
  const x = event.clientX - rect.left - size / 2
  const y = event.clientY - rect.top - size / 2

  rippleStyle.value = {
    width: `${size}px`,
    height: `${size}px`,
    left: `${x}px`,
    top: `${y}px`
  }

  // 重启动画
  ripple.style.animation = 'none'
  nextTick(() => {
    ripple.style.animation = ''
  })
}
</script>

<style scoped>
.enhanced-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-xs);
  border: none;
  border-radius: var(--border-radius-base);
  font-family: var(--font-family-base);
  font-weight: var(--font-weight-medium);
  line-height: 1;
  text-decoration: none;
  cursor: pointer;
  transition: all var(--duration-base) var(--ease-out);
  overflow: hidden;
  user-select: none;
  vertical-align: middle;
  white-space: nowrap;
}

/* 尺寸变体 */
.enhanced-button--sm {
  height: var(--height-sm);
  padding: 0 var(--spacing-md);
  font-size: var(--font-size-sm);
  min-height: 40px;
}

.enhanced-button--md {
  height: var(--height-base);
  padding: 0 var(--spacing-lg);
  font-size: var(--font-size-base);
  min-height: 40px;
}

.enhanced-button--lg {
  height: var(--height-lg);
  padding: 0 var(--spacing-xl);
  font-size: var(--font-size-lg);
  min-height: 48px;
}

.enhanced-button--xl {
  height: var(--height-xl);
  padding: 0 var(--spacing-xxl);
  font-size: var(--font-size-xl);
  min-height: 56px;
}

/* 变体样式 */
.enhanced-button--primary {
  background: var(--color-primary);
  color: white;
  box-shadow: var(--shadow-light);
}

.enhanced-button--primary:hover:not(.enhanced-button--disabled) {
  background: var(--color-primary-light);
  box-shadow: var(--shadow-hover);
  transform: translateY(-1px);
}

.enhanced-button--secondary {
  background: var(--color-background-tertiary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border-primary);
}

.enhanced-button--secondary:hover:not(.enhanced-button--disabled) {
  background: var(--color-background-quaternary);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.enhanced-button--success {
  background: var(--color-success);
  color: white;
}

.enhanced-button--success:hover:not(.enhanced-button--disabled) {
  background: var(--color-success-light);
  transform: translateY(-1px);
}

.enhanced-button--warning {
  background: var(--color-warning);
  color: white;
}

.enhanced-button--warning:hover:not(.enhanced-button--disabled) {
  background: var(--color-warning-light);
  transform: translateY(-1px);
}

.enhanced-button--danger {
  background: var(--color-error);
  color: white;
}

.enhanced-button--danger:hover:not(.enhanced-button--disabled) {
  background: var(--color-error-light);
  transform: translateY(-1px);
}

.enhanced-button--info {
  background: var(--color-info);
  color: white;
}

.enhanced-button--info:hover:not(.enhanced-button--disabled) {
  background: var(--color-info-light);
  transform: translateY(-1px);
}

.enhanced-button--ghost {
  background: transparent;
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
}

.enhanced-button--ghost:hover:not(.enhanced-button--disabled) {
  background: var(--color-primary);
  color: white;
}

/* 状态样式 */
.enhanced-button--disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.enhanced-button--loading {
  cursor: wait;
}

.enhanced-button--rounded {
  border-radius: var(--border-radius-round);
}

/* 动画效果 */
.enhanced-button--animated {
  transition: all var(--duration-base) var(--ease-out-back);
}

.enhanced-button--animated:active:not(.enhanced-button--disabled) {
  transform: scale(0.95) translateY(0);
}

/* 波纹效果 */
.button-ripple {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: scale(0);
  animation: ripple-effect 0.6s ease-out;
  pointer-events: none;
}

@keyframes ripple-effect {
  to {
    transform: scale(4);
    opacity: 0;
  }
}

/* 加载动画 */
.button-loading {
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-loading {
  font-size: 1em;
}

/* 按钮内容 */
.button-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.button-text {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .enhanced-button {
    min-height: 44px; /* 移动端最小点击区域 */
  }
}

/* 无障碍支持 */
.enhanced-button:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

/* 减少动画偏好支持 */
@media (prefers-reduced-motion: reduce) {
  .enhanced-button,
  .enhanced-button--animated {
    transition: none;
  }

  .button-ripple {
    animation: none;
  }

  .icon-spin {
    animation: none;
  }
}
</style>