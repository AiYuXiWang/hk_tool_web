<template>
  <div class="smart-data-preview">
    <!-- 预览头部 -->
    <div class="preview-header">
      <div class="header-left">
        <h3>
          <i class="icon-eye"></i>
          数据预览
        </h3>
        <div class="preview-stats">
          <el-tag type="info" size="small">
            总记录数: {{ totalRecords.toLocaleString() }}
          </el-tag>
          <el-tag type="success" size="small">
            预览: {{ displayRecords }} 条
          </el-tag>
          <el-tag v-if="estimatedSize" type="warning" size="small">
            预计大小: {{ estimatedSize }}
          </el-tag>
        </div>
      </div>
      <div class="header-right">
        <div class="preview-actions">
          <el-button @click="refreshPreview" size="small" :loading="loading">
            <i class="icon-refresh-cw"></i>
            刷新
          </el-button>
          <el-button @click="exportPreview" type="primary" size="small">
            <i class="icon-download"></i>
            导出预览数据
          </el-button>
          <el-button @click="closePreview" size="small" text>
            <i class="icon-x"></i>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 数据质量检查 -->
    <div v-if="dataQuality" class="data-quality-panel">
      <div class="quality-header">
        <h4>
          <i class="icon-shield"></i>
          数据质量检查
        </h4>
        <div class="quality-score">
          <el-progress
            :percentage="dataQuality.score"
            :status="getQualityStatus(dataQuality.score)"
            :stroke-width="8"
            :width="60"
            type="circle"
          />
          <span class="score-label">{{ dataQuality.score }}%</span>
        </div>
      </div>

      <div class="quality-details">
        <div class="quality-item">
          <div class="quality-label">完整性</div>
          <div class="quality-value">
            <el-progress :percentage="dataQuality.completeness" :show-text="false" />
            <span>{{ dataQuality.completeness }}%</span>
          </div>
        </div>
        <div class="quality-item">
          <div class="quality-label">准确性</div>
          <div class="quality-value">
            <el-progress :percentage="dataQuality.accuracy" :show-text="false" />
            <span>{{ dataQuality.accuracy }}%</span>
          </div>
        </div>
        <div class="quality-item">
          <div class="quality-label">一致性</div>
          <div class="quality-value">
            <el-progress :percentage="dataQuality.consistency" :show-text="false" />
            <span>{{ dataQuality.consistency }}%</span>
          </div>
        </div>
      </div>

      <!-- 数据问题提示 -->
      <div v-if="dataQuality.issues && dataQuality.issues.length > 0" class="quality-issues">
        <div class="issues-header">
          <i class="icon-alert-triangle"></i>
          发现 {{ dataQuality.issues.length }} 个数据问题
        </div>
        <div class="issues-list">
          <div
            v-for="issue in dataQuality.issues.slice(0, 3)"
            :key="issue.id"
            class="issue-item"
            :class="issue.severity"
          >
            <i :class="getIssueIcon(issue.severity)"></i>
            <span>{{ issue.message }}</span>
            <span class="issue-count">{{ issue.count }} 条</span>
          </div>
          <div v-if="dataQuality.issues.length > 3" class="more-issues">
            还有 {{ dataQuality.issues.length - 3 }} 个问题...
          </div>
        </div>
      </div>
    </div>

    <!-- 预览控制栏 -->
    <div class="preview-controls">
      <div class="control-group">
        <label>显示字段:</label>
        <el-select
          v-model="selectedColumns"
          multiple
          collapse-tags
          collapse-tags-tooltip
          :max-collapse-tags="3"
          placeholder="选择要显示的字段"
          size="small"
          style="width: 300px"
        >
          <el-option
            v-for="column in availableColumns"
            :key="column.key"
            :label="column.title"
            :value="column.key"
          >
            <div class="column-option">
              <span>{{ column.title }}</span>
              <span class="column-type">{{ column.type }}</span>
            </div>
          </el-option>
        </el-select>
        <el-button @click="selectAllColumns" size="small" text>
          全选
        </el-button>
        <el-button @click="clearColumnSelection" size="small" text>
          清空
        </el-button>
      </div>

      <div class="control-group">
        <label>每页显示:</label>
        <el-select v-model="pageSize" size="small" style="width: 100px">
          <el-option :label="10" :value="10" />
          <el-option :label="25" :value="25" />
          <el-option :label="50" :value="50" />
          <el-option :label="100" :value="100" />
        </el-select>
      </div>

      <div class="control-group">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索预览数据..."
          size="small"
          style="width: 200px"
          clearable
        >
          <template #prefix>
            <i class="icon-search"></i>
          </template>
        </el-input>
      </div>

      <div class="control-group">
        <el-button @click="toggleViewMode" size="small">
          <i :class="viewMode === 'table' ? 'icon-grid' : 'icon-list'"></i>
          {{ viewMode === 'table' ? '卡片视图' : '表格视图' }}
        </el-button>
      </div>
    </div>

    <!-- 预览内容 -->
    <div class="preview-content">
      <div v-if="loading" class="preview-loading">
        <div class="loading-animation">
          <div class="loading-spinner"></div>
          <div class="loading-text">正在加载预览数据...</div>
        </div>
      </div>

      <div v-else-if="filteredData.length === 0" class="preview-empty">
        <div class="empty-icon">
          <i class="icon-inbox"></i>
        </div>
        <div class="empty-text">
          <h4>暂无数据</h4>
          <p>{{ searchKeyword ? '未找到匹配的数据' : '该时间范围内暂无数据' }}</p>
        </div>
      </div>

      <!-- 表格视图 -->
      <div v-else-if="viewMode === 'table'" class="table-view">
        <div class="table-wrapper">
          <el-table
            :data="paginatedData"
            stripe
            border
            size="small"
            :max-height="500"
            @sort-change="handleSortChange"
          >
            <el-table-column
              v-for="column in displayColumns"
              :key="column.key"
              :prop="column.key"
              :label="column.title"
              :width="column.width"
              :align="column.align || 'left'"
              :sortable="column.sortable"
              show-overflow-tooltip
            >
              <template #default="{ row, column: col }">
                <div class="cell-content">
                  <span v-if="formatCellValue(row[col.property], column)">
                    {{ formatCellValue(row[col.property], column) }}
                  </span>
                  <span v-else class="empty-value">—</span>
                </div>
              </template>
            </el-table-column>

            <!-- 操作列 -->
            <el-table-column label="操作" width="80" fixed="right">
              <template #default="{ row }">
                <el-button
                  @click="viewRowDetail(row)"
                  size="small"
                  text
                  type="primary"
                >
                  详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 分页 -->
        <div class="table-pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 25, 50, 100]"
            :total="filteredData.length"
            layout="total, sizes, prev, pager, next, jumper"
            small
          />
        </div>
      </div>

      <!-- 卡片视图 -->
      <div v-else class="card-view">
        <div class="card-grid">
          <div
            v-for="(item, index) in paginatedData"
            :key="index"
            class="data-card"
          >
            <div class="card-header">
              <div class="card-title">
                {{ getCardTitle(item) }}
              </div>
              <div class="card-time">
                {{ formatTime(getCardTime(item)) }}
              </div>
            </div>
            <div class="card-content">
              <div
                v-for="column in displayColumns.slice(0, 4)"
                :key="column.key"
                class="card-field"
              >
                <div class="field-label">{{ column.title }}</div>
                <div class="field-value">
                  {{ formatCellValue(item[column.key], column) || '—' }}
                </div>
              </div>
            </div>
            <div class="card-actions">
              <el-button @click="viewRowDetail(item)" size="small" text>
                查看详情
              </el-button>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div class="card-pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 25, 50, 100]"
            :total="filteredData.length"
            layout="total, sizes, prev, pager, next, jumper"
            small
          />
        </div>
      </div>
    </div>

    <!-- 数据详情模态框 -->
    <el-dialog
      v-model="detailVisible"
      title="数据详情"
      width="600px"
      :destroy-on-close="true"
    >
      <div v-if="selectedRow" class="detail-content">
        <div class="detail-fields">
          <div
            v-for="column in availableColumns"
            :key="column.key"
            class="detail-field"
          >
            <div class="field-label">{{ column.title }}</div>
            <div class="field-value">
              {{ formatCellValue(selectedRow[column.key], column) || '—' }}
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button @click="copyRowData" type="primary">
          <i class="icon-copy"></i>
          复制数据
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 接口定义
interface DataPreviewColumn {
  key: string
  title: string
  type: string
  width?: number
  align?: 'left' | 'center' | 'right'
  sortable?: boolean
  formatter?: (value: any) => string
}

interface DataQuality {
  score: number
  completeness: number
  accuracy: number
  consistency: number
  issues?: Array<{
    id: string
    message: string
    severity: 'low' | 'medium' | 'high'
    count: number
  }>
}

interface Props {
  data: any[]
  columns: DataPreviewColumn[]
  loading?: boolean
  totalRecords?: number
  estimatedSize?: string
  dataQuality?: DataQuality
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  totalRecords: 0,
  estimatedSize: '',
  dataQuality: undefined
})

interface Emits {
  (e: 'close'): void
  (e: 'refresh'): void
  (e: 'export'): void
}

const emit = defineEmits<Emits>()

// 响应式数据
const viewMode = ref<'table' | 'card'>('table')
const selectedColumns = ref<string[]>([])
const pageSize = ref(25)
const currentPage = ref(1)
const searchKeyword = ref('')
const sortField = ref('')
const sortOrder = ref<'asc' | 'desc'>()
const detailVisible = ref(false)
const selectedRow = ref<any>(null)

// 计算属性
const availableColumns = computed(() => props.columns || [])

const displayColumns = computed(() => {
  if (selectedColumns.value.length === 0) {
    return availableColumns.value.slice(0, 8) // 默认显示前8列
  }
  return availableColumns.value.filter(col =>
    selectedColumns.value.includes(col.key)
  )
})

const filteredData = computed(() => {
  let data = props.data || []

  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    data = data.filter(row =>
      displayColumns.value.some(col => {
        const value = row[col.key]
        return value && String(value).toLowerCase().includes(keyword)
      })
    )
  }

  // 排序
  if (sortField.value) {
    data = [...data].sort((a, b) => {
      const aVal = a[sortField.value]
      const bVal = b[sortField.value]

      let result = 0
      if (aVal < bVal) result = -1
      if (aVal > bVal) result = 1

      return sortOrder.value === 'desc' ? -result : result
    })
  }

  return data
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

const displayRecords = computed(() => filteredData.value.length)

// 方法
const getQualityStatus = (score: number) => {
  if (score >= 90) return 'success'
  if (score >= 70) return 'warning'
  return 'exception'
}

const getIssueIcon = (severity: string) => {
  const icons = {
    low: 'icon-info',
    medium: 'icon-alert-triangle',
    high: 'icon-x-circle'
  }
  return icons[severity] || 'icon-info'
}

const formatCellValue = (value: any, column: DataPreviewColumn) => {
  if (value === null || value === undefined || value === '') {
    return ''
  }

  // 自定义格式化
  if (column.formatter) {
    return column.formatter(value)
  }

  // 根据类型格式化
  switch (column.type) {
    case 'datetime':
      return formatTime(value)
    case 'number':
      return formatNumber(value)
    case 'percentage':
      return formatPercentage(value)
    default:
      return String(value)
  }
}

const formatTime = (time: string | Date) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString()
}

const formatNumber = (num: number) => {
  if (typeof num !== 'number') return String(num)
  return num.toLocaleString()
}

const formatPercentage = (num: number) => {
  if (typeof num !== 'number') return String(num)
  return `${(num * 100).toFixed(2)}%`
}

const getCardTitle = (item: any) => {
  // 尝试找到适合作为标题的字段
  const titleFields = ['station_name', 'device_name', 'name', 'title']
  for (const field of titleFields) {
    if (item[field]) return item[field]
  }
  return `数据记录 ${item.id || ''}`
}

const getCardTime = (item: any) => {
  // 尝试找到时间字段
  const timeFields = ['timestamp', 'created_at', 'updated_at', 'time']
  for (const field of timeFields) {
    if (item[field]) return item[field]
  }
  return ''
}

const handleSortChange = ({ prop, order }: { prop: string; order: string | null }) => {
  sortField.value = prop
  sortOrder.value = order === 'descending' ? 'desc' : 'asc'
}

const selectAllColumns = () => {
  selectedColumns.value = availableColumns.value.map(col => col.key)
}

const clearColumnSelection = () => {
  selectedColumns.value = []
}

const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'table' ? 'card' : 'table'
}

const viewRowDetail = (row: any) => {
  selectedRow.value = row
  detailVisible.value = true
}

const copyRowData = async () => {
  if (!selectedRow.value) return

  const data = JSON.stringify(selectedRow.value, null, 2)
  try {
    await navigator.clipboard.writeText(data)
    ElMessage.success('数据已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const refreshPreview = () => {
  emit('refresh')
}

const exportPreview = () => {
  emit('export')
}

const closePreview = () => {
  emit('close')
}

// 监听变化
watch(() => props.columns, () => {
  // 当列变化时，重置选中的列
  selectedColumns.value = []
}, { immediate: true })

watch(searchKeyword, () => {
  // 搜索时重置到第一页
  currentPage.value = 1
})

watch(pageSize, () => {
  // 页面大小变化时重置到第一页
  currentPage.value = 1
})

// 初始化
onMounted(() => {
  // 默认选择前几列
  if (availableColumns.value.length > 0) {
    selectedColumns.value = availableColumns.value
      .slice(0, Math.min(8, availableColumns.value.length))
      .map(col => col.key)
  }
})
</script>

<style scoped>
.smart-data-preview {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* 预览头部 */
.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e4e7ed;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.header-left h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.preview-stats {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.header-right .preview-actions {
  display: flex;
  gap: 8px;
}

/* 数据质量面板 */
.data-quality-panel {
  padding: 20px 24px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
}

.quality-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.quality-header h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.quality-score {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-label {
  font-weight: 600;
  color: #303133;
}

.quality-details {
  margin-bottom: 16px;
}

.quality-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.quality-label {
  min-width: 60px;
  font-size: 14px;
  color: #606266;
}

.quality-value {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.quality-value .el-progress {
  flex: 1;
}

.quality-issues {
  padding: 12px;
  background: #fef0f0;
  border-radius: 6px;
  border-left: 3px solid #f56c6c;
}

.issues-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #f56c6c;
  margin-bottom: 8px;
}

.issue-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  font-size: 14px;
}

.issue-item.high {
  color: #f56c6c;
}

.issue-item.medium {
  color: #e6a23c;
}

.issue-item.low {
  color: #909399;
}

.issue-count {
  margin-left: auto;
  font-size: 12px;
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 10px;
}

.more-issues {
  font-size: 12px;
  color: #909399;
  font-style: italic;
}

/* 预览控制栏 */
.preview-controls {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px 24px;
  background: #fafbfc;
  border-bottom: 1px solid #e4e7ed;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-group label {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  white-space: nowrap;
}

.column-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.column-type {
  font-size: 12px;
  color: #909399;
  background: #f0f2f5;
  padding: 2px 6px;
  border-radius: 4px;
}

/* 预览内容 */
.preview-content {
  min-height: 400px;
}

.preview-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
}

.loading-animation {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e4e7ed;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  color: #606266;
  font-size: 14px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.preview-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: #909399;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-text h4 {
  font-size: 16px;
  margin: 0 0 8px 0;
  color: #606266;
}

.empty-text p {
  margin: 0;
  font-size: 14px;
}

/* 表格视图 */
.table-view {
  padding: 0;
}

.table-wrapper {
  overflow-x: auto;
}

.cell-content {
  line-height: 1.4;
}

.empty-value {
  color: #c0c4cc;
  font-style: italic;
}

.table-pagination {
  padding: 16px 24px;
  display: flex;
  justify-content: center;
  border-top: 1px solid #e4e7ed;
}

/* 卡片视图 */
.card-view {
  padding: 20px 24px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.data-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background: white;
  transition: all 0.2s ease;
}

.data-card:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.card-title {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.card-time {
  font-size: 12px;
  color: #909399;
}

.card-content {
  margin-bottom: 12px;
}

.card-field {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  font-size: 13px;
}

.field-label {
  color: #909399;
  min-width: 80px;
}

.field-value {
  color: #303133;
  text-align: right;
  flex: 1;
}

.card-actions {
  text-align: right;
}

.card-pagination {
  display: flex;
  justify-content: center;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

/* 详情模态框 */
.detail-content {
  max-height: 500px;
  overflow-y: auto;
}

.detail-fields {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.detail-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.detail-field .field-label {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.detail-field .field-value {
  color: #606266;
  font-size: 14px;
  word-break: break-all;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .preview-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .preview-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .control-group {
    flex-direction: column;
    align-items: stretch;
  }

  .card-grid {
    grid-template-columns: 1fr;
  }

  .table-pagination,
  .card-pagination {
    padding: 12px;
  }

  .el-pagination {
    justify-content: center;
  }
}
</style>