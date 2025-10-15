<template>
  <Teleport to="body">
    <Transition name="modal" appear>
      <div
        v-if="visible"
        class="modal-overlay"
        @click="handleOverlayClick"
      >
        <div
          :class="modalClasses"
          @click.stop
          role="dialog"
          :aria-labelledby="titleId"
          :aria-describedby="contentId"
        >
          <!-- 模态框头部 -->
          <div v-if="$slots.header || title || closable" class="modal-header">
            <slot name="header">
              <h3 v-if="title" :id="titleId" class="modal-title">
                {{ title }}
              </h3>
            </slot>
            
            <button
              v-if="closable"
              @click="handleClose"
              class="modal-close-btn"
              aria-label="关闭"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
          
          <!-- 模态框内容 -->
          <div :id="contentId" class="modal-content">
            <slot />
          </div>
          
          <!-- 模态框底部 -->
          <div v-if="$slots.footer" class="modal-footer">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, watch } from 'vue'

interface Props {
  visible: boolean
  title?: string
  width?: string | number
  height?: string | number
  closable?: boolean
  maskClosable?: boolean
  destroyOnClose?: boolean
  centered?: boolean
  fullscreen?: boolean
  size?: 'sm' | 'md' | 'lg' | 'xl'
  zIndex?: number
}

interface Emits {
  (e: 'update:visible', visible: boolean): void
  (e: 'close'): void
  (e: 'open'): void
}

const props = withDefaults(defineProps<Props>(), {
  closable: true,
  maskClosable: true,
  destroyOnClose: false,
  centered: true,
  fullscreen: false,
  size: 'md',
  zIndex: 1000
})

const emit = defineEmits<Emits>()

const titleId = computed(() => `modal-title-${Math.random().toString(36).substr(2, 9)}`)
const contentId = computed(() => `modal-content-${Math.random().toString(36).substr(2, 9)}`)

const modalClasses = computed(() => {
  const classes = ['modal', `modal-${props.size}`]
  
  if (props.centered) classes.push('modal-centered')
  if (props.fullscreen) classes.push('modal-fullscreen')
  
  return classes
})

const modalStyle = computed(() => {
  const style: any = {
    zIndex: props.zIndex
  }
  
  if (props.width) {
    style.width = typeof props.width === 'number' ? `${props.width}px` : props.width
  }
  
  if (props.height) {
    style.height = typeof props.height === 'number' ? `${props.height}px` : props.height
  }
  
  return style
})

const handleClose = () => {
  emit('update:visible', false)
  emit('close')
}

const handleOverlayClick = () => {
  if (props.maskClosable) {
    handleClose()
  }
}

const handleEscapeKey = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.visible && props.closable) {
    handleClose()
  }
}

// 监听键盘事件
onMounted(() => {
  document.addEventListener('keydown', handleEscapeKey)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscapeKey)
})

// 监听可见性变化
watch(() => props.visible, (newVisible) => {
  if (newVisible) {
    emit('open')
    // 禁止背景滚动
    document.body.style.overflow = 'hidden'
  } else {
    // 恢复背景滚动
    document.body.style.overflow = ''
  }
})

// 组件卸载时恢复滚动
onUnmounted(() => {
  document.body.style.overflow = ''
})
</script>

<style scoped>
.modal-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4;
  z-index: v-bind('props.zIndex');
}

.modal {
  @apply bg-white rounded-lg shadow-xl max-w-full max-h-full overflow-hidden;
  v-bind: modalStyle;
}

/* 尺寸变体 */
.modal-sm {
  @apply w-96;
}

.modal-md {
  @apply w-[32rem];
}

.modal-lg {
  @apply w-[48rem];
}

.modal-xl {
  @apply w-[64rem];
}

.modal-fullscreen {
  @apply w-full h-full rounded-none;
}

.modal-centered {
  @apply mx-auto;
}

/* 模态框头部 */
.modal-header {
  @apply flex items-center justify-between p-6 border-b border-gray-200;
}

.modal-title {
  @apply text-lg font-semibold text-gray-900 m-0;
}

.modal-close-btn {
  @apply p-1 text-gray-400 hover:text-gray-600 transition-colors duration-200 rounded-md hover:bg-gray-100;
}

/* 模态框内容 */
.modal-content {
  @apply p-6 overflow-y-auto;
  max-height: calc(100vh - 200px);
}

.modal-fullscreen .modal-content {
  @apply flex-1;
  max-height: none;
}

/* 模态框底部 */
.modal-footer {
  @apply flex items-center justify-end space-x-3 p-6 border-t border-gray-200 bg-gray-50;
}

/* 过渡动画 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-active .modal,
.modal-leave-active .modal {
  transition: transform 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal,
.modal-leave-to .modal {
  transform: scale(0.9) translateY(-20px);
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .modal {
    @apply bg-gray-800 text-gray-100;
  }
  
  .modal-header {
    @apply border-gray-700;
  }
  
  .modal-title {
    @apply text-gray-100;
  }
  
  .modal-close-btn {
    @apply text-gray-400 hover:text-gray-200 hover:bg-gray-700;
  }
  
  .modal-footer {
    @apply border-gray-700 bg-gray-900;
  }
}

/* 响应式设计 */
@media (max-width: 640px) {
  .modal-overlay {
    @apply p-2;
  }
  
  .modal-sm,
  .modal-md,
  .modal-lg,
  .modal-xl {
    @apply w-full;
  }
  
  .modal-header,
  .modal-content,
  .modal-footer {
    @apply p-4;
  }
  
  .modal-content {
    max-height: calc(100vh - 150px);
  }
}
</style>