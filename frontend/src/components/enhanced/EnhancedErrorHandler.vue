<template>
  <div class="enhanced-error-handler">
    <!-- 错误边界捕获 -->
    <div v-if="hasError" class="error-boundary">
      <div class="error-container">
        <div class="error-visual">
          <div class="error-icon">
            <i class="icon-x-circle"></i>
          </div>
          <div class="error-waves">
            <div class="wave"></div>
            <div class="wave"></div>
            <div class="wave"></div>
          </div>
        </div>

        <div class="error-content">
          <h2 class="error-title">{{ errorTitle }}</h2>
          <p class="error-description">{{ errorDescription }}</p>

          <!-- 错误分类标签 -->
          <div class="error-tags">
            <el-tag :type="getErrorTagType()" size="small">
              {{ errorCategory }}
            </el-tag>
            <el-tag v-if="errorCode" type="info" size="small">
              错误码: {{ errorCode }}
            </el-tag>
          </div>

          <!-- 错误详情（可展开） -->
          <div class="error-details">
            <el-collapse v-model="activeCollapse">
              <el-collapse-item name="details" title="查看错误详情">
                <div class="detail-content">
                  <div class="detail-section">
                    <h4>错误信息</h4>
                    <div class="error-message">{{ errorMessage }}</div>
                  </div>

                  <div v-if="errorStack" class="detail-section">
                    <h4>调用栈</h4>
                    <div class="error-stack">
                      <pre>{{ errorStack }}</pre>
                  </div>
                  </div>

                  <div v-if="errorContext" class="detail-section">
                    <h4>上下文信息</h4>
                    <div class="error-context">
                      <el-descriptions :column="1" size="small" border>
                        <el-descriptions-item
                          v-for="(value, key) in errorContext"
                          :key="key"
                          :label="key"
                        >
                          {{ value }}
                        </el-descriptions-item>
                      </el-descriptions>
                    </div>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>

          <!-- 操作建议 -->
          <div v-if="suggestions.length > 0" class="error-suggestions">
            <h4>
              <i class="icon-lightbulb"></i>
              解决建议
            </h4>
            <ul class="suggestion-list">
              <li v-for="suggestion in suggestions" :key="suggestion.id">
                <i class="icon-check"></i>
                {{ suggestion.text }}
              </li>
            </ul>
          </div>

          <!-- 操作按钮 -->
          <div class="error-actions">
            <div class="primary-actions">
              <el-button
                v-if="retryable"
                @click="handleRetry"
                type="primary"
                :loading="retrying"
              >
                <i class="icon-refresh-cw"></i>
                {{ retryButtonText }}
              </el-button>
              <el-button @click="handleReload">
                <i class="icon-refresh-ccw"></i>
                刷新页面
              </el-button>
            </div>

            <div class="secondary-actions">
              <el-button @click="toggleReportModal" text>
                <i class="icon-flag"></i>
                报告问题
              </el-button>
              <el-button @click="copyErrorInfo" text>
                <i class="icon-copy"></i>
                复制错误信息
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 正常内容渲染 -->
    <div v-else>
      <slot />
    </div>

    <!-- 全局错误提示 -->
    <div v-if="showToast" class="error-toast" :class="toastType">
      <div class="toast-content">
        <div class="toast-icon">
          <i :class="getToastIcon()"></i>
        </div>
        <div class="toast-message">
          <div class="toast-title">{{ toastTitle }}</div>
          <div class="toast-description">{{ toastDescription }}</div>
        </div>
        <div class="toast-actions">
          <el-button @click="showToast = false" size="small" text>
            <i class="icon-x"></i>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 网络错误重试组件 -->
    <div v-if="networkError" class="network-error-retry">
      <div class="network-error-content">
        <div class="network-error-icon">
          <i class="icon-wifi-off"></i>
        </div>
        <div class="network-error-text">
          <h4>网络连接异常</h4>
          <p>请检查您的网络连接，然后重试</p>
        </div>
        <div class="network-error-actions">
          <el-button @click="retryNetworkRequest" type="primary" :loading="retryingNetwork">
            <i class="icon-refresh-cw"></i>
            重试
          </el-button>
          <el-button @click="networkError = false" text>
            忽略
          </el-button>
        </div>
      </div>
    </div>

    <!-- 问题报告模态框 -->
    <el-dialog
      v-model="reportModalVisible"
      title="报告问题"
      width="600px"
      :destroy-on-close="true"
    >
      <div class="report-form">
        <el-form ref="reportFormRef" :model="reportForm" :rules="reportRules" label-width="80px">
          <el-form-item label="问题类型" prop="type">
            <el-select v-model="reportForm.type" placeholder="请选择问题类型" style="width: 100%">
              <el-option label="功能异常" value="bug" />
              <el-option label="性能问题" value="performance" />
              <el-option label="界面问题" value="ui" />
              <el-option label="其他问题" value="other" />
            </el-select>
          </el-form-item>

          <el-form-item label="问题描述" prop="description">
            <el-input
              v-model="reportForm.description"
              type="textarea"
              :rows="4"
              placeholder="请详细描述您遇到的问题"
            />
          </el-form-item>

          <el-form-item label="联系方式" prop="contact">
            <el-input
              v-model="reportForm.contact"
              placeholder="邮箱或电话（可选）"
            />
          </el-form-item>

          <el-form-item label="附件信息">
            <div class="error-info-summary">
              <el-descriptions :column="1" size="small" border>
                <el-descriptions-item label="错误类型">
                  {{ errorCategory }}
                </el-descriptions-item>
                <el-descriptions-item label="错误时间">
                  {{ formatTime(errorTimestamp) }}
                </el-descriptions-item>
                <el-descriptions-item label="用户代理">
                  {{ userAgent }}
                </el-descriptions-item>
                <el-descriptions-item label="页面地址">
                  {{ currentUrl }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </el-form-item>

          <el-form-item>
            <el-checkbox v-model="reportForm.includeScreenshot">
              包含页面截图（推荐）
            </el-checkbox>
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <div class="report-actions">
          <el-button @click="reportModalVisible = false">取消</el-button>
          <el-button @click="submitReport" type="primary" :loading="submittingReport">
            <i class="icon-send"></i>
            提交报告
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 加载状态指示器 -->
    <div v-if="showLoadingIndicator" class="loading-indicator">
      <div class="loading-backdrop" @click="cancelLoading"></div>
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">{{ loadingText }}</div>
        <div v-if="loadingProgress" class="loading-progress">
          <el-progress :percentage="loadingProgress" :show-text="false" />
          <span>{{ loadingProgress }}%</span>
        </div>
        <el-button v-if="loadingCancellable" @click="cancelLoading" size="small" text>
          取消
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElForm } from 'element-plus'

// 接口定义
interface ErrorInfo {
  title: string
  description: string
  message: string
  stack?: string
  code?: string
  category: 'network' | 'runtime' | 'validation' | 'permission' | 'system'
  context?: Record<string, any>
  retryable?: boolean
  suggestions?: Array<{
    id: string
    text: string
  }>
}

interface ToastInfo {
  type: 'error' | 'warning' | 'info'
  title: string
  description: string
  duration?: number
}

interface ReportForm {
  type: string
  description: string
  contact: string
  includeScreenshot: boolean
}

// Props
interface Props {
  fallbackComponent?: string
  enableErrorReporting?: boolean
  enablePerformanceMonitoring?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  enableErrorReporting: true,
  enablePerformanceMonitoring: true
})

// 响应式数据
const hasError = ref(false)
const errorInfo = ref<ErrorInfo>({
  title: '出现了一些问题',
  description: '应用程序遇到了意外错误，请稍后重试',
  message: '',
  category: 'runtime',
  retryable: true,
  suggestions: []
})

const showToast = ref(false)
const toastInfo = ref<ToastInfo>({
  type: 'error',
  title: '操作失败',
  description: ''
})

const networkError = ref(false)
const retrying = ref(false)
const retryingNetwork = ref(false)

const reportModalVisible = ref(false)
const submittingReport = ref(false)
const reportFormRef = ref<InstanceType<typeof ElForm>>()

const reportForm = ref<ReportForm>({
  type: '',
  description: '',
  contact: '',
  includeScreenshot: true
})

const reportRules = {
  type: [{ required: true, message: '请选择问题类型', trigger: 'change' }],
  description: [{ required: true, message: '请描述问题详情', trigger: 'blur' }]
}

const activeCollapse = ref<string[]>([])
const errorTimestamp = ref(Date.now())

// 加载状态
const showLoadingIndicator = ref(false)
const loadingText = ref('正在处理...')
const loadingProgress = ref(0)
const loadingCancellable = ref(false)
const loadingCancelCallback = ref<(() => void) | null>(null)

// 计算属性
const errorTitle = computed(() => errorInfo.value.title)
const errorDescription = computed(() => errorInfo.value.description)
const errorMessage = computed(() => errorInfo.value.message)
const errorStack = computed(() => errorInfo.value.stack)
const errorContext = computed(() => errorInfo.value.context)
const errorCode = computed(() => errorInfo.value.code)
const errorCategory = computed(() => {
  const categories = {
    network: '网络错误',
    runtime: '运行时错误',
    validation: '验证错误',
    permission: '权限错误',
    system: '系统错误'
  }
  return categories[errorInfo.value.category] || '未知错误'
})

const retryable = computed(() => errorInfo.value.retryable !== false)
const suggestions = computed(() => errorInfo.value.suggestions || [])

const toastType = computed(() => toastInfo.value.type)
const toastTitle = computed(() => toastInfo.value.title)
const toastDescription = computed(() => toastInfo.value.description)

const retryButtonText = computed(() => {
  return retrying.value ? '重试中...' : '重试操作'
})

const userAgent = computed(() => navigator.userAgent)
const currentUrl = computed(() => window.location.href)

// 方法
const getErrorTagType = () => {
  const types = {
    network: 'danger',
    runtime: 'danger',
    validation: 'warning',
    permission: 'warning',
    system: 'info'
  }
  return types[errorInfo.value.category] || 'danger'
}

const getToastIcon = () => {
  const icons = {
    error: 'icon-x-circle',
    warning: 'icon-alert-triangle',
    info: 'icon-info'
  }
  return icons[toastInfo.value.type] || 'icon-info'
}

const handleError = (error: Error | ErrorInfo, context?: Record<string, any>) => {
  console.error('Error caught by EnhancedErrorHandler:', error)

  let errorData: ErrorInfo

  if (error instanceof Error) {
    errorData = {
      title: '应用程序错误',
      description: '应用程序遇到了意外错误',
      message: error.message,
      stack: error.stack,
      category: 'runtime',
      retryable: true,
      context,
      suggestions: [
        { id: '1', text: '尝试刷新页面' },
        { id: '2', text: '检查网络连接' },
        { id: '3', text: '稍后再试' }
      ]
    }
  } else {
    errorData = {
      ...error,
      context: { ...error.context, ...context }
    }
  }

  errorInfo.value = errorData
  errorTimestamp.value = Date.now()
  hasError.value = true

  // 记录错误日志
  logError(errorData)

  // 发送错误报告（如果启用）
  if (props.enableErrorReporting) {
    sendErrorReport(errorData)
  }
}

const handleNetworkError = (error: any) => {
  networkError.value = true
  console.error('Network error:', error)
}

const handleToast = (toast: ToastInfo) => {
  toastInfo.value = toast
  showToast.value = true

  // 自动隐藏
  if (toast.duration !== 0) {
    setTimeout(() => {
      showToast.value = false
    }, toast.duration || 5000)
  }
}

const handleRetry = async () => {
  if (retrying.value) return

  retrying.value = true

  try {
    // 模拟重试逻辑
    await new Promise(resolve => setTimeout(resolve, 2000))

    // 重试成功，清除错误状态
    hasError.value = false
    ElMessage.success('操作成功')
  } catch (error) {
    // 重试失败，显示错误
    ElMessage.error('重试失败，请稍后再试')
  } finally {
    retrying.value = false
  }
}

const handleReload = () => {
  window.location.reload()
}

const retryNetworkRequest = async () => {
  retryingNetwork.value = true

  try {
    // 模拟网络重试
    await new Promise(resolve => setTimeout(resolve, 2000))

    networkError.value = false
    ElMessage.success('网络连接已恢复')
  } catch (error) {
    ElMessage.error('网络连接仍然异常')
  } finally {
    retryingNetwork.value = false
  }
}

const toggleReportModal = () => {
  reportModalVisible.value = !reportModalVisible.value
}

const copyErrorInfo = async () => {
  const errorText = `
错误类型: ${errorCategory.value}
错误时间: ${formatTime(errorTimestamp.value)}
错误信息: ${errorMessage.value}
错误码: ${errorCode.value || 'N/A'}
页面地址: ${currentUrl.value}
用户代理: ${userAgent.value}
${errorStack.value ? `调用栈:\n${errorStack.value}` : ''}
`.trim()

  try {
    await navigator.clipboard.writeText(errorText)
    ElMessage.success('错误信息已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const submitReport = async () => {
  try {
    await reportFormRef.value?.validate()
    submittingReport.value = true

    // 模拟提交报告
    await new Promise(resolve => setTimeout(resolve, 2000))

    ElMessage.success('问题报告已提交，感谢您的反馈')
    reportModalVisible.value = false

    // 重置表单
    reportForm.value = {
      type: '',
      description: '',
      contact: '',
      includeScreenshot: true
    }
  } catch (error) {
    // 表单验证失败或提交失败
  } finally {
    submittingReport.value = false
  }
}

const showLoading = (text?: string, cancellable?: boolean, cancelCallback?: () => void) => {
  loadingText.value = text || '正在处理...'
  loadingCancellable.value = cancellable || false
  loadingCancelCallback.value = cancelCallback || null
  loadingProgress.value = 0
  showLoadingIndicator.value = true
}

const updateLoadingProgress = (progress: number) => {
  loadingProgress.value = progress
}

const hideLoading = () => {
  showLoadingIndicator.value = false
  loadingProgress.value = 0
  loadingCancelCallback.value = null
}

const cancelLoading = () => {
  if (loadingCancelCallback.value) {
    loadingCancelCallback.value()
  }
  hideLoading()
}

const logError = (error: ErrorInfo) => {
  // 发送到日志服务
  const logData = {
    type: 'error',
    message: error.message,
    category: error.category,
    code: error.code,
    context: error.context,
    stack: error.stack,
    timestamp: new Date().toISOString(),
    url: currentUrl.value,
    userAgent: userAgent.value
  }

  console.log('Error logged:', logData)

  // 这里可以集成实际的日志服务
  // fetch('/api/logs', {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify(logData)
  // }).catch(console.error)
}

const sendErrorReport = async (error: ErrorInfo) => {
  try {
    // 发送错误报告到监控服务
    const reportData = {
      error: error.message,
      stack: error.stack,
      category: error.category,
      code: error.code,
      context: error.context,
      timestamp: new Date().toISOString(),
      url: currentUrl.value,
      userAgent: userAgent.value
    }

    // 这里可以集成实际的错误监控服务，如 Sentry
    console.log('Error report sent:', reportData)

    // 示例：发送到 Sentry
    // Sentry.captureException(error, { extra: error.context })
  } catch (reportError) {
    console.error('Failed to send error report:', reportError)
  }
}

const formatTime = (timestamp: number) => {
  return new Date(timestamp).toLocaleString()
}

// 性能监控
const monitorPerformance = () => {
  if (!props.enablePerformanceMonitoring) return

  // 监控页面加载性能
  window.addEventListener('load', () => {
    if ('performance' in window) {
      const perfData = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming

      const metrics = {
        loadTime: perfData.loadEventEnd - perfData.loadEventStart,
        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
        firstPaint: 0,
        firstContentfulPaint: 0
      }

      // 获取绘制时间
      const paintEntries = performance.getEntriesByType('paint')
      paintEntries.forEach(entry => {
        if (entry.name === 'first-paint') {
          metrics.firstPaint = entry.startTime
        }
        if (entry.name === 'first-contentful-paint') {
          metrics.firstContentfulPaint = entry.startTime
        }
      })

      console.log('Performance metrics:', metrics)

      // 如果性能指标异常，显示提示
      if (metrics.loadTime > 5000) {
        handleToast({
          type: 'warning',
          title: '页面加载较慢',
          description: '检测到页面加载时间较长，建议检查网络连接',
          duration: 8000
        })
      }
    }
  })

  // 监控长任务
  if ('PerformanceObserver' in window) {
    const observer = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.duration > 50) { // 长于50ms的任务
          console.warn('Long task detected:', entry)
        }
      })
    })

    try {
      observer.observe({ entryTypes: ['longtask'] })
    } catch (error) {
      console.log('Long task monitoring not supported')
    }
  }
}

// 全局错误监听
const setupGlobalErrorHandlers = () => {
  // JavaScript 错误
  window.addEventListener('error', (event) => {
    handleError(event.error || new Error(event.message), {
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      type: 'javascript'
    })
  })

  // Promise 拒绝错误
  window.addEventListener('unhandledrejection', (event) => {
    handleError(new Error(event.reason), {
      type: 'promise',
      promise: event.promise
    })
  })

  // 资源加载错误
  window.addEventListener('error', (event) => {
    if (event.target !== window) {
      const target = event.target as HTMLElement
      handleToast({
        type: 'warning',
        title: '资源加载失败',
        description: `无法加载 ${target.tagName.toLowerCase()}: ${target.src || target.href}`,
        duration: 5000
      })
    }
  }, true)
}

// 暴露方法
defineExpose({
  handleError,
  handleToast,
  handleNetworkError,
  showLoading,
  updateLoadingProgress,
  hideLoading
})

// 生命周期
onMounted(() => {
  setupGlobalErrorHandlers()
  monitorPerformance()
})

onUnmounted(() => {
  // 清理工作
})
</script>

<style scoped>
.enhanced-error-handler {
  position: relative;
  width: 100%;
  height: 100%;
}

/* 错误边界样式 */
.error-boundary {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 40px 20px;
  background: #fafbfc;
}

.error-container {
  max-width: 600px;
  width: 100%;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.error-visual {
  position: relative;
  padding: 40px;
  text-align: center;
  background: linear-gradient(135deg, #fef0f0 0%, #fef6ec 100%);
}

.error-icon {
  position: relative;
  z-index: 2;
  font-size: 64px;
  color: #f56c6c;
  margin-bottom: 16px;
}

.error-waves {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1;
}

.wave {
  position: absolute;
  border: 2px solid rgba(245, 108, 108, 0.3);
  border-radius: 50%;
  animation: wave 3s ease-out infinite;
}

.wave:nth-child(1) {
  width: 120px;
  height: 120px;
  margin: -60px 0 0 -60px;
  animation-delay: 0s;
}

.wave:nth-child(2) {
  width: 180px;
  height: 180px;
  margin: -90px 0 0 -90px;
  animation-delay: 1s;
}

.wave:nth-child(3) {
  width: 240px;
  height: 240px;
  margin: -120px 0 0 -120px;
  animation-delay: 2s;
}

@keyframes wave {
  0% {
    opacity: 0.8;
    transform: scale(0.8);
  }
  100% {
    opacity: 0;
    transform: scale(1.5);
  }
}

.error-content {
  padding: 32px;
}

.error-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
  text-align: center;
}

.error-description {
  font-size: 16px;
  color: #606266;
  margin: 0 0 20px 0;
  text-align: center;
  line-height: 1.6;
}

.error-tags {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.error-details {
  margin-bottom: 24px;
}

.detail-content {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.detail-section {
  margin-bottom: 16px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.error-message,
.error-stack {
  font-size: 13px;
  color: #606266;
  background: white;
  padding: 12px;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  word-break: break-all;
}

.error-stack pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.4;
  white-space: pre-wrap;
}

.error-context {
  background: white;
}

.error-suggestions {
  margin-bottom: 32px;
  padding: 20px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.error-suggestions h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
  margin: 0 0 12px 0;
}

.suggestion-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.suggestion-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  color: #606266;
  font-size: 14px;
}

.suggestion-list li i {
  color: #67c23a;
  font-size: 16px;
}

.error-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.primary-actions {
  display: flex;
  gap: 12px;
}

.secondary-actions {
  display: flex;
  gap: 8px;
}

/* 错误提示 Toast */
.error-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 2000;
  max-width: 400px;
  animation: slideInRight 0.3s ease;
}

.error-toast.error {
  background: #fef0f0;
  border: 1px solid #f56c6c;
  color: #f56c6c;
}

.error-toast.warning {
  background: #fdf6ec;
  border: 1px solid #e6a23c;
  color: #e6a23c;
}

.error-toast.info {
  background: #f4f4f5;
  border: 1px solid #909399;
  color: #909399;
}

.toast-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.toast-icon {
  font-size: 20px;
  margin-top: 2px;
}

.toast-message {
  flex: 1;
}

.toast-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.toast-description {
  font-size: 14px;
  opacity: 0.8;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 网络错误重试 */
.network-error-retry {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1500;
  max-width: 350px;
}

.network-error-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border-left: 4px solid #f56c6c;
}

.network-error-icon {
  font-size: 24px;
  color: #f56c6c;
}

.network-error-text {
  flex: 1;
}

.network-error-text h4 {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px 0;
}

.network-error-text p {
  font-size: 12px;
  color: #606266;
  margin: 0;
}

.network-error-actions {
  display: flex;
  gap: 8px;
}

/* 问题报告模态框 */
.report-form {
  padding: 20px 0;
}

.error-info-summary {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.report-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 加载指示器 */
.loading-indicator {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
}

.loading-content {
  position: relative;
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  text-align: center;
  min-width: 200px;
}

.loading-spinner {
  position: relative;
  width: 60px;
  height: 60px;
  margin: 0 auto 20px;
}

.spinner-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 3px solid transparent;
  border-radius: 50%;
  animation: spin 1.5s ease-in-out infinite;
}

.spinner-ring:nth-child(1) {
  border-top-color: #667eea;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #764ba2;
  animation-delay: 0.2s;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #409eff;
  animation-delay: 0.4s;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 16px;
}

.loading-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.loading-progress .el-progress {
  flex: 1;
}

.loading-progress span {
  font-size: 14px;
  color: #606266;
  min-width: 40px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .error-boundary {
    padding: 20px 16px;
  }

  .error-container {
    margin: 0;
  }

  .error-visual {
    padding: 30px 20px;
  }

  .error-content {
    padding: 24px 20px;
  }

  .error-actions {
    flex-direction: column;
    gap: 12px;
  }

  .primary-actions,
  .secondary-actions {
    justify-content: center;
  }

  .error-toast {
    top: 10px;
    right: 10px;
    left: 10px;
    max-width: none;
  }

  .network-error-retry {
    bottom: 10px;
    right: 10px;
    left: 10px;
    max-width: none;
  }

  .network-error-content {
    flex-direction: column;
    text-align: center;
  }

  .loading-content {
    margin: 20px;
    padding: 24px 20px;
    min-width: auto;
  }
}
</style>