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

    <!-- 滑动栏控制区域 -->
    <div class="slider-control-panel">
      <div class="slider-group">
        <div class="slider-header">
          <label>时间范围: {{ timeRangeHours }}小时</label>
          <span class="slider-value">{{ timeRangeHours }}h</span>
        </div>
        <el-slider 
          v-model="timeRangeHours" 
          :min="1" 
          :max="72" 
          :step="1"
          :show-tooltip="true"
          :format-tooltip="formatTimeTooltip"
          @change="onTimeRangeChange"
        />
      </div>

      <div class="slider-group">
        <div class="slider-header">
          <label>刷新间隔: {{ refreshIntervalSeconds }}秒</label>
          <span class="slider-value">{{ refreshIntervalSeconds }}s</span>
        </div>
        <el-slider 
          v-model="refreshIntervalSeconds" 
          :min="10" 
          :max="300" 
          :step="10"
          :show-tooltip="true"
          :format-tooltip="formatIntervalTooltip"
          @change="onRefreshIntervalChange"
        />
      </div>

      <div class="slider-group">
        <div class="slider-header">
          <label>功率阈值: {{ powerThreshold }} W</label>
          <span class="slider-value">{{ powerThreshold }} W</span>
        </div>
        <el-slider 
          v-model="powerThreshold" 
          :min="0" 
          :max="5000" 
          :step="100"
          :show-tooltip="true"
          :format-tooltip="formatPowerTooltip"
          @change="onPowerThresholdChange"
        />
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
        :auto-refresh-interval="refreshIntervalSeconds * 1000"
        :power-threshold="powerThreshold"
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
import { ElMessage, ElSelect, ElOption, ElButton, ElSlider } from 'element-plus'
import { useToast } from '@/composables/useToast'

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

// 滑动栏状态
const timeRangeHours = ref<number>(24)
const refreshIntervalSeconds = ref<number>(30)
const powerThreshold = ref<number>(0)

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

// 滑动栏工具提示格式化
const formatTimeTooltip = (value: number) => {
  if (value < 24) {
    return `${value} 小时`
  } else if (value === 24) {
    return '1 天'
  } else {
    const days = Math.floor(value / 24)
    const hours = value % 24
    return hours > 0 ? `${days} 天 ${hours} 小时` : `${days} 天`
  }
}

const formatIntervalTooltip = (value: number) => {
  if (value < 60) {
    return `${value} 秒`
  } else {
    const minutes = Math.floor(value / 60)
    const seconds = value % 60
    return seconds > 0 ? `${minutes} 分 ${seconds} 秒` : `${minutes} 分钟`
  }
}

const formatPowerTooltip = (value: number) => {
  return `≥ ${value} W`
}

// 滑动栏变化处理
const onTimeRangeChange = (value: number) => {
  console.log('时间范围变化:', value, '小时')
  toast.info(`时间范围已调整为 ${formatTimeTooltip(value)}`)
  // 重新加载数据
  refreshRealtime()
  refreshTrend()
}

const onRefreshIntervalChange = (value: number) => {
  console.log('刷新间隔变化:', value, '秒')
  toast.info(`刷新间隔已调整为 ${formatIntervalTooltip(value)}`)
  // 重启自动刷新
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
  startAutoRefresh()
}

const onPowerThresholdChange = (value: number) => {
  console.log('功率阈值变化:', value, 'W')
  toast.info(`功率阈值已设置为 ${value} W，设备列表已自动筛选`)
  // 功率阈值会通过 powerThreshold prop 传递给 EnergyDeviceMonitor 组件进行筛选
}

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
    const data = await fetchRealtimeEnergy({ 
      line: selectedLine.value, 
      station_ip: selectedStation.value,
      hours: timeRangeHours.value
    })
    const timestamps: string[] = data.timestamps || []
    const seriesData = data.series || []
    const dataPoints = Math.min(timeRangeHours.value, timestamps.length || timeRangeHours.value)
    const clippedTimestamps = timestamps.slice(-dataPoints)

    realtimeData.value = [{
      type: 'line',
      title: '实时能耗',
      data: seriesData,
      xAxis: clippedTimestamps,
      series: seriesData.map((s: any) => ({ 
        name: s.name, 
        type: 'line', 
        data: (s.points || []).slice(-(dataPoints)),
        smooth: true,
        color: '#409EFF'
      }))
    }]
  } catch (error) {
    console.warn('实时数据获取失败，使用示例数据:', error)
    const dataPoints = Math.min(timeRangeHours.value, 24)
    realtimeData.value = [{
      type: 'line',
      title: '实时能耗',
      data: Array.from({ length: dataPoints }, () => Math.round(100 + Math.random() * 50)),
      xAxis: Array.from({ length: dataPoints }, (_, i) => `${i}:00`),
      series: [{
        name: '功率',
        type: 'line',
        data: Array.from({ length: dataPoints }, () => Math.round(100 + Math.random() * 50)),
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
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  refreshTimer = setInterval(() => {
    refreshRealtime()
  }, refreshIntervalSeconds.value * 1000) // 使用滑动栏设置的刷新间隔
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
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 14px;
  background: 
    radial-gradient(ellipse 1200px 800px at 20% 0%, rgba(0, 212, 255, 0.12) 0%, transparent 50%),
    radial-gradient(ellipse 1000px 700px at 80% 100%, rgba(138, 43, 226, 0.08) 0%, transparent 50%),
    linear-gradient(135deg, #0a0e1a 0%, #0d1425 25%, #0e1733 50%, #0f1a3d 75%, #0d1429 100%);
  min-height: 100vh;
  height: 100vh;
  max-height: 100vh;
  box-sizing: border-box;
  color: var(--color-text-primary);
  animation: fadeIn 0.4s ease-out;
  overflow: hidden;
  /* 局部文本令牌提亮，提高标签可读性 */
  --color-text-primary: #ffffff;
  --color-text-secondary: rgba(255,255,255,0.92);
  --color-text-tertiary: rgba(255,255,255,0.82);
  /* Element Plus 输入/占位符文本令牌（局部） */
  --el-input-text-color: #ffffff;
  --el-input-placeholder-color: rgba(255,255,255,0.88);
  --panel-radius: clamp(12px, 2vw, 16px);
}

/* 科技感背景动画 - 扫描线效果 */
.energy-cockpit::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  right: -50%;
  bottom: -50%;
  background: 
    linear-gradient(0deg, transparent 48%, rgba(0, 212, 255, 0.03) 49%, rgba(0, 212, 255, 0.06) 50%, rgba(0, 212, 255, 0.03) 51%, transparent 52%);
  background-size: 100% 40px;
  pointer-events: none;
  animation: scanlines 8s linear infinite;
  opacity: 0.6;
}

/* 发光粒子效果 */
.energy-cockpit::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(2px 2px at 20% 30%, rgba(0, 212, 255, 0.6), transparent),
    radial-gradient(2px 2px at 60% 70%, rgba(138, 43, 226, 0.6), transparent),
    radial-gradient(1px 1px at 50% 50%, rgba(0, 255, 204, 0.6), transparent),
    radial-gradient(1px 1px at 80% 10%, rgba(0, 212, 255, 0.4), transparent),
    radial-gradient(2px 2px at 90% 60%, rgba(138, 43, 226, 0.4), transparent),
    radial-gradient(1px 1px at 33% 80%, rgba(0, 255, 204, 0.4), transparent);
  background-size: 200% 200%;
  animation: particleFloat 20s ease-in-out infinite;
  pointer-events: none;
  opacity: 0.4;
}

.energy-cockpit > * {
  position: relative;
  z-index: 5;
}
@keyframes scanlines {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(40px);
  }
}

@keyframes particleFloat {
  0%, 100% {
    background-position: 0% 0%, 100% 100%, 50% 50%, 80% 10%, 90% 60%, 33% 80%;
  }
  25% {
    background-position: 100% 50%, 0% 50%, 25% 75%, 70% 20%, 80% 70%, 43% 70%;
  }
  50% {
    background-position: 50% 100%, 50% 0%, 75% 25%, 60% 30%, 70% 80%, 53% 60%;
  }
  75% {
    background-position: 0% 50%, 100% 50%, 25% 75%, 50% 40%, 60% 90%, 63% 50%;
  }
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
  position: relative;
  display: flex;
  gap: 10px;
  padding: 10px 14px;
  background: 
    linear-gradient(135deg, rgba(14, 23, 51, 0.75) 0%, rgba(20, 32, 60, 0.65) 100%);
  backdrop-filter: blur(12px) saturate(180%);
  border-radius: var(--border-radius-lg);
  border: 1px solid rgba(0, 212, 255, 0.35);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    0 0 20px rgba(0, 212, 255, 0.15);
  align-items: center;
  flex-wrap: wrap;
  flex-shrink: 0;
  z-index: 10;
  /* 关键修复：让输入框背景透明，避免白底白字 */
  --el-input-bg-color: transparent;
  --el-fill-color-blank: transparent;
}

/* 控制栏边缘发光效果 */
.control-bar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(0, 212, 255, 0.6) 25%, 
    rgba(0, 255, 204, 0.8) 50%, 
    rgba(0, 212, 255, 0.6) 75%, 
    transparent 100%);
  border-radius: var(--border-radius-lg) var(--border-radius-lg) 0 0;
  opacity: 0.8;
  animation: glowPulse 3s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
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

/* 滑动栏控制面板样式 */
.slider-control-panel {
  position: relative;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
  padding: 12px 14px;
  background: 
    linear-gradient(135deg, rgba(14, 23, 51, 0.75) 0%, rgba(20, 32, 60, 0.65) 100%);
  backdrop-filter: blur(12px) saturate(180%);
  border-radius: var(--border-radius-lg);
  border: 1px solid rgba(0, 212, 255, 0.35);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    0 0 20px rgba(0, 212, 255, 0.15);
  z-index: 9;
  animation: slideUp 0.5s ease-out 0.15s both;
  flex-shrink: 0;
}

.slider-control-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(138, 43, 226, 0.6) 25%, 
    rgba(0, 255, 204, 0.8) 50%, 
    rgba(138, 43, 226, 0.6) 75%, 
    transparent 100%);
  border-radius: var(--border-radius-lg) var(--border-radius-lg) 0 0;
  opacity: 0.8;
  animation: glowPulse 4s ease-in-out infinite;
}

.slider-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm);
  background: linear-gradient(135deg, rgba(10, 18, 35, 0.5) 0%, rgba(15, 25, 45, 0.4) 100%);
  border-radius: var(--border-radius-md);
  border: 1px solid rgba(0, 212, 255, 0.2);
  transition: all 0.3s ease;
}

.slider-group:hover {
  border-color: rgba(0, 255, 204, 0.5);
  box-shadow: 0 0 16px rgba(0, 212, 255, 0.2);
  transform: translateY(-2px);
}

.slider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xs);
}

.slider-header label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  letter-spacing: 0.05em;
}

.slider-value {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: rgba(0, 255, 204, 0.95);
  text-shadow: 0 0 12px rgba(0, 255, 204, 0.6);
  font-family: 'Courier New', monospace;
}

/* Element Plus Slider 自定义样式 */
.slider-group :deep(.el-slider__runway) {
  background-color: rgba(0, 212, 255, 0.15);
  height: 8px;
  border-radius: 4px;
}

.slider-group :deep(.el-slider__bar) {
  background: linear-gradient(90deg, 
    rgba(0, 212, 255, 0.8) 0%, 
    rgba(0, 255, 204, 0.9) 100%);
  height: 8px;
  border-radius: 4px;
  box-shadow: 0 0 12px rgba(0, 212, 255, 0.5);
}

.slider-group :deep(.el-slider__button) {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(0, 255, 204, 0.9);
  background: linear-gradient(135deg, 
    rgba(14, 23, 51, 0.95) 0%, 
    rgba(18, 32, 58, 0.9) 100%);
  box-shadow: 
    0 0 16px rgba(0, 255, 204, 0.6),
    0 4px 12px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.slider-group :deep(.el-slider__button:hover) {
  transform: scale(1.2);
  box-shadow: 
    0 0 24px rgba(0, 255, 204, 0.8),
    0 6px 16px rgba(0, 0, 0, 0.4);
}

.slider-group :deep(.el-slider__button-wrapper) {
  top: -6px;
}

.slider-group :deep(.el-slider__button-wrapper:hover .el-slider__button),
.slider-group :deep(.el-slider__button-wrapper.hover .el-slider__button),
.slider-group :deep(.el-slider__button-wrapper.dragging .el-slider__button) {
  transform: scale(1.3);
  border-color: rgba(0, 255, 204, 1);
}

/* Tooltip 样式 */
.slider-group :deep(.el-tooltip__popper) {
  background: linear-gradient(135deg, 
    rgba(14, 23, 51, 0.95) 0%, 
    rgba(18, 32, 58, 0.9) 100%);
  border: 1px solid rgba(0, 212, 255, 0.5);
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
  padding: 8px 12px;
  box-shadow: 0 8px 24px rgba(0, 212, 255, 0.3);
}

.kpi-dashboard {
  position: relative;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
  padding: 8px;
  border-radius: var(--panel-radius);
  background: linear-gradient(135deg, rgba(12, 20, 42, 0.45) 0%, rgba(18, 40, 68, 0.35) 100%);
  backdrop-filter: blur(10px) saturate(160%);
  box-shadow: inset 0 0 0 1px rgba(0, 212, 255, 0.12);
  animation: slideUp 0.5s ease-out 0.1s both;
  flex-shrink: 0;
}

.kpi-dashboard::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  border: 1px solid rgba(0, 212, 255, 0.08);
  pointer-events: none;
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
  position: relative;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  grid-auto-rows: minmax(0, 1fr);
  gap: 14px;
  padding: 10px;
  border-radius: var(--panel-radius);
  background: linear-gradient(135deg, rgba(12, 20, 42, 0.45) 0%, rgba(18, 40, 68, 0.35) 100%);
  backdrop-filter: blur(10px) saturate(160%);
  align-items: stretch;
  flex: 1 1 0;
  min-height: 0;
}

.chart-section::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  border: 1px solid rgba(0, 212, 255, 0.08);
  pointer-events: none;
}

.chart-container {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 0;
  height: 100%;
  background: 
    linear-gradient(135deg, rgba(14, 23, 51, 0.75) 0%, rgba(18, 28, 55, 0.65) 100%);
  backdrop-filter: blur(16px) saturate(180%);
  border-radius: var(--panel-radius);
  border: 1px solid rgba(0, 212, 255, 0.35);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.08),
    0 0 20px rgba(0, 212, 255, 0.1);
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  animation: slideUp 0.6s ease-out 0.2s both;
}

.chart-container :deep(.card-header),
.device-monitor :deep(.card-header),
.optimization-panel :deep(.card-header) {
  background: linear-gradient(135deg, rgba(14, 23, 51, 0.6) 0%, rgba(16, 27, 48, 0.4) 100%);
  border-bottom: 1px solid rgba(0, 212, 255, 0.18);
  backdrop-filter: blur(14px) saturate(140%);
  padding: var(--spacing-md) var(--spacing-lg);
}

.chart-container :deep(.card-title),
.device-monitor :deep(.card-title),
.optimization-panel :deep(.card-title) {
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.chart-container :deep(.card-body),
.device-monitor :deep(.card-body),
.optimization-panel :deep(.card-body) {
  background: transparent;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
}

.chart-container :deep(.card-body > *),
.device-monitor :deep(.card-body > *),
.optimization-panel :deep(.card-body > *) {
  min-height: 0;
}

.chart-container :deep(.card-footer),
.device-monitor :deep(.card-footer),
.optimization-panel :deep(.card-footer) {
  background: rgba(255, 255, 255, 0.02);
  border-top: 1px solid rgba(0, 212, 255, 0.12);
}

/* 图表容器顶部渐变光效 */
.chart-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(0, 212, 255, 0.5) 20%, 
    rgba(138, 43, 226, 0.5) 50%,
    rgba(0, 255, 204, 0.5) 80%, 
    transparent 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.chart-container:hover::before {
  opacity: 1;
}

.chart-container:hover {
  transform: translateY(-6px) scale(1.01);
  box-shadow: 
    0 12px 40px rgba(0, 212, 255, 0.25),
    0 0 30px rgba(0, 212, 255, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.12);
  border-color: rgba(0, 212, 255, 0.6);
}

.bottom-section {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  padding: 10px;
  border-radius: var(--panel-radius);
  background: linear-gradient(135deg, rgba(12, 20, 42, 0.45) 0%, rgba(18, 40, 68, 0.35) 100%);
  backdrop-filter: blur(10px) saturate(160%);
  flex: 1 1 0;
  min-height: 0;
}

.bottom-section::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  border: 1px solid rgba(0, 212, 255, 0.08);
  pointer-events: none;
}

.device-monitor,
.optimization-panel {
  position: relative;
  background: 
    linear-gradient(135deg, rgba(14, 23, 51, 0.75) 0%, rgba(18, 28, 55, 0.65) 100%);
  backdrop-filter: blur(16px) saturate(180%);
  border-radius: var(--panel-radius);
  border: 1px solid rgba(0, 212, 255, 0.35);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.08),
    0 0 20px rgba(0, 212, 255, 0.1);
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  animation: slideUp 0.7s ease-out 0.3s both;
}

/* 底部面板顶部光效 */
.device-monitor::before,
.optimization-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(0, 212, 255, 0.5) 30%, 
    rgba(0, 255, 204, 0.5) 70%, 
    transparent 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.device-monitor:hover::before,
.optimization-panel:hover::before {
  opacity: 1;
}

.device-monitor:hover,
.optimization-panel:hover {
  transform: translateY(-6px) scale(1.01);
  box-shadow: 
    0 12px 40px rgba(0, 212, 255, 0.25),
    0 0 30px rgba(0, 212, 255, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.12);
  border-color: rgba(0, 212, 255, 0.6);
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

  .slider-control-panel {
    grid-template-columns: 1fr;
    gap: var(--spacing-sm);
    padding: var(--spacing-md);
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