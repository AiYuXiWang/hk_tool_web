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
          <aside class="device-sidebar">
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
                >
                  <el-icon><DataAnalysis /></el-icon>
                  测试
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
                  :data="treeDataFiltered"
                  node-key="id"
                  :props="{ label: 'label', children: 'children' }"
                  highlight-current
                  :default-expanded-keys="defaultExpandedKeys"
                  @node-click="onNodeClick"
                  class="device-tree"
                  v-loading="loadingTree"
                  element-loading-text="加载设备数据..."
                >
                  <template #default="{ node, data }">
                    <div class="tree-node-content">
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
            </div>
          </div>
        </div>
      </div>

      <!-- 数据导出页面 -->
      <div v-show="activeTab === 'export'" class="export-page">
        <div class="export-header">
          <h2 class="page-title">
            <el-icon><Download /></el-icon>
            数据导出中心
          </h2>
        </div>
        <div class="export-content">
          <p>数据导出功能页面</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
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
  DataBoard
} from '@element-plus/icons-vue'
import { fetchRealtimeValue, batchWritePoints, fetchDeviceTree, getSeverityColor } from './api/control'

const activeTab = ref('device')
const operatorId = ref('web-admin')
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
  loadDeviceTree(false)
}

function onStationChange() {
  if (selectedStation.value) {
    loadDeviceTree(false)
  }
}

function onNodeClick(node) {
  if (!node.children && node.meta?.data_code) {
    const oc = node.meta.object_code
    const dc = node.meta.data_code
    query.value = { object_code: oc, data_code: dc }
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
    tableRows.value = [{
      object_code: d.object_code,
      data_code: d.data_code,
      value: d.value ?? null,
      setpoint: null,
      unit: d.unit ?? meta.unit ?? '',
      ts: d.ts,
      status: 'ok',
      severity: sev
    }]
  } catch (e) {
    tableRows.value = [{
      object_code: query.value.object_code,
      data_code: query.value.data_code,
      value: null,
      setpoint: null,
      unit: '',
      ts: new Date().toISOString(),
      status: 'failed',
      severity: 'error'
    }]
  } finally {
    loadingQuery.value = false
  }
}

async function refreshRow(row) {
  query.value = { object_code: row.object_code, data_code: row.data_code }
  await fetchRealtime()
}

onMounted(async () => {
  await loadDeviceTree()
})
</script>

<style scoped>
.app-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #fafafa;
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
  background: white;
  border-bottom: 1px solid #f0f0f0;
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
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.device-sidebar {
  width: 380px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: white;
  border-right: 1px solid #f0f0f0;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f5f5f5;
  border-bottom: 1px solid #f0f0f0;
}

.sidebar-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
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
  background: #fafafa;
  border-bottom: 1px solid #f0f0f0;
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
  color: #4c4c4c;
  font-weight: 500;
}

.tree-container {
  flex: 1;
  overflow: hidden;
}

.tree-scrollbar {
  height: 100%;
}

.device-tree {
  padding: 8px;
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
  color: #1a1a1a;
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
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 2px;
  color: #1a1a1a;
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
  margin-bottom: 24px;
  text-align: center;
}

.page-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
}

.export-content {
  flex: 1;
  overflow: hidden;
}
</style>