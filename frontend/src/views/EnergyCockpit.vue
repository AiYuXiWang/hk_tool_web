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
import { ElMessage, ElSelect, ElOption } from 'element-plus'

import { 
  EnergyKpiCard, 
  EnergyChart, 
  EnergyDeviceMonitor, 
  EnergyOptimizationPanel 
} from '@/components/business'
import type { ChartData } from '@/components/business/types'
import { fetchLineConfigs } from '@/api/control'
import { fetchRealtimeEnergy, fetchEnergyTrend, fetchEnergyKpi } from '@/api/energy'

type LineConfigs = { [line: string]: Array<{ station_name: string; station_ip: string }> }

const lineConfigs = ref<LineConfigs>({})
const selectedLine = ref<string>('')
const selectedStation = ref<string>('')
const trendPeriod = ref<string>('24h')

const kpi = ref<any>({})
const realtimeData = ref<ChartData[]>([])
const historyData = ref<ChartData[]>([])
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
  } catch (e) {
    ElMessage.error('加载线路配置失败')
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
  } catch {
    ElMessage.warning('实时数据获取失败，显示示例数据')
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
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.control-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  align-items: center;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 150px;
}

.control-group label {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  white-space: nowrap;
}

.kpi-dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.chart-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.bottom-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.device-monitor,
.optimization-panel {
  background: white;
  border-radius: 8px;
  overflow: hidden;
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
    padding: 16px;
  }
  
  .control-bar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .control-group {
    min-width: auto;
    justify-content: space-between;
  }
  
  .kpi-dashboard {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
  }
  
  .chart-section,
  .bottom-section {
    gap: 16px;
  }
}

@media (max-width: 480px) {
  .kpi-dashboard {
    grid-template-columns: 1fr;
  }
  
  .control-group {
    flex-direction: column;
    align-items: stretch;
    gap: 4px;
  }
  
  .control-group label {
    font-size: 12px;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .energy-cockpit {
    background: #1a1a1a;
  }
  
  .control-bar,
  .chart-container,
  .device-monitor,
  .optimization-panel {
    background: #2d2d2d;
    border: 1px solid #404040;
  }
  
  .control-group label {
    color: #e5e5e5;
  }
}
</style>