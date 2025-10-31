<template>
  <div class="enhanced-data-export">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-background">
        <div class="header-decoration"></div>
      </div>
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">
            <i class="icon-download"></i>
            数据导出中心
          </h1>
          <p class="page-description">
            智能化的数据导出平台，支持多格式、大批量数据处理
          </p>
        </div>
        <div class="header-stats">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="icon-trending-up"></i>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ totalExports.toLocaleString() }}</div>
              <div class="stat-label">总导出次数</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              <i class="icon-check-circle"></i>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ successRate }}%</div>
              <div class="stat-label">成功率</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              <i class="icon-users"></i>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ activeExports }}</div>
              <div class="stat-label">进行中任务</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 快速操作区 -->
      <div class="quick-actions">
        <div class="action-card" @click="startQuickExport('electricity')">
          <div class="action-icon electricity">
            <i class="icon-zap"></i>
          </div>
          <div class="action-content">
            <h3>快速导出电耗数据</h3>
            <p>一键导出最近24小时电耗数据</p>
          </div>
          <div class="action-arrow">
            <i class="icon-chevron-right"></i>
          </div>
        </div>
        <div class="action-card" @click="startQuickExport('sensor')">
          <div class="action-icon sensor">
            <i class="icon-thermometer"></i>
          </div>
          <div class="action-content">
            <h3>快速导出传感器数据</h3>
            <p>一键导出最近24小时传感器数据</p>
          </div>
          <div class="action-arrow">
            <i class="icon-chevron-right"></i>
          </div>
        </div>
        <div class="action-card" @click="openTemplateManager">
          <div class="action-icon template">
            <i class="icon-save"></i>
          </div>
          <div class="action-content">
            <h3>模板管理</h3>
            <p>管理常用导出配置模板</p>
          </div>
          <div class="action-arrow">
            <i class="icon-chevron-right"></i>
          </div>
        </div>
      </div>

      <!-- 导出工作区 -->
      <div class="export-workspace">
        <!-- 增强型导出表单 -->
        <div class="workspace-section">
          <EnhancedExportForm
            ref="exportFormRef"
            :available-lines="availableLines"
            :loading="exporting"
            @export="handleExport"
            @save-template="handleSaveTemplate"
          />
        </div>
      </div>

      <!-- 进度可视化 -->
      <div v-if="showProgress" class="progress-section">
        <EnhancedProgressVisualization
          :title="progressTitle"
          :progress="progress"
          :stages="progressStages"
          :tasks="progressTasks"
          :milestones="progressMilestones"
          :cancellable="true"
          :pausable="true"
          :retryable="true"
          :show-stats="true"
          :show-details="true"
          :show-progress-animation="true"
          :start-time="progressStartTime"
          @cancel="cancelExport"
          @pause="pauseExport"
          @resume="resumeExport"
          @retry="retryTask"
          @retry-failed="retryFailedTasks"
          @export-log="exportProgressLog"
        />
      </div>

      <!-- 导出历史和队列 -->
      <div class="history-section">
        <div class="section-tabs">
          <div
            v-for="tab in historyTabs"
            :key="tab.key"
            :class="['tab-item', { active: activeHistoryTab === tab.key }]"
            @click="activeHistoryTab = tab.key"
          >
            <i :class="tab.icon"></i>
            <span>{{ tab.label }}</span>
            <span v-if="tab.count > 0" class="tab-badge">{{ tab.count }}</span>
          </div>
        </div>

        <div class="tab-content">
          <!-- 导出历史 -->
          <div v-if="activeHistoryTab === 'history'" class="history-list">
            <div
              v-for="record in exportHistory"
              :key="record.id"
              class="history-item"
              :class="record.status"
            >
              <div class="history-icon">
                <i :class="getHistoryIcon(record.status)"></i>
              </div>
              <div class="history-details">
                <div class="history-title">
                  {{ record.dataType === 'electricity' ? '电耗数据' : '传感器数据' }} - {{ record.line }}
                </div>
                <div class="history-meta">
                  <span class="history-time">{{ formatTime(record.time) }}</span>
                  <span class="history-duration" v-if="record.duration">
                    耗时 {{ formatDuration(record.duration) }}
                  </span>
                  <span class="history-size" v-if="record.fileSize">
                    {{ record.fileSize }}
                  </span>
                </div>
                <div v-if="record.error" class="history-error">
                  {{ record.error }}
                </div>
              </div>
              <div class="history-actions">
                <el-button
                  v-if="record.status === 'completed' && record.filePath"
                  @click="downloadFile(record)"
                  size="small"
                  type="primary"
                >
                  <i class="icon-download"></i>
                  下载
                </el-button>
                <el-button
                  v-if="record.partialFiles && record.partialFiles.length > 0"
                  @click="downloadPartial(record)"
                  size="small"
                  type="primary"
                >
                  <i class="icon-download"></i>
                  下载成功部分
                </el-button>
                <el-button
                  v-if="record.status === 'failed' && record.retryable"
                  @click="retryExport(record)"
                  size="small"
                  type="warning"
                >
                  <i class="icon-refresh-cw"></i>
                  重试
                </el-button>
                <el-button @click="viewHistoryDetails(record)" size="small" text>
                  详情
                </el-button>
              </div>
            </div>

            <div v-if="exportHistory.length === 0" class="empty-state">
              <i class="icon-inbox"></i>
              <p>暂无导出历史</p>
            </div>
          </div>

          <!-- 导出队列 -->
          <div v-if="activeHistoryTab === 'queue'" class="queue-list">
            <div
              v-for="task in exportQueue"
              :key="task.id"
              class="queue-item"
              :class="task.status"
            >
              <div class="queue-icon">
                <i :class="getQueueIcon(task.status)"></i>
              </div>
              <div class="queue-details">
                <div class="queue-title">{{ task.title }}</div>
                <div class="queue-progress">
                  <div class="queue-progress-bar">
                    <div
                      class="queue-progress-fill"
                      :style="{ width: `${task.progress}%` }"
                    ></div>
                  </div>
                  <span class="queue-progress-text">{{ task.progress }}%</span>
                </div>
                <div class="queue-meta">
                  <span class="queue-time">{{ formatTime(task.createdAt) }}</span>
                  <span class="queue-estimate" v-if="task.estimatedTime">
                    预计剩余: {{ task.estimatedTime }}
                  </span>
                </div>
              </div>
              <div class="queue-actions">
                <el-button
                  v-if="task.status === 'processing'"
                  @click="pauseTask(task)"
                  size="small"
                >
                  <i class="icon-pause"></i>
                  暂停
                </el-button>
                <el-button
                  v-if="task.status === 'paused'"
                  @click="resumeTask(task)"
                  size="small"
                  type="primary"
                >
                  <i class="icon-play"></i>
                  继续
                </el-button>
                <el-button
                  v-if="task.status !== 'completed'"
                  @click="cancelTask(task)"
                  size="small"
                  type="danger"
                >
                  <i class="icon-x"></i>
                  取消
                </el-button>
              </div>
            </div>

            <div v-if="exportQueue.length === 0" class="empty-state">
              <i class="icon-inbox"></i>
              <p>暂无排队任务</p>
            </div>
          </div>

          <!-- 已下载文件 -->
          <div v-if="activeHistoryTab === 'downloads'" class="downloads-list">
            <div
              v-for="file in downloadedFiles"
              :key="file.id"
              class="download-item"
            >
              <div class="file-icon">
                <i :class="getFileIcon(file.format)"></i>
              </div>
              <div class="file-details">
                <div class="file-name">{{ file.name }}</div>
                <div class="file-meta">
                  <span class="file-size">{{ file.size }}</span>
                  <span class="file-time">{{ formatTime(file.downloadedAt) }}</span>
                </div>
              </div>
              <div class="file-actions">
                <el-button @click="downloadFileAgain(file)" size="small" type="primary">
                  <i class="icon-download"></i>
                  重新下载
                </el-button>
                <el-button @click="deleteFile(file)" size="small" text type="danger">
                  <i class="icon-trash-2"></i>
                  删除
                </el-button>
              </div>
            </div>

            <div v-if="downloadedFiles.length === 0" class="empty-state">
              <i class="icon-inbox"></i>
              <p>暂无下载文件</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 模板管理模态框 -->
    <el-dialog
      v-model="templateManagerVisible"
      title="导出模板管理"
      width="800px"
      :destroy-on-close="true"
    >
      <div class="template-manager">
        <div class="template-actions">
          <el-button @click="createTemplate" type="primary">
            <i class="icon-plus"></i>
            新建模板
          </el-button>
        </div>

        <div class="template-list">
          <div
            v-for="template in exportTemplates"
            :key="template.id"
            class="template-item"
          >
            <div class="template-icon">
              <i class="icon-save"></i>
            </div>
            <div class="template-content">
              <div class="template-name">{{ template.name }}</div>
              <div class="template-description">{{ template.description }}</div>
              <div class="template-meta">
                <span class="template-type">
                  {{ template.dataType === 'electricity' ? '电耗数据' : '传感器数据' }}
                </span>
                <span class="template-updated">
                  更新于 {{ formatTime(template.updatedAt) }}
                </span>
              </div>
            </div>
            <div class="template-actions">
              <el-button @click="applyTemplate(template)" size="small" type="primary">
                应用模板
              </el-button>
              <el-button @click="editTemplate(template)" size="small">
                编辑
              </el-button>
              <el-button @click="deleteTemplate(template)" size="small" type="danger" text>
                删除
              </el-button>
            </div>
          </div>
        </div>

        <div v-if="exportTemplates.length === 0" class="empty-templates">
          <i class="icon-save"></i>
          <p>暂无保存的模板</p>
        </div>
      </div>
    </el-dialog>

    <!-- 错误处理提示 -->
    <el-dialog
      v-model="errorDialogVisible"
      title="操作失败"
      width="500px"
    >
      <div class="error-content">
        <div class="error-icon">
          <i class="icon-x-circle"></i>
        </div>
        <div class="error-message">
          <h4>{{ errorTitle }}</h4>
          <p>{{ errorMessage }}</p>
          <div v-if="errorDetails" class="error-details">
            <el-collapse>
              <el-collapse-item title="详细信息">
                <pre>{{ errorDetails }}</pre>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="errorDialogVisible = false">关闭</el-button>
        <el-button v-if="errorRetryCallback" @click="handleErrorRetry" type="primary">
          重试
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import EnhancedExportForm from '@/components/enhanced/EnhancedExportForm.vue'
import EnhancedProgressVisualization from '@/components/enhanced/EnhancedProgressVisualization.vue'
import { exportElectricityData, exportSensorData, fetchLineConfigs, getTaskStatus, cancelTask as cancelExportTask } from '@/api/control'

// 接口定义
interface ExportHistory {
  id: string
  dataType: 'electricity' | 'sensor'
  line: string
  time: Date
  status: 'completed' | 'failed' | 'cancelled'
  duration?: number
  fileSize?: string
  filePath?: string
  error?: string
  retryable?: boolean
  partialFiles?: string[]
}

interface ExportTask {
  id: string
  title: string
  status: 'pending' | 'processing' | 'paused' | 'completed' | 'failed'
  progress: number
  createdAt: Date
  estimatedTime?: string
}

interface DownloadedFile {
  id: string
  name: string
  format: string
  size: string
  downloadedAt: Date
  filePath: string
}

interface ExportTemplate {
  id: string
  name: string
  description: string
  dataType: 'electricity' | 'sensor'
  config: any
  createdAt: Date
  updatedAt: Date
}

// 响应式数据
const exportFormRef = ref()
const availableLines = ref<string[]>([])
const exporting = ref(false)
const showProgress = ref(false)
const currentTaskId = ref<string | null>(null)
let pollingTimer: number | null = null

const progressTitle = ref('')
const progress = ref({
  percent: 0,
  current: 0,
  total: 0,
  text: ''
})
const progressStages = ref<any[]>([])
const progressTasks = ref<any[]>([])
const progressMilestones = ref([
  { percent: 25, label: '数据准备' },
  { percent: 50, label: '数据处理' },
  { percent: 75, label: '文件生成' },
  { percent: 100, label: '导出完成' }
])
const progressStartTime = ref(0)

const activeHistoryTab = ref('history')
const exportHistory = ref<ExportHistory[]>([])
const exportQueue = ref<ExportTask[]>([])
const downloadedFiles = ref<DownloadedFile[]>([])
const activeExports = ref(0)

const templateManagerVisible = ref(false)
const exportTemplates = ref<ExportTemplate[]>([])

const errorDialogVisible = ref(false)
const errorTitle = ref('')
const errorMessage = ref('')
const errorDetails = ref('')
const errorRetryCallback = ref<(() => void) | null>(null)

// 计算属性
const totalExports = computed(() => exportHistory.value.length)
const successRate = computed(() => {
  if (exportHistory.value.length === 0) return 0
  const successCount = exportHistory.value.filter(h => h.status === 'completed').length
  return Math.round((successCount / exportHistory.value.length) * 100)
})

const historyTabs = computed(() => [
  {
    key: 'history',
    label: '导出历史',
    icon: 'icon-clock',
    count: exportHistory.value.length
  },
  {
    key: 'queue',
    label: '导出队列',
    icon: 'icon-list',
    count: exportQueue.value.length
  },
  {
    key: 'downloads',
    label: '已下载',
    icon: 'icon-download',
    count: downloadedFiles.value.length
  }
])

// 方法
const initializeApp = async () => {
  try {
    // 加载线路配置
    const configs = await fetchLineConfigs()
    availableLines.value = Object.keys(configs || {}).filter(name => /^M\d+$/.test(name))

    // 加载导出历史
    loadExportHistory()

    // 加载下载文件列表
    loadDownloadedFiles()

    // 加载导出模板
    loadExportTemplates()
  } catch (error) {
    showError('初始化失败', '加载应用数据时发生错误', error.message)
  }
}

const startQuickExport = async (dataType: 'electricity' | 'sensor') => {
  // 快速导出逻辑
  // 使用北京时区(Asia/Shanghai)格式化时间
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
    return `${Y}-${M}-${D} ${h}:${m}:${s}`
  }
  const nowUTC = Date.now()
  const yesterdayUTC = nowUTC - 24 * 60 * 60 * 1000

  const exportData = {
    dataType,
    line: availableLines.value[0] || '',
    startTime: formatShanghai(new Date(yesterdayUTC)),
    endTime: formatShanghai(new Date(nowUTC)),
    format: 'xlsx',
    compress: false,
    includeMetadata: true
  }

  await performExport(exportData)
}

const handleExport = async (data: any) => {
  await performExport(data)
}

const performExport = async (data: any) => {
  exporting.value = true
  progressStartTime.value = Date.now()

  try {
    showProgress.value = true
    progressTitle.value = `正在导出${data.dataType === 'electricity' ? '电耗' : '传感器'}数据`

    // 初始化进度
    progress.value = {
      percent: 0,
      current: 0,
      total: 100,
      text: '准备导出...'
    }

    // 初始化阶段
    progressStages.value = [
      { key: 'prepare', title: '数据准备', description: '获取导出参数', status: 'processing', progress: 0 },
      { key: 'fetch', title: '数据获取', description: '从服务器获取数据', status: 'pending', progress: 0 },
      { key: 'process', title: '数据处理', description: '格式化和处理数据', status: 'pending', progress: 0 },
      { key: 'generate', title: '文件生成', description: '生成导出文件', status: 'pending', progress: 0 }
    ]

    // 启动后端异步导出任务
    const req = {
      line: data.line,
      start_time: data.startTime,
      end_time: data.endTime
    }

    let resp: any
    if (data.dataType === 'electricity') {
      resp = await exportElectricityData(req)
    } else {
      // 传感器导出（如后端支持）
      resp = await exportSensorData(req as any)
    }

    const taskId: string | undefined = resp?.task_id
    if (!taskId) {
      throw new Error('无法获取任务ID，导出未启动')
    }
    currentTaskId.value = taskId
    startTaskPolling(taskId)

  } catch (error) {
    showError('导出失败', error.message, error.stack)
  } finally {
    exporting.value = false
    setTimeout(() => {
      showProgress.value = false
    }, 3000)
  }
}

const simulateExportProcess = async (data: any) => {
  const stages = progressStages.value

  // 阶段1: 数据准备
  await updateStageProgress(0, 100, 2000, '准备导出参数...')
  stages[0].status = 'completed'
  stages[0].progress = 100

  // 阶段2: 数据获取
  stages[1].status = 'processing'
  await updateStageProgress(0, 100, 5000, '正在获取数据...')
  stages[1].status = 'completed'
  stages[1].progress = 100

  // 阶段3: 数据处理
  stages[2].status = 'processing'
  await updateStageProgress(0, 100, 3000, '正在处理数据...')
  stages[2].status = 'completed'
  stages[2].progress = 100

  // 阶段4: 文件生成
  stages[3].status = 'processing'
  await updateStageProgress(0, 100, 2000, '正在生成文件...')
  stages[3].status = 'completed'
  stages[3].progress = 100

  // 完成
  progress.value.percent = 100
  progress.value.text = '导出完成'

  // 添加到历史记录
  addToHistory({
    id: Date.now().toString(),
    dataType: data.dataType,
    line: data.line,
    time: new Date(),
    status: 'completed',
    duration: Date.now() - progressStartTime.value,
    fileSize: '2.5 MB'
  })

  ElMessage.success('数据导出成功')
}

const updateStageProgress = async (start: number, end: number, duration: number, text: string) => {
  const steps = 20
  const stepDuration = duration / steps
  const stepSize = (end - start) / steps

  for (let i = 0; i <= steps; i++) {
    const currentProgress = start + (stepSize * i)
    const overallProgress = Math.round((progressStages.value.filter(s => s.status === 'completed').length * 25) + (currentProgress * 0.25))

    progress.value.percent = overallProgress
    progress.value.current = Math.round(overallProgress)
    progress.value.text = text

    if (progressStages.value.find(s => s.status === 'processing')) {
      progressStages.value.find(s => s.status === 'processing').progress = currentProgress
    }

    await new Promise(resolve => setTimeout(resolve, stepDuration))
  }
}

const handleSaveTemplate = (data: any) => {
  // 保存模板逻辑
  const template: ExportTemplate = {
    id: Date.now().toString(),
    name: `模板_${new Date().toLocaleDateString()}`,
    description: `${data.dataType === 'electricity' ? '电耗' : '传感器'}数据导出模板`,
    dataType: data.dataType,
    config: data,
    createdAt: new Date(),
    updatedAt: new Date()
  }

  exportTemplates.value.unshift(template)
  ElMessage.success('模板保存成功')
}

const openTemplateManager = () => {
  templateManagerVisible.value = true
}

const createTemplate = () => {
  // 创建新模板
  ElMessage.info('创建模板功能开发中')
}

const applyTemplate = (template: ExportTemplate) => {
  // 应用模板到表单
  if (exportFormRef.value) {
    exportFormRef.value.applyTemplate(template.config)
  }
  templateManagerVisible.value = false
  ElMessage.success('模板已应用')
}

const editTemplate = (template: ExportTemplate) => {
  // 编辑模板
  ElMessage.info('编辑模板功能开发中')
}

const deleteTemplate = async (template: ExportTemplate) => {
  try {
    await ElMessageBox.confirm('确定要删除这个模板吗？', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const index = exportTemplates.value.findIndex(t => t.id === template.id)
    if (index > -1) {
      exportTemplates.value.splice(index, 1)
      ElMessage.success('模板已删除')
    }
  } catch {
    // 用户取消
  }
}

const cancelExport = async () => {
  try {
    if (!currentTaskId.value) {
      showProgress.value = false
      ElMessage.info('没有正在运行的任务')
      return
    }
    await cancelExportTask(currentTaskId.value)
    stopPolling()
    ElMessage.success('已请求取消任务')
  } catch (e: any) {
    ElMessage.error(e?.message || '取消任务失败')
  }
}

function startTaskPolling(taskId: string) {
  // 初始化阶段到后端任务
  progressStages.value[0].status = 'completed'
  progressStages.value[1].status = 'processing'
  progress.value.text = '后端任务已启动，正在采集数据...'
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
  pollingTimer = window.setInterval(async () => {
    try {
      const status: any = await getTaskStatus(taskId)
      const pct = Math.max(0, Math.min(100, Math.round(status?.progress ?? 0)))
      progress.value = {
        percent: pct,
        current: pct,
        total: 100,
        text: status?.current_step || `正在处理... ${pct}%`
      }

      // 阶段粗映射
      if (pct >= 10) progressStages.value[1].status = 'completed'
      if (pct >= 40) progressStages.value[2].status = 'processing'
      if (pct >= 70) progressStages.value[2].status = 'completed'
      if (pct >= 80) progressStages.value[3].status = 'processing'
      if (pct >= 95) progressStages.value[3].status = 'completed'

      const terminal = ['completed', 'failed', 'cancelled']
      if (terminal.includes(status?.status)) {
        stopPolling()
        exporting.value = false
        progressStages.value.push({ key: 'finalize', title: '完成', description: '收尾', status: 'completed', progress: 100 })
        handleTaskComplete(status)
      }
    } catch (err: any) {
      stopPolling()
      exporting.value = false
      showError('状态获取失败', err?.message || '任务状态获取失败')
    }
  }, 1500)
}

function stopPolling() {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
}

function handleTaskComplete(status: any) {
  const s = status?.status
  if (s === 'completed') {
    progress.value.text = '导出完成'
    const details = status?.result?.details
    const results = details?.results || []
    const successFiles = results.filter((r: any) => r?.success && r?.file_path)
    successFiles.forEach((r: any) => triggerDownload(r.file_path))
    addToHistory({
      id: Date.now().toString(),
      dataType: 'electricity',
      line: (status?.result?.line || ''),
      time: new Date(),
      status: 'completed',
      duration: Date.now() - progressStartTime.value,
      fileSize: `${successFiles.length} 文件`,
      partialFiles: successFiles.map((r: any) => r.file_path)
    })
    ElMessage.success(`导出成功，成功站点数：${details?.success_count ?? successFiles.length}`)
  } else if (s === 'failed') {
    progress.value.text = '导出失败'
    const details = status?.result?.details
    const results = details?.results || []
    const successFiles = results.filter((r: any) => r?.success && r?.file_path)
    addToHistory({
      id: Date.now().toString(),
      dataType: 'electricity',
      line: '',
      time: new Date(),
      status: 'failed',
      duration: Date.now() - progressStartTime.value,
      error: successFiles.length > 0 ? `部分成功：${successFiles.length} 个文件可下载` : (status?.error || '导出失败'),
      partialFiles: successFiles.map((r: any) => r.file_path)
    })
    if (successFiles.length > 0) {
      ElMessage.warning(`导出部分成功，可下载 ${successFiles.length} 个文件`)
    } else {
      ElMessage.error(status?.error || '导出失败')
    }
  } else if (s === 'cancelled') {
    progress.value.text = '已取消'
    addToHistory({
      id: Date.now().toString(),
      dataType: 'electricity',
      line: '',
      time: new Date(),
      status: 'cancelled',
      duration: Date.now() - progressStartTime.value
    })
    ElMessage.warning('任务已取消')
  }
  setTimeout(() => {
    showProgress.value = false
  }, 1200)
}

function triggerDownload(filename: string) {
  // 仅传文件名以匹配后端下载路由
  const name = (filename || '').toString().split(/[\\\/]/).pop() || ''
  const url = `/api/download/${encodeURIComponent(name)}`
  try {
    const a = document.createElement('a')
    a.href = url
    a.download = name
    a.style.display = 'none'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  } catch {
    window.open(url, '_blank')
  }
}

const pauseExport = () => {
  ElMessage.info('暂停导出功能开发中')
}

const resumeExport = () => {
  ElMessage.info('继续导出功能开发中')
}

const retryTask = (taskId: string) => {
  ElMessage.info(`重试任务 ${taskId}`)
}

const retryFailedTasks = () => {
  ElMessage.info('重试失败任务功能开发中')
}

const exportProgressLog = () => {
  ElMessage.info('导出进度日志功能开发中')
}

const pauseTask = (task: ExportTask) => {
  task.status = 'paused'
  ElMessage.success('任务已暂停')
}

const resumeTask = (task: ExportTask) => {
  task.status = 'processing'
  ElMessage.success('任务已继续')
}

const cancelTask = async (task: ExportTask) => {
  try {
    await ElMessageBox.confirm('确定要取消这个任务吗？', '确认取消', {
      confirmButtonText: '取消',
      cancelButtonText: '关闭',
      type: 'warning'
    })

    const index = exportQueue.value.findIndex(t => t.id === task.id)
    if (index > -1) {
      exportQueue.value.splice(index, 1)
      ElMessage.success('任务已取消')
    }
  } catch {
    // 用户取消
  }
}

const downloadFile = (record: ExportHistory) => {
  // 下载文件逻辑
  ElMessage.success(`开始下载 ${record.dataType} 数据文件`)

  // 添加到下载历史
  const file: DownloadedFile = {
    id: Date.now().toString(),
    name: `${record.dataType}_${record.line}_${new Date().toLocaleDateString()}.xlsx`,
    format: 'xlsx',
    size: record.fileSize || '2.5 MB',
    downloadedAt: new Date(),
    filePath: record.filePath || ''
  }

  downloadedFiles.value.unshift(file)
}

const downloadPartial = (record: ExportHistory) => {
  const files = record.partialFiles || []
  if (!files.length) return
  ElMessage.success(`开始下载成功部分，共 ${files.length} 个文件`)
  files.forEach((fp) => {
    triggerDownload(fp)
    const base = fp.split(/\\|\//).pop() || 'data.xlsx'
    downloadedFiles.value.unshift({
      id: `${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
      name: base,
      format: (base.split('.').pop() || 'xlsx'),
      size: record.fileSize || '',
      downloadedAt: new Date(),
      filePath: fp
    })
  })
}

const retryExport = (record: ExportHistory) => {
  // 重试导出
  ElMessage.info('重试导出功能开发中')
}

const viewHistoryDetails = (record: ExportHistory) => {
  // 查看历史详情
  ElMessage.info('查看历史详情功能开发中')
}

const downloadFileAgain = (file: DownloadedFile) => {
  ElMessage.success(`重新下载 ${file.name}`)
}

const deleteFile = async (file: DownloadedFile) => {
  try {
    await ElMessageBox.confirm('确定要删除这个文件记录吗？', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const index = downloadedFiles.value.findIndex(f => f.id === file.id)
    if (index > -1) {
      downloadedFiles.value.splice(index, 1)
      ElMessage.success('文件记录已删除')
    }
  } catch {
    // 用户取消
  }
}

const showError = (title: string, message: string, details?: string, retryCallback?: () => void) => {
  errorTitle.value = title
  errorMessage.value = message
  errorDetails.value = details
  errorRetryCallback.value = retryCallback || null
  errorDialogVisible.value = true
}

const handleErrorRetry = () => {
  errorDialogVisible.value = false
  if (errorRetryCallback.value) {
    errorRetryCallback.value()
  }
}

// 工具方法
const getHistoryIcon = (status: string) => {
  const icons = {
    completed: 'icon-check-circle',
    failed: 'icon-x-circle',
    cancelled: 'icon-x-square'
  }
  return icons[status] || 'icon-clock'
}

const getQueueIcon = (status: string) => {
  const icons = {
    pending: 'icon-clock',
    processing: 'icon-loader animate-spin',
    paused: 'icon-pause',
    completed: 'icon-check-circle',
    failed: 'icon-x-circle'
  }
  return icons[status] || 'icon-clock'
}

const getFileIcon = (format: string) => {
  const icons = {
    xlsx: 'icon-file-text',
    csv: 'icon-file',
    json: 'icon-code'
  }
  return icons[format] || 'icon-file'
}

const formatTime = (time: Date) => {
  return time.toLocaleString()
}

const formatDuration = (ms: number) => {
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)

  if (hours > 0) return `${hours}小时${minutes % 60}分钟`
  if (minutes > 0) return `${minutes}分钟${seconds % 60}秒`
  return `${seconds}秒`
}

const addToHistory = (record: ExportHistory) => {
  exportHistory.value.unshift(record)
  // 保持最多100条记录
  if (exportHistory.value.length > 100) {
    exportHistory.value = exportHistory.value.slice(0, 100)
  }
}

const loadExportHistory = () => {
  // 从本地存储或API加载历史记录
  const saved = localStorage.getItem('exportHistory')
  if (saved) {
    try {
      exportHistory.value = JSON.parse(saved).map((item: any) => ({
        ...item,
        time: new Date(item.time)
      }))
    } catch (error) {
      console.error('Failed to load export history:', error)
    }
  }
}

const loadDownloadedFiles = () => {
  // 从本地存储加载下载文件列表
  const saved = localStorage.getItem('downloadedFiles')
  if (saved) {
    try {
      downloadedFiles.value = JSON.parse(saved).map((item: any) => ({
        ...item,
        downloadedAt: new Date(item.downloadedAt)
      }))
    } catch (error) {
      console.error('Failed to load downloaded files:', error)
    }
  }
}

const loadExportTemplates = () => {
  // 从本地存储加载导出模板
  const saved = localStorage.getItem('exportTemplates')
  if (saved) {
    try {
      exportTemplates.value = JSON.parse(saved).map((item: any) => ({
        ...item,
        createdAt: new Date(item.createdAt),
        updatedAt: new Date(item.updatedAt)
      }))
    } catch (error) {
      console.error('Failed to load export templates:', error)
    }
  }
}

// 保存数据到本地存储
const saveToLocalStorage = () => {
  localStorage.setItem('exportHistory', JSON.stringify(exportHistory.value))
  localStorage.setItem('downloadedFiles', JSON.stringify(downloadedFiles.value))
  localStorage.setItem('exportTemplates', JSON.stringify(exportTemplates.value))
}

// 生命周期
onMounted(() => {
  initializeApp()

  // 定期保存数据
  const saveInterval = setInterval(saveToLocalStorage, 30000)

  onUnmounted(() => {
    clearInterval(saveInterval)
    saveToLocalStorage()
  })
})
</script>

<style scoped>
.enhanced-data-export {
  min-height: 100vh;
  background: #f5f7fa;
}

/* 页面头部 */
.page-header {
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 32px 0;
  overflow: hidden;
}

.header-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0.1;
}

.header-decoration {
  position: absolute;
  top: -50%;
  right: -10%;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
  border-radius: 50%;
}

.header-content {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
}

.page-title i {
  font-size: 32px;
}

.page-description {
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
}

.header-stats {
  display: flex;
  gap: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
}

.stat-icon i {
  font-size: 20px;
}

.stat-content {
  text-align: left;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  opacity: 0.8;
}

/* 主要内容区域 */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

/* 快速操作区 */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-color: #667eea;
}

.action-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  font-size: 24px;
  color: white;
}

.action-icon.electricity {
  background: linear-gradient(135deg, #ffd700, #ff8c00);
}

.action-icon.sensor {
  background: linear-gradient(135deg, #00bcd4, #009688);
}

.action-icon.template {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.action-content {
  flex: 1;
}

.action-content h3 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px 0;
}

.action-content p {
  font-size: 14px;
  color: #606266;
  margin: 0;
}

.action-arrow {
  color: #c0c4cc;
  font-size: 20px;
  transition: all 0.3s ease;
}

.action-card:hover .action-arrow {
  color: #667eea;
  transform: translateX(4px);
}

/* 导出工作区 */
.export-workspace {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

.workspace-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

/* 进度区域 */
.progress-section {
  margin-bottom: 32px;
}

/* 历史记录区域 */
.history-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.section-tabs {
  display: flex;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 16px 24px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 2px solid transparent;
}

.tab-item:hover {
  background: rgba(102, 126, 234, 0.05);
}

.tab-item.active {
  background: white;
  border-bottom-color: #667eea;
  color: #667eea;
}

.tab-badge {
  background: #667eea;
  color: white;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

.tab-content {
  padding: 24px;
  min-height: 300px;
}

/* 历史记录列表 */
.history-list,
.queue-list,
.downloads-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item,
.queue-item,
.download-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.history-item:hover,
.queue-item:hover,
.download-item:hover {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.02);
}

.history-icon,
.queue-icon,
.file-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-size: 18px;
}

.history-item.completed .history-icon {
  background: #f0f9ff;
  color: #67c23a;
}

.history-item.failed .history-icon {
  background: #fef0f0;
  color: #f56c6c;
}

.history-item.cancelled .history-icon {
  background: #f4f4f5;
  color: #909399;
}

.queue-item.processing .queue-icon {
  background: #f0f9ff;
  color: #409eff;
}

.queue-item.paused .queue-icon {
  background: #fdf6ec;
  color: #e6a23c;
}

.file-icon {
  background: #f0f2f5;
  color: #606266;
}

.history-details,
.queue-details,
.file-details {
  flex: 1;
}

.history-title,
.queue-title,
.file-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.history-meta,
.queue-meta,
.file-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.history-error {
  font-size: 12px;
  color: #f56c6c;
  margin-top: 4px;
}

.queue-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.queue-progress-bar {
  flex: 1;
  height: 4px;
  background: #e4e7ed;
  border-radius: 2px;
  overflow: hidden;
}

.queue-progress-fill {
  height: 100%;
  background: #667eea;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.queue-progress-text {
  font-size: 12px;
  color: #606266;
  min-width: 32px;
}

.history-actions,
.queue-actions,
.file-actions {
  display: flex;
  gap: 8px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #c0c4cc;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state p {
  font-size: 16px;
  margin: 0;
}

/* 模板管理 */
.template-manager {
  max-height: 500px;
  overflow-y: auto;
}

.template-actions {
  margin-bottom: 20px;
}

.template-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.template-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.template-item:hover {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.02);
}

.template-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
  color: #606266;
  border-radius: 8px;
  font-size: 18px;
}

.template-content {
  flex: 1;
}

.template-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.template-description {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.template-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.template-actions {
  display: flex;
  gap: 8px;
}

.empty-templates {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #c0c4cc;
}

.empty-templates i {
  font-size: 48px;
  margin-bottom: 16px;
}

/* 错误对话框 */
.error-content {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.error-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fef0f0;
  color: #f56c6c;
  border-radius: 50%;
  font-size: 24px;
  flex-shrink: 0;
}

.error-message h4 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.error-message p {
  color: #606266;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.error-details pre {
  font-size: 12px;
  color: #909399;
  background: #f8f9fa;
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 24px;
    align-items: stretch;
  }

  .header-stats {
    justify-content: space-around;
  }

  .quick-actions {
    grid-template-columns: 1fr;
  }

  .main-content {
    padding: 16px;
  }

  .section-tabs {
    flex-direction: column;
  }

  .tab-item {
    justify-content: center;
  }

  .history-item,
  .queue-item,
  .download-item {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .history-actions,
  .queue-actions,
  .file-actions {
    justify-content: flex-end;
  }
}

/* 动画效果 */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>