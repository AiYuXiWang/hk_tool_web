<template>
  <form
    :class="formClasses"
    @submit.prevent="handleSubmit"
    @reset="handleReset"
  >
    <!-- 自动渲染字段 -->
    <div v-if="fields.length > 0" class="form-fields">
      <div
        v-for="field in fields"
        :key="field.key"
        class="form-item"
        :class="{ 'has-error': errors[field.key] }"
      >
        <label v-if="field.label" class="form-label" :for="field.key">
          {{ field.label }}
          <span v-if="field.required" class="required-mark">*</span>
        </label>
        
        <div class="form-control">
          <!-- 文本输入框 -->
          <input
            v-if="field.type === 'text' || field.type === 'email' || field.type === 'password' || !field.type"
            :id="field.key"
            :type="field.type || 'text'"
            :value="form[field.key]"
            :placeholder="field.placeholder"
            :disabled="field.disabled || loading"
            class="form-input"
            @input="handleFieldChange(field.key, ($event.target as HTMLInputElement).value)"
            @blur="handleFieldBlur(field.key)"
          />
          
          <!-- 数字输入框 -->
          <input
            v-else-if="field.type === 'number'"
            :id="field.key"
            type="number"
            :value="form[field.key]"
            :placeholder="field.placeholder"
            :disabled="field.disabled || loading"
            :min="field.min"
            :max="field.max"
            :step="field.step"
            class="form-input"
            @input="handleFieldChange(field.key, ($event.target as HTMLInputElement).value)"
            @blur="handleFieldBlur(field.key)"
          />
          
          <!-- 日期时间选择器 -->
          <input
            v-else-if="field.type === 'datetime' || field.type === 'date' || field.type === 'time'"
            :id="field.key"
            :type="field.type === 'datetime' ? 'datetime-local' : field.type"
            :value="form[field.key]"
            :placeholder="field.placeholder"
            :disabled="field.disabled || loading"
            class="form-input"
            @input="handleFieldChange(field.key, ($event.target as HTMLInputElement).value)"
            @blur="handleFieldBlur(field.key)"
          />
          
          <!-- 下拉选择框 -->
          <select
            v-else-if="field.type === 'select'"
            :id="field.key"
            :value="form[field.key]"
            :disabled="field.disabled || loading"
            class="form-select"
            @change="handleFieldChange(field.key, ($event.target as HTMLSelectElement).value)"
            @blur="handleFieldBlur(field.key)"
          >
            <option value="" disabled>{{ field.placeholder || '请选择' }}</option>
            <option
              v-for="option in field.options"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>
          
          <!-- 多行文本框 -->
          <textarea
            v-else-if="field.type === 'textarea'"
            :id="field.key"
            :value="form[field.key]"
            :placeholder="field.placeholder"
            :disabled="field.disabled || loading"
            :rows="field.rows || 3"
            class="form-textarea"
            @input="handleFieldChange(field.key, ($event.target as HTMLTextAreaElement).value)"
            @blur="handleFieldBlur(field.key)"
          ></textarea>
          
          <!-- 开关 -->
          <label
            v-else-if="field.type === 'switch'"
            class="form-switch"
          >
            <input
              :id="field.key"
              type="checkbox"
              :checked="form[field.key]"
              :disabled="field.disabled || loading"
              class="form-switch-input"
              @change="handleFieldChange(field.key, ($event.target as HTMLInputElement).checked)"
            />
            <span class="form-switch-slider"></span>
          </label>
          
          <!-- 复选框 -->
          <label
            v-else-if="field.type === 'checkbox'"
            class="form-checkbox"
          >
            <input
              :id="field.key"
              type="checkbox"
              :checked="form[field.key]"
              :disabled="field.disabled || loading"
              class="form-checkbox-input"
              @change="handleFieldChange(field.key, ($event.target as HTMLInputElement).checked)"
            />
            <span class="form-checkbox-label">{{ field.checkboxLabel || field.label }}</span>
          </label>
          
          <!-- 单选框组 -->
          <div
            v-else-if="field.type === 'radio'"
            class="form-radio-group"
          >
            <label
              v-for="option in field.options"
              :key="option.value"
              class="form-radio"
            >
              <input
                type="radio"
                :name="field.key"
                :value="option.value"
                :checked="form[field.key] === option.value"
                :disabled="field.disabled || loading"
                class="form-radio-input"
                @change="handleFieldChange(field.key, option.value)"
              />
              <span class="form-radio-label">{{ option.label }}</span>
            </label>
          </div>
        </div>
        
        <!-- 字段帮助文本 -->
        <div v-if="field.help" class="form-help">
          {{ field.help }}
        </div>
        
        <!-- 错误信息 -->
        <div v-if="errors[field.key]" class="form-error">
          {{ errors[field.key] }}
        </div>
      </div>
    </div>
    
    <!-- 插槽内容 -->
    <slot
      :form="form"
      :errors="errors"
      :loading="loading"
      :validate="validate"
      :validateField="validateField"
      :resetField="resetField"
      :setFieldValue="setFieldValue"
      :getFieldValue="getFieldValue"
    />
    
    <!-- 表单操作按钮 -->
    <div v-if="showActions" class="form-actions">
      <slot name="actions" :form="form" :errors="errors" :loading="loading">
        <el-button
          v-if="showReset"
          type="default"
          @click="handleReset"
          :disabled="loading"
        >
          重置
        </el-button>
        
        <el-button
          type="primary"
          :loading="loading"
          :disabled="!isValid || loading"
          @click="handleSubmit"
        >
          {{ submitText }}
        </el-button>
      </slot>
    </div>
  </form>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

interface ValidationRule {
  required?: boolean
  min?: number
  max?: number
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  validator?: (value: any) => boolean | string
  message?: string
}

interface FormField {
  key: string
  name?: string
  label?: string
  type?: string
  value?: any
  rules?: ValidationRule[]
  validation?: ValidationRule[]
  placeholder?: string
  disabled?: boolean
  required?: boolean
  options?: { label: string; value: any }[]
  help?: string
  min?: number
  max?: number
  step?: number
  rows?: number
  checkboxLabel?: string
}

interface Props {
  fields?: FormField[]
  initialValues?: Record<string, any>
  layout?: 'horizontal' | 'vertical' | 'inline'
  size?: 'sm' | 'md' | 'lg'
  labelWidth?: string
  showActions?: boolean
  showReset?: boolean
  submitText?: string
  validateOnChange?: boolean
  validateOnBlur?: boolean
  loading?: boolean
}

interface Emits {
  (e: 'submit', values: Record<string, any>): void
  (e: 'reset'): void
  (e: 'change', field: string, value: any): void
  (e: 'validate', field: string, error: string | null): void
}

const props = withDefaults(defineProps<Props>(), {
  fields: () => [],
  initialValues: () => ({}),
  layout: 'vertical',
  size: 'md',
  labelWidth: '120px',
  showActions: true,
  showReset: true,
  submitText: '提交',
  validateOnChange: true,
  validateOnBlur: true,
  loading: false
})

const emit = defineEmits<Emits>()

// 表单数据
const form = reactive<Record<string, any>>({})
const errors = reactive<Record<string, string>>({})
const touched = reactive<Record<string, boolean>>({})

// 初始化表单数据
const initializeForm = () => {
  // 清空现有数据
  Object.keys(form).forEach(key => delete form[key])
  Object.keys(errors).forEach(key => delete errors[key])
  Object.keys(touched).forEach(key => delete touched[key])
  
  // 设置初始值
  props.fields.forEach(field => {
    const fieldKey = field.key || field.name
    if (fieldKey) {
      form[fieldKey] = props.initialValues[fieldKey] ?? field.value ?? (field.type === 'switch' || field.type === 'checkbox' ? false : '')
    }
  })
  
  // 设置额外的初始值
  Object.keys(props.initialValues).forEach(key => {
    if (!(key in form)) {
      form[key] = props.initialValues[key]
    }
  })
}

// 处理字段值变化
const handleFieldChange = (fieldKey: string, value: any) => {
  setFieldValue(fieldKey, value)
}

// 处理字段失焦
const handleFieldBlur = (fieldKey: string) => {
  touched[fieldKey] = true
  if (props.validateOnBlur) {
    validateField(fieldKey)
  }
}

// 计算属性
const formClasses = computed(() => {
  const classes = ['base-form', `form-${props.layout}`, `form-${props.size}`]
  return classes
})

const isValid = computed(() => {
  return Object.keys(errors).length === 0
})

// 验证单个字段
const validateField = (fieldName: string): string | null => {
  const field = props.fields.find(f => (f.key || f.name) === fieldName)
  if (!field) return null
  
  const rules = field.rules || field.validation || []
  if (rules.length === 0 && !field.required) return null
  
  const value = form[fieldName]
  
  // 必填验证
  if (field.required && (!value || (typeof value === 'string' && !value.trim()))) {
    const error = `${field.label || fieldName}是必填项`
    errors[fieldName] = error
    emit('validate', fieldName, error)
    return error
  }
  
  for (const rule of rules) {
    // 必填验证
    if (rule.required && (!value || (typeof value === 'string' && !value.trim()))) {
      const error = rule.message || `${field.label || fieldName}是必填项`
      errors[fieldName] = error
      emit('validate', fieldName, error)
      return error
    }
    
    // 如果值为空且不是必填，跳过其他验证
    if (!value && !rule.required) continue
    
    // 最小值验证
    if (rule.min !== undefined && Number(value) < rule.min) {
      const error = rule.message || `${field.label || fieldName}不能小于${rule.min}`
      errors[fieldName] = error
      emit('validate', fieldName, error)
      return error
    }
    
    // 最大值验证
    if (rule.max !== undefined && Number(value) > rule.max) {
      const error = rule.message || `${field.label || fieldName}不能大于${rule.max}`
      errors[fieldName] = error
      emit('validate', fieldName, error)
      return error
    }
    
    // 最小长度验证
    if (rule.minLength !== undefined && String(value).length < rule.minLength) {
      const error = rule.message || `${field.label || fieldName}长度不能少于${rule.minLength}个字符`
      errors[fieldName] = error
      emit('validate', fieldName, error)
      return error
    }
    
    // 最大长度验证
    if (rule.maxLength !== undefined && String(value).length > rule.maxLength) {
      const error = rule.message || `${field.label || fieldName}长度不能超过${rule.maxLength}个字符`
      errors[fieldName] = error
      emit('validate', fieldName, error)
      return error
    }
    
    // 正则验证
    if (rule.pattern && !rule.pattern.test(String(value))) {
      const error = rule.message || `${field.label || fieldName}格式不正确`
      errors[fieldName] = error
      emit('validate', fieldName, error)
      return error
    }
    
    // 自定义验证器
    if (rule.validator) {
      const result = rule.validator(value)
      if (result !== true) {
        const error = typeof result === 'string' ? result : (rule.message || `${field.label || fieldName}验证失败`)
        errors[fieldName] = error
        emit('validate', fieldName, error)
        return error
      }
    }
  }
  
  // 验证通过，清除错误
  delete errors[fieldName]
  emit('validate', fieldName, null)
  return null
}

// 验证整个表单
const validate = (): boolean => {
  let isFormValid = true
  
  props.fields.forEach(field => {
    const fieldKey = field.key || field.name
    if (fieldKey) {
      const error = validateField(fieldKey)
      if (error) {
        isFormValid = false
      }
    }
  })
  
  return isFormValid
}

// 重置字段
const resetField = (fieldName: string) => {
  const field = props.fields.find(f => (f.key || f.name) === fieldName)
  if (field) {
    form[fieldName] = props.initialValues[fieldName] ?? field.value ?? (field.type === 'switch' || field.type === 'checkbox' ? false : '')
  }
  delete errors[fieldName]
  delete touched[fieldName]
}

// 设置字段值
const setFieldValue = (fieldName: string, value: any) => {
  form[fieldName] = value
  touched[fieldName] = true
  
  if (props.validateOnChange) {
    validateField(fieldName)
  }
  
  emit('change', fieldName, value)
}

// 获取字段值
const getFieldValue = (fieldName: string) => {
  return form[fieldName]
}

// 处理表单提交
const handleSubmit = () => {
  // 标记所有字段为已触摸
  props.fields.forEach(field => {
    const fieldKey = field.key || field.name
    if (fieldKey) {
      touched[fieldKey] = true
    }
  })
  
  if (validate()) {
    emit('submit', { ...form })
  }
}

// 处理表单重置
const handleReset = () => {
  initializeForm()
  emit('reset')
}

// 监听初始值变化
watch(() => props.initialValues, () => {
  initializeForm()
}, { deep: true })

watch(() => props.fields, () => {
  initializeForm()
}, { deep: true })

// 初始化
initializeForm()

// 暴露方法给父组件
defineExpose({
  validate,
  validateField,
  resetField,
  setFieldValue,
  getFieldValue,
  initializeForm,
  form,
  errors,
  isValid
})
</script>

<style scoped>
.base-form {
  width: 100%;
}

/* 布局样式 */
.form-vertical .form-item {
  margin-bottom: 1rem;
}

.form-horizontal .form-item {
  margin-bottom: 1rem;
  display: flex;
  align-items: flex-start;
}

.form-horizontal .form-label {
  flex-shrink: 0;
  text-align: right;
  padding-right: 1rem;
  padding-top: 0.5rem;
  width: v-bind('props.labelWidth');
}

.form-horizontal .form-control {
  flex: 1;
}

.form-inline {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
}

.form-inline .form-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* 尺寸样式 */
.form-sm .form-item {
  margin-bottom: 0.75rem;
}

.form-sm .form-label {
  font-size: 0.875rem;
}

.form-lg .form-item {
  margin-bottom: 1.5rem;
}

.form-lg .form-label {
  font-size: 1.125rem;
}

/* 表单操作 */
.form-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.form-vertical .form-actions {
  margin-top: 1.5rem;
}

.form-horizontal .form-actions {
  margin-top: 1.5rem;
  margin-left: v-bind('props.labelWidth');
}

.form-inline .form-actions {
  margin-top: 0;
  padding-top: 0;
  border-top: none;
}

/* 表单控件样式 */
.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.required-mark {
  color: #ef4444;
  margin-left: 0.25rem;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background-color: #fff;
  color: #1f2937;
  font-size: 0.875rem;
  line-height: 1.25rem;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #60a5fa;
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.2);
}

.form-input:disabled,
.form-select:disabled,
.form-textarea:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
}

.form-textarea {
  min-height: 6rem;
  resize: vertical;
}

.form-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
}

/* 开关样式 */
.form-switch {
  position: relative;
  display: inline-block;
  width: 3rem;
  height: 1.5rem;
}

.form-switch-input {
  opacity: 0;
  width: 0;
  height: 0;
}

.form-switch-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #d1d5db;
  transition: .4s;
  border-radius: 1.5rem;
}

.form-switch-slider:before {
  position: absolute;
  content: "";
  height: 1.25rem;
  width: 1.25rem;
  left: 0.125rem;
  bottom: 0.125rem;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

.form-switch-input:checked + .form-switch-slider {
  background-color: #3b82f6;
}

.form-switch-input:checked + .form-switch-slider:before {
  transform: translateX(1.5rem);
}

.form-switch-input:disabled + .form-switch-slider {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 复选框样式 */
.form-checkbox {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.form-checkbox-input {
  appearance: none;
  width: 1rem;
  height: 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.25rem;
  margin-right: 0.5rem;
  background-color: #fff;
  cursor: pointer;
}

.form-checkbox-input:checked {
  background-color: #3b82f6;
  border-color: #3b82f6;
  background-image: url("data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='M12.207 4.793a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0l-2-2a1 1 0 011.414-1.414L6.5 9.086l4.293-4.293a1 1 0 011.414 0z'/%3e%3c/svg%3e");
}

.form-checkbox-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-checkbox-label {
  font-size: 0.875rem;
  color: #4b5563;
}

/* 单选框样式 */
.form-radio-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-radio {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.form-radio-input {
  appearance: none;
  width: 1rem;
  height: 1rem;
  border: 1px solid #d1d5db;
  border-radius: 50%;
  margin-right: 0.5rem;
  background-color: #fff;
  cursor: pointer;
}

.form-radio-input:checked {
  border-color: #3b82f6;
  border-width: 4px;
  background-color: #fff;
}

.form-radio-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-radio-label {
  font-size: 0.875rem;
  color: #4b5563;
}

/* 帮助文本和错误信息 */
.form-help {
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #6b7280;
}

.form-error {
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #ef4444;
}

.has-error .form-input,
.has-error .form-select,
.has-error .form-textarea {
  border-color: #ef4444;
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .form-actions {
    border-color: #374151;
  }
  
  .form-label {
    color: #e5e7eb;
  }
  
  .form-input,
  .form-select,
  .form-textarea {
    background-color: #1f2937;
    border-color: #4b5563;
    color: #e5e7eb;
  }
  
  .form-input:focus,
  .form-select:focus,
  .form-textarea:focus {
    border-color: #60a5fa;
  }
  
  .form-input:disabled,
  .form-select:disabled,
  .form-textarea:disabled {
    background-color: #374151;
  }
  
  .form-switch-slider {
    background-color: #4b5563;
  }
  
  .form-checkbox-input {
    border-color: #4b5563;
    background-color: #1f2937;
  }
  
  .form-radio-input {
    border-color: #4b5563;
    background-color: #1f2937;
  }
  
  .form-checkbox-label,
  .form-radio-label {
    color: #d1d5db;
  }
  
  .form-help {
    color: #9ca3af;
  }
}

/* 响应式设计 */
@media (max-width: 640px) {
  .form-horizontal {
    display: block;
  }
  
  .form-horizontal .form-item {
    display: block;
  }
  
  .form-horizontal .form-label {
    width: 100%;
    text-align: left;
    padding-right: 0;
    padding-bottom: 0.25rem;
    padding-top: 0;
  }
  
  .form-horizontal .form-actions {
    margin-left: 0;
  }
  
  .form-inline {
    display: block;
  }
  
  .form-inline .form-item {
    display: block;
    margin-bottom: 1rem;
  }
  
  .form-inline .form-actions {
    padding-top: 1.5rem;
    border-top: 1px solid #e5e7eb;
  }
}
</style>