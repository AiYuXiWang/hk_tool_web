<template>
  <div class="app-layout">
    <!-- 应用头部 -->
    <header class="app-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="app-title">
            <el-icon><Setting /></el-icon>
            环控平台维护工具
          </h1>
          <el-tag class="version-tag" type="info">Web版 v1.0</el-tag>
        </div>
        <div class="header-right">
          <el-tag class="operator-tag" type="success">
            <el-icon><User /></el-icon>
            {{ operatorId }}
          </el-tag>
          <el-tooltip content="深色主题" placement="bottom">
            <el-switch
              v-model="isDarkTheme"
              size="small"
              inline-prompt
              active-text="暗"
              inactive-text="明"
            />
          </el-tooltip>
        </div>
      </div>
    </header>

    <!-- 标签页导航 -->
    <nav class="nav-tabs">
      <el-tabs v-model="activeTab" class="main-tabs">
        <el-tab-pane name="device">
          <template #label>
            <span class="tab-label">
              <el-icon><Monitor /></el-icon>
              设备控制
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="cockpit">
          <template #label>
            <span class="tab-label">
              <el-icon><DataAnalysis /></el-icon>
              能源驾驶舱
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="export">
          <template #label>
            <span class="tab-label">
              <el-icon><Download /></el-icon>
              数据导出
            </span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </nav>

    <!-- 主要内容区域 -->
    <main class="app-main">
      <!-- 设备控制页面 -->
      <div v-show="activeTab === 'device'" class="device-control-page">
        <div class="device-layout">
          <!-- 左侧设备树面板 -->
          <aside class="device-sidebar" :class="{ collapsed: sidebarCollapsed }">
            <div class="sidebar-header">
              <h3 class="sidebar-title">
                <el-icon><List /></el-icon>
                设备树
              </h3>
              <div class="sidebar-actions">
                <el-button 
                  size="small" 
                  @click="loadDeviceTree()" 
                  :loading="loadingTree" 
                  type="primary"
                  class="action-btn"
                  aria-label="刷新设备树"
                  aria-controls="device-tree"
                >
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
                <el-button 
                  size="small" 
                  @click="loadDeviceTree(true)" 
                  :loading="loadingTree" 
                  type="warning"
                  class="action-btn"
                  aria-label="测试加载设备树"
                  aria-controls="device-tree"
                >
                  <el-icon><DataAnalysis /></el-icon>
                  测试
                </el-button>
                <el-button 
                  size="small" 
                  text
                  @click="sidebarCollapsed = !sidebarCollapsed"
                  class="action-btn"
                  aria-label="折叠或展开侧栏"
                >
                  {{ sidebarCollapsed ? '展开侧栏' : '折叠侧栏' }}
                </el-button>
              </div>
            </div>

            <!-- 筛选和选择器 -->
            <div class="filter-section">
              <div class="search-box">
                <el-input 
                  v-model="filter" 
                  placeholder="搜索设备或点位..."
                  size="small"
                  clearable
                  class="filter-input"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
              </div>
              
              <div class="selector-group">
                <div class="selector-item">
                  <label class="selector-label">线路</label>
                  <el-select 
                    v-model="selectedLine" 
                    placeholder="选择线路" 
                    size="small" 
                    @change="onLineChange"
                    class="selector"
                  >
                    <el-option 
                      v-for="(stations, line) in lineConfigs" 
                      :key="line" 
                      :label="line" 
                      :value="line" 
                    />
                  </el-select>
                </div>
                
                <div class="selector-item">
                  <label class="selector-label">车站</label>
                  <el-select 
                    v-model="selectedStation" 
                    placeholder="选择车站" 
                    size="small" 
                    @change="onStationChange"
                    class="selector"
                  >
                    <el-option 
                      v-for="st in stationsForLine" 
                      :key="st.station_ip" 
                      :label="st.station_name || st.station_ip" 
                      :value="st.station_ip" 
                    />
                  </el-select>
                </div>
              </div>
            </div>

            <!-- 设备树 -->
            <div class="tree-container">
              <el-scrollbar class="tree-scrollbar">
                <el-tree
                  id="device-tree"
                  :data="treeDataFiltered"
                  node-key="id"
                  :props="{ label: 'label', children: 'children' }"
                  highlight-current
                  :default-expanded-keys="defaultExpandedKeys"
                  @node-click="onNodeClick"
                  class="device-tree"
                  v-loading="loadingTree"
                  element-loading-text="加载设备数据..."
                  role="tree"
                  aria-label="设备树导航"
                >
                  <template #default="{ node, data }">
                    <div class="tree-node-content" role="treeitem" :aria-selected="node.isCurrent" tabindex="0">
                      <el-icon v-if="isPointNode(data)" class="node-icon point-icon">
                        <Aim />
                      </el-icon>
                      <el-icon v-else-if="data.meta?.object_type === 'device'" class="node-icon device-icon">
                        <Monitor />
                      </el-icon>
                      <el-icon v-else class="node-icon folder-icon">
                        <Folder />
                      </el-icon>
                      
                      <span 
                        class="node-label"
                        :class="{
                          'exceptional-node': isExceptionalNode(data),
                          'point-node': isPointNode(data),
                          'writable-point': isPointNode(data) && data.meta?.is_writable
                        }"
                        :title="getNodeTooltip(data)"
                      >
                        {{ data.label }}
                      </span>
                      
                      <el-tag 
                        v-if="isPointNode(data) && data.meta?.is_writable" 
                        size="small" 
                        type="success" 
                        class="writable-tag"
                      >
                        可写
                      </el-tag>
                    </div>
                  </template>
                </el-tree>
              </el-scrollbar>
            </div>
          </aside>

          <!-- 主内容区域 -->
          <div class="device-main">
            <!-- 查询控制面板 -->
            <div class="query-panel">
              <div class="panel-header">
                <h3 class="panel-title">
                  <el-icon><Search /></el-icon>
                  实时查询
                </h3>
                <div class="query-actions">
                  <div class="input-group">
                    <div class="input-item">
                      <label class="input-label">设备编码</label>
                      <el-input
                        v-model="query.object_code"
                        placeholder="请输入object_code"
                        size="small"
                        class="query-input"
                        clearable
                      />
                    </div>
                    <div class="input-item">
                      <label class="input-label">点位编码</label>
                      <el-input
                        v-model="query.data_code"
                        placeholder="请输入data_code"
                        size="small"
                        class="query-input"
                        clearable
                      />
                    </div>
                    <el-button 
                      type="primary" 
                      @click="fetchRealtime" 
                      :loading="loadingQuery"
                      :disabled="!query.object_code || !query.data_code"
                      class="query-btn"
                    >
                      <el-icon><Search /></el-icon>
                      查询实时值
                    </el-button>
                    <el-button
                      type="success"
                      @click="addSelectedToBatch"
                      :disabled="!query.object_code || !query.data_code"
                      class="query-btn"
                    >
                      <el-icon><Edit /></el-icon>
                      加入批量
                    </el-button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 数据显示区域 -->
            <div class="data-display">
              <!-- 实时数据表格 -->
              <div class="data-table-section">
                <div class="section-header">
                  <h4 class="section-title">
                    <el-icon><DataBoard /></el-icon>
                    点位实时数据
                  </h4>
                  <el-button 
                    type="success" 
                    size="small" 
                    @click="openBatch = true"
                    class="action-btn"
                  >
                    <el-icon><Edit /></el-icon>
                    批量写值
                  </el-button>
                </div>
                
                <div class="table-container">
                  <el-table 
                    :data="tableRows" 
                    v-loading="loadingQuery"
                    element-loading-text="正在查询数据..."
                    :height="tableHeight"
                    class="data-table"
                    stripe
                    border
                  >
                    <el-table-column prop="object_code" label="设备编码" width="140" fixed="left">
                      <template #default="{ row }">
                        <el-tag type="info" size="small">{{ row.object_code }}</el-tag>
                      </template>
                    </el-table-column>
                    
                    <el-table-column prop="data_code" label="点位编码" width="160">
                      <template #default="{ row }">
                        <code class="code-text">{{ row.data_code }}</code>
                      </template>
                    </el-table-column>
                    
                    <el-table-column prop="value" label="当前值" width="120" align="center">
                      <template #default="{ row }">
                        <div class="value-cell">
                          <span 
                            class="value-text"
                            :class="{
                              'value-error': row.severity === 'error',
                              'value-warning': row.severity === 'warn',
                              'value-normal': row.severity === 'ok'
                            }"
                          >
                            {{ formatValue(row.value) }}
                          </span>
                          <span v-if="row.unit" class="unit-text">{{ row.unit }}</span>
                        </div>
                      </template>
                    </el-table-column>

                    <el-table-column label="快速写值" width="140" align="center">
                      <template #default="{ row }">
                        <el-button 
                          size="small" 
                          type="warning" 
                          @click="quickWrite(row)"
                          class="write-btn"
                        >
                          <el-icon><Edit /></el-icon>
                          写值
                        </el-button>
                      </template>
                    </el-table-column>
                    
                    <el-table-column label="操作" width="120" align="center" fixed="right">
                      <template #default="{ row }">
                        <el-button 
                          size="small" 
                          type="primary" 
                          @click="refreshRow(row)"
                          class="refresh-btn"
                        >
                          <el-icon><Refresh /></el-icon>
                          刷新
                        </el-button>
                      </template>
                    </el-table-column>
                    
                    <template #empty>
                      <div class="empty-state">
                        <el-icon class="empty-icon"><Search /></el-icon>
                        <p class="empty-text">请选择点位并查询实时数据</p>
                      </div>
                    </template>
                  </el-table>
                </div>
              </div>
              
              <!-- 操作日志面板 -->
              <div class="operation-logs-section">
                <div class="section-header">
                  <h4 class="section-title">
                    <el-icon><Document /></el-icon>
                    操作日志
                  </h4>
                </div>
                <div class="logs-container">
                  <div 
                    v-for="(log, index) in operationLogs" 
                    :key="index" 
                    class="log-item"
                    :class="{
                      'log-success': log.type === 'success',
                      'log-error': log.type === 'error',
                      'log-warning': log.type === 'warning',
                      'log-info': log.type === 'info'
                    }"
                  >
                    <span class="log-time">{{ log.time }}</span>
                    <span class="log-message">{{ log.message }}</span>
                  </div>
                  <div v-if="operationLogs.length === 0" class="empty-logs">
                    <el-icon><Document /></el-icon>
                    <p>暂无操作日志</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 数据导出页面 -->
      <div v-show="activeTab === 'export'" class="export-page">
        <DataExport />
      </div>

      <!-- 能源驾驶舱页面 -->
      <div v-show="activeTab === 'cockpit'" class="export-page">
        <EnergyCockpit />
      </div>
    </main>

    <!-- 批量写值对话框 -->
    <el-dialog
      v-model="openBatch"
      title="批量写值"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="batch-dialog-content">
        <div class="batch-input-section">
          <h4>添加写值命令</h4>
          <el-form :model="batchForm" label-width="100px" size="small">
            <el-form-item label="设备编码">
              <el-input v-model="batchForm.object_code" placeholder="请输入object_code" />
            </el-form-item>
            <el-form-item label="点位编码">
              <el-input v-model="batchForm.data_code" placeholder="请输入data_code" />
            </el-form-item>
            <el-form-item label="写入值">
              <el-input v-model="batchForm.value" placeholder="请输入要写入的值" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="addBatchCommand" size="small">
                <el-icon><Plus /></el-icon>
                添加命令
              </el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <div class="batch-commands-section">
          <h4>待执行命令列表 ({{ batchCommands.length }})</h4>
          <el-table :data="batchCommands" size="small" height="200px" border>
            <el-table-column prop="object_code" label="设备编码" width="120" />
            <el-table-column prop="data_code" label="点位编码" width="120" />
            <el-table-column prop="value" label="写入值" width="100" />
            <el-table-column label="操作" width="80">
              <template #default="{ $index }">
                <el-button 
                  type="danger" 
                  size="small" 
                  @click="removeBatchCommand($index)"
                  :icon="Delete"
                />
              </template>
            </el-table-column>
          </el-table>
          <div class="batch-progress-section" style="margin-top: 8px;">
            <el-alert v-if="batchWriting" type="info" :closable="false" show-icon>
              <template #title>
                正在执行批量写值：{{ batchProgress.done }}/{{ batchProgress.total }}，成功 {{ batchProgress.success }}，失败 {{ batchProgress.failed }}
              </template>
            </el-alert>
            <el-progress
              v-if="batchWriting"
              :percentage="Math.round((batchProgress.done / (batchProgress.total || 1)) * 100)"
              :status="batchProgress.failed > 0 ? 'exception' : (batchProgress.done === batchProgress.total ? 'success' : undefined)"
              style="margin-top: 8px;"
            />
            <div v-else-if="batchProgress.total > 0" class="progress-summary">
              上次执行：总数 {{ batchProgress.total }}，成功 {{ batchProgress.success }}，失败 {{ batchProgress.failed }}
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="openBatch = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="executeBatchWrite" 
            :loading="batchWriting"
            :disabled="batchCommands.length === 0"
          >
            <el-icon><Edit /></el-icon>
            执行批量写值 ({{ batchCommands.length }})
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Lightning, 
  Monitor, 
  Download, 
  Aim,
  Setting,
  User,
  Refresh,
  List,
  DataAnalysis,
  Search,
  Folder,
  Edit,
  DataBoard,
  Plus,
  Delete,
  Document
} from '@element-plus/icons-vue'
import { fetchRealtimeValue, batchWritePoints, fetchDeviceTree, getSeverityColor, fetchLineConfigs, exportElectricityData, exportSensorData, fetchDefaultPoints, setStationIp } from './api/control'
import DataExport from './views/DataExport.vue'
import EnergyCockpit from './views/EnergyCockpit.vue'

const activeTab = ref('cockpit')
const operatorId = ref('web-admin')
const isDarkTheme = ref(false)
const sidebarCollapsed = ref(false)
const filter = ref('')
const treeData = ref([])
const pointMeta = ref({})
const loadingTree = ref(false)
const lineConfigs = ref({})
const selectedLine = ref('')
const selectedStation = ref('')
const defaultExpandedKeys = ref([])
const query = ref({ object_code: '', data_code: '' })
const loadingQuery = ref(false)
const tableRows = ref([])
const openBatch = ref(false)
const tableHeight = computed(() => Math.round(window.innerHeight * 0.4))
// 操作日志与批量进度
const operationLogs = ref([])
const batchProgress = ref({ total: 0, done: 0, success: 0, failed: 0 })
// 点位数据源缓存（key: object_code|data_code -> 1|2|3）
const dataSourceCache = ref<Record<string, 1 | 2 | 3>>({})

// 批量写值相关状态
const batchForm = ref({
  object_code: '',
  data_code: '',
  value: ''
})
const batchCommands = ref([])
const batchWriting = ref(false)

// 数据导出相关状态
const exportActiveTab = ref('electricity')
const electricityForm = ref({
  line: '',
  start_time: null,
  end_time: null
})
const sensorForm = ref({
  line: '',
  start_time: null,
  end_time: null
})
// 下载中心已移除：相关状态与方法删除
const electricityExporting = ref(false)
const sensorExporting = ref(false)
const exportLogs = ref([])
const exportLogContainer = ref(null)

const treeDataFiltered = computed(() => {
  const q = filter.value.trim()
  if (!q) return treeData.value
  const match = (node) => node.label.toLowerCase().includes(q.toLowerCase())
  const walk = (nodes) => nodes.map(n => {
    if (!n.children) return match(n) ? n : null
    const kids = walk(n.children).filter(Boolean)
    if (kids.length || match(n)) return { ...n, children: kids }
    return null
  }).filter(Boolean)
  return walk(treeData.value)
})

const stationsForLine = computed(() => {
  const arr = lineConfigs.value[selectedLine.value] || []
  return Array.isArray(arr) ? arr : []
})

const availableLines = computed(() => {
  // 只返回真正的线路名称，过滤掉非线路数据
  const lineNames = Object.keys(lineConfigs.value)
  // 线路名称通常以M开头，如M1, M2, M3等
  return lineNames.filter(name => /^M\d+$/.test(name))
})

const exceptionalStations = computed(() => {
  const set = new Set()
  for (const r of tableRows.value) {
    if (r && (r.severity === 'error' || r.status === 'failed')) {
      if (r.object_code) set.add(r.object_code)
    }
  }
  return set
})

function isExceptionalNode(data) {
  if (data && data.children) {
    return exceptionalStations.value.has(data.id)
  }
  const oc = data?.meta?.object_code
  return oc ? exceptionalStations.value.has(oc) : false
}

function isPointNode(data) {
  return !data.children && data.meta && data.meta.data_code
}

function getNodeTooltip(data) {
  if (isPointNode(data)) {
    const meta = data.meta
    const writable = meta.is_writable ? '可写' : '只读'
    const unit = meta.unit ? ` (${meta.unit})` : ''
    return `点位: ${meta.object_code}:${meta.data_code}${unit} - ${writable}\n点击填入查询框`
  }
  return data.meta?.object_name || data.label
}

function formatValue(value) {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'number') {
    return Number.isInteger(value) ? value.toString() : value.toFixed(2)
  }
  return String(value)
}

async function loadDeviceTree(forceTest = false) {
  loadingTree.value = true
  try {
    const res = await fetchDeviceTree(
      forceTest ? { forceTest: true } :
      (selectedStation.value ? { station_ip: selectedStation.value } : undefined)
    )
    const source = Array.isArray(res) ? res : (res.tree || [])
    
    if (forceTest) {
      ElMessage.success('已切换为测试树数据')
    }
    
    treeData.value = source
    defaultExpandedKeys.value = source.map(n => String(n.id))
    
  } catch (error) {
    console.error('加载设备树失败:', error)
    ElMessage.error('加载设备树失败')
  } finally {
    loadingTree.value = false
  }
}

function onLineChange() {
  const stations = lineConfigs.value[selectedLine.value] || []
  const firstStation = stations[0]
  selectedStation.value = firstStation && firstStation.station_ip ? firstStation.station_ip : ''
  // 切换线路时同步设置站点请求头
  setStationIp(selectedStation.value || '')
  loadDeviceTree(false)
}

function onStationChange() {
  if (selectedStation.value) {
    // 站点切换时更新请求头，后续查询与写值使用对应站点
    setStationIp(selectedStation.value)
    loadDeviceTree(false)
  }
}

function onNodeClick(node) {
  if (!node.children && node.meta?.data_code) {
    const oc = node.meta.object_code
    const dc = node.meta.data_code
    query.value = { object_code: oc, data_code: dc }
    // 缓存点位元数据用于后续校验与高亮
    const k = oc + '|' + dc
    pointMeta.value[k] = { ...(pointMeta.value[k] || {}), ...(node.meta || {}) }
    ElMessage.success(`已填入: ${oc}:${dc}`)
  }
}

async function fetchRealtime() {
  if (!query.value.object_code || !query.value.data_code) return
  loadingQuery.value = true
  const oc = query.value.object_code
  const dc = query.value.data_code
  try {
    const d = await fetchRealtimeValue(query.value.object_code, query.value.data_code)
    const k = oc + '|' + dc
    const meta = pointMeta.value[k] || {}
    const sev = typeof d.value === 'number'
      ? getSeverityColor(d.value, meta.warn_min ?? null, meta.warn_max ?? null, meta.error_min ?? null, meta.error_max ?? null)
      : 'ok'
    const newRow = {
      object_code: d.object_code,
      data_code: d.data_code,
      value: d.value ?? null,
      setpoint: null,
      unit: d.unit ?? meta.unit ?? '',
      ts: d.ts,
      status: 'ok',
      severity: sev
    }
    const idx = tableRows.value.findIndex(r => r.object_code === newRow.object_code && r.data_code === newRow.data_code)
    if (idx >= 0) {
      tableRows.value[idx] = newRow
    } else {
      tableRows.value.push(newRow)
    }
  } catch (e) {
    const failedRow = {
      object_code: query.value.object_code,
      data_code: query.value.data_code,
      value: null,
      setpoint: null,
      unit: '',
      ts: new Date().toISOString(),
      status: 'failed',
      severity: 'error'
    }
    const idx = tableRows.value.findIndex(r => r.object_code === failedRow.object_code && r.data_code === failedRow.data_code)
    if (idx >= 0) {
      tableRows.value[idx] = failedRow
    } else {
      tableRows.value.push(failedRow)
    }
  } finally {
    loadingQuery.value = false
  }
}

// 查询并解析点位的 data_source，优先使用缓存与已知元信息
async function resolveDataSource(oc: string, dc: string): Promise<1 | 2 | 3 | undefined> {
  const k = oc + '|' + dc
  // 1) 元信息中可能已包含 data_source（例如设备树或默认点位返回）
  const meta = getMeta(oc, dc)
  const metaDs = (meta && (meta as any).data_source) as 1 | 2 | 3 | undefined
  if (metaDs === 1 || metaDs === 2 || metaDs === 3) {
    dataSourceCache.value[k] = metaDs
    return metaDs
  }
  // 2) 本地缓存
  const cached = dataSourceCache.value[k]
  if (cached === 1 || cached === 2 || cached === 3) return cached
  // 3) 远程查询默认点位元数据并匹配 data_source
  try {
    // 确保站点头已设置（在 onStationChange/onLineChange 中也会设置）
    if (selectedStation.value) setStationIp(selectedStation.value)
    const resp = await fetchDefaultPoints([oc])
    const items = Array.isArray((resp as any)?.items) ? (resp as any).items : (Array.isArray(resp) ? (resp as any) : [])
    const found = items.find((it: any) => (it?.object_code === oc && it?.data_code === dc) || it?.point_key === `${oc}:${dc}`)
    const ds: 1 | 2 | 3 | undefined = found?.data_source as any
    if (ds === 1 || ds === 2 || ds === 3) {
      dataSourceCache.value[k] = ds
      // 同步写入元信息，便于后续使用
      pointMeta.value[k] = { ...(pointMeta.value[k] || {}), ...(found || {}), data_source: ds }
      return ds
    }
  } catch (e) {
    console.warn('查询点位数据源失败:', e)
  }
  return undefined
}

async function refreshRow(row) {
  query.value = { object_code: row.object_code, data_code: row.data_code }
  await fetchRealtime()
}

// 批量写值功能
function addSelectedToBatch() {
  if (!query.value.object_code || !query.value.data_code) {
    ElMessage.warning('请先选择点位或输入设备与点位编码')
    return
  }
  openBatch.value = true
  batchForm.value.object_code = query.value.object_code
  batchForm.value.data_code = query.value.data_code
  // 预填写入值：若表格已有查询结果，则预填当前值，便于调整
  if (Array.isArray(tableRows.value) && tableRows.value.length > 0) {
    const r = tableRows.value.find(x => x.object_code === query.value.object_code && x.data_code === query.value.data_code)
    if (r) {
      batchForm.value.value = r.value ?? ''
    }
  }
}

function addBatchCommand() {
  if (!batchForm.value.object_code || !batchForm.value.data_code || batchForm.value.value === '') {
    ElMessage.warning('请填写完整的命令信息')
    return
  }
  const vres = validateControlValue(batchForm.value.object_code, batchForm.value.data_code, batchForm.value.value)
  if (!vres.ok) {
    ElMessage.error(vres.message || '输入值不合法')
    return
  }
  
  const command = {
    object_code: batchForm.value.object_code.trim(),
    data_code: batchForm.value.data_code.trim(),
    value: batchForm.value.value.trim(),
    point_key: `${batchForm.value.object_code.trim()}:${batchForm.value.data_code.trim()}`
  }
  
  batchCommands.value.push(command)
  
  // 清空表单
  batchForm.value = {
    object_code: '',
    data_code: '',
    value: ''
  }
  
  ElMessage.success(`已添加命令: ${command.point_key} = ${command.value}`)
}

function removeBatchCommand(index) {
  batchCommands.value.splice(index, 1)
  ElMessage.info('已移除命令')
}

async function executeBatchWrite() {
  if (batchCommands.value.length === 0) {
    ElMessage.warning('没有要执行的命令')
    return
  }
  // 基础输入校验：逐项检查类型与范围
  for (const cmd of batchCommands.value) {
    const vres = validateControlValue(cmd.object_code, cmd.data_code, cmd.value)
    if (!vres.ok) {
      ElMessage.error(`命令 ${cmd.object_code}:${cmd.data_code} 不合法：${vres.message}`)
      return
    }
  }
  
  batchWriting.value = true
  batchProgress.value = { total: batchCommands.value.length, done: 0, success: 0, failed: 0 }
  
  try {
    // 先解析每个命令的 data_source
    const dsList = await Promise.all(batchCommands.value.map(cmd => resolveDataSource(cmd.object_code, cmd.data_code)))
    const unresolvedIndex = dsList.findIndex(ds => ds !== 1 && ds !== 2 && ds !== 3)
    if (unresolvedIndex >= 0) {
      const bad = batchCommands.value[unresolvedIndex]
      ElMessage.error(`无法获取点位数据源：${bad.object_code}:${bad.data_code}`)
      return
    }
    // 转换为 API 所需格式
    const commands = batchCommands.value.map((cmd, i) => ({
      point_key: cmd.point_key,
      data_source: dsList[i] as 1 | 2 | 3,
      control_value: coerceControlValue(cmd.object_code, cmd.data_code, cmd.value),
      object_code: cmd.object_code,
      data_code: cmd.data_code
    }))
    
    ElMessage.info(`开始执行 ${commands.length} 个写值命令...`)
    
    const result = await batchWritePoints(
      commands,
      selectedStation.value,
      { timeoutMs: 12000 }
    )
    
    if (result && result.items) {
      const successCount = result.items.filter(item => item.status === 'ok').length
      const failedCount = result.items.filter(item => item.status === 'failed').length
      batchProgress.value = { total: commands.length, done: commands.length, success: successCount, failed: failedCount }
      
      if (successCount === result.items.length) {
        ElMessage.success(`批量写值成功！成功: ${successCount}, 失败: ${failedCount}`)
      } else {
        ElMessage.warning(`批量写值部分成功！成功: ${successCount}, 失败: ${failedCount}`)
        
        // 显示失败详情
        const failedItems = result.items.filter(item => item.status === 'failed')
        failedItems.forEach(item => {
          console.error(`写值失败: ${item.point_key} - ${item.message}`)
        })
      }
      
      // 清空成功的命令
      batchCommands.value = batchCommands.value.filter((cmd, index) => 
        result.items[index]?.status !== 'ok'
      )
      // 操作日志记录
      const ts = new Date().toLocaleTimeString()
      operationLogs.value.push({ time: ts, type: failedCount > 0 ? 'warning' : 'success', message: `批量写值完成：总数 ${commands.length}，成功 ${successCount}，失败 ${failedCount}` })
      result.items.forEach(item => {
        operationLogs.value.push({ time: ts, type: item.status === 'ok' ? 'success' : 'error', message: `${item.point_key} → ${item.status}${item.message ? ' - ' + item.message : ''}` })
      })
      
      if (batchCommands.value.length === 0) {
        openBatch.value = false
      }
    }
  } catch (error) {
    console.error('批量写值失败:', error)
    ElMessage.error(`批量写值失败: ${error.message || error}`)
    operationLogs.value.push({ time: new Date().toLocaleTimeString(), type: 'error', message: `批量写值失败：${error.message || String(error)}` })
  } finally {
    batchWriting.value = false
  }
}

// 表格行内快速写值
async function quickWrite(row) {
  try {
    const { value } = await ElMessageBox.prompt('请输入写入值', '快速写值', {
      confirmButtonText: '执行',
      cancelButtonText: '取消',
      inputValue: row?.setpoint ?? row?.value ?? '',
    })
    if (value === undefined || value === null || String(value).trim() === '') {
      ElMessage.warning('写入值不能为空')
      return
    }
    const vres = validateControlValue(row.object_code, row.data_code, value)
    if (!vres.ok) {
      ElMessage.error(vres.message || '输入值不合法')
      return
    }
    // 解析该点位的真实数据源
    const ds = await resolveDataSource(row.object_code, row.data_code)
    if (ds !== 1 && ds !== 2 && ds !== 3) {
      ElMessage.error(`无法获取点位数据源：${row.object_code}:${row.data_code}`)
      return
    }
    const processed = coerceControlValue(row.object_code, row.data_code, value)
    const cmd = [{
      point_key: `${row.object_code}:${row.data_code}`,
      data_source: ds,
      control_value: processed,
      object_code: row.object_code,
      data_code: row.data_code,
    }]
    ElMessage.info(`正在写入: ${cmd[0].point_key} = ${processed}`)
    const result = await batchWritePoints(
      cmd,
      selectedStation.value,
      { timeoutMs: 12000 }
    )
    const ok = result && (result.items?.[0]?.status === 'ok' || result.success)
    if (ok) {
      ElMessage.success('写值成功')
      operationLogs.value.push({ time: new Date().toLocaleTimeString(), type: 'success', message: `${cmd[0].point_key} 写值成功，值=${cmd[0].control_value}` })
      await refreshRow(row)
    } else {
      const msg = result?.items?.[0]?.message || '未知错误'
      ElMessage.error(`写值失败：${msg}`)
      operationLogs.value.push({ time: new Date().toLocaleTimeString(), type: 'error', message: `${cmd[0].point_key} 写值失败 - ${msg}` })
    }
  } catch (e) {
    // 用户取消或异常
    if (e && e !== 'cancel') {
      ElMessage.error(`写值异常：${e.message || e}`)
    }
  }
}

// ===== 输入校验 =====
function getMeta(object_code, data_code) {
  const k = object_code + '|' + data_code
  return pointMeta.value[k] || {}
}

function isNumeric(val) {
  if (val === '' || val === null || val === undefined) return false
  const n = Number(val)
  return Number.isFinite(n)
}

// 写值类型规整：基于点位元数据与输入值进行类型转换
function coerceControlValue(object_code, data_code, raw) {
  const v = typeof raw === 'string' ? raw.trim() : raw
  const meta = getMeta(object_code, data_code)
  // 若存在数值阈值配置，优先按数值处理
  const hasNumericHints = [meta.warn_min, meta.warn_max, meta.error_min, meta.error_max, meta.border_min, meta.border_max]
    .some(x => x !== undefined && x !== null)
  if (hasNumericHints && isNumeric(v)) return Number(v)
  // 布尔/开关值常见格式
  if (typeof v === 'string') {
    const s = v.toLowerCase()
    if (s === 'true') return true
    if (s === 'false') return false
    if (s === 'on') return 1
    if (s === 'off') return 0
  }
  // 兜底：若是纯数字则转数字，否则原样传递
  if (isNumeric(v)) return Number(v)
  return v
}

function validateControlValue(object_code, data_code, value) {
  const meta = getMeta(object_code, data_code)
  const hasStrictBounds = (meta.error_min !== undefined && meta.error_min !== null) || (meta.error_max !== undefined && meta.error_max !== null)
  const expectNumber = hasStrictBounds || meta.data_type === 'number' || !!meta.unit
  if (expectNumber) {
    if (!isNumeric(value)) {
      return { ok: false, message: '值必须为数值类型' }
    }
    const n = Number(value)
    if (meta.error_min !== undefined && meta.error_min !== null && n < meta.error_min) {
      return { ok: false, message: `值低于下限 ${meta.error_min}` }
    }
    if (meta.error_max !== undefined && meta.error_max !== null && n > meta.error_max) {
      return { ok: false, message: `值高于上限 ${meta.error_max}` }
    }
  }
  return { ok: true }
}

// 数据导出功能
function addExportLog(message, type = 'info') {
  const now = new Date()
  const timeStr = now.toLocaleTimeString()
  exportLogs.value.push({
    time: timeStr,
    message,
    type
  })
  
  // 保持日志数量在合理范围内
  if (exportLogs.value.length > 100) {
    exportLogs.value = exportLogs.value.slice(-100)
  }

  // 日志更新后自动滚动到底部
  nextTick(() => {
    if (exportLogContainer.value) {
      exportLogContainer.value.scrollTop = exportLogContainer.value.scrollHeight
    }
  })
}

function clearExportLogs() {
  exportLogs.value = []
  ElMessage.success('日志已清空')
}

// 导出成功后触发本地下载
function downloadFile(filePath) {
  if (!filePath) return
  const filename = filePath.split('/').pop()
  const downloadUrl = `/api/download/${filename}`
  // 创建下载链接
  const link = document.createElement('a')
  link.href = downloadUrl
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

async function exportElectricityDataAction() {
  if (!electricityForm.value.line || !electricityForm.value.start_time || !electricityForm.value.end_time) {
    ElMessage.warning('请填写完整的导出参数')
    return
  }
  
  electricityExporting.value = true
  
  const request = {
    line: electricityForm.value.line,
    start_time: electricityForm.value.start_time,
    end_time: electricityForm.value.end_time
  }
  
  addExportLog(`🚀 开始导出电耗数据: 线路=${request.line}, 时间=${request.start_time} 至 ${request.end_time}`, 'info')
  
  try {
    const result = await exportElectricityData(request)
    
    if (result.success) {
      addExportLog(`✅ 电耗数据导出成功: ${result.message}`, 'success')
      
      if (result.details && result.details.results) {
        result.details.results.forEach(station => {
          if (station.success) {
            addExportLog(`✓ ${station.station_name} (${station.station_ip}): 导出成功`, 'success')
            if (station.file_path) {
              addExportLog(`└─ 文件: ${station.file_path}，已开始下载到本地`, 'info')
              downloadFile(station.file_path)
            }
          } else {
            addExportLog(`❌ ${station.station_name} (${station.station_ip}): ${station.message}`, 'error')
          }
        })
      }
    } else {
      addExportLog(`❌ 电耗数据导出失败: ${result.message}`, 'error')
      ElMessage.error(`导出失败: ${result.message}`)
    }
  } catch (error) {
    addExportLog(`❌ 导出请求失败: ${error.message}`, 'error')
    ElMessage.error(`导出请求失败: ${error.message}`)
    console.error('导出电耗数据错误:', error)
  } finally {
    electricityExporting.value = false
  }
}

async function exportSensorDataAction() {
  if (!sensorForm.value.line || !sensorForm.value.start_time || !sensorForm.value.end_time) {
    ElMessage.warning('请填写完整的导出参数')
    return
  }
  
  sensorExporting.value = true
  
  const request = {
    line: sensorForm.value.line,
    start_time: sensorForm.value.start_time,
    end_time: sensorForm.value.end_time
  }
  
  addExportLog(`🚀 开始导出传感器数据: 线路=${request.line}, 时间=${request.start_time} 至 ${request.end_time}`, 'info')
  
  try {
    const result = await exportSensorData(request)
    
    if (result.success) {
      addExportLog(`✅ 传感器数据导出成功: ${result.message}`, 'success')
      
      if (result.details && result.details.results) {
        result.details.results.forEach(station => {
          if (station.success) {
            addExportLog(`✓ ${station.station_name} (${station.station_ip}): 导出成功`, 'success')
            if (station.file_path) {
              addExportLog(`└─ 文件: ${station.file_path}，已开始下载到本地`, 'info')
              downloadFile(station.file_path)
            }
          } else {
            addExportLog(`❌ ${station.station_name} (${station.station_ip}): ${station.message}`, 'error')
          }
        })
      }
    } else {
      addExportLog(`❌ 传感器数据导出失败: ${result.message}`, 'error')
      ElMessage.error(`导出失败: ${result.message}`)
    }
  } catch (error) {
    addExportLog(`❌ 导出请求失败: ${error.message}`, 'error')
    ElMessage.error(`导出请求失败: ${error.message}`)
    console.error('导出传感器数据错误:', error)
  } finally {
    sensorExporting.value = false
  }
}

function cancelElectricityExport() {
  electricityExporting.value = false
  addExportLog('🚫 用户取消了电耗数据导出操作', 'warning')
  ElMessage.warning('已取消导出操作')
}

function cancelSensorExport() {
  sensorExporting.value = false
  addExportLog('🚫 用户取消了传感器数据导出操作', 'warning')
  ElMessage.warning('已取消导出操作')
}

onMounted(async () => {
  // 主题切换：在 html 上设置/移除 theme-dark 类
  watch(isDarkTheme, (v) => {
    const el = document.documentElement
    if (v) el.classList.add('theme-dark')
    else el.classList.remove('theme-dark')
  }, { immediate: true })

  // 首先加载线路配置
  try {
    const configs = await fetchLineConfigs()
    lineConfigs.value = configs || {}
    
    // 设置默认选择第一条线路和第一个车站
    const firstLine = Object.keys(lineConfigs.value)[0]
    if (firstLine) {
      selectedLine.value = firstLine
      const stations = lineConfigs.value[firstLine] || []
      const firstStation = stations[0]
      if (firstStation && firstStation.station_ip) {
        selectedStation.value = firstStation.station_ip
        // 设置默认车站后立即加载对应的设备树
        await loadDeviceTree(false)
        return // 已经加载了设备树，不需要再次加载
      }
    }
  } catch (error) {
    console.error('加载线路配置失败:', error)
    ElMessage.warning('线路配置加载失败，将使用测试数据')
  }
  
  // 如果没有设置默认车站，则加载默认设备树
  await loadDeviceTree()
})
</script>

<style scoped>
.app-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-background-secondary);
}

.app-header {
  background: linear-gradient(135deg, #1890FF 0%, #40A9FF 100%);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  max-width: 1600px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.app-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  color: white;
  font-size: 20px;
  font-weight: 600;
}

.version-tag {
  background: rgba(255, 255, 255, 0.2) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  color: white !important;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.operator-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(255, 255, 255, 0.15) !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  color: white !important;
}

.nav-tabs {
  background: var(--color-background-primary);
  border-bottom: 1px solid var(--color-border-secondary);
  padding: 0 24px;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
}

.app-main {
  flex: 1;
  overflow: hidden;
  padding: 24px;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
}

.device-control-page {
  height: 100%;
}

.device-layout {
  display: flex;
  height: 100%;
  gap: 24px;
  background: var(--color-background-primary);
  border-radius: 8px;
  box-shadow: var(--shadow-base);
  overflow: hidden;
}

.device-sidebar {
  width: 380px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: var(--color-background-primary);
  border-right: 1px solid var(--color-border-secondary);
  transition: width var(--duration-base) var(--ease-out);
}
.device-sidebar.collapsed {
  width: var(--sidebar-collapsed-width);
}
.device-sidebar.collapsed .filter-section,
.device-sidebar.collapsed .search-box,
.device-sidebar.collapsed .selector-group,
.device-sidebar.collapsed .sidebar-title {
  display: none;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--color-background-tertiary);
  border-bottom: 1px solid var(--color-border-secondary);
}

.sidebar-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.sidebar-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  padding: 6px 8px !important;
  min-width: auto !important;
}

.filter-section {
  padding: 16px;
  background: var(--color-background-secondary);
  border-bottom: 1px solid var(--color-border-secondary);
}

.search-box {
  margin-bottom: 16px;
}

.selector-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.selector-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.selector-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.tree-container {
  flex: 1;
  overflow-x: auto;
  overflow-y: hidden;
}

.tree-scrollbar {
  height: 100%;
}

/* 允许 el-scrollbar 内部出现横向滚动 */
.tree-scrollbar .el-scrollbar__wrap {
  overflow-x: auto !important;
}
.tree-scrollbar .el-scrollbar__view {
  width: max-content;
}

.device-tree {
  padding: 8px;
  min-width: 480px; /* 保证设备树出现水平滚动条时不挤压标签 */
}

.tree-node-content {
  display: flex;
  align-items: center;
  gap: 4px;
  width: 100%;
  padding: 4px 0;
}

.node-icon {
  flex-shrink: 0;
  font-size: 16px;
}

.point-icon {
  color: #1890FF;
}

.device-icon {
  color: #52C41A;
}

.folder-icon {
  color: #FAAD14;
}

.node-label {
  flex: 1;
  font-size: 12px;
  white-space: nowrap; /* 设备树标签不换行，允许出现水平滚动 */
}

.node-label.exceptional-node {
  color: #FF4D4F !important;
  font-weight: 600;
}

.node-label.point-node {
  color: #1890FF;
  cursor: pointer;
}

.node-label.point-node:hover {
  color: #40A9FF;
}

.node-label.writable-point {
  color: #52C41A;
}

.writable-tag {
  margin-left: auto;
  font-size: 10px !important;
  padding: 0 4px !important;
  height: 16px !important;
  line-height: 16px !important;
}

.device-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 24px;
}

.query-panel {
  margin-bottom: 24px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.query-actions {
  flex: 1;
}

.input-group {
  display: flex;
  align-items: flex-end;
  gap: 16px;
}

.input-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 160px;
}

.input-label {
  font-size: 12px;
  color: #4c4c4c;
  font-weight: 500;
}

.query-btn {
  min-width: 120px;
}

.data-display {
  flex: 1;
  display: flex;
  gap: 24px;
  overflow: hidden;
}

.data-table-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.table-container {
  flex: 1;
  overflow: hidden;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
}

.code-text {
  font-family: monospace;
  font-size: 12px;
  background: var(--color-background-tertiary);
  padding: 2px 6px;
  border-radius: 2px;
  color: var(--color-text-primary);
}

.value-cell {
  display: flex;
  align-items: center;
  gap: 4px;
}

.value-text {
  font-weight: 600;
}

.value-normal {
  color: #52C41A;
}

.value-warning {
  color: #FAAD14;
}

.value-error {
  color: #FF4D4F;
}

.unit-text {
  font-size: 11px;
  color: #8C8C8C;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 32px;
  color: #8C8C8C;
}

.empty-icon {
  font-size: 48px;
  opacity: 0.5;
}

.empty-text {
  margin: 0;
  font-size: 12px;
}

.export-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.export-header {
  margin-bottom: 12px;
  text-align: center;
  padding: 8px 0;
}

.page-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.export-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: row;
  align-items: stretch;
  gap: 16px;
}

.export-tabs {
  flex: 1 1 auto;
  overflow: hidden;
  min-height: 0;
  min-width: 0;
}

.export-main-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.export-main-tabs .el-tabs__content {
  flex: 1;
  overflow: auto;
}

.export-form-container {
  padding: 20px 24px;
  flex: 1;
  overflow: auto;
}

.export-card {
  width: 100%;
  max-width: none;
  margin: 0;
  height: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1a1a1a;
}

.page-description {
  margin: 2px 0 0 0;
  color: #8C8C8C;
  font-size: 12px;
  line-height: 1.3;
}

.logs-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.logs-container {
  flex: 1;
  overflow-y: auto;
  padding-right: 4px;
  padding-bottom: 8px; /* 防止底部日志被卡住遮挡 */
}

.export-logs .logs-container {
  max-height: 280px; /* 导出页面日志区固定高度并可滚动 */
}

.log-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 12px;
  line-height: 1.4;
}

.log-time {
  flex-shrink: 0;
  color: #8C8C8C;
  font-family: monospace;
  min-width: 80px;
}

.log-message {
  flex: 1;
  word-break: break-word;
}

.log-success {
  color: #52C41A;
}

.log-error {
  color: #FF4D4F;
}

.log-warning {
  color: #FAAD14;
}

.log-info {
  color: #1890FF;
}

.empty-logs {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #8C8C8C;
  gap: 16px;
}

.empty-logs .el-icon {
  font-size: 48px;
  opacity: 0.5;
}

.empty-logs p {
  margin: 0;
  font-size: 14px;
}

.batch-dialog-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.batch-input-section h4,
.batch-commands-section h4 {
  margin: 0 0 16px 0;
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 数据导出表单优化 */
.export-card .el-form {
  padding: 16px 0;
}

.export-card .el-form-item {
  margin-bottom: 24px;
}

.export-card .el-form-item__label {
  font-weight: 500;
  color: #333;
}

.export-card .el-select,
.export-card .el-date-editor {
  width: 100%;
  max-width: 300px;
}

.export-card .el-button {
  margin-right: 12px;
  padding: 10px 20px;
}

.export-logs {
  flex-shrink: 0;
  width: 340px;
  flex: 0 0 340px;
}

.download-table {
  margin-top: 8px;
}
/* 固定设备页面操作日志高度，避免压缩上方数据表 */
.operation-logs-section {
  flex: 0 0 240px;
  max-height: 240px;
  display: flex;
  flex-direction: column;
}

.operation-logs-section .logs-container {
  flex: 1;
  overflow-y: auto;
}
</style>