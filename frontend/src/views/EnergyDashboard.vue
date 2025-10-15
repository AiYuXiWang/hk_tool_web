<template>
  <div class="energy-dashboard">
    <!-- 顶部标题栏 -->
    <div class="dashboard-header">
      <h1 class="dashboard-title">
        <i class="icon-dashboard"></i>
        环控节能平台 - 能源管理驾驶舱
      </h1>
      <div class="header-info">
        <span class="update-time">最后更新: {{ lastUpdateTime }}</span>
        <button @click="refreshData" class="refresh-btn" :disabled="loading">
          <i class="icon-refresh" :class="{ spinning: loading }"></i>
          刷新数据
        </button>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="dashboard-content">
      <!-- 实时监测模块 -->
      <div class="module realtime-monitoring">
        <RealtimeEnergyChart />
      </div>

      <!-- 第一行：总览KPI -->
      <div class="row kpi-row">
        <div class="kpi-card total-consumption">
          <div class="kpi-header">
            <h3>总能耗</h3>
            <i class="icon-total-energy"></i>
          </div>
          <div class="kpi-value">
            <span class="value">{{ totalConsumption.toLocaleString() }}</span>
            <span class="unit">kWh</span>
          </div>
          <div class="kpi-trend">
            <span class="trend-indicator" :class="totalTrend.direction">
              <i :class="totalTrend.icon"></i>
              {{ totalTrend.percentage }}%
            </span>
            <span class="trend-text">较昨日</span>
          </div>
        </div>

        <div class="kpi-card current-power">
          <div class="kpi-header">
            <h3>当前功率</h3>
            <i class="icon-power"></i>
          </div>
          <div class="kpi-value">
            <span class="value">{{ currentPower.toLocaleString() }}</span>
            <span class="unit">kW</span>
          </div>
          <div class="kpi-trend">
            <span class="trend-indicator" :class="powerTrend.direction">
              <i :class="powerTrend.icon"></i>
              {{ powerTrend.percentage }}%
            </span>
            <span class="trend-text">较上时</span>
          </div>
        </div>

        <div class="kpi-card efficiency-ratio">
          <div class="kpi-header">
            <h3>能效比</h3>
            <i class="icon-efficiency"></i>
          </div>
          <div class="kpi-value">
            <span class="value">{{ efficiencyRatio }}</span>
            <span class="unit">COP</span>
          </div>
          <div class="kpi-trend">
            <span class="trend-indicator" :class="efficiencyTrend.direction">
              <i :class="efficiencyTrend.icon"></i>
              {{ efficiencyTrend.percentage }}%
            </span>
            <span class="trend-text">较昨日</span>
          </div>
        </div>

        <div class="kpi-card cost-saving">
          <div class="kpi-header">
            <h3>节能收益</h3>
            <i class="icon-savings"></i>
          </div>
          <div class="kpi-value">
            <span class="value">{{ costSaving.toLocaleString() }}</span>
            <span class="unit">元</span>
          </div>
          <div class="kpi-trend">
            <span class="trend-indicator positive">
              <i class="icon-arrow-up"></i>
              {{ savingTrend.percentage }}%
            </span>
            <span class="trend-text">本月累计</span>
          </div>
        </div>
      </div>

      <!-- 第二行：实时监控和地图 -->
      <div class="row monitoring-row">
        <!-- 实时能耗监控 -->
        <div class="panel realtime-panel">
          <div class="panel-header">
            <h3>实时能耗监控</h3>
            <div class="panel-controls">
              <select v-model="selectedLine" @change="onLineChange">
                <option value="">全部线路</option>
                <option value="M3">3号线</option>
                <option value="M8">8号线</option>
                <option value="M11">11号线</option>
              </select>
              <button class="refresh-btn" @click="refreshData">
                <i class="icon-refresh"></i>
              </button>
            </div>
          </div>
          <div class="panel-content">
            <div class="realtime-chart" ref="realtimeChart"></div>
          </div>
        </div>

        <!-- 站点分布地图 -->
        <div class="panel map-panel">
          <div class="panel-header">
            <h3>站点能耗分布</h3>
            <div class="legend">
              <span class="legend-item high">高耗能</span>
              <span class="legend-item medium">中等</span>
              <span class="legend-item low">低耗能</span>
            </div>
          </div>
          <div class="panel-content">
            <div class="station-map">
              <div class="map-container" ref="stationMap">
                <!-- 地铁线路图 -->
                <svg class="metro-lines" viewBox="0 0 800 600">
                  <!-- M3线 -->
                  <path d="M50 300 L750 300" class="metro-line line-m3" stroke="#0066cc" stroke-width="8"/>
                  <!-- M8线 -->
                  <path d="M400 50 L400 550" class="metro-line line-m8" stroke="#00cc66" stroke-width="8"/>
                  <!-- M11线 -->
                  <path d="M100 150 L700 450" class="metro-line line-m11" stroke="#cc6600" stroke-width="8"/>
                  
                  <!-- 站点标记 -->
                  <g v-for="station in visibleStations" :key="station.id">
                    <circle 
                      :cx="station.x" 
                      :cy="station.y" 
                      :r="station.radius"
                      :class="['station-marker', station.energyLevel]"
                      @click="selectStation(station)"
                    />
                    <text 
                      :x="station.x" 
                      :y="station.y - 15" 
                      class="station-label"
                      text-anchor="middle"
                    >
                      {{ station.name }}
                    </text>
                  </g>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 第三行：历史趋势和设备状态 -->
      <div class="row analysis-row">
        <!-- 历史趋势分析 -->
        <div class="panel trend-panel">
          <HistoryTrendChart />
        </div>

        <!-- 设备运行状态 -->
        <div class="panel equipment-panel">
          <div class="panel-header">
            <h3>设备运行状态</h3>
            <div class="status-summary">
              <span class="status-count normal">正常: {{ equipmentStatus.normal }}</span>
              <span class="status-count warning">告警: {{ equipmentStatus.warning }}</span>
              <span class="status-count error">故障: {{ equipmentStatus.error }}</span>
            </div>
          </div>
          <div class="panel-content">
            <div class="equipment-list">
              <div 
                v-for="equipment in equipmentList" 
                :key="equipment.id"
                class="equipment-item"
                :class="equipment.status"
              >
                <div class="equipment-info">
                  <div class="equipment-name">{{ equipment.name }}</div>
                  <div class="equipment-location">{{ equipment.location }}</div>
                </div>
                <div class="equipment-metrics">
                  <div class="metric">
                    <span class="metric-label">功率</span>
                    <span class="metric-value">{{ equipment.power }}kW</span>
                  </div>
                  <div class="metric">
                    <span class="metric-label">效率</span>
                    <span class="metric-value">{{ equipment.efficiency }}%</span>
                  </div>
                </div>
                <div class="equipment-status">
                  <span class="status-indicator" :class="equipment.status"></span>
                  <span class="status-text">{{ equipment.statusText }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 第四行：节能建议和报表 -->
      <div class="row optimization-row">
        <!-- 节能优化建议 -->
        <div class="panel suggestions-panel">
          <div class="panel-header">
            <h3>节能优化建议</h3>
            <div class="ai-indicator">
              <i class="icon-ai"></i>
              <span>AI智能分析</span>
            </div>
          </div>
          <div class="panel-content">
            <div class="suggestions-list">
              <div 
                v-for="suggestion in optimizationSuggestions" 
                :key="suggestion.id"
                class="suggestion-item"
                :class="suggestion.priority"
              >
                <div class="suggestion-header">
                  <div class="suggestion-title">{{ suggestion.title }}</div>
                  <div class="suggestion-priority">{{ suggestion.priorityText }}</div>
                </div>
                <div class="suggestion-content">
                  <p class="suggestion-description">{{ suggestion.description }}</p>
                  <div class="suggestion-metrics">
                    <span class="metric">预计节能: {{ suggestion.energySaving }}kWh</span>
                    <span class="metric">预计收益: {{ suggestion.costSaving }}元</span>
                  </div>
                </div>
                <div class="suggestion-actions">
                  <button class="action-btn primary" @click="applySuggestion(suggestion)">
                    应用建议
                  </button>
                  <button class="action-btn secondary" @click="viewDetails(suggestion)">
                    查看详情
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 能耗报表 -->
        <div class="panel report-panel">
          <div class="panel-header">
            <h3>能耗统计报表</h3>
            <div class="report-controls">
              <select v-model="reportType">
                <option value="daily">日报</option>
                <option value="weekly">周报</option>
                <option value="monthly">月报</option>
              </select>
              <button class="export-btn" @click="exportReport">
                <i class="icon-export"></i>
                导出
              </button>
            </div>
          </div>
          <div class="panel-content">
            <div class="report-chart" ref="reportChart"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import RealtimeEnergyChart from '@/components/RealtimeEnergyChart.vue'
import HistoryTrendChart from '@/components/HistoryTrendChart.vue'

export default {
  name: 'EnergyDashboard',
  components: {
    RealtimeEnergyChart,
    HistoryTrendChart
  },
  setup() {
    // 响应式数据
    const currentDate = ref('')
    const currentTime = ref('')
    const systemStatus = ref('normal')
    const selectedLine = ref('')
    const selectedPeriod = ref('24h')
    const reportType = ref('daily')

    // 天气信息
    const weather = reactive({
      temperature: 24,
      humidity: 65
    })

    // KPI数据
    const totalConsumption = ref(4347.5)
    const currentPower = ref(1375.2)
    const efficiencyRatio = ref(3.8)
    const costSaving = ref(28450)

    // 趋势数据
    const totalTrend = reactive({
      direction: 'positive',
      icon: 'icon-arrow-up',
      percentage: 5.2
    })

    const powerTrend = reactive({
      direction: 'negative',
      icon: 'icon-arrow-down',
      percentage: 2.1
    })

    const efficiencyTrend = reactive({
      direction: 'positive',
      icon: 'icon-arrow-up',
      percentage: 3.5
    })

    const savingTrend = reactive({
      percentage: 15.8
    })

    // 时间周期选项
    const timePeriods = [
      { label: '24小时', value: '24h' },
      { label: '7天', value: '7d' },
      { label: '30天', value: '30d' },
      { label: '90天', value: '90d' }
    ]

    // 设备状态统计
    const equipmentStatus = reactive({
      normal: 156,
      warning: 8,
      error: 2
    })

    // 设备列表
    const equipmentList = ref([
      {
        id: 1,
        name: '冷机LS01',
        location: '振华路站',
        power: 137,
        efficiency: 95,
        status: 'normal',
        statusText: '正常运行'
      },
      {
        id: 2,
        name: '冷冻水泵LD01',
        location: '五四广场站',
        power: 30,
        efficiency: 88,
        status: 'warning',
        statusText: '效率偏低'
      },
      {
        id: 3,
        name: '冷却塔LQT01',
        location: '延安三路站',
        power: 11,
        efficiency: 92,
        status: 'normal',
        statusText: '正常运行'
      }
    ])

    // 站点数据
    const visibleStations = ref([
      { id: 1, name: '振华路', x: 100, y: 300, radius: 8, energyLevel: 'medium' },
      { id: 2, name: '五四广场', x: 200, y: 300, radius: 10, energyLevel: 'high' },
      { id: 3, name: '延安三路', x: 300, y: 300, radius: 6, energyLevel: 'low' },
      { id: 4, name: '青岛北站', x: 400, y: 200, radius: 12, energyLevel: 'high' },
      { id: 5, name: '宁夏路', x: 500, y: 300, radius: 8, energyLevel: 'medium' }
    ])

    // 优化建议
    const optimizationSuggestions = ref([
      {
        id: 1,
        title: '冷机运行时间优化',
        description: '建议在非高峰时段降低冷机运行功率，预计可节能15%',
        priority: 'high',
        priorityText: '高优先级',
        energySaving: 2500,
        costSaving: 3750
      },
      {
        id: 2,
        title: '水泵变频调节',
        description: '根据负荷需求调整水泵频率，提高系统效率',
        priority: 'medium',
        priorityText: '中优先级',
        energySaving: 1200,
        costSaving: 1800
      }
    ])

    // 图表引用
    const realtimeChart = ref(null)
    const trendChart = ref(null)
    const reportChart = ref(null)

    // 方法
    const updateDateTime = () => {
      const now = new Date()
      currentDate.value = now.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
      currentTime.value = now.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }

    const onLineChange = () => {
      // 根据选择的线路过滤站点
      console.log('Line changed:', selectedLine.value)
    }

    const refreshData = () => {
      // 刷新实时数据
      console.log('Refreshing data...')
    }

    const selectStation = (station) => {
      console.log('Selected station:', station)
    }

    const selectTimePeriod = (period) => {
      selectedPeriod.value = period
      // 更新趋势图表
    }

    const applySuggestion = (suggestion) => {
      console.log('Applying suggestion:', suggestion)
    }

    const viewDetails = (suggestion) => {
      console.log('Viewing details:', suggestion)
    }

    const exportReport = () => {
      console.log('Exporting report...')
    }

    // 初始化图表
    const initCharts = () => {
      // 实时监控图表
      if (realtimeChart.value) {
        const chart = echarts.init(realtimeChart.value)
        const option = {
          backgroundColor: 'transparent',
          grid: { top: 20, right: 20, bottom: 40, left: 60 },
          xAxis: {
            type: 'category',
            data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
            axisLine: { lineStyle: { color: '#4a5568' } },
            axisLabel: { color: '#a0aec0' }
          },
          yAxis: {
            type: 'value',
            axisLine: { lineStyle: { color: '#4a5568' } },
            axisLabel: { color: '#a0aec0' },
            splitLine: { lineStyle: { color: '#2d3748' } }
          },
          series: [{
            data: [1200, 1100, 1350, 1500, 1400, 1300],
            type: 'line',
            smooth: true,
            lineStyle: { color: '#00d4ff', width: 3 },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(0, 212, 255, 0.3)' },
                  { offset: 1, color: 'rgba(0, 212, 255, 0)' }
                ]
              }
            }
          }]
        }
        chart.setOption(option)
      }

      // 趋势分析图表
      if (trendChart.value) {
        const chart = echarts.init(trendChart.value)
        const option = {
          backgroundColor: 'transparent',
          grid: { top: 20, right: 20, bottom: 40, left: 60 },
          xAxis: {
            type: 'category',
            data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
            axisLine: { lineStyle: { color: '#4a5568' } },
            axisLabel: { color: '#a0aec0' }
          },
          yAxis: {
            type: 'value',
            axisLine: { lineStyle: { color: '#4a5568' } },
            axisLabel: { color: '#a0aec0' },
            splitLine: { lineStyle: { color: '#2d3748' } }
          },
          series: [
            {
              name: '能耗',
              data: [28000, 26500, 29000, 31000, 28500, 25000, 24000],
              type: 'bar',
              itemStyle: { color: '#00d4ff' }
            },
            {
              name: '目标',
              data: [30000, 30000, 30000, 30000, 30000, 30000, 30000],
              type: 'line',
              lineStyle: { color: '#ff6b6b', type: 'dashed' }
            }
          ]
        }
        chart.setOption(option)
      }

      // 报表图表
      if (reportChart.value) {
        const chart = echarts.init(reportChart.value)
        const option = {
          backgroundColor: 'transparent',
          grid: { top: 20, right: 20, bottom: 40, left: 60 },
          xAxis: {
            type: 'category',
            data: ['1月', '2月', '3月', '4月', '5月', '6月'],
            axisLine: { lineStyle: { color: '#4a5568' } },
            axisLabel: { color: '#a0aec0' }
          },
          yAxis: {
            type: 'value',
            axisLine: { lineStyle: { color: '#4a5568' } },
            axisLabel: { color: '#a0aec0' },
            splitLine: { lineStyle: { color: '#2d3748' } }
          },
          series: [{
            data: [850000, 820000, 780000, 750000, 720000, 680000],
            type: 'line',
            smooth: true,
            lineStyle: { color: '#4ecdc4', width: 3 },
            itemStyle: { color: '#4ecdc4' }
          }]
        }
        chart.setOption(option)
      }
    }

    // 生命周期
    onMounted(() => {
      updateDateTime()
      const timer = setInterval(updateDateTime, 1000)
      
      // 延迟初始化图表，确保DOM已渲染
      setTimeout(initCharts, 100)

      onUnmounted(() => {
        clearInterval(timer)
      })
    })

    return {
      currentDate,
      currentTime,
      systemStatus,
      weather,
      totalConsumption,
      currentPower,
      efficiencyRatio,
      costSaving,
      totalTrend,
      powerTrend,
      efficiencyTrend,
      savingTrend,
      selectedLine,
      selectedPeriod,
      reportType,
      timePeriods,
      equipmentStatus,
      equipmentList,
      visibleStations,
      optimizationSuggestions,
      realtimeChart,
      trendChart,
      reportChart,
      onLineChange,
      refreshData,
      selectStation,
      selectTimePeriod,
      applySuggestion,
      viewDetails,
      exportReport
    }
  }
}
</script>

<style scoped>
.energy-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #0c1426 0%, #1a2332 100%);
  color: #ffffff;
  font-family: 'Microsoft YaHei', sans-serif;
  overflow-x: auto;
}

/* 顶部标题栏 */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 30px;
}

.dashboard-title {
  font-size: 28px;
  font-weight: bold;
  margin: 0;
  background: linear-gradient(45deg, #00d4ff, #4ecdc4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: flex;
  align-items: center;
  gap: 10px;
}

.system-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #4ecdc4;
  box-shadow: 0 0 10px rgba(78, 205, 196, 0.5);
  animation: pulse 2s infinite;
}

.status-indicator.normal {
  background: #4ecdc4;
  box-shadow: 0 0 10px rgba(78, 205, 196, 0.5);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 30px;
}

.datetime {
  text-align: right;
}

.date {
  font-size: 16px;
  color: #a0aec0;
}

.time {
  font-size: 24px;
  font-weight: bold;
  color: #00d4ff;
}

.weather-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.temperature {
  font-size: 18px;
  font-weight: bold;
  color: #4ecdc4;
}

.humidity {
  font-size: 14px;
  color: #a0aec0;
}

/* 主要内容区域 */
.dashboard-content {
  padding: 20px 30px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.row {
  display: flex;
  gap: 20px;
  min-height: 300px;
}

/* KPI卡片 */
.kpi-row {
  min-height: 150px;
}

.kpi-card {
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 24px;
  position: relative;
  overflow: hidden;
}

.kpi-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #00d4ff, #4ecdc4);
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.kpi-header h3 {
  margin: 0;
  font-size: 16px;
  color: #a0aec0;
}

.kpi-value {
  margin-bottom: 12px;
}

.kpi-value .value {
  font-size: 36px;
  font-weight: bold;
  color: #ffffff;
}

.kpi-value .unit {
  font-size: 18px;
  color: #a0aec0;
  margin-left: 8px;
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: 8px;
}

.trend-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: bold;
}

.trend-indicator.positive {
  color: #4ecdc4;
}

.trend-indicator.negative {
  color: #ff6b6b;
}

.trend-text {
  color: #a0aec0;
  font-size: 14px;
}

/* 面板样式 */
.panel {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
}

.panel-header {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
  color: #ffffff;
}

.panel-content {
  padding: 24px;
  height: calc(100% - 80px);
}

/* 实时监控面板 */
.realtime-panel {
  flex: 2;
}

.panel-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.panel-controls select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  padding: 8px 12px;
  color: #ffffff;
  font-size: 14px;
}

.refresh-btn {
  background: rgba(0, 212, 255, 0.2);
  border: 1px solid #00d4ff;
  border-radius: 6px;
  padding: 8px 12px;
  color: #00d4ff;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background: rgba(0, 212, 255, 0.3);
}

.realtime-chart {
  height: 100%;
  min-height: 200px;
}

/* 地图面板 */
.map-panel {
  flex: 1;
}

.legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.legend-item::before {
  content: '';
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-item.high::before {
  background: #ff6b6b;
}

.legend-item.medium::before {
  background: #ffa726;
}

.legend-item.low::before {
  background: #4ecdc4;
}

.station-map {
  height: 100%;
}

.map-container {
  height: 100%;
  position: relative;
}

.metro-lines {
  width: 100%;
  height: 100%;
}

.station-marker {
  cursor: pointer;
  transition: all 0.3s ease;
}

.station-marker:hover {
  r: 12;
}

.station-marker.high {
  fill: #ff6b6b;
}

.station-marker.medium {
  fill: #ffa726;
}

.station-marker.low {
  fill: #4ecdc4;
}

.station-label {
  fill: #ffffff;
  font-size: 12px;
  pointer-events: none;
}

/* 趋势分析面板 */
.trend-panel {
  flex: 2;
}

.time-selector {
  display: flex;
  gap: 8px;
}

.time-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  padding: 6px 12px;
  color: #a0aec0;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 12px;
}

.time-btn.active,
.time-btn:hover {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
  color: #00d4ff;
}

.trend-chart {
  height: 100%;
  min-height: 200px;
}

/* 设备状态面板 */
.equipment-panel {
  flex: 1;
}

.status-summary {
  display: flex;
  gap: 16px;
  font-size: 12px;
}

.status-count {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-count::before {
  content: '';
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-count.normal::before {
  background: #4ecdc4;
}

.status-count.warning::before {
  background: #ffa726;
}

.status-count.error::before {
  background: #ff6b6b;
}

.equipment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
  overflow-y: auto;
}

.equipment-item {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s ease;
}

.equipment-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

.equipment-info {
  margin-bottom: 8px;
}

.equipment-name {
  font-weight: bold;
  color: #ffffff;
}

.equipment-location {
  font-size: 12px;
  color: #a0aec0;
}

.equipment-metrics {
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.metric-label {
  font-size: 10px;
  color: #a0aec0;
}

.metric-value {
  font-size: 14px;
  font-weight: bold;
  color: #ffffff;
}

.equipment-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.equipment-status .status-indicator {
  width: 8px;
  height: 8px;
}

.equipment-status .status-indicator.normal {
  background: #4ecdc4;
}

.equipment-status .status-indicator.warning {
  background: #ffa726;
}

.equipment-status .status-indicator.error {
  background: #ff6b6b;
}

.status-text {
  font-size: 12px;
  color: #a0aec0;
}

/* 优化建议面板 */
.suggestions-panel {
  flex: 1;
}

.ai-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #4ecdc4;
  font-size: 12px;
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
  overflow-y: auto;
}

.suggestion-item {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s ease;
}

.suggestion-item.high {
  border-left: 4px solid #ff6b6b;
}

.suggestion-item.medium {
  border-left: 4px solid #ffa726;
}

.suggestion-item.low {
  border-left: 4px solid #4ecdc4;
}

.suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.suggestion-title {
  font-weight: bold;
  color: #ffffff;
}

.suggestion-priority {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(255, 107, 107, 0.2);
  color: #ff6b6b;
}

.suggestion-content {
  margin-bottom: 12px;
}

.suggestion-description {
  color: #a0aec0;
  font-size: 14px;
  margin-bottom: 8px;
}

.suggestion-metrics {
  display: flex;
  gap: 16px;
  font-size: 12px;
}

.suggestion-metrics .metric {
  color: #4ecdc4;
}

.suggestion-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn.primary {
  background: #00d4ff;
  border: none;
  color: #ffffff;
}

.action-btn.primary:hover {
  background: #00b8e6;
}

.action-btn.secondary {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #a0aec0;
}

.action-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.05);
}

/* 报表面板 */
.report-panel {
  flex: 1;
}

.report-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.report-controls select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  padding: 8px 12px;
  color: #ffffff;
  font-size: 14px;
}

.export-btn {
  background: rgba(78, 205, 196, 0.2);
  border: 1px solid #4ecdc4;
  border-radius: 6px;
  padding: 8px 12px;
  color: #4ecdc4;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.export-btn:hover {
  background: rgba(78, 205, 196, 0.3);
}

.report-chart {
  height: 100%;
  min-height: 200px;
}

/* 动画效果 */
@keyframes pulse {
  0% {
    box-shadow: 0 0 10px rgba(78, 205, 196, 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(78, 205, 196, 0.8);
  }
  100% {
    box-shadow: 0 0 10px rgba(78, 205, 196, 0.5);
  }
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .row {
    flex-direction: column;
  }
  
  .kpi-row {
    flex-direction: row;
  }
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .kpi-row {
    flex-direction: column;
  }
  
  .dashboard-content {
    padding: 16px;
  }
}
</style>