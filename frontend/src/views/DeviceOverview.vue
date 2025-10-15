<template>
  <div class="device-overview">
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
        </div>
      </div>

      <!-- 线路/车站选择器 -->
      <div class="selector-bar">
        <el-select
          v-model="selectedLine"
          placeholder="选择线路"
          size="small"
          class="selector-item"
          @change="onLineChange"
          :disabled="loadingLineConfigs"
        >
          <el-option
            v-for="(stations, line) in lineConfigs"
            :key="line"
            :label="line"
            :value="line"
          />
        </el-select>
        <el-select
          v-model="selectedStation"
          placeholder="选择车站"
          size="small"
          class="selector-item"
          @change="onStationChange"
          :disabled="loadingLineConfigs || !selectedLine"
        >
          <el-option
            v-for="s in stationsForSelectedLine"
            :key="s.station_ip"
            :label="s.station_name"
            :value="s.station_ip"
          />
        </el-select>
      </div>

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
      </div>

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
                    'point-node': isPointNode(data),
                    'writable-point': isPointNode(data) && data.meta?.is_writable
                  }"
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
              <div class="input-item current-value">
                <label class="input-label">当前值</label>
                <el-input
                  :model-value="currentValueText || ''"
                  placeholder="—"
                  size="small"
                  class="query-input"
                  readonly
                />
              </div>
              <el-button 
                type="primary" 
                :loading="loadingQuery"
                @click="fetchRealtime"
                class="query-btn"
              >
                <el-icon><Search /></el-icon>
                查询实时值
              </el-button>
              <el-switch
                v-model="autoQuery"
                inline-prompt
                active-text="自动查询"
                inactive-text="手动查询"
                size="small"
              />
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
            <div class="section-actions">
              <div class="section-stats">
                <span>当前行数：{{ tableRows.length }}</span>
                <span class="dot">•</span>
                <span>最后更新时间：{{ lastUpdateText || '—' }}</span>
              </div>
              <el-button type="success" size="small" @click="addSelectedToBatch">加入批量</el-button>
              <el-button type="warning" size="small" @click="() => (batchOpen = true)">批量命令</el-button>
              <el-button type="danger" size="small" @click="clearTable">清空已查询</el-button>
              <el-button size="small" @click="batchRefreshSelected">批量刷新</el-button>
              <el-button type="danger" size="small" @click="batchRemoveSelected">批量移除</el-button>
              <el-button type="primary" plain size="small" @click="exportCSV">导出 CSV</el-button>
            </div>
          </div>
          <el-alert type="info" :closable="false" show-icon class="write-policy-hint" style="margin: 8px 0;">
            <template #title>
              默认写值策略：跳过写前读取（X-Skip-Before: 1），路由超时 10 秒（X-Timeout-Ms: 10000）。
            </template>
          </el-alert>
          <div class="table-container">
            <el-table 
              :data="tableRows" 
              v-loading="loadingQuery"
              element-loading-text="正在查询数据..."
              :height="tableHeight"
              class="data-table"
              ref="tableRef"
              stripe
              border
              @selection-change="onSelectionChange"
            >
              <el-table-column type="selection" width="45" fixed="left" />
              <el-table-column prop="object_code" label="设备编码" width="140" fixed="left" sortable>
                <template #default="{ row }">
                  <el-tag type="info" size="small">{{ row.object_code }}</el-tag>
                </template>
              </el-table-column>

              <el-table-column prop="data_code" label="点位编码" width="160" sortable>
                <template #default="{ row }">
                  <code class="code-text">{{ row.data_code }}</code>
                </template>
              </el-table-column>

              <el-table-column prop="value" label="当前值" width="120" align="center">
                <template #default="{ row }">
                  <div class="value-cell">
                    <span class="value-text">{{ row.value }}</span>
                    <span v-if="row.unit" class="unit-text">{{ row.unit }}</span>
                  </div>
                </template>
              </el-table-column>

              <el-table-column label="快速写值" width="220" align="center">
                <template #default="{ row }">
                  <div class="quick-write">
                    <el-input 
                      v-model="quickValues[getRowKey(row)]"
                      size="small"
                      placeholder="输入值"
                      class="quick-input"
                    />
                    <el-button 
                      size="small" 
                      type="success" 
                      :loading="writingKeys.has(getRowKey(row))"
                      @click="writeSingle(row)"
                      class="write-btn"
                      aria-label="写入点位值"
                    >
                      写入
                    </el-button>
                  </div>
                </template>
              </el-table-column>

              <el-table-column label="操作" width="180" align="center" fixed="right">
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
                  <el-button 
                    size="small" 
                    type="danger" 
                    @click="removeRow(row)"
                    class="remove-btn"
                  >
                    移除
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

      <!-- 批量命令抽屉 -->
      <el-drawer v-model="batchOpen" title="批量命令" size="50%">
        <div class="batch-toolbar">
          <el-button type="primary" @click="executeBatch">执行批量写入</el-button>
          <el-button @click="batchRows = []">清空列表</el-button>
        </div>
        <el-table :data="batchRows" class="drawer-table" border stripe>
          <el-table-column label="设备编码" width="160">
            <template #default="{ row }">
              <code class="code-text">{{ row.object_code }}</code>
            </template>
          </el-table-column>
          <el-table-column label="点位编码" width="180">
            <template #default="{ row }">
              <code class="code-text">{{ row.data_code }}</code>
            </template>
          </el-table-column>
          <el-table-column label="写入值" width="180" align="center">
            <template #default="{ row, $index }">
              <el-input v-model="batchRows[$index].control_value" size="small" placeholder="输入写入值" />
            </template>
          </el-table-column>
          <el-table-column label="状态" width="120" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.last_status === 'ok'" type="success" size="small">成功</el-tag>
              <el-tag v-else-if="row.last_status === 'failed'" type="danger" size="small">失败</el-tag>
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
          <el-table-column label="错误信息" min-width="240">
            <template #default="{ row }">
              <span class="error-text" v-if="row.last_status === 'failed'">{{ row.last_message || '未知错误' }}</span>
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" align="center">
            <template #default="{ row, $index }">
              <el-button 
                size="small" 
                type="primary" 
                :loading="retryingKeys.has(`${row.object_code}:${row.data_code}`)"
                @click="retryBatchRow(row, $index)"
              >重试</el-button>
              <el-button size="small" type="danger" @click="removeBatchRow($index)">移除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-drawer>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { 
  Monitor,
  List,
  Refresh,
  DataAnalysis,
  Search,
  Folder,
  Aim,
  DataBoard
} from '@element-plus/icons-vue'
import { fetchDeviceTree, fetchRealtimeValue, batchWritePoints, fetchLineConfigs, setStationIp } from '../api/control'
import { ElMessage } from 'element-plus'

const filter = ref('')
const treeData = ref([])
const loadingTree = ref(false)
const defaultExpandedKeys = ref([])
// 线路/车站选择相关状态
const lineConfigs = ref({})
const loadingLineConfigs = ref(false)
const selectedLine = ref('')
const selectedStation = ref('')
const stationsForSelectedLine = computed(() => {
  const cfg = lineConfigs.value || {}
  const arr = cfg[selectedLine.value] || []
  return Array.isArray(arr) ? arr : []
})
// 查询相关最小状态
const query = ref({ object_code: '', data_code: '' })
const loadingQuery = ref(false)
const tableRows = ref([])
const tableRef = ref(null)
const lastUpdatedAt = ref(null)
const lastUpdateText = computed(() => {
  if (!lastUpdatedAt.value) return ''
  try {
    const d = new Date(lastUpdatedAt.value)
    return d.toLocaleTimeString()
  } catch { return '' }
})
const tableHeight = computed(() => Math.round(window.innerHeight * 0.4))
// 快速写值相关状态
const quickValues = ref({})
const writingKeys = ref(new Set())
// 自动查询开关
const autoQuery = ref(true)
// 当前值展示
const lastRealtime = ref(null)
const currentValueText = computed(() => {
  const r = lastRealtime.value
  if (!r) return ''
  const v = r.value
  const unit = r.unit ? ` ${r.unit}` : ''
  return v == null ? '—' : `${v}${unit}`
})

const treeDataFiltered = computed(() => {
  const q = filter.value.trim()
  if (!q) return treeData.value
  const match = (node) => node.label?.toLowerCase?.().includes(q.toLowerCase())
  const walk = (nodes) => nodes.map(n => {
    if (!n.children) return match(n) ? n : null
    const kids = walk(n.children).filter(Boolean)
    if (kids.length || match(n)) return { ...n, children: kids }
    return null
  }).filter(Boolean)
  return walk(treeData.value)
})

function isPointNode(data) {
  // 后端点位节点未设置object_type为'point'，以是否存在data_code判断
  return !!(data && data.meta && typeof data.meta.data_code === 'string')
}

function onNodeClick(data) {
  // 迁移阶段：仅记录点击，后续接入右侧查询面板
  console.debug('Node clicked:', data)
  if (isPointNode(data)) {
    query.value = { object_code: data.meta?.object_code || '', data_code: data.meta?.data_code || '' }
    // 点击点位时确保请求头包含站点，避免后端路由错误
    if (selectedStation.value) setStationIp(selectedStation.value)
    // 点击点位后自动查询（可配置开关）
    if (autoQuery.value) fetchRealtime()
  }
}

async function loadDeviceTree(isTest = false) {
  loadingTree.value = true
  try {
    // 每次加载设备树前设置站点请求头，确保后端按站点路由
    if (selectedStation.value) setStationIp(selectedStation.value)
    const opts = isTest 
      ? { forceTest: true, station_ip: selectedStation.value || undefined }
      : { station_ip: selectedStation.value || undefined }
    const { tree } = await fetchDeviceTree(opts)
    treeData.value = Array.isArray(tree) ? tree : []
    defaultExpandedKeys.value = treeData.value.slice(0, 5).map(n => n.id)
  } finally {
    loadingTree.value = false
  }
}

async function loadLineConfigs() {
  loadingLineConfigs.value = true
  try {
    const cfg = await fetchLineConfigs()
    lineConfigs.value = cfg || {}
    const lines = Object.keys(lineConfigs.value)
    if (lines.length) {
      selectedLine.value = lines[0]
      const stations = stationsForSelectedLine.value
      if (stations.length) selectedStation.value = stations[0].station_ip
    }
  } finally {
    loadingLineConfigs.value = false
  }
}

function onLineChange() {
  const stations = stationsForSelectedLine.value
  selectedStation.value = stations.length ? stations[0].station_ip : ''
  loadDeviceTree()
}

function onStationChange() {
  loadDeviceTree()
}

onMounted(async () => {
  await loadLineConfigs()
  await loadDeviceTree()
})

// 支持控制滚动行为：默认仅在追加新行时滚动到底部
async function fetchRealtime(opts = {}) {
  const { scroll } = opts || {}
  if (!query.value.object_code || !query.value.data_code) return
  loadingQuery.value = true
  try {
    const res = await fetchRealtimeValue(query.value.object_code, query.value.data_code)
    const rows = Array.isArray(res) ? res : (res ? [res] : [])
    // 过滤非法项（如错误对象）
    const validRows = rows.filter((item) => item && item.object_code && item.data_code)
    // 更新当前值展示为最新一条
    lastRealtime.value = validRows[0] || null
    let appendedCount = 0
    validRows.forEach((item) => {
      const key = `${item.object_code}|${item.data_code}`
      const idx = tableRows.value.findIndex(r => `${r.object_code}|${r.data_code}` === key)
      if (idx >= 0) {
        tableRows.value[idx] = item
      } else {
        tableRows.value.push(item)
        appendedCount += 1
      }
    })
    if (validRows.length === 0) {
      // 无有效结果：提示并不更新行数
      ElMessage.error('查询失败：后端拒绝或返回异常')
    } else {
      lastUpdatedAt.value = Date.now()
      await nextTick()
      const shouldScroll = scroll === true || (scroll !== false && appendedCount > 0)
      if (shouldScroll) scrollTableToBottom()
    }
  } catch (e) {
    ElMessage.error(`查询异常：${e?.message || e}`)
  } finally {
    loadingQuery.value = false
  }
}

function clearTable() {
  tableRows.value = []
}

function removeRow(row) {
  const key = `${row.object_code}|${row.data_code}`
  const idx = tableRows.value.findIndex(r => `${r.object_code}|${r.data_code}` === key)
  if (idx >= 0) tableRows.value.splice(idx, 1)
}

function scrollTableToBottom() {
  const root = tableRef.value?.$el || document
  const wrap = root.querySelector('.el-scrollbar__wrap') || root.querySelector('.el-table__body-wrapper')
  if (wrap) {
    wrap.scrollTop = wrap.scrollHeight
  }
}

async function refreshRow(row, opts = {}) {
  query.value = { object_code: row.object_code, data_code: row.data_code }
  await fetchRealtime(opts)
}

function getRowKey(row) {
  return `${row.object_code}|${row.data_code}`
}

async function writeSingle(row) {
  const key = getRowKey(row)
  const platformKey = `${row.object_code}:${row.data_code}`
  const value = quickValues.value[key]
  if (value === undefined || value === null || value === '') return
  writingKeys.value.add(key)
  try {
    // 写入前确保设置站点请求头，避免后端路由错误
    if (selectedStation.value) setStationIp(selectedStation.value)
    // 规范化控制值：数字优先，其次布尔
    const normalized = (() => {
      if (value === true || value === 'true' || value === 1 || value === '1') return 1
      if (value === false || value === 'false' || value === 0 || value === '0') return 0
      const n = Number(value)
      return Number.isNaN(n) ? value : n
    })()

    const resp = await batchWritePoints([
      {
        point_key: platformKey,
        data_source: 1,
        control_value: normalized,
        object_code: row.object_code,
        data_code: row.data_code,
      },
    ], selectedStation.value, { timeoutMs: 12000 })
    const item = Array.isArray(resp?.items) ? resp.items[0] : null
    if (item && item.status === 'ok') {
      ElMessage.success(`写入成功：${row.object_code}:${row.data_code} = ${normalized}`)
      // 写入后刷新但不触发滚动到底部，避免视图跳动
      await refreshRow(row, { scroll: false })
    } else {
      const msg = (item && item.message) ? String(item.message).slice(0, 140) : '未知错误'
      ElMessage.error(`写入失败：${row.object_code}:${row.data_code}，原因：${msg}`)
    }
  } catch (e) {
    ElMessage.error(`写入异常：${e?.message || e}`)
  } finally {
    writingKeys.value.delete(key)
  }
}

// 批量写入相关逻辑
const batchOpen = ref(false)
const batchRows = ref([])
const selectedRows = ref([])
const retryingKeys = ref(new Set())

function onSelectionChange(rows) {
  selectedRows.value = rows
}

function addSelectedToBatch() {
  const addList = selectedRows.value.length ? selectedRows.value : (tableRows.value.length ? [tableRows.value[0]] : [])
  addList.forEach((row) => {
    const key = getRowKey(row)
    const exists = batchRows.value.find((r) => `${r.object_code}|${r.data_code}` === key)
    if (!exists) {
      batchRows.value.push({
        object_code: row.object_code,
        data_code: row.data_code,
        control_value: '',
        last_status: null,
        last_message: ''
      })
    }
  })
  batchOpen.value = true
}

function removeBatchRow(idx) {
  batchRows.value.splice(idx, 1)
}

async function executeBatch() {
  if (!batchRows.value.length) {
    ElMessage.warning('请先加入待写入的点位')
    return
  }
  const commands = batchRows.value.map((r) => ({
    point_key: `${r.object_code}:${r.data_code}`,
    data_source: 1,
    control_value: r.control_value,
    object_code: r.object_code,
    data_code: r.data_code,
  }))
  try {
    const result = await batchWritePoints(commands, selectedStation.value, { timeoutMs: 12000 })
    const items = Array.isArray(result?.items) ? result.items : []
    const successCount = items.filter((i) => i.status === 'ok').length
    const failedCount = items.length - successCount

    if (items.length === 0) {
      ElMessage.error('批量写值响应异常：无返回项')
      return
    }

    // 更新批量行的状态与错误信息，便于逐条查看与重试
    const itemByKey = new Map(items.map((i) => [i.point_key, i]))
    batchRows.value.forEach((row) => {
      const k = `${row.object_code}:${row.data_code}`
      const it = itemByKey.get(k)
      if (it) {
        row.last_status = it.status
        row.last_message = it.message || ''
      }
    })

    if (failedCount === 0) {
      ElMessage.success(`批量写值成功：${successCount}/${result.total}`)
      batchOpen.value = false
    } else if (successCount > 0) {
      ElMessage.warning(`批量写值部分成功：成功 ${successCount}，失败 ${failedCount}`)
      // 保持对话框打开，便于用户修正失败项
      batchOpen.value = true
    } else {
      ElMessage.error(`批量写值失败：全部失败 ${failedCount}/${result.total}`)
      batchOpen.value = true
    }

    // 仅刷新成功的行，且不触发滚动
    const okKeys = new Set(items.filter((i) => i.status === 'ok').map((i) => i.point_key))
    for (const row of selectedRows.value) {
      const k = `${row.object_code}:${row.data_code}`
      if (okKeys.has(k)) {
        await refreshRow(row, { scroll: false })
      }
    }
  } catch (e) {
    ElMessage.error('批量写入失败，请稍后重试')
  }
}

async function retryBatchRow(row, idx) {
  const k = `${row.object_code}:${row.data_code}`
  retryingKeys.value.add(k)
  try {
    const resp = await batchWritePoints([
      {
        point_key: k,
        data_source: 1,
        control_value: row.control_value,
        object_code: row.object_code,
        data_code: row.data_code,
      },
    ], selectedStation.value, { timeoutMs: 12000 })
    const item = Array.isArray(resp?.items) ? resp.items[0] : null
    if (item && item.status === 'ok') {
      row.last_status = 'ok'
      row.last_message = ''
      ElMessage.success(`重试成功：${k}`)
      // 刷新主表对应行
      const target = tableRows.value.find((r) => `${r.object_code}:${r.data_code}` === k)
      if (target) await refreshRow(target, { scroll: false })
    } else {
      row.last_status = 'failed'
      row.last_message = (item && item.message) ? String(item.message).slice(0, 140) : '未知错误'
      ElMessage.error(`重试失败：${k}，原因：${row.last_message}`)
    }
  } catch (e) {
    row.last_status = 'failed'
    row.last_message = e?.message || String(e)
    ElMessage.error(`重试异常：${k}，${row.last_message}`)
  } finally {
    retryingKeys.value.delete(k)
  }
}

// 表格增强：批量刷新、批量移除、导出 CSV
async function batchRefreshSelected() {
  if (!selectedRows.value.length) {
    ElMessage.warning('请先在表格中选择行')
    return
  }
  for (const row of selectedRows.value) {
    await refreshRow(row)
  }
  ElMessage.success(`已刷新 ${selectedRows.value.length} 行`)
}

function batchRemoveSelected() {
  if (!selectedRows.value.length) {
    ElMessage.warning('请先在表格中选择行')
    return
  }
  selectedRows.value.forEach((row) => removeRow(row))
  selectedRows.value = []
  ElMessage.success('已移除所选行')
}

function exportCSV() {
  const headers = ['object_code', 'data_code', 'value', 'unit']
  const lines = [headers.join(',')]
  tableRows.value.forEach((r) => {
    const vals = [r.object_code, r.data_code, r.value ?? '', r.unit ?? '']
      .map((v) => `"${String(v).replace(/"/g, '""')}"`)
    lines.push(vals.join(','))
  })
  const csv = '\ufeff' + lines.join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `point-data-${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.device-overview {
  height: calc(100vh - var(--header-height) - var(--tab-height));
  background: var(--color-background-primary);
  display: flex;
  align-items: stretch;
  justify-content: flex-start;
}

.device-sidebar {
  width: 360px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: var(--color-background-primary);
  border-right: 1px solid var(--color-border-secondary);
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--color-background-secondary);
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

.search-box { margin-bottom: 8px; }

.tree-container { flex: 1; overflow: hidden; }
.tree-scrollbar { height: 100%; }
.device-tree { padding: 8px; }

.tree-node-content {
  display: flex;
  align-items: center;
  gap: 4px;
  width: 100%;
  padding: 4px 0;
}

.node-icon { flex-shrink: 0; font-size: 16px; }
.point-icon { color: var(--color-primary); }
.device-icon { color: var(--color-success); }
.folder-icon { color: var(--color-warning); }

.node-label { flex: 1; font-size: 12px; }
.node-label.point-node { cursor: pointer; }

.writable-tag {
  margin-left: auto;
  font-size: 10px !important;
  padding: 0 4px !important;
  height: 16px !important;
  line-height: 16px !important;
}

/* 右侧主内容：查询与数据表 */
.device-main { flex: 1; display: flex; flex-direction: column; overflow: auto; padding: 16px; }
.query-panel { margin-bottom: 16px; }
.panel-header { position: sticky; top: 0; z-index: 20; background: var(--color-background-primary); display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; padding-bottom: 8px; border-bottom: 1px solid var(--color-border-secondary); }
.panel-title { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 16px; font-weight: 600; color: var(--color-text-primary); }
.query-actions { flex: 1; }
.input-group { display: flex; align-items: flex-end; gap: 12px; }
.input-item { display: flex; flex-direction: column; gap: 4px; min-width: 160px; }
.input-label { font-size: 12px; color: var(--color-text-secondary); font-weight: 500; }
.query-btn { min-width: 120px; }
.data-display { flex: 1; display: flex; gap: 16px; overflow: hidden; }
.data-table-section { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.section-header { position: sticky; top: 0; z-index: 10; background: var(--color-background-primary); }
.section-actions { display: flex; align-items: center; gap: 8px; }
.section-stats { display: flex; align-items: center; gap: 6px; color: var(--color-text-secondary); }
.section-stats .dot { color: var(--color-text-secondary); }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.section-title { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 16px; font-weight: 600; color: var(--color-text-primary); }
.table-container { flex: 1; overflow: hidden; border-radius: 8px; border: 1px solid var(--color-border-secondary); }
.code-text { font-family: monospace; font-size: 12px; background: var(--color-background-tertiary); padding: 2px 6px; border-radius: 4px; }
.quick-write { display: flex; align-items: center; gap: 8px; justify-content: center; }
.quick-input { width: 100px; }
.write-btn { min-width: 60px; }
/* 批量命令样式 */
.batch-toolbar { display: flex; gap: 8px; margin-bottom: 12px; }
.drawer-table { --el-table-bg-color: var(--color-background-primary); }
</style>