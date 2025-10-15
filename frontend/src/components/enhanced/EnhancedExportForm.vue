<template>
  <div class="enhanced-export-form">
    <!-- 步骤指示器 -->
    <div class="steps-indicator">
      <div
        v-for="(step, index) in steps"
        :key="step.key"
        :class="[
          'step-item',
          {
            active: currentStep === index,
            completed: currentStep > index,
            disabled: currentStep < index && !canProceedToStep(index)
          }
        ]"
        @click="goToStep(index)"
      >
        <div class="step-number">
          <i v-if="currentStep > index" class="icon-check"></i>
          <span v-else>{{ index + 1 }}</span>
        </div>
        <div class="step-content">
          <div class="step-title">{{ step.title }}</div>
          <div class="step-description">{{ step.description }}</div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="form-content">
      <!-- 步骤1: 数据类型选择 -->
      <div v-show="currentStep === 0" class="step-content-1">
        <div class="step-header">
          <h3>选择数据类型</h3>
          <p>请选择您要导出的数据类型</p>
        </div>

        <div class="data-type-cards">
          <div
            v-for="type in dataTypes"
            :key="type.key"
            :class="[
              'data-type-card',
              { selected: formData.dataType === type.key }
            ]"
            @click="selectDataType(type.key)"
          >
            <div class="card-icon">
              <i :class="type.icon"></i>
            </div>
            <div class="card-content">
              <h4>{{ type.title }}</h4>
              <p>{{ type.description }}</p>
              <div class="card-features">
                <span v-for="feature in type.features" :key="feature" class="feature-tag">
                  {{ feature }}
                </span>
              </div>
            </div>
            <div class="card-selected">
              <i class="icon-check-circle"></i>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤2: 筛选条件配置 -->
      <div v-show="currentStep === 1" class="step-content-2">
        <div class="step-header">
          <h3>配置筛选条件</h3>
          <p>设置数据筛选条件，选择您需要的数据范围</p>
        </div>

        <div class="filter-sections">
          <!-- 线路选择 -->
          <div class="filter-section">
            <div class="section-header">
              <i class="icon-map-pin"></i>
              <h4>选择线路</h4>
            </div>
            <div class="section-content">
              <div class="line-selector">
                <el-select
                  v-model="formData.line"
                  placeholder="请选择线路"
                  filterable
                  size="large"
                  class="line-select"
                >
                  <el-option
                    v-for="line in availableLines"
                    :key="line"
                    :label="line"
                    :value="line"
                  >
                    <div class="line-option">
                      <span class="line-name">{{ line }}</span>
                      <span class="line-status online">在线</span>
                    </div>
                  </el-option>
                </el-select>
              </div>

              <!-- 快速选择 -->
              <div class="quick-select">
                <span class="quick-label">快速选择:</span>
                <div class="quick-buttons">
                  <el-button
                    v-for="preset in linePresets"
                    :key="preset.key"
                    size="small"
                    @click="selectLines(preset.lines)"
                  >
                    {{ preset.label }}
                  </el-button>
                </div>
              </div>
            </div>
          </div>

          <!-- 时间范围选择 -->
          <div class="filter-section">
            <div class="section-header">
              <i class="icon-clock"></i>
              <h4>时间范围</h4>
            </div>
            <div class="section-content">
              <!-- 快捷时间选择 -->
              <div class="time-presets">
                <div class="preset-buttons">
                  <el-button
                    v-for="preset in timePresets"
                    :key="preset.key"
                    :type="selectedTimePreset === preset.key ? 'primary' : 'default'"
                    size="small"
                    @click="setTimePreset(preset)"
                  >
                    {{ preset.label }}
                  </el-button>
                </div>
              </div>

              <!-- 自定义时间选择 -->
              <div class="custom-time-range">
                <div class="time-range-group">
                  <label>开始时间</label>
                  <el-date-picker
                    v-model="formData.startTime"
                    type="datetime"
                    placeholder="选择开始时间"
                    format="YYYY-MM-DD HH:mm:ss"
                    value-format="YYYY-MM-DD HH:mm:ss"
                    size="large"
                  />
                </div>
                <div class="time-separator">至</div>
                <div class="time-range-group">
                  <label>结束时间</label>
                  <el-date-picker
                    v-model="formData.endTime"
                    type="datetime"
                    placeholder="选择结束时间"
                    format="YYYY-MM-DD HH:mm:ss"
                    value-format="YYYY-MM-DD HH:mm:ss"
                    size="large"
                  />
                </div>
              </div>

              <!-- 时间验证提示 -->
              <div v-if="timeValidationError" class="validation-error">
                <i class="icon-alert-triangle"></i>
                {{ timeValidationError }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤3: 导出选项设置 -->
      <div v-show="currentStep === 2" class="step-content-3">
        <div class="step-header">
          <h3>导出选项设置</h3>
          <p>自定义导出格式和附加选项</p>
        </div>

        <div class="export-options">
          <!-- 基本选项 -->
          <div class="option-group">
            <h4>基本选项</h4>
            <div class="option-items">
              <div class="option-item">
                <label>导出格式</label>
                <el-select v-model="formData.format" size="large">
                  <el-option
                    v-for="format in exportFormats"
                    :key="format.value"
                    :label="format.label"
                    :value="format.value"
                  >
                    <div class="format-option">
                      <i :class="format.icon"></i>
                      <span>{{ format.label }}</span>
                      <span class="format-desc">{{ format.description }}</span>
                    </div>
                  </el-option>
                </el-select>
              </div>

              <div class="option-item">
                <label>文件名前缀</label>
                <el-input
                  v-model="formData.filePrefix"
                  placeholder="可选，默认使用时间戳"
                  size="large"
                />
              </div>
            </div>
          </div>

          <!-- 高级选项 -->
          <div class="option-group">
            <h4>高级选项</h4>
            <div class="option-items">
              <div class="option-item checkbox-item">
                <el-checkbox v-model="formData.compress">
                  <div class="checkbox-content">
                    <div class="checkbox-title">压缩文件</div>
                    <div class="checkbox-desc">推荐大文件使用，可减少下载时间</div>
                  </div>
                </el-checkbox>
              </div>

              <div class="option-item checkbox-item">
                <el-checkbox v-model="formData.includeMetadata">
                  <div class="checkbox-content">
                    <div class="checkbox-title">包含元数据</div>
                    <div class="checkbox-desc">添加数据采集时间、来源等信息</div>
                  </div>
                </el-checkbox>
              </div>

              <div class="option-item checkbox-item">
                <el-checkbox v-model="formData.splitByStation">
                  <div class="checkbox-content">
                    <div class="checkbox-title">按车站分文件</div>
                    <div class="checkbox-desc">每个车站生成独立文件</div>
                  </div>
                </el-checkbox>
              </div>
            </div>
          </div>

          <!-- 数据筛选 -->
          <div class="option-group">
            <h4>数据筛选</h4>
            <div class="option-items">
              <div class="option-item">
                <label>数据采样</label>
                <el-select v-model="formData.sampling" size="large">
                  <el-option label="原始数据" value="original" />
                  <el-option label="5分钟采样" value="5min" />
                  <el-option label="15分钟采样" value="15min" />
                  <el-option label="1小时采样" value="1hour" />
                </el-select>
              </div>

              <div class="option-item">
                <label>异常数据处理</label>
                <el-select v-model="formData.anomalyHandling" size="large">
                  <el-option label="保留所有数据" value="keep" />
                  <el-option label="标记异常值" value="mark" />
                  <el-option label="过滤异常值" value="filter" />
                </el-select>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤4: 确认并导出 -->
      <div v-show="currentStep === 3" class="step-content-4">
        <div class="step-header">
          <h3>确认导出配置</h3>
          <p>请确认您的导出配置，然后开始导出</p>
        </div>

        <!-- 配置摘要 -->
        <div class="config-summary">
          <div class="summary-section">
            <h4>数据类型</h4>
            <div class="summary-item">
              <span class="label">类型:</span>
              <span class="value">{{ getDataTypeLabel(formData.dataType) }}</span>
            </div>
          </div>

          <div class="summary-section">
            <h4>筛选条件</h4>
            <div class="summary-item">
              <span class="label">线路:</span>
              <span class="value">{{ formData.line || '全部' }}</span>
            </div>
            <div class="summary-item">
              <span class="label">时间范围:</span>
              <span class="value">{{ formData.startTime }} 至 {{ formData.endTime }}</span>
            </div>
          </div>

          <div class="summary-section">
            <h4>导出选项</h4>
            <div class="summary-item">
              <span class="label">格式:</span>
              <span class="value">{{ getFormatLabel(formData.format) }}</span>
            </div>
            <div class="summary-item">
              <span class="label">文件名:</span>
              <span class="value">{{ formData.filePrefix || '自动生成' }}</span>
            </div>
            <div class="summary-options">
              <el-tag v-if="formData.compress" size="small">压缩文件</el-tag>
              <el-tag v-if="formData.includeMetadata" size="small">包含元数据</el-tag>
              <el-tag v-if="formData.splitByStation" size="small">按车站分文件</el-tag>
            </div>
          </div>
        </div>

        <!-- 预计信息 -->
        <div class="estimated-info">
          <div class="info-item">
            <i class="icon-database"></i>
            <div class="info-content">
              <span class="info-label">预计数据量</span>
              <span class="info-value">~{{ estimatedDataSize }} MB</span>
            </div>
          </div>
          <div class="info-item">
            <i class="icon-clock"></i>
            <div class="info-content">
              <span class="info-label">预计耗时</span>
              <span class="info-value">{{ estimatedTime }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="form-actions">
      <div class="action-buttons">
        <el-button
          v-if="currentStep > 0"
          @click="previousStep"
          size="large"
        >
          <i class="icon-chevron-left"></i>
          上一步
        </el-button>

        <el-button
          v-if="currentStep < steps.length - 1"
          type="primary"
          @click="nextStep"
          size="large"
          :disabled="!isCurrentStepValid"
        >
          下一步
          <i class="icon-chevron-right"></i>
        </el-button>

        <el-button
          v-if="currentStep === steps.length - 1"
          type="primary"
          @click="startExport"
          size="large"
          :loading="loading"
          :disabled="!isFormValid"
        >
          <i class="icon-download"></i>
          开始导出
        </el-button>
      </div>

      <!-- 保存模板 -->
      <div class="template-actions">
        <el-button
          v-if="isFormValid && currentStep === steps.length - 1"
          @click="saveTemplate"
          size="default"
          plain
        >
          <i class="icon-save"></i>
          保存为模板
        </el-button>

        <el-button
          @click="resetForm"
          size="default"
          plain
        >
          <i class="icon-refresh-cw"></i>
          重置
        </el-button>
      </div>
    </div>

    <!-- 进度显示 -->
    <div v-if="showProgress" class="progress-overlay">
      <div class="progress-modal">
        <div class="progress-header">
          <h3>正在导出数据</h3>
          <el-button @click="cancelExport" type="text" size="small">
            取消
          </el-button>
        </div>

        <div class="progress-content">
          <div class="progress-info">
            <div class="progress-text">{{ progressText }}</div>
            <div class="progress-details">
              <span>{{ progress.current }} / {{ progress.total }}</span>
              <span>{{ progress.percent }}%</span>
            </div>
          </div>

          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: `${progress.percent}%` }"
            ></div>
          </div>

          <div v-if="progressDetails" class="progress-details-list">
            <div
              v-for="detail in progressDetails"
              :key="detail.id"
              class="detail-item"
              :class="detail.status"
            >
              <i :class="getStatusIcon(detail.status)"></i>
              <span>{{ detail.message }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 接口定义
interface FormData {
  dataType: string
  line: string
  startTime: string
  endTime: string
  format: string
  filePrefix: string
  compress: boolean
  includeMetadata: boolean
  splitByStation: boolean
  sampling: string
  anomalyHandling: string
}

interface Progress {
  show: boolean
  percent: number
  current: number
  total: number
  text: string
}

interface ProgressDetail {
  id: string
  message: string
  status: 'pending' | 'processing' | 'success' | 'error'
}

// Props
interface Props {
  availableLines: string[]
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

// Emits
interface Emits {
  (e: 'export', data: FormData): void
  (e: 'preview', data: FormData): void
  (e: 'save-template', data: FormData): void
}

const emit = defineEmits<Emits>()

// 响应式数据
const currentStep = ref(0)
const selectedTimePreset = ref('')

// 表单数据
const formData = ref<FormData>({
  dataType: '',
  line: '',
  startTime: '',
  endTime: '',
  format: 'xlsx',
  filePrefix: '',
  compress: false,
  includeMetadata: true,
  splitByStation: false,
  sampling: 'original',
  anomalyHandling: 'keep'
})

// 进度相关
const showProgress = ref(false)
const progress = ref<Progress>({
  show: false,
  percent: 0,
  current: 0,
  total: 0,
  text: ''
})
const progressDetails = ref<ProgressDetail[]>([])
const progressText = ref('')

// 步骤配置
const steps = [
  {
    key: 'dataType',
    title: '选择数据类型',
    description: '选择要导出的数据类型'
  },
  {
    key: 'filters',
    title: '配置筛选条件',
    description: '设置数据筛选条件'
  },
  {
    key: 'options',
    title: '导出选项',
    description: '自定义导出格式和选项'
  },
  {
    key: 'confirm',
    title: '确认导出',
    description: '确认配置并开始导出'
  }
]

// 数据类型配置
const dataTypes = [
  {
    key: 'electricity',
    title: '电耗数据',
    description: '包含功率、电量、电压、电流等电能耗用信息',
    icon: 'icon-zap',
    features: ['实时数据', '历史趋势', '统计分析']
  },
  {
    key: 'sensor',
    title: '传感器数据',
    description: '包含温度、湿度、压力等环境传感器数据',
    icon: 'icon-thermometer',
    features: ['多类型传感器', '环境监测', '状态监控']
  }
]

// 导出格式配置
const exportFormats = [
  {
    value: 'xlsx',
    label: 'Excel (.xlsx)',
    icon: 'icon-file-text',
    description: '适合数据分析和报表制作'
  },
  {
    value: 'csv',
    label: 'CSV (.csv)',
    icon: 'icon-file',
    description: '适合程序处理和数据分析'
  },
  {
    value: 'json',
    label: 'JSON (.json)',
    icon: 'icon-code',
    description: '适合API集成和程序开发'
  }
]

// 时间预设
const timePresets = [
  { key: 'last1h', label: '最近1小时', hours: 1 },
  { key: 'last6h', label: '最近6小时', hours: 6 },
  { key: 'last24h', label: '最近24小时', hours: 24 },
  { key: 'last7d', label: '最近7天', hours: 24 * 7 },
  { key: 'last30d', label: '最近30天', hours: 24 * 30 }
]

// 线路预设
const linePresets = [
  { key: 'all', label: '全部线路', lines: props.availableLines },
  { key: 'main', label: '主要线路', lines: props.availableLines.filter(line =>
    /M[1-5]/.test(line)
  ) }
]

// 计算属性
const isCurrentStepValid = computed(() => {
  switch (currentStep.value) {
    case 0:
      return !!formData.value.dataType
    case 1:
      return !!formData.value.line &&
             !!formData.value.startTime &&
             !!formData.value.endTime &&
             !timeValidationError.value
    case 2:
      return true // 导出选项都有默认值
    case 3:
      return isFormValid.value
    default:
      return false
  }
})

const isFormValid = computed(() => {
  return !!formData.value.dataType &&
         !!formData.value.line &&
         !!formData.value.startTime &&
         !!formData.value.endTime &&
         new Date(formData.value.endTime) > new Date(formData.value.startTime)
})

const timeValidationError = computed(() => {
  if (!formData.value.startTime || !formData.value.endTime) return ''

  const start = new Date(formData.value.startTime)
  const end = new Date(formData.value.endTime)
  const now = new Date()

  if (start >= end) return '结束时间必须晚于开始时间'
  if (end > now) return '结束时间不能晚于当前时间'

  const dayDiff = (end - start) / (1000 * 60 * 60 * 24)
  if (dayDiff > 90) return '时间范围不能超过90天'

  return ''
})

const estimatedDataSize = computed(() => {
  // 简单估算逻辑
  const baseSize = formData.value.dataType === 'electricity' ? 2 : 1.5
  const timeRange = new Date(formData.value.endTime).getTime() -
                   new Date(formData.value.startTime).getTime()
  const days = timeRange / (1000 * 60 * 60 * 24)

  return Math.round(baseSize * days * (formData.value.sampling === 'original' ? 24 : 1))
})

const estimatedTime = computed(() => {
  const size = estimatedDataSize.value
  if (size < 10) return '1-2分钟'
  if (size < 50) return '2-5分钟'
  if (size < 100) return '5-10分钟'
  return '10-20分钟'
})

// 方法
const goToStep = (step: number) => {
  if (canProceedToStep(step)) {
    currentStep.value = step
  }
}

const canProceedToStep = (step: number) => {
  // 只能前进到已验证的步骤
  for (let i = 0; i < step; i++) {
    if (!isStepValid(i)) return false
  }
  return true
}

const isStepValid = (step: number) => {
  const originalStep = currentStep.value
  currentStep.value = step
  const valid = isCurrentStepValid.value
  currentStep.value = originalStep
  return valid
}

const nextStep = () => {
  if (isCurrentStepValid.value && currentStep.value < steps.length - 1) {
    currentStep.value++
  }
}

const previousStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const selectDataType = (type: string) => {
  formData.value.dataType = type
}

const setTimePreset = (preset: any) => {
  selectedTimePreset.value = preset.key
  // 使用北京时区(Asia/Shanghai)计算并格式化时间
  const formatShanghai = (d: Date) => {
    const parts = new Intl.DateTimeFormat('zh-CN', {
      timeZone: 'Asia/Shanghai',
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit',
      hour12: false
    }).formatToParts(d)
    const get = (type: string) => parts.find(p => p.type === type)?.value || ''
    const Y = get('year')
    const M = get('month')
    const D = get('day')
    const h = get('hour')
    const m = get('minute')
    const s = get('second')
    // 统一为 YYYY-MM-DD HH:mm:ss 格式
    return `${Y}-${M}-${D} ${h}:${m}:${s}`
  }

  const nowUTC = Date.now()
  const startUTC = nowUTC - preset.hours * 60 * 60 * 1000
  formData.value.endTime = formatShanghai(new Date(nowUTC))
  formData.value.startTime = formatShanghai(new Date(startUTC))
}

const selectLines = (lines: string[]) => {
  formData.value.line = lines.join(',')
}

const startExport = async () => {
  try {
    await ElMessageBox.confirm(
      '确认开始导出数据？',
      '确认导出',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    showProgress.value = true
    progress.value = {
      show: true,
      percent: 0,
      current: 0,
      total: 100,
      text: '准备导出...'
    }

    emit('export', { ...formData.value })
  } catch {
    // 用户取消
  }
}

const cancelExport = () => {
  showProgress.value = false
  ElMessage.info('导出已取消')
}

const saveTemplate = () => {
  emit('save-template', { ...formData.value })
  ElMessage.success('模板保存成功')
}

const resetForm = () => {
  currentStep.value = 0
  selectedTimePreset.value = ''
  formData.value = {
    dataType: '',
    line: '',
    startTime: '',
    endTime: '',
    format: 'xlsx',
    filePrefix: '',
    compress: false,
    includeMetadata: true,
    splitByStation: false,
    sampling: 'original',
    anomalyHandling: 'keep'
  }
}

// 工具方法
const getDataTypeLabel = (type: string) => {
  const dataType = dataTypes.find(t => t.key === type)
  return dataType?.title || type
}

const getFormatLabel = (format: string) => {
  const formatObj = exportFormats.find(f => f.value === format)
  return formatObj?.label || format
}

const getStatusIcon = (status: string) => {
  const icons = {
    pending: 'icon-clock',
    processing: 'icon-loader',
    success: 'icon-check-circle',
    error: 'icon-x-circle'
  }
  return icons[status] || 'icon-clock'
}

// 监听时间变化，清除预设
watch([() => formData.value.startTime, () => formData.value.endTime], () => {
  selectedTimePreset.value = ''
})

// 暴露方法
defineExpose({
  resetForm,
  startExport,
  saveTemplate
})
</script>

<style scoped>
.enhanced-export-form {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* 步骤指示器 */
.steps-indicator {
  display: flex;
  padding: 32px 24px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.step-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  opacity: 0.6;
  transition: all 0.3s ease;
  position: relative;
}

.step-item.active {
  opacity: 1;
}

.step-item.completed {
  opacity: 0.8;
}

.step-item.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.step-item:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 24px;
  right: -16px;
  width: 32px;
  height: 2px;
  background: rgba(255, 255, 255, 0.3);
  z-index: 1;
}

.step-item.completed:not(:last-child)::after {
  background: rgba(255, 255, 255, 0.8);
}

.step-number {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  z-index: 2;
}

.step-item.active .step-number {
  background: white;
  color: #667eea;
  border-color: white;
  transform: scale(1.1);
}

.step-item.completed .step-number {
  background: rgba(255, 255, 255, 0.9);
  color: #67c23a;
  border-color: white;
}

.step-content {
  flex: 1;
}

.step-title {
  font-weight: 600;
  font-size: 16px;
  margin-bottom: 4px;
}

.step-description {
  font-size: 14px;
  opacity: 0.8;
}

/* 主要内容区域 */
.form-content {
  padding: 32px;
  min-height: 500px;
}

.step-header {
  text-align: center;
  margin-bottom: 32px;
}

.step-header h3 {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.step-header p {
  color: #606266;
  font-size: 16px;
}

/* 数据类型卡片 */
.data-type-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.data-type-card {
  display: flex;
  gap: 20px;
  padding: 24px;
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.data-type-card:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
}

.data-type-card.selected {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
}

.card-icon {
  font-size: 48px;
  color: #667eea;
}

.card-content {
  flex: 1;
}

.card-content h4 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.card-content p {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 16px;
}

.card-features {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.feature-tag {
  padding: 4px 8px;
  background: #f0f2f5;
  color: #667eea;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.card-selected {
  position: absolute;
  top: 16px;
  right: 16px;
  color: #67c23a;
  font-size: 24px;
}

/* 筛选条件配置 */
.filter-sections {
  max-width: 800px;
  margin: 0 auto;
}

.filter-section {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.section-header i {
  font-size: 20px;
  color: #667eea;
}

.section-header h4 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.line-selector {
  margin-bottom: 16px;
}

.line-select {
  width: 100%;
}

.line-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.line-status.online {
  color: #67c23a;
  font-size: 12px;
}

.quick-select {
  display: flex;
  align-items: center;
  gap: 12px;
}

.quick-label {
  font-weight: 500;
  color: #606266;
}

.quick-buttons {
  display: flex;
  gap: 8px;
}

/* 时间范围选择 */
.time-presets {
  margin-bottom: 20px;
}

.preset-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.custom-time-range {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 16px;
  align-items: end;
}

.time-range-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.time-range-group label {
  font-weight: 500;
  color: #303133;
}

.time-separator {
  padding-bottom: 8px;
  color: #606266;
  font-weight: 500;
}

.validation-error {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 8px 12px;
  background: #fef0f0;
  color: #f56c6c;
  border-radius: 4px;
  font-size: 14px;
}

/* 导出选项 */
.export-options {
  max-width: 800px;
  margin: 0 auto;
}

.option-group {
  margin-bottom: 32px;
}

.option-group h4 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.option-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.option-item label {
  min-width: 120px;
  font-weight: 500;
  color: #303133;
}

.option-item .el-select,
.option-item .el-input {
  flex: 1;
}

.checkbox-item {
  align-items: flex-start;
}

.checkbox-content {
  flex: 1;
}

.checkbox-title {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.checkbox-desc {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.format-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.format-desc {
  font-size: 12px;
  color: #909399;
  margin-left: auto;
}

/* 配置摘要 */
.config-summary {
  max-width: 600px;
  margin: 0 auto 32px;
}

.summary-section {
  margin-bottom: 24px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.summary-section h4 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.summary-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.summary-item .label {
  min-width: 80px;
  color: #606266;
  font-weight: 500;
}

.summary-item .value {
  color: #303133;
}

.summary-options {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;
}

/* 预计信息 */
.estimated-info {
  max-width: 400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
}

.info-item i {
  font-size: 24px;
}

.info-content {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-size: 12px;
  opacity: 0.8;
}

.info-value {
  font-size: 16px;
  font-weight: 600;
}

/* 操作按钮 */
.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  background: #f8f9fa;
  border-top: 1px solid #e4e7ed;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.template-actions {
  display: flex;
  gap: 12px;
}

/* 进度覆盖层 */
.progress-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.progress-modal {
  background: white;
  border-radius: 12px;
  padding: 32px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.progress-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.progress-info {
  margin-bottom: 16px;
}

.progress-text {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.progress-details {
  display: flex;
  justify-content: space-between;
  color: #606266;
  font-size: 14px;
}

.progress-bar {
  height: 8px;
  background: #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 16px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-details-list {
  margin-top: 16px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  font-size: 14px;
}

.detail-item.success {
  color: #67c23a;
}

.detail-item.error {
  color: #f56c6c;
}

.detail-item.processing {
  color: #409eff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .steps-indicator {
    flex-direction: column;
    gap: 16px;
    padding: 24px 16px;
  }

  .step-item {
    flex-direction: column;
    text-align: center;
  }

  .step-item:not(:last-child)::after {
    display: none;
  }

  .form-content {
    padding: 20px 16px;
  }

  .data-type-cards {
    grid-template-columns: 1fr;
  }

  .custom-time-range {
    grid-template-columns: 1fr;
  }

  .time-separator {
    text-align: center;
  }

  .estimated-info {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .action-buttons,
  .template-actions {
    justify-content: center;
  }
}

/* 动画效果 */
.step-item {
  transition: all 0.3s ease;
}

.data-type-card {
  transition: all 0.3s ease;
}

.progress-modal {
  animation: modalSlideIn 0.3s ease;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>