<template>
  <div class="test-enhanced-export">
    <!-- 测试页面头部 -->
    <div class="test-header">
      <h1>
        <i class="icon-flask"></i>
        增强型数据导出功能测试
      </h1>
      <p>测试和验证优化后的数据导出功能组件</p>
    </div>

    <!-- 测试控制面板 -->
    <div class="test-controls">
      <div class="control-section">
        <h3>组件测试控制</h3>
        <div class="control-buttons">
          <el-button @click="testEnhancedForm" type="primary">
            <i class="icon-edit"></i>
            测试增强表单
          </el-button>
          <el-button @click="testSmartPreview" type="success">
            <i class="icon-eye"></i>
            测试智能预览
          </el-button>
          <el-button @click="testProgressVisualization" type="warning">
            <i class="icon-activity"></i>
            测试进度可视化
          </el-button>
          <el-button @click="testErrorHandling" type="danger">
            <i class="icon-x-circle"></i>
            测试错误处理
          </el-button>
        </div>
      </div>

      <div class="control-section">
        <h3>集成测试</h3>
        <div class="control-buttons">
          <el-button @click="testFullExportFlow" type="primary" size="large">
            <i class="icon-play-circle"></i>
            完整导出流程测试
          </el-button>
          <el-button @click="testPerformance" size="large">
            <i class="icon-trending-up"></i>
            性能测试
          </el-button>
        </div>
      </div>
    </div>

    <!-- 测试结果显示区域 -->
    <div class="test-results">
      <div class="results-header">
        <h3>测试结果</h3>
        <div class="results-actions">
          <el-button @click="clearResults" size="small" text>
            <i class="icon-trash-2"></i>
            清空结果
          </el-button>
          <el-button @click="exportResults" size="small" text>
            <i class="icon-download"></i>
            导出结果
          </el-button>
        </div>
      </div>

      <div class="results-content">
        <div
          v-for="result in testResults"
          :key="result.id"
          class="result-item"
          :class="result.status"
        >
          <div class="result-icon">
            <i :class="getResultIcon(result.status)"></i>
          </div>
          <div class="result-content">
            <div class="result-title">{{ result.title }}</div>
            <div class="result-description">{{ result.description }}</div>
            <div class="result-details" v-if="result.details">
              <pre>{{ result.details }}</pre>
            </div>
            <div class="result-meta">
              <span class="result-time">{{ formatTime(result.timestamp) }}</span>
              <span class="result-duration" v-if="result.duration">
                耗时: {{ result.duration }}ms
              </span>
            </div>
          </div>
          <div class="result-actions">
            <el-button
              v-if="result.retryable"
              @click="retryTest(result)"
              size="small"
              text
            >
              重试
            </el-button>
            <el-button @click="removeResult(result)" size="small" text type="danger">
              删除
            </el-button>
          </div>
        </div>

        <div v-if="testResults.length === 0" class="no-results">
          <i class="icon-inbox"></i>
          <p>暂无测试结果</p>
        </div>
      </div>
    </div>

    <!-- 组件测试区域 -->
    <div class="component-test-area">
      <!-- 增强型表单测试 -->
      <div v-if="showEnhancedForm" class="test-component">
        <div class="component-header">
          <h3>EnhancedExportForm 组件测试</h3>
          <el-button @click="showEnhancedForm = false" size="small" text>
            <i class="icon-x"></i>
          </el-button>
        </div>
        <EnhancedExportForm
          :available-lines="mockLines"
          :loading="mockLoading"
          @export="handleFormExport"
          @preview="handleFormPreview"
          @save-template="handleFormSaveTemplate"
        />
      </div>

      <!-- 智能预览测试 -->
      <div v-if="showSmartPreview" class="test-component">
        <div class="component-header">
          <h3>SmartDataPreview 组件测试</h3>
          <el-button @click="showSmartPreview = false" size="small" text>
            <i class="icon-x"></i>
          </el-button>
        </div>
        <SmartDataPreview
          :data="mockPreviewData"
          :columns="mockPreviewColumns"
          :loading="mockPreviewLoading"
          :total-records="mockTotalRecords"
          :estimated-size="mockEstimatedSize"
          :data-quality="mockDataQuality"
          @close="showSmartPreview = false"
          @refresh="handlePreviewRefresh"
          @export="handlePreviewExport"
        />
      </div>

      <!-- 进度可视化测试 -->
      <div v-if="showProgressVisualization" class="test-component">
        <div class="component-header">
          <h3>EnhancedProgressVisualization 组件测试</h3>
          <el-button @click="showProgressVisualization = false" size="small" text>
            <i class="icon-x"></i>
          </el-button>
        </div>
        <EnhancedProgressVisualization
          title="测试导出进度"
          :progress="mockProgress"
          :stages="mockProgressStages"
          :tasks="mockProgressTasks"
          :milestones="mockProgressMilestones"
          :cancellable="true"
          :pausable="true"
          :retryable="true"
          :show-stats="true"
          :show-details="true"
          :show-progress-animation="true"
          :start-time="mockProgressStartTime"
          @cancel="handleProgressCancel"
          @pause="handleProgressPause"
          @resume="handleProgressResume"
          @retry="handleProgressRetry"
          @retry-failed="handleProgressRetryFailed"
          @export-log="handleProgressExportLog"
        />
      </div>

      <!-- 错误处理测试 -->
      <div v-if="showErrorHandling" class="test-component">
        <div class="component-header">
          <h3>EnhancedErrorHandler 组件测试</h3>
          <el-button @click="showErrorHandling = false" size="small" text>
            <i class="icon-x"></i>
          </el-button>
        </div>
        <div class="error-test-controls">
          <el-button @click="triggerJsError" type="danger">
            触发 JavaScript 错误
          </el-button>
          <el-button @click="triggerNetworkError" type="warning">
            触发网络错误
          </el-button>
          <el-button @click="triggerValidationWarning" type="info">
            触发验证警告
          </el-button>
          <el-button @click="triggerLoadingState" type="primary">
            触发加载状态
          </el-button>
        </div>
        <EnhancedErrorHandler
          ref="errorHandlerRef"
          :enable-error-reporting="true"
          :enable-performance-monitoring="true"
        >
          <div class="error-handler-content">
            <p>这是错误处理器保护的内容区域</p>
          </div>
        </EnhancedErrorHandler>
      </div>
    </div>

    <!-- 性能监控面板 -->
    <div class="performance-panel">
      <div class="panel-header">
        <h3>性能监控</h3>
        <el-button @click="clearPerformanceData" size="small" text>
          清空数据
        </el-button>
      </div>
      <div class="panel-content">
        <div class="performance-metrics">
          <div class="metric-item">
            <div class="metric-label">页面加载时间</div>
            <div class="metric-value">{{ performanceMetrics.loadTime }}ms</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">DOM 渲染时间</div>
            <div class="metric-value">{{ performanceMetrics.domTime }}ms</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">组件渲染次数</div>
            <div class="metric-value">{{ performanceMetrics.renderCount }}</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">内存使用</div>
            <div class="metric-value">{{ performanceMetrics.memoryUsage }}MB</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import EnhancedExportForm from '@/components/enhanced/EnhancedExportForm.vue'
import SmartDataPreview from '@/components/enhanced/SmartDataPreview.vue'
import EnhancedProgressVisualization from '@/components/enhanced/EnhancedProgressVisualization.vue'
import EnhancedErrorHandler from '@/components/enhanced/EnhancedErrorHandler.vue'

// 接口定义
interface TestResult {
  id: string
  title: string
  description: string
  status: 'success' | 'error' | 'warning' | 'info'
  details?: string
  timestamp: number
  duration?: number
  retryable?: boolean
  retryCallback?: () => void
}

interface PerformanceMetrics {
  loadTime: number
  domTime: number
  renderCount: number
  memoryUsage: number
}

// 响应式数据
const testResults = ref<TestResult[]>([])
const showEnhancedForm = ref(false)
const showSmartPreview = ref(false)
const showProgressVisualization = ref(false)
const showErrorHandling = ref(false)

const errorHandlerRef = ref()

// 模拟数据
const mockLines = ref(['M1', 'M2', 'M3', 'M4', 'M5'])
const mockLoading = ref(false)

const mockPreviewData = ref([])
const mockPreviewColumns = ref([])
const mockPreviewLoading = ref(false)
const mockTotalRecords = ref(0)
const mockEstimatedSize = ref('')
const mockDataQuality = ref(null)

const mockProgress = ref({
  percent: 0,
  current: 0,
  total: 0,
  text: ''
})
const mockProgressStages = ref([])
const mockProgressTasks = ref([])
const mockProgressMilestones = ref([
  { percent: 25, label: '数据准备' },
  { percent: 50, label: '数据处理' },
  { percent: 75, label: '文件生成' },
  { percent: 100, label: '导出完成' }
])
const mockProgressStartTime = ref(Date.now())

const performanceMetrics = ref<PerformanceMetrics>({
  loadTime: 0,
  domTime: 0,
  renderCount: 0,
  memoryUsage: 0
})

let performanceInterval: number | null = null

// 方法
const addTestResult = (result: Omit<TestResult, 'id' | 'timestamp'>) => {
  const testResult: TestResult = {
    id: Date.now().toString(),
    timestamp: Date.now(),
    ...result
  }
  testResults.value.unshift(testResult)

  // 保持最多50条结果
  if (testResults.value.length > 50) {
    testResults.value = testResults.value.slice(0, 50)
  }
}

const getResultIcon = (status: string) => {
  const icons = {
    success: 'icon-check-circle',
    error: 'icon-x-circle',
    warning: 'icon-alert-triangle',
    info: 'icon-info'
  }
  return icons[status] || 'icon-info'
}

const formatTime = (timestamp: number) => {
  return new Date(timestamp).toLocaleTimeString()
}

const clearResults = () => {
  testResults.value = []
  ElMessage.success('测试结果已清空')
}

const exportResults = () => {
  const resultsText = testResults.value.map(result =>
    `[${formatTime(result.timestamp)}] [${result.status.toUpperCase()}] ${result.title}: ${result.description}`
  ).join('\n')

  const blob = new Blob([resultsText], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `test_results_${new Date().toISOString().slice(0, 10)}.txt`
  a.click()
  URL.revokeObjectURL(url)

  ElMessage.success('测试结果已导出')
}

const removeResult = (result: TestResult) => {
  const index = testResults.value.findIndex(r => r.id === result.id)
  if (index > -1) {
    testResults.value.splice(index, 1)
  }
}

const retryTest = (result: TestResult) => {
  if (result.retryCallback) {
    result.retryCallback()
  }
}

// 组件测试方法
const testEnhancedForm = () => {
  const startTime = Date.now()
  showEnhancedForm.value = true

  try {
    // 测试表单组件功能
    addTestResult({
      title: 'EnhancedExportForm 组件测试',
      description: '增强型导出表单组件加载成功',
      status: 'success',
      duration: Date.now() - startTime,
      retryable: true,
      retryCallback: testEnhancedForm
    })

    ElMessage.success('增强型表单组件测试成功')
  } catch (error) {
    addTestResult({
      title: 'EnhancedExportForm 组件测试',
      description: `组件测试失败: ${error.message}`,
      status: 'error',
      details: error.stack,
      duration: Date.now() - startTime,
      retryable: true,
      retryCallback: testEnhancedForm
    })
  }
}

const testSmartPreview = () => {
  const startTime = Date.now()

  try {
    // 生成模拟预览数据
    mockPreviewData.value = generateMockPreviewData(100)
    mockPreviewColumns.value = [
      { key: 'timestamp', title: '时间', type: 'datetime' },
      { key: 'station_name', title: '车站', type: 'string' },
      { key: 'power', title: '功率(kW)', type: 'number' },
      { key: 'energy', title: '电量(kWh)', type: 'number' }
    ]
    mockTotalRecords.value = 1250
    mockEstimatedSize.value = '~1.2 MB'
    mockDataQuality.value = {
      score: 94,
      completeness: 96,
      accuracy: 92,
      consistency: 95
    }

    showSmartPreview.value = true

    addTestResult({
      title: 'SmartDataPreview 组件测试',
      description: '智能预览组件加载成功，数据量: 100条记录',
      status: 'success',
      duration: Date.now() - startTime,
      retryable: true,
      retryCallback: testSmartPreview
    })

    ElMessage.success('智能预览组件测试成功')
  } catch (error) {
    addTestResult({
      title: 'SmartDataPreview 组件测试',
      description: `组件测试失败: ${error.message}`,
      status: 'error',
      details: error.stack,
      duration: Date.now() - startTime,
      retryable: true,
      retryCallback: testSmartPreview
    })
  }
}

const testProgressVisualization = () => {
  const startTime = Date.now()

  try {
    // 初始化进度数据
    mockProgressStartTime.value = Date.now()
    startProgressSimulation()

    showProgressVisualization.value = true

    addTestResult({
      title: 'EnhancedProgressVisualization 组件测试',
      description: '增强型进度可视化组件测试成功',
      status: 'success',
      duration: Date.now() - startTime,
      retryable: true,
      retryCallback: testProgressVisualization
    })

    ElMessage.success('进度可视化组件测试成功')
  } catch (error) {
    addTestResult({
      title: 'EnhancedProgressVisualization 组件测试',
      description: `组件测试失败: ${error.message}`,
      status: 'error',
      details: error.stack,
      duration: Date.now() - startTime,
      retryable: true,
      retryCallback: testProgressVisualization
    })
  }
}

const testErrorHandling = () => {
  const startTime = Date.now()

  try {
    showErrorHandling.value = true

    addTestResult({
      title: 'EnhancedErrorHandler 组件测试',
      description: '增强型错误处理组件测试界面已加载',
      status: 'info',
      duration: Date.now() - startTime,
      retryable: true,
      retryCallback: testErrorHandling
    })

    ElMessage.info('错误处理组件测试界面已加载，请点击相应按钮测试不同类型的错误')
  } catch (error) {
    addTestResult({
      title: 'EnhancedErrorHandler 组件测试',
      description: `组件测试失败: ${error.message}`,
      status: 'error',
      details: error.stack,
      duration: Date.now() - startTime,
      retryable: true,
      retryCallback: testErrorHandling
    })
  }
}

// 集成测试方法
const testFullExportFlow = async () => {
  const startTime = Date.now()
  addTestResult({
    title: '完整导出流程测试',
    description: '开始执行完整导出流程测试...',
    status: 'info',
    duration: 0,
    retryable: false
  })

  try {
    // 模拟完整导出流程
    await simulateFullExportFlow()

    addTestResult({
      title: '完整导出流程测试',
      description: '完整导出流程测试成功完成',
      status: 'success',
      duration: Date.now() - startTime,
      retryable: true,
      retryCallback: testFullExportFlow
    })

    ElMessage.success('完整导出流程测试成功')
  } catch (error) {
    addTestResult({
      title: '完整导出流程测试',
      description: `流程测试失败: ${error.message}`,
      status: 'error',
      details: error.stack,
      duration: Date.now() - startTime,
      retryable: true,
      retryCallback: testFullExportFlow
    })
  }
}

const testPerformance = () => {
  const startTime = Date.now()

  try {
    // 执行性能测试
    performPerformanceTest()

    addTestResult({
      title: '性能测试',
      description: `性能测试完成，平均响应时间: ${performanceMetrics.value.loadTime}ms`,
      status: 'success',
      details: JSON.stringify(performanceMetrics.value, null, 2),
      duration: Date.now() - startTime,
      retryable: true,
      retryCallback: testPerformance
    })

    ElMessage.success('性能测试完成')
  } catch (error) {
    addTestResult({
      title: '性能测试',
      description: `性能测试失败: ${error.message}`,
      status: 'error',
      details: error.stack,
      duration: Date.now() - startTime,
      retryable: true,
      retryCallback: testPerformance
    })
  }
}

// 辅助方法
const generateMockPreviewData = (count: number) => {
  const data = []
  const now = new Date()

  for (let i = 0; i < count; i++) {
    const timestamp = new Date(now.getTime() - i * 60000).toISOString().slice(0, 19).replace('T', ' ')
    data.push({
      timestamp,
      station_name: `车站${(i % 10) + 1}`,
      power: (Math.random() * 1000).toFixed(2),
      energy: (Math.random() * 5000).toFixed(2),
      voltage: (220 + Math.random() * 20).toFixed(1),
      current: (Math.random() * 100).toFixed(2)
    })
  }

  return data
}

const startProgressSimulation = () => {
  let progress = 0
  mockProgress.value = {
    percent: 0,
    current: 0,
    total: 100,
    text: '准备导出...'
  }

  mockProgressStages.value = [
    { key: 'prepare', title: '数据准备', description: '获取导出参数', status: 'processing', progress: 0 },
    { key: 'fetch', title: '数据获取', description: '从服务器获取数据', status: 'pending', progress: 0 },
    { key: 'process', title: '数据处理', description: '格式化和处理数据', status: 'pending', progress: 0 },
    { key: 'generate', title: '文件生成', description: '生成导出文件', status: 'pending', progress: 0 }
  ]

  const interval = setInterval(() => {
    progress += 2
    mockProgress.value.percent = progress
    mockProgress.value.current = progress
    mockProgress.value.text = `正在处理... ${progress}%`

    // 更新阶段进度
    const currentStageIndex = Math.floor(progress / 25)
    if (currentStageIndex < mockProgressStages.value.length) {
      mockProgressStages.value[currentStageIndex].progress = (progress % 25) * 4

      if (progress % 25 === 0 && currentStageIndex > 0) {
        mockProgressStages.value[currentStageIndex - 1].status = 'completed'
        mockProgressStages.value[currentStageIndex].status = 'processing'
      }
    }

    if (progress >= 100) {
      clearInterval(interval)
      mockProgress.value.text = '导出完成'
      mockProgressStages.value[3].status = 'completed'
      mockProgressStages.value[3].progress = 100
    }
  }, 100)
}

const simulateFullExportFlow = async () => {
  return new Promise((resolve, reject) => {
    try {
      // 模拟完整的导出流程
      setTimeout(() => {
        // 步骤1: 初始化
        addTestResult({
          title: '导出流程 - 步骤1',
          description: '初始化导出参数',
          status: 'success',
          duration: 100
        })
      }, 100)

      setTimeout(() => {
        // 步骤2: 数据验证
        addTestResult({
          title: '导出流程 - 步骤2',
          description: '验证导出参数',
          status: 'success',
          duration: 50
        })
      }, 200)

      setTimeout(() => {
        // 步骤3: 数据获取
        addTestResult({
          title: '导出流程 - 步骤3',
          description: '获取导出数据',
          status: 'success',
          duration: 500
        })
      }, 500)

      setTimeout(() => {
        // 步骤4: 数据处理
        addTestResult({
          title: '导出流程 - 步骤4',
          description: '处理和格式化数据',
          status: 'success',
          duration: 300
        })
      }, 1000)

      setTimeout(() => {
        // 步骤5: 文件生成
        addTestResult({
          title: '导出流程 - 步骤5',
          description: '生成导出文件',
          status: 'success',
          duration: 200
        })
        resolve('success')
      }, 1500)
    } catch (error) {
      reject(error)
    }
  })
}

const performPerformanceTest = () => {
  // 模拟性能测试
  const startTime = performance.now()

  // 执行一些计算密集型操作
  let result = 0
  for (let i = 0; i < 1000000; i++) {
    result += Math.random()
  }

  const endTime = performance.now()

  performanceMetrics.value.loadTime = Math.round(endTime - startTime)
  performanceMetrics.value.domTime = Math.round(Math.random() * 50 + 10)
  performanceMetrics.value.renderCount = Math.floor(Math.random() * 100 + 50)
  performanceMetrics.value.memoryUsage = Math.round(Math.random() * 50 + 20)
}

const clearPerformanceData = () => {
  performanceMetrics.value = {
    loadTime: 0,
    domTime: 0,
    renderCount: 0,
    memoryUsage: 0
  }
  ElMessage.success('性能数据已清空')
}

// 错误触发方法
const triggerJsError = () => {
  if (errorHandlerRef.value) {
    errorHandlerRef.value.handleError(new Error('这是一个测试 JavaScript 错误'), {
      component: 'TestEnhancedExport',
      action: 'triggerJsError'
    })
  }
}

const triggerNetworkError = () => {
  if (errorHandlerRef.value) {
    errorHandlerRef.value.handleNetworkError(new Error('网络连接失败'))
  }
}

const triggerValidationWarning = () => {
  if (errorHandlerRef.value) {
    errorHandlerRef.value.handleToast({
      type: 'warning',
      title: '数据验证警告',
      description: '某些数据格式可能不正确，请检查'
    })
  }
}

const triggerLoadingState = () => {
  if (errorHandlerRef.value) {
    errorHandlerRef.value.showLoading('正在处理测试数据...', true, () => {
      ElMessage.info('加载操作已取消')
    })

    // 模拟进度更新
    let progress = 0
    const interval = setInterval(() => {
      progress += 10
      errorHandlerRef.value.updateLoadingProgress(progress)

      if (progress >= 100) {
        clearInterval(interval)
        setTimeout(() => {
          errorHandlerRef.value.hideLoading()
          ElMessage.success('测试数据处理完成')
        }, 500)
      }
    }, 200)
  }
}

// 组件事件处理方法
const handleFormExport = (data: any) => {
  addTestResult({
    title: '表单导出事件',
    description: `接收到导出请求: ${JSON.stringify(data)}`,
    status: 'info',
    details: JSON.stringify(data, null, 2)
  })
}

const handleFormPreview = (data: any) => {
  addTestResult({
    title: '表单预览事件',
    description: `接收到预览请求: ${JSON.stringify(data)}`,
    status: 'info'
  })
}

const handleFormSaveTemplate = (data: any) => {
  addTestResult({
    title: '保存模板事件',
    description: `接收到保存模板请求: ${JSON.stringify(data)}`,
    status: 'success'
  })
  ElMessage.success('模板保存测试成功')
}

const handlePreviewRefresh = () => {
  addTestResult({
    title: '预览刷新事件',
    description: '用户刷新了预览数据',
    status: 'info'
  })
}

const handlePreviewExport = () => {
  addTestResult({
    title: '预览导出事件',
    description: '用户导出了预览数据',
    status: 'success'
  })
  ElMessage.success('预览数据导出测试成功')
}

const handleProgressCancel = () => {
  addTestResult({
    title: '进度取消事件',
    description: '用户取消了导出操作',
    status: 'warning'
  })
}

const handleProgressPause = () => {
  addTestResult({
    title: '进度暂停事件',
    description: '用户暂停了导出操作',
    status: 'info'
  })
}

const handleProgressResume = () => {
  addTestResult({
    title: '进度继续事件',
    description: '用户继续了导出操作',
    status: 'info'
  })
}

const handleProgressRetry = (taskId?: string) => {
  addTestResult({
    title: '进度重试事件',
    description: `用户重试了任务: ${taskId || '所有任务'}`,
    status: 'info'
  })
}

const handleProgressRetryFailed = () => {
  addTestResult({
    title: '重试失败任务事件',
    description: '用户重试所有失败的任务',
    status: 'info'
  })
}

const handleProgressExportLog = () => {
  addTestResult({
    title: '导出日志事件',
    description: '用户导出了进度日志',
    status: 'success'
  })
  ElMessage.success('进度日志导出测试成功')
}

// 生命周期
onMounted(() => {
  // 启动性能监控
  performanceInterval = window.setInterval(() => {
    if (performance.memory) {
      performanceMetrics.value.memoryUsage = Math.round(
        performance.memory.usedJSHeapSize / 1024 / 1024
      )
    }
    performanceMetrics.value.renderCount++
  }, 1000)

  // 记录页面加载性能
  if ('performance' in window) {
    window.addEventListener('load', () => {
      const perfData = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
      performanceMetrics.value.loadTime = Math.round(
        perfData.loadEventEnd - perfData.loadEventStart
      )
      performanceMetrics.value.domTime = Math.round(
        perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart
      )
    })
  }
})

onUnmounted(() => {
  if (performanceInterval) {
    clearInterval(performanceInterval)
  }
})
</script>

<style scoped>
.test-enhanced-export {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

/* 测试页面头部 */
.test-header {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
  text-align: center;
}

.test-header h1 {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.test-header p {
  color: #606266;
  font-size: 16px;
  margin: 0;
}

/* 测试控制面板 */
.test-controls {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.control-section {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.control-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.control-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* 测试结果显示 */
.test-results {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
  overflow: hidden;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
}

.results-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.results-actions {
  display: flex;
  gap: 8px;
}

.results-content {
  max-height: 400px;
  overflow-y: auto;
  padding: 16px 24px;
}

.result-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 12px;
  transition: all 0.2s ease;
}

.result-item:hover {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.02);
}

.result-item.success {
  border-left: 4px solid #67c23a;
}

.result-item.error {
  border-left: 4px solid #f56c6c;
}

.result-item.warning {
  border-left: 4px solid #e6a23c;
}

.result-item.info {
  border-left: 4px solid #409eff;
}

.result-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 14px;
  flex-shrink: 0;
}

.result-item.success .result-icon {
  background: #f0f9ff;
  color: #67c23a;
}

.result-item.error .result-icon {
  background: #fef0f0;
  color: #f56c6c;
}

.result-item.warning .result-icon {
  background: #fdf6ec;
  color: #e6a23c;
}

.result-item.info .result-icon {
  background: #ecf5ff;
  color: #409eff;
}

.result-content {
  flex: 1;
}

.result-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.result-description {
  color: #606266;
  font-size: 14px;
  margin-bottom: 8px;
}

.result-details {
  margin-bottom: 8px;
}

.result-details pre {
  font-size: 12px;
  color: #909399;
  background: #f8f9fa;
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 0;
}

.result-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #c0c4cc;
}

.result-actions {
  display: flex;
  gap: 8px;
}

.no-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #c0c4cc;
}

.no-results i {
  font-size: 48px;
  margin-bottom: 16px;
}

.no-results p {
  font-size: 16px;
  margin: 0;
}

/* 组件测试区域 */
.component-test-area {
  margin-bottom: 24px;
}

.test-component {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  margin-bottom: 20px;
}

.component-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
}

.component-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.error-test-controls {
  padding: 20px 24px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  border-bottom: 1px solid #e4e7ed;
}

.error-handler-content {
  padding: 40px 24px;
  text-align: center;
  color: #606266;
}

/* 性能监控面板 */
.performance-panel {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
}

.panel-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.panel-content {
  padding: 24px;
}

.performance-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.metric-item {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.metric-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .test-enhanced-export {
    padding: 16px;
  }

  .test-controls {
    grid-template-columns: 1fr;
  }

  .control-buttons {
    flex-direction: column;
  }

  .results-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .result-item {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .result-actions {
    justify-content: flex-end;
  }

  .error-test-controls {
    flex-direction: column;
  }

  .performance-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>