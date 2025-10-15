<template>
  <BaseCard :title="title" shadow="md" :hover="true">
    <template #header>
      <div class="export-form-header">
        <div class="header-title">
          <i :class="icon" class="header-icon"></i>
          <span>{{ title }}</span>
        </div>
      </div>
    </template>

    <BaseForm
      ref="formRef"
      :fields="formFields"
      :initial-values="form"
      :loading="loading"
      layout="vertical"
      size="default"
      :show-submit="false"
      :show-reset="false"
      @change="onFieldChange"
    />

    <!-- 表单验证状态提示 -->
    <div v-if="!isFormValid" class="validation-hint">
      <el-alert
        title="请完善表单信息"
        type="warning"
        :closable="false"
        show-icon
      >
        <template #default>
          <ul class="validation-list">
            <li v-if="!form.line">请选择线路</li>
            <li v-if="!form.start_time">请选择开始时间</li>
            <li v-if="!form.end_time">请选择结束时间</li>
            <li v-if="!form.format">请选择导出格式</li>
            <li v-if="form.start_time && form.end_time && new Date(form.start_time) >= new Date(form.end_time)">
              结束时间必须晚于开始时间
            </li>
          </ul>
        </template>
      </el-alert>
    </div>

    <!-- 成功状态提示 -->
    <div v-if="isFormValid" class="success-hint">
      <el-alert
        title="表单信息完整，可以开始操作"
        type="success"
        :closable="false"
        show-icon
      />
    </div>

    <!-- 操作按钮区域 - 优化布局 -->
    <div class="form-actions">
      <!-- 主要操作按钮组 -->
      <div class="primary-actions">
        <el-button 
          type="primary" 
          size="large"
          :disabled="!isFormValid"
          @click="handleExport"
          :loading="loading"
          class="export-btn"
        >
          <el-icon><Download /></el-icon>
          开始导出
        </el-button>
        
        <el-button 
          type="info" 
          size="large"
          :disabled="!isFormValid"
          @click="handlePreviewData"
          :loading="previewLoading"
          class="preview-btn"
        >
          <el-icon><View /></el-icon>
          预览数据
        </el-button>
      </div>
      
      <!-- 辅助操作按钮组 -->
      <div class="secondary-actions">
        <el-button 
          size="default"
          @click="resetForm"
          class="reset-btn"
        >
          <el-icon><RefreshLeft /></el-icon>
          重置表单
        </el-button>
      </div>
    </div>

    <!-- 导出进度 -->
    <div v-if="progress.show" class="export-progress">
      <div class="progress-header">
        <span class="progress-title">导出进度</span>
        <span class="progress-text">{{ progress.text }}</span>
      </div>
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: `${progress.percent}%` }"
        ></div>
      </div>
      <div class="progress-details">
        <span>{{ progress.current }} / {{ progress.total }}</span>
        <span>{{ progress.percent }}%</span>
      </div>
    </div>

    <!-- 预览模态框 -->
    <BaseModal
      :visible="previewVisible"
      @update:visible="previewVisible = $event"
      title="数据预览"
      width="800px"
      :destroy-on-close="true"
    >
      <div class="preview-content">
        <div v-if="previewLoading" class="preview-loading">
          <i class="icon-loader animate-spin"></i>
          <span>正在加载预览数据...</span>
        </div>
        
        <div v-else-if="previewData.length > 0" class="preview-data">
          <div class="preview-summary">
            <span>预览数据：共 {{ previewData.length }} 条记录</span>
            <span>时间范围：{{ form.start_time }} 至 {{ form.end_time }}</span>
          </div>
          
          <BaseTable
            :data="previewData.slice(0, 100)"
            :columns="previewColumns"
            :pagination="false"
            size="small"
            stripe
            border
          />
          
          <div v-if="previewData.length > 100" class="preview-note">
            <i class="icon-info"></i>
            <span>仅显示前100条记录，完整数据请导出查看</span>
          </div>
        </div>
        
        <div v-else class="preview-empty">
          <i class="icon-inbox"></i>
          <span>该时间范围内暂无数据</span>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="previewVisible = false">
          关闭
        </el-button>
        <el-button 
          @click="handleExportFromPreview" 
          type="primary"
          :disabled="previewData.length === 0"
        >
          确认导出
        </el-button>
      </template>
    </BaseModal>
  </BaseCard>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Download, View, RefreshLeft } from '@element-plus/icons-vue'
import { BaseCard, BaseForm, BaseTable, BaseModal } from '@/components/common'
import type { FormField, TableColumn } from '@/components/common'

interface ExportFormData {
  line: string
  start_time: string
  end_time: string
  format?: string
  compress?: boolean
}

interface ExportProgress {
  show: boolean
  percent: number
  current: number
  total: number
  text: string
}

interface Props {
  title: string
  icon: string
  exportType: 'electricity' | 'sensor'
  availableLines: string[]
  loading?: boolean
  showPreview?: boolean
}

interface Emits {
  (e: 'export', data: ExportFormData): void
  (e: 'cancel'): void
  (e: 'preview', data: ExportFormData): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  showPreview: true
})

const emit = defineEmits<Emits>()

// 表单数据
const form = ref<ExportFormData>({
  line: '',
  start_time: '',
  end_time: '',
  format: 'xlsx',
  compress: false
})

// 表单字段配置
const formFields = computed<FormField[]>(() => [
  {
    key: 'line',
    label: '选择线路',
    type: 'select',
    required: true,
    placeholder: '请选择线路',
    options: props.availableLines.map(line => ({
      label: line,
      value: line
    }))
  },
  {
    key: 'start_time',
    label: '开始时间',
    type: 'datetime',
    required: true,
    placeholder: '选择开始时间'
  },
  {
    key: 'end_time',
    label: '结束时间',
    type: 'datetime',
    required: true,
    placeholder: '选择结束时间',
    validation: [
      {
        validator: (value: string) => {
          if (!value || !form.value.start_time) return true
          return new Date(value) > new Date(form.value.start_time)
        },
        message: '结束时间必须大于开始时间'
      }
    ]
  },
  {
    key: 'format',
    label: '导出格式',
    type: 'select',
    required: true,
    options: [
      { label: 'Excel (.xlsx)', value: 'xlsx' },
      { label: 'CSV (.csv)', value: 'csv' },
      { label: 'JSON (.json)', value: 'json' }
    ]
  },
  {
    key: 'compress',
    label: '压缩文件',
    type: 'switch',
    help: '大文件建议开启压缩以减少下载时间'
  }
])

// 表单验证
const formRef = ref()
const isFormValid = computed(() => {
  const hasLine = !!(form.value.line && form.value.line.trim() !== '')
  const hasStartTime = !!(form.value.start_time && form.value.start_time.trim() !== '')
  const hasEndTime = !!(form.value.end_time && form.value.end_time.trim() !== '')
  
  let timeValid = true
  if (hasStartTime && hasEndTime) {
    try {
      const startDate = new Date(form.value.start_time)
      const endDate = new Date(form.value.end_time)
      timeValid = endDate > startDate
    } catch (e) {
      timeValid = false
    }
  }
  
  const valid = hasLine && hasStartTime && hasEndTime && timeValid
  console.log('isFormValid computed:', {
    hasLine,
    hasStartTime,
    hasEndTime,
    timeValid,
    valid,
    form: form.value
  })
  
  return valid
})

// 导出进度
const progress = ref<ExportProgress>({
  show: false,
  percent: 0,
  current: 0,
  total: 0,
  text: ''
})

// 预览相关
const previewVisible = ref(false)
const previewLoading = ref(false)
const previewData = ref<any[]>([])
const previewColumns = computed<TableColumn[]>(() => {
  if (props.exportType === 'electricity') {
    return [
      { key: 'timestamp', title: '时间', width: 180 },
      { key: 'station_name', title: '车站', width: 120 },
      { key: 'power', title: '功率(kW)', width: 100, align: 'right' },
      { key: 'energy', title: '电量(kWh)', width: 100, align: 'right' },
      { key: 'voltage', title: '电压(V)', width: 100, align: 'right' },
      { key: 'current', title: '电流(A)', width: 100, align: 'right' }
    ]
  } else {
    return [
      { key: 'timestamp', title: '时间', width: 180 },
      { key: 'station_name', title: '车站', width: 120 },
      { key: 'sensor_type', title: '传感器类型', width: 120 },
      { key: 'sensor_value', title: '数值', width: 100, align: 'right' },
      { key: 'unit', title: '单位', width: 80 },
      { key: 'status', title: '状态', width: 80 }
    ]
  }
})

// 方法
const onFieldChange = (key: string, value: any) => {
  console.log('Field changed:', key, value)
  form.value[key as keyof ExportFormData] = value
  console.log('Updated form:', form.value)
  
  // 强制触发响应式更新
  form.value = { ...form.value }
}

const handleExport = async () => {
  console.log('handleExport called, isFormValid:', isFormValid.value, 'form:', form.value)
  
  if (!isFormValid.value) {
    console.log('Form is not valid, cannot export')
    return
  }
  
  const valid = await formRef.value?.validate()
  if (!valid) {
    console.log('Form validation failed')
    return
  }
  
  console.log('Emitting export event with data:', form.value)
  emit('export', { ...form.value })
}

const handleCancel = () => {
  emit('cancel')
}

const resetForm = () => {
  form.value = {
    line: '',
    start_time: '',
    end_time: '',
    format: 'xlsx',
    compress: false
  }
  formRef.value?.resetFields()
}

const handlePreviewData = async () => {
  if (!isFormValid.value) return
  
  previewVisible.value = true
  previewLoading.value = true
  
  try {
    emit('preview', { ...form.value })
    // 这里应该从父组件接收预览数据
  } catch (error) {
    console.error('预览数据失败:', error)
  } finally {
    previewLoading.value = false
  }
}

const handleExportFromPreview = () => {
  previewVisible.value = false
  handleExport()
}

// 更新进度
const updateProgress = (current: number, total: number, text: string) => {
  progress.value = {
    show: true,
    current,
    total,
    percent: Math.round((current / total) * 100),
    text
  }
}

// 隐藏进度
const hideProgress = () => {
  progress.value.show = false
}

// 设置预览数据
const setPreviewData = (data: any[]) => {
  previewData.value = data
  previewLoading.value = false
}

// 监听loading状态
watch(() => props.loading, (loading) => {
  if (!loading) {
    hideProgress()
  }
})

// 监听BaseForm的数据变化
// 注释掉原有的BaseForm数据同步watch
/*
watch(() => formRef.value?.form, (newFormData) => {
  if (newFormData) {
    Object.assign(form.value, newFormData)
    console.log('Form data synced from BaseForm:', form.value)
  }
}, { deep: true })
*/

// 添加新的初始化逻辑，确保BaseForm获得正确的初始值
watch(() => props.availableLines, () => {
  // 当可用线路变化时，重置表单
  if (formRef.value && typeof formRef.value.initializeForm === 'function') {
    formRef.value.initializeForm()
  }
}, { immediate: false })

// 暴露方法给父组件
defineExpose({
  updateProgress,
  hideProgress,
  setPreviewData,
  resetForm
})
</script>

<style scoped>
.export-form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.header-icon {
  font-size: 18px;
  color: var(--el-color-primary);
}

/* 表单验证提示样式 */
.validation-hint {
  margin: 16px 0;
}

.validation-list {
  margin: 0;
  padding-left: 16px;
  list-style-type: disc;
}

.validation-list li {
  margin: 4px 0;
  color: var(--el-color-warning);
}

.success-hint {
  margin: 16px 0;
}

/* 操作按钮区域样式 */
.form-actions {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--el-border-color-light);
}

.primary-actions {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.secondary-actions {
  display: flex;
  gap: 12px;
}

.export-btn {
  min-width: 140px;
  font-weight: 600;
}

.preview-btn {
  min-width: 120px;
}

.reset-btn {
  color: var(--el-color-info);
}

/* 导出进度样式 */
.export-progress {
  margin-top: 20px;
  padding: 16px;
  background: var(--el-bg-color-page);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-light);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-title {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.progress-text {
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.progress-bar {
  height: 8px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--el-color-primary), var(--el-color-primary-light-3));
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-details {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--el-text-color-regular);
}

/* 预览模态框样式 */
.preview-content {
  min-height: 200px;
}

.preview-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px;
  color: var(--el-text-color-regular);
}

.preview-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px;
  background: var(--el-bg-color-page);
  border-radius: 6px;
  font-size: 14px;
}

.preview-note {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 8px 12px;
  background: var(--el-color-warning-light-9);
  color: var(--el-color-warning);
  border-radius: 4px;
  font-size: 12px;
}

.preview-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px;
  color: var(--el-text-color-placeholder);
}

.preview-empty i {
  font-size: 48px;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .primary-actions {
    flex-direction: column;
  }
  
  .export-form-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .progress-header,
  .preview-summary {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
}

/* 按钮悬停效果 */
.export-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.preview-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(144, 147, 153, 0.3);
}

/* 禁用状态样式优化 */
.export-btn:disabled,
.preview-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
</style>