<template>
  <div class="energy-cockpit">
    <!-- 顶部控制栏 -->
    <div class="control-bar">
      <div class="control-group">
        <label>线路选择:</label>
        <el-select v-model="selectedLine" placeholder="选择线路" size="small" @change="onLineChange">
          <el-option v-for="(stations, line) in lineConfigs" :key="line" :label="line" :value="line" />
        </el-select>
      </div>
      
      <div class="control-group">
        <label>车站选择:</label>
        <el-select v-model="selectedStation" placeholder="选择车站" size="small" @change="refreshAll">
          <el-option v-for="st in stationsOfSelectedLine" :key="st.station_ip" :label="st.station_name" :value="st.station_ip" />
        </el-select>
      </div>
      
      <div class="control-group">
        <label>趋势周期:</label>
        <el-select v-model="trendPeriod" placeholder="趋势周期" size="small" @change="refreshTrend">
          <el-option label="24小时" value="24h" />
          <el-option label="7天" value="7d" />
          <el-option label="30天" value="30d" />
        </el-select>
      </div>
      
      <div class="control-group">
        <el-button @click="refreshAll" type="primary" size="small">
          <i class="icon-refresh"></i>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- KPI看板 -->
    <div class="kpi-dashboard">
      <EnergyKpiCard
        title="总能耗"
        :value="kpi.total_kwh_today || 0"
        unit="kWh"
        :trend="{ type: 'up', value: 5.2, icon: 'icon-trending-up' }"
        icon="icon-zap"
        variant="primary"
      />
      
      <EnergyKpiCard
        title="实时功率"
        :value="kpi.current_kw || 0"
        unit="kW"
        :trend="{ type: 'down', value: 2.1, icon: 'icon-trending-down' }"
        icon="icon-activity"
        variant="success"
      />
      
      <EnergyKpiCard
        title="峰值功率"
        :value="kpi.peak_kw || 0"
        unit="kW"
        :trend="{ type: 'up', value: 8.3, icon: 'icon-trending-up' }"
        icon="icon-trending-up"
        variant="info"
      />
      
      <EnergyKpiCard
        title="监控车站"
        :value="kpi.station_count || 0"
        unit="个"
        :trend="{ type: 'stable', value: 0, icon: 'icon-minus' }"
        icon="icon-map-pin"
        variant="warning"
      />

      <!-- 同比/环比对比 -->
      <EnergyKpiCard
        title="同比变化"
        subtitle="同比去年同期"
        :value="Number((compareData?.yoy_percent ?? 0).toFixed(1))"
        unit="%"
        :formatter="formatPercent"
        :trend="{
          direction: (compareData?.yoy_percent ?? 0) > 0 ? 'up' : (compareData?.yoy_percent ?? 0) < 0 ? 'down' : 'stable',
          percentage: Number(Math.abs(compareData?.yoy_percent ?? 0).toFixed(1)),
          text: '同比去年同期'
        }"
        icon="icon-percent"
        variant="info"
      />

      <EnergyKpiCard
        title="环比变化"
        subtitle="环比上一周期"
        :value="Number((compareData?.mom_percent ?? 0).toFixed(1))"
        unit="%"
        :formatter="formatPercent"
        :trend="{
          direction: (compareData?.mom_percent ?? 0) > 0 ? 'up' : (compareData?.mom_percent ?? 0) < 0 ? 'down' : 'stable',
          percentage: Number(Math.abs(compareData?.mom_percent ?? 0).toFixed(1)),
          text: '环比上一周期'
        }"
        icon="icon-percent"
        variant="info"
      />
    </div>

    <!-- 图表区域 -->
    <div class="chart-section">
      <EnergyChart
        title="实时能耗监测"
        :data="realtimeData"
        chart-type="line"
        :loading="false"
        :time-period="trendPeriod"
        @refresh="refreshRealtime"
        class="chart-container"
      />
      
      <EnergyChart
        title="历史数据趋势"
        :data="historyData"
        chart-type="bar"
        :loading="false"
        :time-period="trendPeriod"
        :show-export="true"
        @export="exportHistoryData"
        @refresh="refreshTrend"
        class="chart-container"
      />

      <!-- 分类分项能耗分析 -->
      <EnergyChart
        title="分类分项能耗"
        :data="classificationData"
        chart-type="pie"
        :loading="false"
        :time-period="trendPeriod"
        @refresh="refreshClassification"
        class="chart-container"
      />
    </div>

    <!-- 设备监控和优化建议 -->
    <div class="bottom-section">
      <EnergyDeviceMonitor
        title="设备监控"
        :auto-refresh="true"
        :refresh-interval="10000"
        @device-selected="onDeviceSelected"
        @device-controlled="onDeviceControlled"
        class="device-monitor"
      />
      
      <EnergyOptimizationPanel
        title="智能节能建议"
        :auto-refresh="true"
        :refresh-interval="300000"
        @suggestion-implemented="onSuggestionImplemented"
        @suggestion-viewed="onSuggestionViewed"
        class="optimization-panel"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { ElMessage, ElSelect, ElOption, ElButton } from 'element-plus'
import { useToast } from '@/composables/useToast'
import { useDataRefresh } from '@/composables/useDataRefresh'

// 百分比显示格式化：正数加+号，保留1位小数
const formatPercent = (val: number | string) => {
  const num = typeof val === 'number' ? val : Number(val)
  if (!isFinite(num)) return String(val)
  const sign = num > 0 ? '+' : ''
  return `${sign}${num.toFixed(1)}`
}

import { 
  EnergyKpiCard, 
  EnergyChart, 
  EnergyDeviceMonitor, 
  EnergyOptimizationPanel 
} from '@/components/business'
import type { ChartData } from '@/components/business/types'
import { fetchLineConfigs } from '@/api/control'
import { fetchRealtimeEnergy, fetchEnergyTrend, fetchEnergyKpi, fetchEnergyCompare, fetchEnergyClassification } from '@/api/energy'

type LineConfigs = { [line: string]: Array<{ station_name: string; station_ip: string }> }

const toast = useToast()

const lineConfigs = ref<LineConfigs>({})
const selectedLine = ref<string>('')
const selectedStation = ref<string>('')
const trendPeriod = ref<string>('24h')

const kpi = ref<any>({})
const realtimeData = ref<ChartData[]>([])
const historyData = ref<ChartData[]>([])
const classificationData = ref<ChartData[]>([])
const compareData = ref<{ yoy_percent: number; mom_percent: number; current_kwh: number } | null>(null)
let refreshTimer: NodeJS.Timeout | null = null

const stationsOfSelectedLine = computed(() => {
  if (!selectedLine.value) return []
  return lineConfigs.value[selectedLine.value] || []
})

function exportHistoryData() {
  console.log('导出历史数据')
}

function onDeviceSelected(device: any) {
  console.log('选择设备:', device)
}

function onDeviceControlled(device: any, action: any) {
  console.log('控制设备:', device, action)
}

function onSuggestionImplemented(suggestion: any) {
  console.log('实施建议:', suggestion)
}

function onSuggestionViewed(suggestion: any) {
  console.log('查看建议:', suggestion)
}

async function loadLineConfigs() {
  try {
    const cfg = await fetchLineConfigs()
    lineConfigs.value = cfg || {}
    const lines = Object.keys(cfg || {})
    if (lines.length > 0) {
      selectedLine.value = lines[0]
      const stations = cfg[selectedLine.value]
      if (stations && stations.length > 0) selectedStation.value = stations[0].station_ip
    }
    toast.success('线路配置加载成功')
  } catch (e) {
    toast.error('加载线路配置失败，请重试')
    console.error('Failed to load line configs:', e)
  }
}

function onLineChange() {
  const stations = stationsOfSelectedLine.value
  selectedStation.value = stations.length > 0 ? stations[0].station_ip : ''
  refreshAll()
}

async function refreshRealtime() {
  if (!selectedLine.value || !selectedStation.value) return
  try {
    const data = await fetchRealtimeEnergy({ line: selectedLine.value, station_ip: selectedStation.value })
    realtimeData.value = [{
      type: 'line',
      title: '实时能耗',
      data: data.series || [],
      xAxis: data.timestamps || [],
      series: (data.series || []).map((s: any) => ({ 
        name: s.name, 
        type: 'line', 
        data: s.points,
        smooth: true,
        color: '#409EFF'
      }))
    }]
  } catch (error) {
    console.warn('实时数据获取失败，使用示例数据:', error)
    realtimeData.value = [{
      type: 'line',
      title: '实时能耗',
      data: Array.from({ length: 12 }, () => Math.round(100 + Math.random() * 50)),
      xAxis: Array.from({ length: 12 }, (_, i) => `${i}:00`),
      series: [{
        name: '功率',
        type: 'line',
        data: Array.from({ length: 12 }, () => Math.round(100 + Math.random() * 50)),
        smooth: true,
        color: '#409EFF'
      }]
    }]
  }
}

async function refreshClassification() {
  if (!selectedLine.value || !selectedStation.value) return
  try {
    const data = await fetchEnergyClassification({ line: selectedLine.value, station_ip: selectedStation.value, period: trendPeriod.value })
    const cats = (data?.items ? data.items.map((it: any) => it.name) : (data?.categories || []))
    const vals = (data?.items ? data.items.map((it: any) => it.kwh) : (data?.values || []))
    classificationData.value = [{
      type: 'pie',
      title: '分类分项能耗',
      data: vals || [],
      xAxis: cats || []
    }]
  } catch {
    ElMessage.warning('分类数据获取失败，显示示例数据')
    const cats = ['冷机', '水泵', '冷却塔', '照明', '其他']
    const vals = cats.map(() => Math.round(500 + Math.random() * 300))
    classificationData.value = [{
      type: 'pie',
      title: '分类分项能耗',
      data: vals,
      xAxis: cats
    }]
  }
}

async function refreshCompare() {
  if (!selectedLine.value || !selectedStation.value) return
  try {
    const data = await fetchEnergyCompare({ line: selectedLine.value, station_ip: selectedStation.value, period: trendPeriod.value })
    compareData.value = data || null
  } catch {
    // 示例数据：当前周期能耗与同比/环比百分比
    compareData.value = { yoy_percent: (Math.random() * 20 - 10), mom_percent: (Math.random() * 20 - 10), current_kwh: Math.round(12000 + Math.random() * 3000) }
  }
}

async function refreshTrend() {
  if (!selectedLine.value || !selectedStation.value) return
  try {
    const data = await fetchEnergyTrend({ line: selectedLine.value, station_ip: selectedStation.value, period: trendPeriod.value })
    historyData.value = [{
      type: 'bar',
      title: '历史趋势',
      data: data.values || [],
      xAxis: data.timestamps || [],
      series: [{
        name: '耗电量',
        type: 'bar',
        data: data.values || [],
        color: '#67C23A'
      }]
    }]
  } catch {
    ElMessage.warning('趋势数据获取失败，显示示例数据')
    historyData.value = [{
      type: 'bar',
      title: '历史趋势',
      data: Array.from({ length: 24 }, () => Math.round(50 + Math.random() * 30)),
      xAxis: Array.from({ length: 24 }, (_, i) => `${i}:00`),
      series: [{
        name: '耗电量',
        type: 'bar',
        data: Array.from({ length: 24 }, () => Math.round(50 + Math.random() * 30)),
        color: '#67C23A'
      }]
    }]
  }
}

async function refreshKpi() {
  if (!selectedLine.value) return
  try {
    const data = await fetchEnergyKpi({ line: selectedLine.value, station_ip: selectedStation.value })
    kpi.value = data
  } catch {
    kpi.value = {
      total_kwh_today: 12850.4,
      current_kw: 432.2,
      peak_kw: 680.5,
      station_count: stationsOfSelectedLine.value.length,
    }
  }
}



function refreshAll() {
  refreshRealtime()
  refreshTrend()
  refreshKpi()
  refreshCompare()
  refreshClassification()
}

function startAutoRefresh() {
  refreshTimer = setInterval(() => {
    refreshRealtime()
  }, 30000) // 30秒刷新一次实时数据
}

onMounted(async () => {
  await loadLineConfigs()
  refreshAll()
  startAutoRefresh()
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})

watch([selectedLine, selectedStation], () => {
  // 可根据选择变化做联动
})
</script>

<style scoped>
.energy-cockpit {
  padding: var(--spacing-layout-md);
  background: radial-gradient(1200px circle at 20% 0%, rgba(0,212,255,0.08) 0%, rgba(0,212,255,0) 40%),
              linear-gradient(180deg, #0b1020 0%, #0e1733 100%);
  min-height: 100vh;
  color: var(--color-text-primary);
  animation: fadeIn 0.4s ease-out;
  /* 局部文本令牌提亮，提高标签可读性 */
  --color-text-primary: #ffffff;
  --color-text-secondary: rgba(255,255,255,0.92);
  --color-text-tertiary: rgba(255,255,255,0.82);
  /* Element Plus 输入/占位符文本令牌（局部） */
  --el-input-text-color: #ffffff;
  --el-input-placeholder-color: rgba(255,255,255,0.88);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.control-bar {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  padding: var(--spacing-md);
  background: rgba(14, 23, 51, 0.65);
  backdrop-filter: blur(6px);
  border-radius: var(--border-radius-lg);
  border: 1px solid rgba(0, 212, 255, 0.35);
  box-shadow: var(--shadow-light);
  align-items: center;
  flex-wrap: wrap;
  /* 关键修复：让输入框背景透明，避免白底白字 */
  --el-input-bg-color: transparent;
  --el-fill-color-blank: transparent;
}

/* 控制栏标签与选择器文字对比度增强 */
.control-group label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  white-space: nowrap;
}

/* Element Plus 选择器文本（值/占位符） */
.control-bar :deep(.el-input__inner),
.control-bar :deep(.el-select__selected-item),
.control-bar :deep(.el-select__selected-item span) {
  color: var(--el-input-text-color);
}

.control-bar :deep(.el-select__placeholder),
.control-bar :deep(.el-input__inner::placeholder) {
  color: var(--el-input-placeholder-color);
  opacity: 1;
}

/* 关键修复：输入容器背景与边框，确保白字可见 */
.control-bar :deep(.el-input__wrapper),
.control-bar :deep(.el-input__inner) {
  background-color: transparent;
  border-color: rgba(0, 212, 255, 0.35);
}

.control-bar :deep(.el-input__wrapper:hover),
.control-bar :deep(.el-input__inner:hover) {
  border-color: rgba(0, 255, 204, 0.5);
}

.control-bar :deep(.el-input__wrapper.is-focus),
.control-bar :deep(.el-select.is-focus .el-input__wrapper),
.control-bar :deep(.is-focus .el-input__inner) {
  border-color: rgba(0, 255, 204, 0.85);
  box-shadow: 0 0 0 1px rgba(0, 255, 204, 0.18);
}

/* 可读性微增强（不改布局） */
.control-bar :deep(.el-select .el-input__inner) {
  font-weight: var(--font-weight-medium);
}

.control-bar :deep(.el-select) {
  min-width: 200px;
}

.control-bar :deep(.el-button) {
  box-shadow: var(--shadow-active);
}

.control-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  min-width: 150px;
}

/* 统一标签颜色为主文本色，避免低对比 */
.control-group label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  white-space: nowrap;
}

.kpi-dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  animation: slideUp 0.5s ease-out 0.1s both;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.chart-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-md);
}

.chart-container {
  background: rgba(14, 23, 51, 0.65);
  backdrop-filter: blur(6px);
  border-radius: var(--border-radius-lg);
  border: 1px solid rgba(0, 212, 255, 0.35);
  box-shadow: var(--shadow-light);
  overflow: hidden;
  transition: all var(--duration-base) var(--ease-out);
  animation: slideUp 0.6s ease-out 0.2s both;
}

.chart-container:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 212, 255, 0.2);
  border-color: rgba(0, 212, 255, 0.5);
}

.bottom-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
}

.device-monitor,
.optimization-panel {
  background: rgba(14, 23, 51, 0.65);
  backdrop-filter: blur(6px);
  border-radius: var(--border-radius-lg);
  border: 1px solid rgba(0, 212, 255, 0.35);
  box-shadow: var(--shadow-light);
  overflow: hidden;
  transition: all var(--duration-base) var(--ease-out);
  animation: slideUp 0.7s ease-out 0.3s both;
}

.device-monitor:hover,
.optimization-panel:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 212, 255, 0.2);
  border-color: rgba(0, 212, 255, 0.5);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .chart-section {
    grid-template-columns: 1fr;
  }
  
  .bottom-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .energy-cockpit {
    padding: var(--spacing-md);
  }
  
  .control-bar {
    flex-direction: column;
    gap: var(--spacing-sm);
    align-items: stretch;
  }
  
  .control-group {
    min-width: auto;
    justify-content: space-between;
  }
  
  .kpi-dashboard {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-sm);
  }
  
  .chart-section,
  .bottom-section {
    gap: var(--spacing-md);
  }
}

@media (max-width: 480px) {
  .kpi-dashboard {
    grid-template-columns: 1fr;
  }
  
  .control-group {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-xs);
  }
  
  .control-group label {
    font-size: var(--font-size-xs);
  }

  .control-bar :deep(.el-select),
  .control-bar :deep(.el-button) {
    width: 100%;
  }
}

/* 深色模式使用设计令牌，保持风格一致 */
@media (prefers-color-scheme: dark) {
  .energy-cockpit {
    background: radial-gradient(1200px circle at 20% 0%, rgba(0,212,255,0.08) 0%, rgba(0,212,255,0) 40%),
                linear-gradient(180deg, #0b1020 0%, #0e1733 100%);
    /* 深色下进一步保持主文本高对比 */
    --color-text-primary: #ffffff;
    --color-text-secondary: rgba(255,255,255,0.94);
    --color-text-tertiary: rgba(255,255,255,0.85);
    /* 深色下占位符维持高对比 */
    --el-input-text-color: #ffffff;
    --el-input-placeholder-color: rgba(255,255,255,0.9);
  }
  
  .control-bar,
  .chart-container,
  .device-monitor,
  .optimization-panel {
    background: rgba(14, 23, 51, 0.65);
    border-color: rgba(0, 212, 255, 0.45);
  }
  
  .control-group label {
    color: var(--color-text-primary);
  }
}

/* Tech cyan highlight interactions */
.control-bar,
.chart-container,
.device-monitor,
.optimization-panel {
  transition: border-color 120ms ease, box-shadow 200ms ease, transform 200ms ease;
}

.control-bar:hover,
.chart-container:hover,
.device-monitor:hover,
.optimization-panel:hover {
  border-color: rgba(0, 255, 204, 0.85);
  box-shadow: 0 0 0 1px rgba(0, 255, 204, 0.18), 0 0 16px rgba(0, 255, 204, 0.25);
}

.control-bar:focus-within,
.chart-container:focus-within,
.device-monitor:focus-within,
.optimization-panel:focus-within {
  border-color: rgba(0, 255, 204, 0.85);
  box-shadow: 0 0 0 1px rgba(0, 255, 204, 0.18), 0 0 16px rgba(0, 255, 204, 0.25), inset 0 0 8px rgba(0, 255, 204, 0.15);
}

@media (prefers-color-scheme: dark) {
  .control-bar:hover,
  .chart-container:hover,
  .device-monitor:hover,
  .optimization-panel:hover {
    box-shadow: 0 0 0 1px rgba(0, 255, 204, 0.2), 0 0 18px rgba(0, 255, 204, 0.3);
  }
}
</style>