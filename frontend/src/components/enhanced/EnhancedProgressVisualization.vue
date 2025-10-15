<template>
  <div class="enhanced-progress-visualization">
    <!-- 主要进度显示 -->
    <div class="progress-main">
      <div class="progress-header">
        <div class="progress-title">
          <i class="icon-activity"></i>
          <h3>{{ title }}</h3>
        </div>
        <div class="progress-status">
          <el-tag :type="getStatusTagType()" size="small">
            {{ getStatusText() }}
          </el-tag>
        </div>
      </div>

      <!-- 整体进度条 -->
      <div class="overall-progress">
        <div class="progress-info">
          <span class="progress-text">{{ progressText }}</span>
          <span class="progress-percentage">{{ progress.percent }}%</span>
        </div>
        <div class="progress-bar-container">
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: `${progress.percent}%` }"
            ></div>
            <div
              v-if="showProgressAnimation"
              class="progress-glow"
              :style="{ width: `${progress.percent}%` }"
            ></div>
          </div>
          <div class="progress-milestones">
            <div
              v-for="milestone in milestones"
              :key="milestone.percent"
              class="milestone"
              :class="{ reached: progress.percent >= milestone.percent }"
              :style="{ left: `${milestone.percent}%` }"
            >
              <el-tooltip :content="milestone.label" placement="top">
                <div class="milestone-dot"></div>
              </el-tooltip>
            </div>
          </div>
        </div>
        <div class="progress-details">
          <span>{{ progress.current }} / {{ progress.total }}</span>
          <span v-if="estimatedTime">预计剩余: {{ estimatedTime }}</span>
        </div>
      </div>

      <!-- 统计信息 -->
      <div v-if="showStats" class="progress-stats">
        <div class="stat-item">
          <div class="stat-icon">
            <i class="icon-clock"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ elapsedTime }}</div>
            <div class="stat-label">已用时间</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon">
            <i class="icon-trending-up"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ processingSpeed }}</div>
            <div class="stat-label">处理速度</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-icon">
            <i class="icon-database"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ processedSize }}</div>
            <div class="stat-label">已处理数据</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 阶段进度 -->
    <div v-if="stages && stages.length > 0" class="progress-stages">
      <h4>
        <i class="icon-layers"></i>
        处理阶段
      </h4>
      <div class="stages-container">
        <div
          v-for="(stage, index) in stages"
          :key="stage.key"
          class="stage-item"
          :class="getStageClass(stage)"
        >
          <div class="stage-connector" v-if="index > 0"></div>
          <div class="stage-icon">
            <i :class="getStageIcon(stage)"></i>
          </div>
          <div class="stage-content">
            <div class="stage-title">{{ stage.title }}</div>
            <div class="stage-description">{{ stage.description }}</div>
            <div v-if="stage.progress !== undefined" class="stage-progress">
              <div class="stage-progress-bar">
                <div
                  class="stage-progress-fill"
                  :style="{ width: `${stage.progress}%` }"
                ></div>
              </div>
              <span class="stage-progress-text">{{ stage.progress }}%</span>
            </div>
          </div>
          <div class="stage-time">
            <span v-if="stage.duration">{{ formatDuration(stage.duration) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 详细任务列表 -->
    <div v-if="showDetails && tasks.length > 0" class="progress-tasks">
      <div class="tasks-header">
        <h4>
          <i class="icon-list"></i>
          任务详情
        </h4>
        <div class="task-controls">
          <el-button @click="toggleTaskCollapse" size="small" text>
            <i :class="allTasksCollapsed ? 'icon-chevron-down' : 'icon-chevron-up'"></i>
            {{ allTasksCollapsed ? '展开' : '收起' }}
          </el-button>
        </div>
      </div>

      <div class="tasks-list">
        <div
          v-for="task in tasks"
          :key="task.id"
          class="task-item"
          :class="{
            expanded: !task.collapsed,
            [task.status]: true
          }"
        >
          <div class="task-header" @click="toggleTask(task)">
            <div class="task-status">
              <i :class="getTaskIcon(task.status)"></i>
            </div>
            <div class="task-info">
              <div class="task-title">{{ task.title }}</div>
              <div class="task-meta">
                <span class="task-time">{{ formatTime(task.timestamp) }}</span>
                <span v-if="task.duration" class="task-duration">
                  耗时: {{ formatDuration(task.duration) }}
                </span>
              </div>
            </div>
            <div class="task-actions">
              <el-button
                v-if="task.retryable && task.status === 'error'"
                @click.stop="retryTask(task)"
                size="small"
                text
                type="primary"
              >
                重试
              </el-button>
              <i class="icon-chevron-down task-expand-icon"></i>
            </div>
          </div>

          <div v-if="!task.collapsed" class="task-details">
            <div v-if="task.description" class="task-description">
              {{ task.description }}
            </div>
            <div v-if="task.progress !== undefined" class="task-progress">
              <div class="task-progress-bar">
                <div
                  class="task-progress-fill"
                  :style="{ width: `${task.progress}%` }"
                ></div>
              </div>
              <span>{{ task.progress }}%</span>
            </div>
            <div v-if="task.details" class="task-extra-details">
              <pre>{{ JSON.stringify(task.details, null, 2) }}</pre>
            </div>
            <div v-if="task.error" class="task-error">
              <div class="error-header">
                <i class="icon-x-circle"></i>
                错误信息
              </div>
              <div class="error-message">{{ task.error }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 控制按钮 -->
    <div class="progress-controls">
      <div class="control-buttons">
        <el-button
          v-if="cancellable"
          @click="cancelProgress"
          type="danger"
          size="small"
          :disabled="progress.percent === 100"
        >
          <i class="icon-x"></i>
          取消
        </el-button>
        <el-button
          v-if="pausable"
          @click="togglePause"
          size="small"
          :disabled="progress.percent === 100"
        >
          <i :class="paused ? 'icon-play' : 'icon-pause'"></i>
          {{ paused ? '继续' : '暂停' }}
        </el-button>
        <el-button
          v-if="retryable && hasErrors"
          @click="retryFailedTasks"
          type="warning"
          size="small"
        >
          <i class="icon-refresh-cw"></i>
          重试失败项
        </el-button>
      </div>
      <div class="control-info">
        <el-button @click="exportLog" size="small" text>
          <i class="icon-download"></i>
          导出日志
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 接口定义
interface Progress {
  percent: number
  current: number
  total: number
  text: string
}

interface Stage {
  key: string
  title: string
  description: string
  status: 'pending' | 'processing' | 'completed' | 'error'
  progress?: number
  duration?: number
}

interface Task {
  id: string
  title: string
  description?: string
  status: 'pending' | 'processing' | 'completed' | 'error'
  progress?: number
  timestamp: number
  duration?: number
  details?: any
  error?: string
  retryable?: boolean
  collapsed?: boolean
}

interface Milestone {
  percent: number
  label: string
}

interface Props {
  title: string
  progress: Progress
  stages?: Stage[]
  tasks?: Task[]
  milestones?: Milestone[]
  cancellable?: boolean
  pausable?: boolean
  retryable?: boolean
  showStats?: boolean
  showDetails?: boolean
  showProgressAnimation?: boolean
  startTime?: number
}

const props = withDefaults(defineProps<Props>(), {
  stages: () => [],
  tasks: () => [],
  milestones: () => [],
  cancellable: true,
  pausable: false,
  retryable: true,
  showStats: true,
  showDetails: true,
  showProgressAnimation: true,
  startTime: 0
})

interface Emits {
  (e: 'cancel'): void
  (e: 'pause'): void
  (e: 'resume'): void
  (e: 'retry', taskId?: string): void
  (e: 'retry-failed'): void
  (e: 'export-log'): void
}

const emit = defineEmits<Emits>()

// 响应式数据
const paused = ref(false)
const allTasksCollapsed = ref(false)
const currentTime = ref(Date.now())
let timer: number | null = null

// 计算属性
const elapsedTime = computed(() => {
  if (!props.startTime) return '00:00:00'
  const elapsed = (currentTime.value - props.startTime) / 1000
  return formatDuration(elapsed)
})

const estimatedTime = computed(() => {
  if (props.progress.percent === 0 || !props.startTime) return ''

  const elapsed = (currentTime.value - props.startTime) / 1000
  const rate = props.progress.percent / elapsed
  const remaining = (100 - props.progress.percent) / rate

  return formatDuration(remaining)
})

const processingSpeed = computed(() => {
  if (!props.startTime || props.progress.current === 0) return '0 条/秒'

  const elapsed = (currentTime.value - props.startTime) / 1000
  const speed = props.progress.current / elapsed

  return `${speed.toFixed(1)} 条/秒`
})

const processedSize = computed(() => {
  // 简单估算，可以根据实际情况调整
  const sizeKB = props.progress.current * 0.5 // 假设每条记录0.5KB

  if (sizeKB < 1024) {
    return `${sizeKB.toFixed(1)} KB`
  } else {
    return `${(sizeKB / 1024).toFixed(1)} MB`
  }
})

const hasErrors = computed(() => {
  return props.tasks.some(task => task.status === 'error')
})

// 方法
const getStatusTagType = () => {
  if (props.progress.percent === 100) return 'success'
  if (hasErrors.value) return 'danger'
  if (paused.value) return 'warning'
  return 'primary'
}

const getStatusText = () => {
  if (props.progress.percent === 100) return '已完成'
  if (paused.value) return '已暂停'
  if (hasErrors.value) return '有错误'
  return '进行中'
}

const getStageClass = (stage: Stage) => {
  return {
    'stage-pending': stage.status === 'pending',
    'stage-processing': stage.status === 'processing',
    'stage-completed': stage.status === 'completed',
    'stage-error': stage.status === 'error'
  }
}

const getStageIcon = (stage: Stage) => {
  const icons = {
    pending: 'icon-clock',
    processing: 'icon-loader animate-spin',
    completed: 'icon-check-circle',
    error: 'icon-x-circle'
  }
  return icons[stage.status] || 'icon-clock'
}

const getTaskIcon = (status: string) => {
  const icons = {
    pending: 'icon-clock',
    processing: 'icon-loader animate-spin',
    completed: 'icon-check-circle',
    error: 'icon-x-circle'
  }
  return icons[status] || 'icon-clock'
}

const formatDuration = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  } else {
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }
}

const formatTime = (timestamp: number) => {
  return new Date(timestamp).toLocaleTimeString()
}

const cancelProgress = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要取消当前操作吗？',
      '确认取消',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    emit('cancel')
  } catch {
    // 用户取消
  }
}

const togglePause = () => {
  if (paused.value) {
    emit('resume')
    paused.value = false
  } else {
    emit('pause')
    paused.value = true
  }
}

const retryTask = (task: Task) => {
  emit('retry', task.id)
}

const retryFailedTasks = () => {
  emit('retry-failed')
}

const toggleTaskCollapse = () => {
  allTasksCollapsed.value = !allTasksCollapsed.value
  props.tasks.forEach(task => {
    task.collapsed = allTasksCollapsed.value
  })
}

const toggleTask = (task: Task) => {
  task.collapsed = !task.collapsed
}

const exportLog = () => {
  emit('export-log')
}

// 生命周期
onMounted(() => {
  // 启动定时器更新时间
  timer = window.setInterval(() => {
    currentTime.value = Date.now()
  }, 1000)

  // 初始化任务折叠状态
  props.tasks.forEach(task => {
    if (task.collapsed === undefined) {
      task.collapsed = task.status === 'completed'
    }
  })
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
})

// 监听进度变化
watch(() => props.progress.percent, (newPercent) => {
  if (newPercent === 100) {
    paused.value = false
  }
})
</script>

<style scoped>
.enhanced-progress-visualization {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* 主要进度显示 */
.progress-main {
  padding: 24px;
  border-bottom: 1px solid #e4e7ed;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.progress-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-title h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.progress-title i {
  color: #667eea;
  font-size: 20px;
}

/* 整体进度条 */
.overall-progress {
  margin-bottom: 24px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-text {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.progress-percentage {
  font-size: 18px;
  font-weight: 700;
  color: #667eea;
}

.progress-bar-container {
  position: relative;
  margin-bottom: 8px;
}

.progress-bar {
  height: 12px;
  background: #e4e7ed;
  border-radius: 6px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 6px;
  transition: width 0.3s ease;
  position: relative;
}

.progress-glow {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  border-radius: 6px;
  animation: glow 2s ease-in-out infinite;
}

@keyframes glow {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.progress-milestones {
  position: absolute;
  top: -4px;
  left: 0;
  right: 0;
  height: 20px;
}

.milestone {
  position: absolute;
  transform: translateX(-50%);
}

.milestone-dot {
  width: 8px;
  height: 8px;
  background: #e4e7ed;
  border-radius: 50%;
  border: 2px solid white;
  transition: all 0.3s ease;
}

.milestone.reached .milestone-dot {
  background: #67c23a;
  transform: scale(1.2);
}

.progress-details {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}

/* 统计信息 */
.progress-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-radius: 8px;
}

.stat-icon i {
  font-size: 18px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

/* 阶段进度 */
.progress-stages {
  padding: 24px;
  border-bottom: 1px solid #e4e7ed;
}

.progress-stages h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 20px 0;
}

.progress-stages h4 i {
  color: #667eea;
}

.stages-container {
  position: relative;
}

.stage-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
  position: relative;
}

.stage-connector {
  position: absolute;
  left: 20px;
  top: 40px;
  width: 2px;
  height: 40px;
  background: #e4e7ed;
  z-index: 1;
}

.stage-item.stage-completed .stage-connector {
  background: #67c23a;
}

.stage-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
  border-radius: 50%;
  border: 3px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 2;
  position: relative;
}

.stage-item.stage-processing .stage-icon {
  background: #667eea;
  color: white;
}

.stage-item.stage-completed .stage-icon {
  background: #67c23a;
  color: white;
}

.stage-item.stage-error .stage-icon {
  background: #f56c6c;
  color: white;
}

.stage-content {
  flex: 1;
}

.stage-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.stage-description {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.stage-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stage-progress-bar {
  flex: 1;
  height: 4px;
  background: #e4e7ed;
  border-radius: 2px;
  overflow: hidden;
}

.stage-progress-fill {
  height: 100%;
  background: #667eea;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.stage-progress-text {
  font-size: 12px;
  color: #606266;
  min-width: 32px;
}

.stage-time {
  font-size: 12px;
  color: #909399;
}

/* 详细任务列表 */
.progress-tasks {
  padding: 24px;
  border-bottom: 1px solid #e4e7ed;
}

.tasks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.tasks-header h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.tasks-header h4 i {
  color: #667eea;
}

.task-controls {
  display: flex;
  gap: 8px;
}

.tasks-list {
  max-height: 400px;
  overflow-y: auto;
}

.task-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 8px;
  overflow: hidden;
  transition: all 0.2s ease;
}

.task-item:hover {
  border-color: #667eea;
}

.task-item.completed {
  border-color: #67c23a;
  background: rgba(103, 194, 58, 0.02);
}

.task-item.error {
  border-color: #f56c6c;
  background: rgba(245, 108, 108, 0.02);
}

.task-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  cursor: pointer;
}

.task-status {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.task-status i {
  font-size: 16px;
}

.task-item.pending .task-status i {
  color: #909399;
}

.task-item.processing .task-status i {
  color: #667eea;
}

.task-item.completed .task-status i {
  color: #67c23a;
}

.task-item.error .task-status i {
  color: #f56c6c;
}

.task-info {
  flex: 1;
}

.task-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.task-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.task-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-expand-icon {
  color: #c0c4cc;
  font-size: 14px;
  transition: transform 0.2s ease;
}

.task-item.expanded .task-expand-icon {
  transform: rotate(180deg);
}

.task-details {
  padding: 0 12px 12px 48px;
  border-top: 1px solid #f0f2f5;
}

.task-description {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
  line-height: 1.4;
}

.task-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.task-progress-bar {
  flex: 1;
  height: 4px;
  background: #e4e7ed;
  border-radius: 2px;
  overflow: hidden;
}

.task-progress-fill {
  height: 100%;
  background: #667eea;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.task-progress span {
  font-size: 12px;
  color: #606266;
  min-width: 32px;
}

.task-extra-details {
  margin-bottom: 8px;
}

.task-extra-details pre {
  font-size: 11px;
  color: #606266;
  background: #f8f9fa;
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 0;
}

.task-error {
  padding: 8px;
  background: #fef0f0;
  border-radius: 4px;
  border-left: 3px solid #f56c6c;
}

.error-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #f56c6c;
  margin-bottom: 4px;
}

.error-message {
  font-size: 12px;
  color: #f56c6c;
  line-height: 1.4;
}

/* 控制按钮 */
.progress-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #f8f9fa;
}

.control-buttons {
  display: flex;
  gap: 8px;
}

.control-info {
  display: flex;
  gap: 8px;
}

/* 动画效果 */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .progress-main {
    padding: 16px;
  }

  .progress-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .progress-stats {
    grid-template-columns: 1fr;
  }

  .stage-item {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .stage-connector {
    display: none;
  }

  .task-header {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .task-actions {
    justify-content: flex-end;
  }

  .progress-controls {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .control-buttons,
  .control-info {
    justify-content: center;
  }
}
</style>