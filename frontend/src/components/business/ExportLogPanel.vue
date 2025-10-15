<template>
  <BaseCard title="操作日志" shadow="md" :hover="true">
    <template #header>
      <div class="log-header">
        <div class="header-title">
          <i class="icon-file-text header-icon"></i>
          <span>操作日志</span>
          <span v-if="logs.length > 0" class="log-count">({{ logs.length }})</span>
        </div>
        <div class="header-actions">
          <el-button
            @click="exportLogs"
            plain
            size="small"
            :disabled="logs.length === 0"
          >
            <i class="icon-download"></i>
            导出日志
          </el-button>
          <el-button
            @click="clearLogs"
            plain
            size="small"
            :disabled="logs.length === 0"
          >
            <i class="icon-trash-2"></i>
            清空日志
          </el-button>
        </div>
      </div>
    </template>

    <div class="log-container" ref="logContainer">
      <div class="log-filters">
        <div class="filter-group">
          <label>日志级别:</label>
          <div class="filter-buttons">
            <button
              v-for="level in logLevels"
              :key="level.value"
              @click="toggleFilter(level.value)"
              :class="[
                'filter-btn',
                `filter-btn-${level.value}`,
                { active: activeFilters.includes(level.value) }
              ]"
            >
              <i :class="level.icon"></i>
              {{ level.label }}
              <span class="count">({{ getLogCountByLevel(level.value) }})</span>
            </button>
          </div>
        </div>
        
        <div class="filter-group">
          <label>搜索:</label>
          <div class="search-input">
            <i class="icon-search"></i>
            <input
              v-model="searchKeyword"
              type="text"
              placeholder="搜索日志内容..."
              @input="onSearch"
            />
            <button
              v-if="searchKeyword"
              @click="clearSearch"
              class="clear-search"
            >
              <i class="icon-x"></i>
            </button>
          </div>
        </div>
      </div>

      <div class="log-content" ref="logContent">
        <div
          v-for="(log, index) in filteredLogs"
          :key="log.id || index"
          :class="[
            'log-item',
            `log-${log.level}`,
            { 'log-highlight': log.highlight }
          ]"
          @click="selectLog(log)"
        >
          <div class="log-meta">
            <span class="log-time">{{ formatTime(log.timestamp) }}</span>
            <span :class="['log-level', `level-${log.level}`]">
              <i :class="getLevelIcon(log.level)"></i>
              {{ getLevelLabel(log.level) }}
            </span>
            <span v-if="log.category" class="log-category">{{ log.category }}</span>
          </div>
          
          <div class="log-message">
            <span v-html="highlightSearch(log.message)"></span>
          </div>
          
          <div v-if="log.details" class="log-details">
            <button
              @click.stop="toggleDetails(log)"
              class="details-toggle"
            >
              <i :class="log.showDetails ? 'icon-chevron-up' : 'icon-chevron-down'"></i>
              {{ log.showDetails ? '收起详情' : '查看详情' }}
            </button>
            
            <div v-if="log.showDetails" class="details-content">
              <pre>{{ JSON.stringify(log.details, null, 2) }}</pre>
            </div>
          </div>
          
          <div v-if="log.actions && log.actions.length > 0" class="log-actions">
            <el-button
              v-for="action in log.actions"
              :key="action.key"
              @click.stop="handleAction(action, log)"
              :plain="action.variant === 'outline'"
              size="small"
              :disabled="action.disabled"
            >
              <i v-if="action.icon" :class="action.icon"></i>
              {{ action.label }}
            </el-button>
          </div>
        </div>
        
        <div v-if="filteredLogs.length === 0" class="empty-logs">
          <div v-if="logs.length === 0" class="empty-state">
            <i class="icon-file-text"></i>
            <p>暂无操作日志</p>
            <span>系统操作日志将在此处显示</span>
          </div>
          
          <div v-else class="no-results">
            <i class="icon-search"></i>
            <p>未找到匹配的日志</p>
            <span>尝试调整筛选条件或搜索关键词</span>
          </div>
        </div>
      </div>
      
      <div v-if="showLoadMore" class="load-more">
        <el-button
          @click="loadMoreLogs"
          plain
          :loading="loadingMore"
        >
          <i class="icon-more-horizontal"></i>
          加载更多
        </el-button>
      </div>
    </div>

    <!-- 日志详情模态框 -->
    <BaseModal
      :visible="detailModalVisible"
      @update:visible="detailModalVisible = $event"
      title="日志详情"
      width="600px"
      :destroy-on-close="true"
    >
      <div v-if="selectedLog" class="log-detail-modal">
        <div class="detail-header">
          <div class="detail-meta">
            <span class="detail-time">{{ formatTime(selectedLog.timestamp, true) }}</span>
            <span :class="['detail-level', `level-${selectedLog.level}`]">
              <i :class="getLevelIcon(selectedLog.level)"></i>
              {{ getLevelLabel(selectedLog.level) }}
            </span>
          </div>
          <div v-if="selectedLog.category" class="detail-category">
            分类: {{ selectedLog.category }}
          </div>
        </div>
        
        <div class="detail-message">
          <h4>消息内容</h4>
          <p>{{ selectedLog.message }}</p>
        </div>
        
        <div v-if="selectedLog.details" class="detail-data">
          <h4>详细信息</h4>
          <pre>{{ JSON.stringify(selectedLog.details, null, 2) }}</pre>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="detailModalVisible = false" plain>
          关闭
        </el-button>
        <el-button
          v-if="selectedLog"
          @click="copyLogToClipboard(selectedLog)"
          type="primary"
        >
          <i class="icon-copy"></i>
          复制日志
        </el-button>
      </template>
    </BaseModal>
  </BaseCard>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { BaseCard, BaseModal } from '@/components/common'

interface LogAction {
  key: string
  label: string
  icon?: string
  variant?: string
  disabled?: boolean
}

interface ExportLog {
  id?: string
  timestamp: number | Date
  level: 'info' | 'success' | 'warning' | 'error'
  message: string
  category?: string
  details?: any
  actions?: LogAction[]
  showDetails?: boolean
  highlight?: boolean
}

interface Props {
  logs: ExportLog[]
  maxLogs?: number
  autoScroll?: boolean
  showLoadMore?: boolean
  loadingMore?: boolean
}

interface Emits {
  (e: 'clear'): void
  (e: 'export'): void
  (e: 'load-more'): void
  (e: 'action', action: LogAction, log: ExportLog): void
}

const props = withDefaults(defineProps<Props>(), {
  maxLogs: 1000,
  autoScroll: true,
  showLoadMore: false,
  loadingMore: false
})

const emit = defineEmits<Emits>()

// 日志级别配置
const logLevels = [
  { value: 'info', label: '信息', icon: 'icon-info' },
  { value: 'success', label: '成功', icon: 'icon-check-circle' },
  { value: 'warning', label: '警告', icon: 'icon-alert-triangle' },
  { value: 'error', label: '错误', icon: 'icon-x-circle' }
]

// 筛选和搜索
const activeFilters = ref<string[]>(['info', 'success', 'warning', 'error'])
const searchKeyword = ref('')

// 模态框
const detailModalVisible = ref(false)
const selectedLog = ref<ExportLog | null>(null)

// DOM引用
const logContainer = ref<HTMLElement>()
const logContent = ref<HTMLElement>()

// 计算属性
const filteredLogs = computed(() => {
  let filtered = props.logs.filter(log => 
    activeFilters.value.includes(log.level)
  )
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(log =>
      log.message.toLowerCase().includes(keyword) ||
      (log.category && log.category.toLowerCase().includes(keyword))
    )
  }
  
  return filtered
})

// 方法
const toggleFilter = (level: string) => {
  const index = activeFilters.value.indexOf(level)
  if (index > -1) {
    activeFilters.value.splice(index, 1)
  } else {
    activeFilters.value.push(level)
  }
}

const getLogCountByLevel = (level: string) => {
  return props.logs.filter(log => log.level === level).length
}

const onSearch = () => {
  // 搜索时高亮匹配的日志
  if (searchKeyword.value) {
    props.logs.forEach(log => {
      log.highlight = log.message.toLowerCase().includes(searchKeyword.value.toLowerCase())
    })
  } else {
    props.logs.forEach(log => {
      log.highlight = false
    })
  }
}

const clearSearch = () => {
  searchKeyword.value = ''
  props.logs.forEach(log => {
    log.highlight = false
  })
}

const highlightSearch = (text: string) => {
  if (!searchKeyword.value) return text
  
  const regex = new RegExp(`(${searchKeyword.value})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

const formatTime = (timestamp: number | Date, detailed = false) => {
  const date = new Date(timestamp)
  if (detailed) {
    return date.toLocaleString()
  }
  return date.toLocaleTimeString()
}

const getLevelIcon = (level: string) => {
  const levelConfig = logLevels.find(l => l.value === level)
  return levelConfig?.icon || 'icon-info'
}

const getLevelLabel = (level: string) => {
  const levelConfig = logLevels.find(l => l.value === level)
  return levelConfig?.label || level
}

const toggleDetails = (log: ExportLog) => {
  log.showDetails = !log.showDetails
}

const selectLog = (log: ExportLog) => {
  selectedLog.value = log
  detailModalVisible.value = true
}

const handleAction = (action: LogAction, log: ExportLog) => {
  emit('action', action, log)
}

const clearLogs = () => {
  emit('clear')
}

const exportLogs = () => {
  emit('export')
}

const loadMoreLogs = () => {
  emit('load-more')
}

const copyLogToClipboard = async (log: ExportLog) => {
  const logText = `[${formatTime(log.timestamp, true)}] [${getLevelLabel(log.level)}] ${log.message}`
  
  try {
    await navigator.clipboard.writeText(logText)
    // 这里可以显示复制成功的提示
  } catch (error) {
    console.error('复制失败:', error)
  }
}

// 自动滚动到底部
const scrollToBottom = () => {
  if (props.autoScroll && logContent.value) {
    nextTick(() => {
      logContent.value!.scrollTop = logContent.value!.scrollHeight
    })
  }
}

// 监听日志变化
watch(() => props.logs.length, () => {
  scrollToBottom()
})

// 暴露方法
defineExpose({
  scrollToBottom,
  clearSearch
})
</script>

<style scoped>
.log-header {
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
  color: var(--primary-color, #409eff);
}

.log-count {
  font-size: 12px;
  color: var(--text-color-regular, #606266);
  font-weight: normal;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.log-container {
  max-height: 600px;
  display: flex;
  flex-direction: column;
}

.log-filters {
  padding: 16px;
  border-bottom: 1px solid var(--border-color, #ebeef5);
  background: var(--bg-color-light, #f8f9fa);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.filter-group:last-child {
  margin-bottom: 0;
}

.filter-group label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-color-primary, #303133);
  min-width: 60px;
}

.filter-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border: 1px solid var(--border-color, #dcdfe6);
  border-radius: 4px;
  background: white;
  color: var(--text-color-regular, #606266);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: var(--primary-color, #409eff);
  color: var(--primary-color, #409eff);
}

.filter-btn.active {
  border-color: var(--primary-color, #409eff);
  background: var(--primary-color, #409eff);
  color: white;
}

.filter-btn-success.active {
  border-color: var(--success-color, #67c23a);
  background: var(--success-color, #67c23a);
}

.filter-btn-warning.active {
  border-color: var(--warning-color, #e6a23c);
  background: var(--warning-color, #e6a23c);
}

.filter-btn-error.active {
  border-color: var(--danger-color, #f56c6c);
  background: var(--danger-color, #f56c6c);
}

.count {
  font-size: 10px;
  opacity: 0.8;
}

.search-input {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  max-width: 300px;
}

.search-input i {
  position: absolute;
  left: 8px;
  color: var(--text-color-placeholder, #c0c4cc);
  font-size: 14px;
}

.search-input input {
  width: 100%;
  padding: 6px 32px 6px 28px;
  border: 1px solid var(--border-color, #dcdfe6);
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.search-input input:focus {
  border-color: var(--primary-color, #409eff);
}

.clear-search {
  position: absolute;
  right: 8px;
  background: none;
  border: none;
  color: var(--text-color-placeholder, #c0c4cc);
  cursor: pointer;
  padding: 2px;
  border-radius: 2px;
}

.clear-search:hover {
  color: var(--text-color-regular, #606266);
  background: var(--bg-color, #f5f7fa);
}

.log-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.log-item {
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 8px;
  border-left: 3px solid transparent;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.log-item:hover {
  background: var(--bg-color-light, #f8f9fa);
  transform: translateX(2px);
}

.log-item.log-highlight {
  background: var(--warning-color-light, #fdf6ec);
  border-left-color: var(--warning-color, #e6a23c);
}

.log-info {
  border-left-color: var(--info-color, #909399);
}

.log-success {
  border-left-color: var(--success-color, #67c23a);
}

.log-warning {
  border-left-color: var(--warning-color, #e6a23c);
}

.log-error {
  border-left-color: var(--danger-color, #f56c6c);
}

.log-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
  font-size: 12px;
}

.log-time {
  color: var(--text-color-placeholder, #c0c4cc);
  font-family: monospace;
}

.log-level {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 500;
}

.level-info {
  background: var(--info-color-light, #f4f4f5);
  color: var(--info-color, #909399);
}

.level-success {
  background: var(--success-color-light, #f0f9ff);
  color: var(--success-color, #67c23a);
}

.level-warning {
  background: var(--warning-color-light, #fdf6ec);
  color: var(--warning-color, #e6a23c);
}

.level-error {
  background: var(--danger-color-light, #fef0f0);
  color: var(--danger-color, #f56c6c);
}

.log-category {
  padding: 2px 6px;
  background: var(--primary-color-light, #ecf5ff);
  color: var(--primary-color, #409eff);
  border-radius: 3px;
  font-size: 11px;
}

.log-message {
  color: var(--text-color-primary, #303133);
  line-height: 1.4;
  margin-bottom: 8px;
}

.log-message :deep(mark) {
  background: var(--warning-color-light, #fdf6ec);
  color: var(--warning-color-dark, #cf9236);
  padding: 1px 2px;
  border-radius: 2px;
}

.log-details {
  margin-top: 8px;
}

.details-toggle {
  background: none;
  border: 1px solid var(--border-color, #dcdfe6);
  color: var(--text-color-regular, #606266);
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s;
}

.details-toggle:hover {
  border-color: var(--primary-color, #409eff);
  color: var(--primary-color, #409eff);
}

.details-content {
  margin-top: 8px;
  padding: 8px;
  background: var(--bg-color, #f5f7fa);
  border-radius: 4px;
  border: 1px solid var(--border-color, #ebeef5);
}

.details-content pre {
  margin: 0;
  font-size: 11px;
  color: var(--text-color-regular, #606266);
  white-space: pre-wrap;
  word-break: break-all;
}

.log-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.empty-logs {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--text-color-placeholder, #c0c4cc);
}

.empty-state i,
.no-results i {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-state p,
.no-results p {
  margin: 0 0 4px 0;
  font-size: 16px;
  color: var(--text-color-regular, #606266);
}

.empty-state span,
.no-results span {
  font-size: 14px;
}

.load-more {
  padding: 16px;
  text-align: center;
  border-top: 1px solid var(--border-color, #ebeef5);
}

.log-detail-modal {
  max-height: 500px;
  overflow-y: auto;
}

.detail-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color, #ebeef5);
}

.detail-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.detail-time {
  font-family: monospace;
  color: var(--text-color-placeholder, #c0c4cc);
}

.detail-level {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.detail-category {
  font-size: 14px;
  color: var(--text-color-regular, #606266);
}

.detail-message h4,
.detail-data h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: var(--text-color-primary, #303133);
}

.detail-message p {
  margin: 0;
  line-height: 1.5;
  color: var(--text-color-regular, #606266);
}

.detail-data pre {
  margin: 0;
  padding: 12px;
  background: var(--bg-color, #f5f7fa);
  border-radius: 4px;
  border: 1px solid var(--border-color, #ebeef5);
  font-size: 12px;
  color: var(--text-color-regular, #606266);
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .log-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .filter-group {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .filter-group label {
    min-width: auto;
  }
  
  .search-input {
    max-width: none;
  }
  
  .log-meta {
    flex-wrap: wrap;
  }
  
  .log-actions {
    flex-wrap: wrap;
  }
}

/* 深色模式 */
@media (prefers-color-scheme: dark) {
  .log-filters {
    background: #2d2d2d;
    border-color: #404040;
  }
  
  .filter-btn {
    background: #3d3d3d;
    border-color: #555;
    color: #e5e5e5;
  }
  
  .search-input input {
    background: #3d3d3d;
    border-color: #555;
    color: #e5e5e5;
  }
  
  .log-item {
    background: #3d3d3d;
  }
  
  .log-item:hover {
    background: #4d4d4d;
  }
  
  .details-content,
  .detail-data pre {
    background: #2d2d2d;
    border-color: #404040;
  }
}
</style>