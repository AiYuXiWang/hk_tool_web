import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface ExportTask {
  id: string
  name: string
  type: 'energy' | 'device' | 'log' | 'report'
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  startTime: Date
  endTime?: Date
  fileSize?: number
  downloadUrl?: string
  error?: string
  config: ExportConfig
}

export interface ExportConfig {
  format: 'csv' | 'excel' | 'pdf' | 'json'
  dateRange: {
    start: Date
    end: Date
  }
  devices?: string[]
  dataTypes?: string[]
  includeHeaders?: boolean
  compression?: boolean
  filters?: Record<string, any>
}

export interface ExportLog {
  id: string
  taskId: string
  timestamp: Date
  level: 'info' | 'warning' | 'error'
  message: string
  details?: any
}

export interface ExportTemplate {
  id: string
  name: string
  description: string
  type: 'energy' | 'device' | 'log' | 'report'
  config: ExportConfig
  isDefault: boolean
  createdAt: Date
  updatedAt: Date
}

export const useExportStore = defineStore('export', () => {
  // 状态定义
  const tasks = ref<ExportTask[]>([])
  const logs = ref<ExportLog[]>([])
  const templates = ref<ExportTemplate[]>([])
  const currentTask = ref<ExportTask | null>(null)
  const isExporting = ref(false)
  const error = ref<string | null>(null)
  const lastUpdateTime = ref<Date | null>(null)

  // 计算属性
  const activeTasks = computed(() => 
    tasks.value.filter(task => task.status === 'running' || task.status === 'pending')
  )

  const completedTasks = computed(() => 
    tasks.value.filter(task => task.status === 'completed')
  )

  const failedTasks = computed(() => 
    tasks.value.filter(task => task.status === 'failed')
  )

  const taskStats = computed(() => ({
    total: tasks.value.length,
    pending: tasks.value.filter(t => t.status === 'pending').length,
    running: tasks.value.filter(t => t.status === 'running').length,
    completed: completedTasks.value.length,
    failed: failedTasks.value.length,
    cancelled: tasks.value.filter(t => t.status === 'cancelled').length
  }))

  const recentLogs = computed(() => 
    logs.value
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, 100)
  )

  const errorLogs = computed(() => 
    logs.value.filter(log => log.level === 'error')
  )

  const downloadableFiles = computed(() => 
    completedTasks.value.filter(task => task.downloadUrl)
  )

  const totalExportedSize = computed(() => 
    completedTasks.value.reduce((sum, task) => sum + (task.fileSize || 0), 0)
  )

  // Actions
  const setError = (errorMessage: string | null) => {
    error.value = errorMessage
  }

  const setCurrentTask = (task: ExportTask | null) => {
    currentTask.value = task
  }

  const addTask = (config: ExportConfig, name: string, type: ExportTask['type']) => {
    const task: ExportTask = {
      id: `task-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name,
      type,
      status: 'pending',
      progress: 0,
      startTime: new Date(),
      config
    }
    
    tasks.value.unshift(task)
    return task
  }

  const updateTaskStatus = (taskId: string, status: ExportTask['status']) => {
    const task = tasks.value.find(t => t.id === taskId)
    if (task) {
      task.status = status
      if (status === 'completed' || status === 'failed' || status === 'cancelled') {
        task.endTime = new Date()
        if (task === currentTask.value) {
          currentTask.value = null
          isExporting.value = false
        }
      }
      lastUpdateTime.value = new Date()
    }
  }

  const updateTaskProgress = (taskId: string, progress: number) => {
    const task = tasks.value.find(t => t.id === taskId)
    if (task) {
      task.progress = Math.max(0, Math.min(100, progress))
      lastUpdateTime.value = new Date()
    }
  }

  const setTaskError = (taskId: string, errorMessage: string) => {
    const task = tasks.value.find(t => t.id === taskId)
    if (task) {
      task.error = errorMessage
      task.status = 'failed'
      task.endTime = new Date()
      lastUpdateTime.value = new Date()
    }
  }

  const setTaskDownloadUrl = (taskId: string, url: string, fileSize?: number) => {
    const task = tasks.value.find(t => t.id === taskId)
    if (task) {
      task.downloadUrl = url
      task.fileSize = fileSize
      task.status = 'completed'
      task.endTime = new Date()
      lastUpdateTime.value = new Date()
    }
  }

  const removeTask = (taskId: string) => {
    const index = tasks.value.findIndex(t => t.id === taskId)
    if (index > -1) {
      tasks.value.splice(index, 1)
    }
  }

  const cancelTask = (taskId: string) => {
    updateTaskStatus(taskId, 'cancelled')
    addLog(taskId, 'info', '导出任务已取消')
  }

  const retryTask = (taskId: string) => {
    const task = tasks.value.find(t => t.id === taskId)
    if (task) {
      task.status = 'pending'
      task.progress = 0
      task.error = undefined
      task.endTime = undefined
      task.startTime = new Date()
      addLog(taskId, 'info', '重新开始导出任务')
    }
  }

  const addLog = (taskId: string, level: ExportLog['level'], message: string, details?: any) => {
    const log: ExportLog = {
      id: `log-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      taskId,
      timestamp: new Date(),
      level,
      message,
      details
    }
    
    logs.value.unshift(log)
    
    // 保持日志数量在合理范围内
    if (logs.value.length > 1000) {
      logs.value = logs.value.slice(0, 1000)
    }
  }

  const clearLogs = () => {
    logs.value = []
  }

  const clearCompletedTasks = () => {
    tasks.value = tasks.value.filter(task => 
      task.status !== 'completed' && task.status !== 'failed' && task.status !== 'cancelled'
    )
  }

  const saveTemplate = (template: Omit<ExportTemplate, 'id' | 'createdAt' | 'updatedAt'>) => {
    const newTemplate: ExportTemplate = {
      ...template,
      id: `template-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      createdAt: new Date(),
      updatedAt: new Date()
    }
    
    templates.value.push(newTemplate)
    return newTemplate
  }

  const updateTemplate = (templateId: string, updates: Partial<ExportTemplate>) => {
    const template = templates.value.find(t => t.id === templateId)
    if (template) {
      Object.assign(template, updates, { updatedAt: new Date() })
    }
  }

  const removeTemplate = (templateId: string) => {
    const index = templates.value.findIndex(t => t.id === templateId)
    if (index > -1) {
      templates.value.splice(index, 1)
    }
  }

  // 模拟导出过程
  const startExport = async (config: ExportConfig, name: string, type: ExportTask['type']) => {
    if (isExporting.value) {
      throw new Error('已有导出任务在进行中')
    }

    const task = addTask(config, name, type)
    setCurrentTask(task)
    isExporting.value = true
    
    addLog(task.id, 'info', '开始导出任务')
    
    try {
      // 模拟导出过程
      updateTaskStatus(task.id, 'running')
      
      // 模拟进度更新
      for (let progress = 0; progress <= 100; progress += 10) {
        await new Promise(resolve => setTimeout(resolve, 200))
        updateTaskProgress(task.id, progress)
        
        if (progress === 30) {
          addLog(task.id, 'info', '正在收集数据...')
        } else if (progress === 60) {
          addLog(task.id, 'info', '正在处理数据...')
        } else if (progress === 90) {
          addLog(task.id, 'info', '正在生成文件...')
        }
      }
      
      // 模拟文件生成
      const fileSize = Math.floor(Math.random() * 10000000) + 1000000 // 1MB - 10MB
      const downloadUrl = `/api/exports/${task.id}/download`
      
      setTaskDownloadUrl(task.id, downloadUrl, fileSize)
      addLog(task.id, 'info', `导出完成，文件大小: ${(fileSize / 1024 / 1024).toFixed(2)} MB`)
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '导出失败'
      setTaskError(task.id, errorMessage)
      addLog(task.id, 'error', errorMessage)
    } finally {
      isExporting.value = false
      setCurrentTask(null)
    }
    
    return task
  }

  const downloadFile = async (taskId: string) => {
    const task = tasks.value.find(t => t.id === taskId)
    if (!task || !task.downloadUrl) {
      throw new Error('文件不存在或已过期')
    }
    
    // 模拟下载
    addLog(taskId, 'info', '开始下载文件')
    
    // 在实际应用中，这里会触发文件下载
    // window.open(task.downloadUrl, '_blank')
    
    return task.downloadUrl
  }

  const loadTemplates = async () => {
    try {
      // 模拟加载模板
      const mockTemplates: ExportTemplate[] = [
        {
          id: 'template-1',
          name: '每日能耗报告',
          description: '导出每日设备能耗数据',
          type: 'energy',
          isDefault: true,
          config: {
            format: 'excel',
            dateRange: {
              start: new Date(Date.now() - 24 * 60 * 60 * 1000),
              end: new Date()
            },
            includeHeaders: true,
            compression: false
          },
          createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
          updatedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
        },
        {
          id: 'template-2',
          name: '设备状态报告',
          description: '导出设备状态和告警信息',
          type: 'device',
          isDefault: false,
          config: {
            format: 'csv',
            dateRange: {
              start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
              end: new Date()
            },
            includeHeaders: true,
            compression: true
          },
          createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
          updatedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000)
        }
      ]
      
      templates.value = mockTemplates
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载模板失败')
    }
  }

  const clearData = () => {
    tasks.value = []
    logs.value = []
    templates.value = []
    currentTask.value = null
    isExporting.value = false
    error.value = null
    lastUpdateTime.value = null
  }

  return {
    // 状态
    tasks,
    logs,
    templates,
    currentTask,
    isExporting,
    error,
    lastUpdateTime,
    
    // 计算属性
    activeTasks,
    completedTasks,
    failedTasks,
    taskStats,
    recentLogs,
    errorLogs,
    downloadableFiles,
    totalExportedSize,
    
    // Actions
    setError,
    setCurrentTask,
    addTask,
    updateTaskStatus,
    updateTaskProgress,
    setTaskError,
    setTaskDownloadUrl,
    removeTask,
    cancelTask,
    retryTask,
    addLog,
    clearLogs,
    clearCompletedTasks,
    saveTemplate,
    updateTemplate,
    removeTemplate,
    startExport,
    downloadFile,
    loadTemplates,
    clearData
  }
})