<template>
  <div class="data-export-page">
    <!-- 主要内容区域 -->
    <div class="export-container">
      <!-- 左侧：导出配置面板 -->
      <div class="export-config-panel">
        <el-scrollbar height="calc(100vh - 120px)">
          <el-card class="config-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><Setting /></el-icon>
              <span class="header-title">导出配置</span>
            </div>
          </template>

          <!-- 数据类型选择 -->
          <div class="form-section">
            <label class="section-label">数据类型</label>
            <el-radio-group v-model="exportConfig.dataType" class="data-type-selector">
              <el-radio-button value="electricity" class="type-option electricity">
                <el-icon><Lightning /></el-icon>
                <span>电耗数据</span>
              </el-radio-button>
              <el-radio-button value="sensor" class="type-option sensor">
                <el-icon><Monitor /></el-icon>
                <span>传感器数据</span>
              </el-radio-button>
            </el-radio-group>
          </div>

          <!-- 线路选择 -->
          <div class="form-section">
            <label class="section-label">选择线路</label>
            <el-select 
              v-model="exportConfig.line" 
              placeholder="请选择线路"
              class="line-selector"
              size="large"
              filterable
            >
              <el-option
                v-for="line in availableLines"
                :key="line"
                :label="line"
                :value="line"
                class="line-option"
              >
                <div class="line-option-content">
                  <span class="line-name">{{ line }}</span>
                  <span class="line-status">在线</span>
                </div>
              </el-option>
            </el-select>
          </div>

          <!-- 时间范围选择 -->
          <div class="form-section">
            <label class="section-label">时间范围</label>
            <div class="time-range-container">
              <div class="quick-time-buttons">
                <el-button 
                  v-for="preset in timePresets" 
                  :key="preset.key"
                  @click="setTimePreset(preset)"
                  size="small"
                  :type="selectedPreset === preset.key ? 'primary' : 'default'"
                  class="preset-btn"
                >
                  {{ preset.label }}
                </el-button>
              </div>
              <div class="custom-time-range">
                <el-date-picker
                  v-model="exportConfig.startTime"
                  type="datetime"
                  placeholder="开始时间"
                  format="YYYY-MM-DD HH:mm:ss"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  class="time-picker"
                />
                <el-date-picker
                  v-model="exportConfig.endTime"
                  type="datetime"
                  placeholder="结束时间"
                  format="YYYY-MM-DD HH:mm:ss"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  class="time-picker"
                />
              </div>
            </div>
          </div>

          <!-- 导出选项 -->
          <div class="form-section">
            <label class="section-label">导出选项</label>
            <div class="export-options">
              <div class="option-row">
                <label class="option-label">导出格式</label>
                <el-select v-model="exportConfig.format" class="format-selector">
                  <el-option label="Excel (.xlsx)" value="xlsx">
                    <el-icon><Document /></el-icon>
                    Excel (.xlsx)
                  </el-option>
                  <el-option label="CSV (.csv)" value="csv">
                    <el-icon><Document /></el-icon>
                    CSV (.csv)
                  </el-option>
                  <el-option label="JSON (.json)" value="json">
                    <el-icon><Document /></el-icon>
                    JSON (.json)
                  </el-option>
                </el-select>
              </div>
              <div class="option-row">
                <el-checkbox v-model="exportConfig.compress" class="compress-option">
                  <el-icon><FolderOpened /></el-icon>
                  压缩文件（推荐大文件使用）
                </el-checkbox>
              </div>
              <div class="option-row">
                <el-checkbox v-model="exportConfig.includeMetadata" class="metadata-option">
                  <el-icon><InfoFilled /></el-icon>
                  包含元数据信息
                </el-checkbox>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <el-button 
              type="success" 
              size="large"
              :disabled="!isConfigValid"
              @click="handleExport"
              :loading="exporting"
              class="export-btn"
            >
              <el-icon><Download /></el-icon>
              开始导出
            </el-button>
          </div>
        </el-card>
        </el-scrollbar>
      </div>

      <!-- 右侧：状态和结果面板 -->
      <div class="export-status-panel">
        <!-- 导出进度卡片 -->
        <el-card v-if="exportProgress.show" class="progress-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><Loading /></el-icon>
              <span class="header-title">导出进度</span>
              <el-button 
                type="danger" 
                size="small" 
                @click="cancelExport"
                class="cancel-btn"
              >
                取消
              </el-button>
            </div>
          </template>
          
          <div class="progress-content">
            <div class="progress-info">
              <div class="progress-text">{{ exportProgress.text }}</div>
              <div class="progress-stats">
                {{ exportProgress.current }} / {{ exportProgress.total }}
              </div>
            </div>
            <el-progress 
              :percentage="exportProgress.percent" 
              :status="exportProgress.percent === 100 ? 'success' : 'primary'"
              :stroke-width="8"
              class="progress-bar"
            />
          <div class="progress-details">
            <span>预计剩余时间: {{ estimatedTime }}</span>
            <span>{{ exportProgress.percent }}%</span>
          </div>

          <!-- 部分成功下载入口 -->
          <div class="partial-download" v-if="hasPartialSuccess && exportProgress.percent === 100">
            <el-alert type="warning" :closable="false" show-icon class="partial-alert">
              <template #title>
                部分成功：已成功 {{ partialFiles.length }} 个站点，失败 {{ failedStations.length }} 个
              </template>
            </el-alert>
            <div class="partial-actions">
              <el-button type="primary" @click="downloadPartial">下载成功部分</el-button>
              <el-button @click="showFailureDialog = true">查看失败详情</el-button>
            </div>
          </div>
        </div>
      </el-card>

        <!-- 导出历史卡片 -->
        <el-card class="history-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><Clock /></el-icon>
              <span class="header-title">导出历史</span>
              <el-button 
                type="text" 
                size="small" 
                @click="clearHistory"
                class="clear-btn"
              >
                清空
              </el-button>
            </div>
          </template>
          
          <div class="history-content">
            <div v-if="exportHistory.length === 0" class="empty-history">
              <el-icon><DocumentRemove /></el-icon>
              <span>暂无导出记录</span>
            </div>
            <div v-else class="history-list">
              <div 
                v-for="record in exportHistory.slice(0, 5)" 
                :key="record.id"
                class="history-item"
                :class="{ success: record.success, failed: !record.success }"
              >
                <div class="history-icon">
                  <el-icon v-if="record.success"><SuccessFilled /></el-icon>
                  <el-icon v-else><CircleCloseFilled /></el-icon>
                </div>
                <div class="history-details">
                  <div class="history-title">
                    {{ record.dataType === 'electricity' ? '电耗数据' : '传感器数据' }} - {{ record.line }}
                  </div>
                  <div class="history-meta">
                    <span class="history-time">{{ formatTime(record.time) }}</span>
                    <span class="history-status">{{ record.success ? '成功' : '失败' }}</span>
                  </div>
                </div>
                <div class="history-actions">
                  <el-button 
                    v-if="record.success && record.filePath" 
                    type="text" 
                    size="small"
                    @click="downloadFile(record.filePath)"
                  >
                    下载
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 底部：操作日志 -->
    <div class="export-logs-section">
      <el-card class="logs-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon class="header-icon"><ChatLineRound /></el-icon>
            <span class="header-title">操作日志</span>
            <div class="log-actions">
              <el-button type="text" size="small" @click="clearLogs">清空日志</el-button>
              <el-button type="text" size="small" @click="exportLogsToFile">导出日志</el-button>
            </div>
          </div>
        </template>
        
        <div class="logs-content">
          <div v-if="exportLogs.length === 0" class="empty-logs">
            <el-icon><ChatLineRound /></el-icon>
            <span>暂无操作日志</span>
          </div>
          <div v-else class="logs-list" ref="logsContainer">
            <div 
              v-for="log in exportLogs" 
              :key="log.id"
              class="log-item"
              :class="log.type"
            >
              <div class="log-time">{{ log.time }}</div>
              <div class="log-icon">
                <el-icon v-if="log.type === 'success'"><SuccessFilled /></el-icon>
                <el-icon v-else-if="log.type === 'error'"><CircleCloseFilled /></el-icon>
                <el-icon v-else-if="log.type === 'warning'"><WarningFilled /></el-icon>
                <el-icon v-else><InfoFilled /></el-icon>
              </div>
              <div class="log-message">{{ log.message }}</div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 失败详情弹窗 -->
    <el-dialog v-model="showFailureDialog" title="失败详情" width="600px">
      <div v-if="failedStations.length === 0" class="empty-logs">
        <el-icon><InfoFilled /></el-icon>
        <span>无失败记录</span>
      </div>
      <div v-else class="failed-list">
        <div class="log-item error" v-for="item in failedStations" :key="item.station_ip + item.message">
          <div class="log-time">{{ item.station_name }} ({{ item.station_ip }})</div>
          <div class="log-message">{{ item.message }}</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showFailureDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Download, Lightning, Monitor, Setting, View, Loading, Clock, 
  Document, FolderOpened, InfoFilled, SuccessFilled, CircleCloseFilled,
  WarningFilled, ChatLineRound, DocumentRemove
} from '@element-plus/icons-vue'
import { http, exportElectricityData, exportSensorData, fetchLineConfigs, getTaskStatus, cancelTask } from '../api/control'

// 导出配置
const exportConfig = ref({
  dataType: 'electricity',
  line: '',
  startTime: '',
  endTime: '',
  format: 'xlsx',
  compress: false,
  includeMetadata: true
})

// 时间预设选项
const timePresets = [
  { key: 'last1h', label: '最近1小时', hours: 1 },
  { key: 'last6h', label: '最近6小时', hours: 6 },
  { key: 'last24h', label: '最近24小时', hours: 24 },
  { key: 'last7d', label: '最近7天', hours: 24 * 7 }
]

const selectedPreset = ref('')

// 线路配置
const lineConfigs = ref({})
const availableLines = computed(() => {
  const lineNames = Object.keys(lineConfigs.value || {})
  return lineNames.filter(name => /^M\d+$/.test(name))
})

// 导出状态
const exporting = ref(false)
const exportProgress = ref({
  show: false,
  percent: 0,
  current: 0,
  total: 0,
  text: ''
})

// 部分成功与失败详情
const partialFiles = ref([])
const failedStations = ref([])
const showFailureDialog = ref(false)
const hasPartialSuccess = computed(() => failedStations.value.length > 0 && partialFiles.value.length > 0)

// 已下载文件去重集合（非响应式）
const downloadedFiles = new Set()
const downloadingFiles = new Set()

// 异步任务状态
const currentTaskId = ref('')
const taskPollingInterval = ref(null)

// 导出历史
const exportHistory = ref([])
const totalExports = computed(() => exportHistory.value.length)
const successRate = computed(() => {
  if (exportHistory.value.length === 0) return 0
  const successCount = exportHistory.value.filter(h => h.success).length
  return Math.round((successCount / exportHistory.value.length) * 100)
})

// 操作日志
const exportLogs = ref([])
const logsContainer = ref()

// 表单验证
const isConfigValid = computed(() => {
  return exportConfig.value.line && 
         exportConfig.value.startTime && 
         exportConfig.value.endTime &&
         new Date(exportConfig.value.endTime) > new Date(exportConfig.value.startTime)
})

// 预计剩余时间
const estimatedTime = computed(() => {
  if (!exportProgress.value.show || exportProgress.value.percent === 0) return '--'
  const elapsed = Date.now() - exportProgress.value.startTime
  const remaining = (elapsed / exportProgress.value.percent) * (100 - exportProgress.value.percent)
  return formatDuration(remaining)
})

// 设置时间预设
function setTimePreset(preset) {
  selectedPreset.value = preset.key
  // 使用北京时区(Asia/Shanghai)计算并格式化时间
  const formatShanghai = (d) => {
    const parts = new Intl.DateTimeFormat('zh-CN', {
      timeZone: 'Asia/Shanghai',
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit',
      hour12: false
    }).formatToParts(d)
    const get = (type) => parts.find(p => p.type === type)?.value || ''
    const Y = get('year')
    const M = get('month')
    const D = get('day')
    const h = get('hour')
    const m = get('minute')
    const s = get('second')
    return `${Y}-${M}-${D} ${h}:${m}:${s}`
  }

  const nowUTC = Date.now()
  const startUTC = nowUTC - preset.hours * 60 * 60 * 1000
  exportConfig.value.endTime = formatShanghai(new Date(nowUTC))
  exportConfig.value.startTime = formatShanghai(new Date(startUTC))
}

// 开始导出
async function handleExport() {
  if (!isConfigValid.value) {
    ElMessage.warning('请完善导出配置')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确认导出${exportConfig.value.dataType === 'electricity' ? '电耗' : '传感器'}数据？`,
      '确认导出',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
  } catch {
    return
  }
  
  exporting.value = true
  exportProgress.value = {
    show: true,
    percent: 0,
    current: 0,
    total: 0,
    text: '准备导出...',
    startTime: Date.now()
  }
  // 重置部分成功与失败详情
  partialFiles.value = []
  failedStations.value = []
  showFailureDialog.value = false
  downloadedFiles.clear()
  downloadingFiles.clear()
  
  const params = {
    line: exportConfig.value.line,
    start_time: exportConfig.value.startTime,
    end_time: exportConfig.value.endTime,
    format: exportConfig.value.format,
    compress: exportConfig.value.compress
  }
  
  addLog(`🚀 开始导出${exportConfig.value.dataType === 'electricity' ? '电耗' : '传感器'}数据: 线路=${params.line}, 时间=${params.start_time} 至 ${params.end_time}`, 'info')
  
  try {
    let result
    if (exportConfig.value.dataType === 'electricity') {
      result = await exportElectricityData(params)
    } else {
      result = await exportSensorData(params)
    }
    
    if (result.success && result.task_id) {
      // 异步任务模式
      currentTaskId.value = result.task_id
      addLog(`📋 导出任务已启动，任务ID: ${result.task_id}`, 'info')
      addLog(`⏳ 正在后台处理，请稍候...`, 'info')
      
      // 开始轮询任务状态
      startTaskPolling()
    } else if (result.success) {
      // 同步模式（向后兼容）
      exportProgress.value.percent = 100
      exportProgress.value.text = '导出完成'
      
      addLog(`✅ ${exportConfig.value.dataType === 'electricity' ? '电耗' : '传感器'}数据导出成功: ${result.message}`, 'success')
      ElMessage.success('数据导出成功')
      
      // 添加到导出历史
      addToHistory(true, result.file_path)
      
      // 处理详细结果
      if (result.details && result.details.results) {
        result.details.results.forEach(station => {
          if (station.success) {
            addLog(`✓ ${station.station_name} (${station.station_ip}): 导出成功`, 'success')
            if (station.file_path) {
              addLog(`└─ 文件: ${station.file_path}`, 'info')
            }
          } else {
            addLog(`❌ ${station.station_name} (${station.station_ip}): ${station.message}`, 'error')
          }
        })
      }
      
      exporting.value = false
      setTimeout(() => {
        exportProgress.value.show = false
      }, 3000)
    } else {
      addLog(`❌ ${exportConfig.value.dataType === 'electricity' ? '电耗' : '传感器'}数据导出失败: ${result.message}`, 'error')
      ElMessage.error(`导出失败: ${result.message}`)
      addToHistory(false)
      exporting.value = false
      exportProgress.value.show = false
    }
  } catch (error) {
    addLog(`❌ 导出请求失败: ${error.message}`, 'error')
    ElMessage.error(`导出请求失败: ${error.message}`)
    addToHistory(false)
    exporting.value = false
    exportProgress.value.show = false
  }
}

// 开始任务状态轮询
function startTaskPolling() {
  if (taskPollingInterval.value) {
    clearInterval(taskPollingInterval.value)
  }
  
  taskPollingInterval.value = setInterval(async () => {
    try {
      const taskStatus = await getTaskStatus(currentTaskId.value)
      // 兜底：若后端已返回结果但状态仍为 running，按完成处理
      if (taskStatus && taskStatus.status === 'running' && taskStatus.result && taskStatus.result.details) {
        addLog('⚠️ 检测到结果已生成但状态未切换，按完成处理', 'warning')
        stopTaskPolling()
        handleTaskComplete({ ...taskStatus, status: 'completed' })
        return
      }

      // 增量下载：在运行过程中，下载新成功的站点文件
      if (taskStatus && taskStatus.result && taskStatus.result.details && Array.isArray(taskStatus.result.details.results)) {
        const newlySucceeded = taskStatus.result.details.results
          .filter(s => s.success && s.file_path)
          .map(s => s.file_path)
          .filter(fp => fp)

        for (const fp of newlySucceeded) {
          await triggerDownload(fp)
        }
      }
      updateTaskProgress(taskStatus)
      
      // 兜底2：若进度已经达到100%，但状态仍为running，则视为已完成
      if (taskStatus && taskStatus.status === 'running') {
        const pct = Number(taskStatus.progress) || 0
        const stepsOk = (Number(taskStatus.total_steps) > 0) && (Number(taskStatus.completed_steps) >= Number(taskStatus.total_steps))
        if (pct >= 100 || stepsOk) {
          addLog('⚠️ 检测到进度为100%但状态为running，按完成处理', 'warning')
          stopTaskPolling()
          handleTaskComplete({ ...taskStatus, status: 'completed' })
          return
        }
      }
      
      // 任务完成或失败时停止轮询
      if (['completed', 'failed', 'cancelled'].includes(taskStatus.status)) {
        stopTaskPolling()
        handleTaskComplete(taskStatus)
      }
    } catch (error) {
      addLog(`❌ 获取任务状态失败: ${error.message}`, 'error')
      // 继续轮询，可能是临时网络问题
    }
  }, 2000) // 每2秒查询一次
}

// 停止任务状态轮询
function stopTaskPolling() {
  if (taskPollingInterval.value) {
    clearInterval(taskPollingInterval.value)
    taskPollingInterval.value = null
  }
}

// 更新任务进度
function updateTaskProgress(taskStatus) {
  exportProgress.value.percent = taskStatus.progress
  exportProgress.value.text = taskStatus.current_step
  exportProgress.value.current = taskStatus.completed_steps
  exportProgress.value.total = taskStatus.total_steps
  
  // 更新日志
  if (taskStatus.progress > 0) {
    addLog(`📊 导出进度: ${taskStatus.progress}% (${taskStatus.completed_steps}/${taskStatus.total_steps}) - ${taskStatus.current_step}`, 'info')
  }
}

// 处理任务完成
function handleTaskComplete(taskStatus) {
  exporting.value = false
  
  if (taskStatus.status === 'completed') {
    exportProgress.value.percent = 100
    exportProgress.value.text = '导出完成'
    
    addLog(`✅ ${exportConfig.value.dataType === 'electricity' ? '电耗' : '传感器'}数据导出成功`, 'success')
    ElMessage.success('数据导出成功')
    
    // 处理导出结果
    if (taskStatus.result && taskStatus.result.details) {
      const details = taskStatus.result.details
      const total = details.total ?? details.total_count
      addLog(`📈 导出统计: 总计 ${total} 个站点，成功 ${details.success_count} 个，失败 ${details.fail_count} 个`, 'info')
      
      // 添加到导出历史
      addToHistory(true, taskStatus.result.file_path)
      
      // 显示详细结果
      if (details.results) {
        // 收集成功与失败项
        const successes = details.results.filter(s => s.success && s.file_path)
        const failures = details.results.filter(s => !s.success)
        partialFiles.value = successes.map(s => s.file_path)
        failedStations.value = failures.map(s => ({ station_name: s.station_name, station_ip: s.station_ip, message: s.message }))

        for (const station of details.results) {
          if (station.success) {
            addLog(`✓ ${station.station_name} (${station.station_ip}): 导出成功`, 'success')
            if (station.file_path) {
              addLog(`└─ 文件: ${station.file_path}`, 'info')
              // 完成阶段确保所有成功文件已下载
              await triggerDownload(station.file_path)
            }
          } else {
            addLog(`❌ ${station.station_name} (${station.station_ip}): ${station.message}`, 'error')
          }
        }
      }
    } else {
      addToHistory(true)
    }
  } else if (taskStatus.status === 'failed') {
    addLog(`❌ 导出任务失败: ${taskStatus.error || '未知错误'}`, 'error')
    ElMessage.error(`导出失败: ${taskStatus.error || '未知错误'}`)
    addToHistory(false)
  } else if (taskStatus.status === 'cancelled') {
    addLog(`🚫 导出任务已取消`, 'warning')
    ElMessage.warning('导出任务已取消')
    addToHistory(false)
  }
  
  // 清理状态
  currentTaskId.value = ''
  setTimeout(() => {
    exportProgress.value.show = false
  }, 3000)
  downloadedFiles.clear()
  downloadingFiles.clear()
}

// 触发浏览器下载
async function triggerDownload(filename, options = {}) {
  const key = (filename || '').toString()
  const name = key.split(/[\\\/]/).pop()
  const force = Boolean(options.force)

  if (!name) {
    addLog('❌ 下载失败: 文件名无效', 'error')
    return false
  }

  if (!force && downloadedFiles.has(name)) {
    addLog(`⏭️ 已下载过，跳过: ${name}`, 'info')
    return true
  }

  if (!force && downloadingFiles.has(name)) {
    addLog(`⏳ 正在下载中，跳过重复请求: ${name}`, 'info')
    return false
  }

  if (!force) {
    downloadingFiles.add(name)
  }

  try {
    const url = `/api/download/${encodeURIComponent(name)}`
    addLog(`📥 正在下载: ${name}`, 'info')

    // 使用 axios 获取文件 blob
    const response = await http.get(url, {
      responseType: 'blob',
      timeout: 60000 // 60秒超时
    })

    // 创建 blob URL
    const blob = new Blob([response.data])
    const blobUrl = URL.createObjectURL(blob)

    // 创建下载链接并触发下载
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = name
    document.body.appendChild(link)
    link.click()

    // 清理
    document.body.removeChild(link)
    URL.revokeObjectURL(blobUrl)

    addLog(`✅ 下载成功: ${name}`, 'success')
    downloadedFiles.add(name)
    return true
  } catch (e) {
    addLog(`❌ 下载失败: ${name} - ${e?.message || e}`, 'error')
    ElMessage.error(`下载失败: ${name}`)
    downloadedFiles.delete(name)
    return false
  } finally {
    downloadingFiles.delete(name)
  }
}

// 取消导出
async function cancelExport() {
  if (currentTaskId.value) {
    try {
      await cancelTask(currentTaskId.value)
      addLog('🚫 正在取消导出任务...', 'warning')
    } catch (error) {
      addLog(`❌ 取消任务失败: ${error.message}`, 'error')
      ElMessage.error('取消任务失败')
    }
  } else {
    // 直接取消本地状态
    exporting.value = false
    exportProgress.value.show = false
    addLog('🚫 用户取消了导出操作', 'warning')
    ElMessage.warning('导出操作已取消')
  }
}

// 添加到导出历史
function addToHistory(success, filePath = null) {
  const record = {
    id: Date.now(),
    dataType: exportConfig.value.dataType,
    line: exportConfig.value.line,
    time: new Date(),
    success,
    filePath
  }
  exportHistory.value.unshift(record)
  
  // 保持最多50条记录
  if (exportHistory.value.length > 50) {
    exportHistory.value = exportHistory.value.slice(0, 50)
  }
}

// 添加日志
function addLog(message, type = 'info') {
  const log = {
    id: Date.now() + Math.random(),
    time: new Date().toLocaleTimeString(),
    message,
    type
  }
  exportLogs.value.push(log)
  
  // 保持最多100条日志
  if (exportLogs.value.length > 100) {
    exportLogs.value = exportLogs.value.slice(-100)
  }
  
  // 自动滚动到底部
  nextTick(() => {
    if (logsContainer.value) {
      logsContainer.value.scrollTop = logsContainer.value.scrollHeight
    }
  })
}

// 清空历史
function clearHistory() {
  exportHistory.value = []
  ElMessage.success('导出历史已清空')
}

// 清空日志
function clearLogs() {
  exportLogs.value = []
  ElMessage.success('操作日志已清空')
}

// 导出日志
function exportLogsToFile() {
  const logText = exportLogs.value.map(log => `[${log.time}] ${log.message}`).join('\n')
  const blob = new Blob([logText], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `export_logs_${new Date().toISOString().slice(0, 10)}.txt`
  a.click()
  URL.revokeObjectURL(url)
}

// 下载文件
function downloadFile(filePath) {
  addLog(`开始下载文件: ${filePath}`, 'info')
  triggerDownload(filePath, { force: true })
}

// 下载成功部分
async function downloadPartial() {
  if (!partialFiles.value.length) {
    ElMessage.warning('无可下载的成功文件')
    return
  }
  addLog(`批量下载成功部分，共 ${partialFiles.value.length} 个文件`, 'info')
  for (const file of partialFiles.value) {
    await triggerDownload(file, { force: true })
    await new Promise(r => setTimeout(r, 300))
  }
}

// 格式化时间
function formatTime(time) {
  return time.toLocaleString()
}

// 格式化持续时间
function formatDuration(ms) {
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  
  if (hours > 0) return `${hours}小时${minutes % 60}分钟`
  if (minutes > 0) return `${minutes}分钟${seconds % 60}秒`
  return `${seconds}秒`
}

// 生成模拟数据
function generateMockData(dataType, count) {
  const data = []
  const now = new Date()
  
  for (let i = 0; i < count; i++) {
    const timestamp = new Date(now.getTime() - i * 60000).toISOString().slice(0, 19).replace('T', ' ')
    
    if (dataType === 'electricity') {
      data.push({
        timestamp,
        station_name: `车站${i + 1}`,
        power: (Math.random() * 1000).toFixed(2),
        energy: (Math.random() * 5000).toFixed(2),
        voltage: (220 + Math.random() * 20).toFixed(1),
        current: (Math.random() * 100).toFixed(2)
      })
    } else {
      data.push({
        timestamp,
        station_name: `车站${i + 1}`,
        sensor_type: ['温度', '湿度', '压力'][i % 3],
        value: (Math.random() * 100).toFixed(2),
        unit: ['°C', '%', 'Pa'][i % 3],
        status: ['正常', '异常'][Math.floor(Math.random() * 2)]
      })
    }
  }
  
  return data
}

// 初始化
onMounted(async () => {
  try {
    const configs = await fetchLineConfigs()
    lineConfigs.value = configs || {}
    
    // 设置默认线路
    const firstLine = Object.keys(lineConfigs.value)[0]
    if (firstLine) {
      exportConfig.value.line = firstLine
    }
    
    addLog('线路配置加载完成', 'success')
  } catch (error) {
    addLog(`线路配置加载失败: ${error.message}`, 'error')
  }
})

// 监听自定义时间变化，清除预设选择
watch([() => exportConfig.value.startTime, () => exportConfig.value.endTime], () => {
  selectedPreset.value = ''
})

// 组件卸载时清理
onUnmounted(() => {
  stopTaskPolling()
})
</script>

<style scoped>
.data-export-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

/* 页面头部 */
.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.header-left {
  flex: 1;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.title-icon {
  font-size: 32px;
  color: #409eff;
}

.page-description {
  margin: 0;
  color: #909399;
  font-size: 16px;
}

.header-stats {
  display: flex;
  gap: 24px;
}

.stat-card {
  text-align: center;
  padding: 16px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
  min-width: 120px;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

/* 主要内容区域 */
.export-container {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

/* 配置面板 */
.config-card {
  height: fit-content;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.header-icon {
  color: #409eff;
}

.form-section {
  margin-bottom: 24px;
}

.section-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #303133;
}

/* 数据类型选择器 */
.data-type-selector {
  width: 100%;
}

.data-type-selector .el-radio-button {
  flex: 1;
}

.type-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
}

.electricity.is-active {
  background: linear-gradient(135deg, #ffd700, #ff8c00);
}

.sensor.is-active {
  background: linear-gradient(135deg, #00bcd4, #009688);
}

/* 线路选择器 */
.line-selector {
  width: 100%;
}

.line-option-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.line-status {
  color: #67c23a;
  font-size: 12px;
}

/* 时间范围 */
.time-range-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quick-time-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.preset-btn {
  flex: 1;
  min-width: 80px;
}

.custom-time-range {
  display: flex;
  gap: 12px;
}

.time-picker {
  flex: 1;
}

/* 导出选项 */
.export-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.option-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.option-label {
  min-width: 80px;
  font-weight: 500;
}

.format-selector {
  flex: 1;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.export-btn {
  flex: 1;
  height: 48px;
  font-weight: 600;
  background: linear-gradient(135deg, #67c23a, #85ce61);
  border: none;
}

.export-btn:hover {
  background: linear-gradient(135deg, #85ce61, #67c23a);
}

/* 状态面板 */
.export-status-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 进度卡片 */
.progress-card {
  border-left: 4px solid #409eff;
}

.progress-content {
  padding: 16px 0;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-text {
  font-weight: 600;
  color: #303133;
}

.progress-stats {
  color: #909399;
  font-size: 14px;
}

.progress-bar {
  margin-bottom: 8px;
}

.progress-details {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}

.partial-download {
  margin-top: 12px;
}
.partial-actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}

/* 历史卡片 */
.history-card {
  border-left: 4px solid #e6a23c;
}

.empty-history {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 40px;
  color: #c0c4cc;
}

.history-list {
  max-height: 300px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.history-item:hover {
  background: #f8f9fa;
}

.history-item.success .history-icon {
  color: #67c23a;
}

.history-item.failed .history-icon {
  color: #f56c6c;
}

.history-details {
  flex: 1;
}

.history-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.history-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

/* 日志区域 */
.export-logs-section {
  margin-top: 24px;
}

.logs-card {
  border-left: 4px solid #909399;
}

.log-actions {
  display: flex;
  gap: 8px;
}

.empty-logs {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 40px;
  color: #c0c4cc;
}

.logs-list {
  max-height: 300px;
  overflow-y: auto;
  padding: 8px 0;
}

.log-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 4px;
  font-size: 14px;
  line-height: 1.4;
}

.log-item.success {
  background: #f0f9ff;
  color: #67c23a;
}

.log-item.error {
  background: #fef0f0;
  color: #f56c6c;
}

.log-item.warning {
  background: #fdf6ec;
  color: #e6a23c;
}

.log-item.info {
  background: #f4f4f5;
  color: #909399;
}

.log-time {
  font-size: 12px;
  color: #c0c4cc;
  min-width: 80px;
}

.log-icon {
  margin-top: 2px;
}

.log-message {
  flex: 1;
  word-break: break-all;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .export-container {
    grid-template-columns: 1fr;
  }
  
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .header-stats {
    align-self: stretch;
    justify-content: space-around;
  }
}

@media (max-width: 768px) {
  .data-export-page {
    padding: 12px;
  }
  
  .custom-time-range {
    flex-direction: column;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .quick-time-buttons {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 动画效果 */
.el-card {
  transition: all 0.3s ease;
}

.el-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.log-item {
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>