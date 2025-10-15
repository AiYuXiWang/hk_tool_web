<template>
  <div :class="wrapperClasses">
    <!-- 标签 -->
    <label v-if="label" :for="inputId" class="input-label">
      {{ label }}
      <span v-if="required" class="input-required">*</span>
    </label>
    
    <!-- 输入框容器 -->
    <div class="input-container">
      <!-- 前缀图标 -->
      <span v-if="prefixIcon" class="input-prefix">
        <component :is="prefixIcon" />
      </span>
      
      <!-- 输入框 -->
      <input
        :id="inputId"
        ref="inputRef"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :maxlength="maxlength"
        :class="inputClasses"
        @input="handleInput"
        @change="handleChange"
        @focus="handleFocus"
        @blur="handleBlur"
        @keydown="handleKeydown"
      />
      
      <!-- 后缀图标 -->
      <span v-if="suffixIcon || clearable" class="input-suffix">
        <!-- 清除按钮 -->
        <button
          v-if="clearable && modelValue && !disabled && !readonly"
          type="button"
          class="input-clear"
          @click="handleClear"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </button>
        
        <!-- 后缀图标 -->
        <component v-if="suffixIcon" :is="suffixIcon" />
      </span>
    </div>
    
    <!-- 帮助文本或错误信息 -->
    <div v-if="helpText || errorMessage" class="input-help">
      <span v-if="errorMessage" class="input-error">{{ errorMessage }}</span>
      <span v-else-if="helpText" class="input-help-text">{{ helpText }}</span>
    </div>
    
    <!-- 字符计数 -->
    <div v-if="showCount && maxlength" class="input-count">
      {{ (modelValue || '').length }} / {{ maxlength }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, nextTick } from 'vue'

interface Props {
  modelValue?: string | number
  type?: 'text' | 'password' | 'email' | 'number' | 'tel' | 'url' | 'search'
  label?: string
  placeholder?: string
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  clearable?: boolean
  showCount?: boolean
  maxlength?: number
  size?: 'sm' | 'md' | 'lg'
  status?: 'default' | 'error' | 'warning' | 'success'
  prefixIcon?: any
  suffixIcon?: any
  helpText?: string
  errorMessage?: string
}

interface Emits {
  (e: 'update:modelValue', value: string | number): void
  (e: 'change', value: string | number): void
  (e: 'focus', event: FocusEvent): void
  (e: 'blur', event: FocusEvent): void
  (e: 'clear'): void
  (e: 'keydown', event: KeyboardEvent): void
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  disabled: false,
  readonly: false,
  required: false,
  clearable: false,
  showCount: false,
  size: 'md',
  status: 'default'
})

const emit = defineEmits<Emits>()

const inputRef = ref<HTMLInputElement>()
const inputId = ref(`input-${Math.random().toString(36).substr(2, 9)}`)
const isFocused = ref(false)

const wrapperClasses = computed(() => {
  const classes = ['input-wrapper', `input-${props.size}`]
  if (props.disabled) classes.push('input-wrapper-disabled')
  return classes
})

const inputClasses = computed(() => {
  const classes = ['input-field']
  
  if (props.prefixIcon) classes.push('input-with-prefix')
  if (props.suffixIcon || props.clearable) classes.push('input-with-suffix')
  if (props.status !== 'default') classes.push(`input-${props.status}`)
  if (isFocused.value) classes.push('input-focused')
  
  return classes
})

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  let value: string | number = target.value
  
  if (props.type === 'number') {
    value = target.valueAsNumber || 0
  }
  
  emit('update:modelValue', value)
}

const handleChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  let value: string | number = target.value
  
  if (props.type === 'number') {
    value = target.valueAsNumber || 0
  }
  
  emit('change', value)
}

const handleFocus = (event: FocusEvent) => {
  isFocused.value = true
  emit('focus', event)
}

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false
  emit('blur', event)
}

const handleClear = () => {
  emit('update:modelValue', '')
  emit('clear')
  nextTick(() => {
    inputRef.value?.focus()
  })
}

const handleKeydown = (event: KeyboardEvent) => {
  emit('keydown', event)
}

// 暴露方法
defineExpose({
  focus: () => inputRef.value?.focus(),
  blur: () => inputRef.value?.blur(),
  select: () => inputRef.value?.select()
})
</script>

<style scoped>
.input-wrapper {
  @apply w-full;
}

/* 标签样式 */
.input-label {
  @apply block text-sm font-medium text-gray-700 mb-1;
}

.input-required {
  @apply text-red-500 ml-1;
}

/* 输入框容器 */
.input-container {
  @apply relative flex items-center;
}

/* 输入框基础样式 */
.input-field {
  @apply w-full border border-gray-300 rounded-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500;
  background-color: white;
}

/* 尺寸变体 */
.input-sm .input-field {
  @apply px-3 py-1.5 text-sm;
  min-height: 32px;
}

.input-md .input-field {
  @apply px-3 py-2 text-sm;
  min-height: 36px;
}

.input-lg .input-field {
  @apply px-4 py-3 text-base;
  min-height: 44px;
}

/* 状态变体 */
.input-error {
  @apply border-red-300 focus:ring-red-500 focus:border-red-500;
}

.input-warning {
  @apply border-yellow-300 focus:ring-yellow-500 focus:border-yellow-500;
}

.input-success {
  @apply border-green-300 focus:ring-green-500 focus:border-green-500;
}

/* 禁用状态 */
.input-wrapper-disabled .input-field {
  @apply bg-gray-100 text-gray-500 cursor-not-allowed;
}

/* 前缀和后缀图标 */
.input-prefix,
.input-suffix {
  @apply absolute flex items-center text-gray-400 pointer-events-none;
  z-index: 1;
}

.input-prefix {
  @apply left-3;
}

.input-suffix {
  @apply right-3;
}

.input-with-prefix {
  @apply pl-10;
}

.input-with-suffix {
  @apply pr-10;
}

/* 清除按钮 */
.input-clear {
  @apply text-gray-400 hover:text-gray-600 transition-colors duration-200 pointer-events-auto;
}

.input-clear:hover {
  @apply bg-gray-100 rounded;
}

/* 帮助文本 */
.input-help {
  @apply mt-1 text-sm;
}

.input-error {
  @apply text-red-600;
}

.input-help-text {
  @apply text-gray-500;
}

/* 字符计数 */
.input-count {
  @apply mt-1 text-xs text-gray-400 text-right;
}

/* 聚焦状态 */
.input-focused {
  @apply ring-2 ring-blue-500 border-blue-500;
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .input-label {
    @apply text-gray-300;
  }
  
  .input-field {
    @apply bg-gray-800 border-gray-600 text-gray-100;
  }
  
  .input-field:focus {
    @apply border-blue-400 ring-blue-400;
  }
  
  .input-wrapper-disabled .input-field {
    @apply bg-gray-700 text-gray-400;
  }
  
  .input-prefix,
  .input-suffix {
    @apply text-gray-500;
  }
  
  .input-help-text {
    @apply text-gray-400;
  }
  
  .input-count {
    @apply text-gray-500;
  }
}

/* 响应式设计 */
@media (max-width: 640px) {
  .input-sm .input-field {
    @apply px-2 py-1 text-xs;
    min-height: 28px;
  }
  
  .input-md .input-field {
    @apply px-3 py-1.5 text-sm;
    min-height: 32px;
  }
  
  .input-lg .input-field {
    @apply px-3 py-2 text-sm;
    min-height: 36px;
  }
}
</style>