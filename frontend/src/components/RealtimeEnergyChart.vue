<template>
  <div class="realtime-energy-chart">
    <div class="chart-header">
      <h3 class="chart-title">
        <i class="icon-energy"></i>
        实时能耗监测
      </h3>
      <div class="chart-controls">
        <select v-model="selectedLine" @change="onLineChange" class="line-selector">
          <option value="">选择线路</option>
          <option v-for="line in lines" :key="line" :value="line">{{ line }}</option>
        </select>
        <select v-model="selectedStation" @change="onStationChange" class="station-selector">
          <option value="">全部站点</option>
          <option v-for="station in stations" :key="station.ip" :value="station.ip">
            {{ station.name }}
          </option>
        </select>
        <button @click="toggleAutoRefresh" class="refresh-btn" :class="{ active: autoRefresh }">
          <i class="icon-refresh" :class="{ spinning: autoRefresh }"></i>
          {{ autoRefresh ? '停止刷新' : '自动刷新' }}
        </button>
      </div>
    </div>

    <div class="chart-container">
      <div class="loading-overlay" v-if="loading">
        <div class="spinner"></div>
        <span>加载中...</span>
      </div>
      
      <div class="chart-content" v-show="!loading">
        <!-- 实时功率图表 -->
        <div class="power-chart">
          <h4>实时功率 (kW)</h4>
          <div ref="powerChart" class="chart-canvas"></div>
        </div>

        <!-- 能耗趋势图表 -->
        <div class="consumption-chart">
          <h4>能耗趋势 (kWh)</h4>
          <div ref="consumptionChart" class="chart-canvas"></div>
        </div>

        <!-- 站点对比图表 -->
        <div class="comparison-chart" v-if="!selectedStation">
          <h4>站点能耗对比</h4>
          <div ref="comparisonChart" class="chart-canvas"></div>
        </div>
      </div>

      <!-- 数据统计卡片 -->
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon power-icon"></div>
          <div class="stat-content">
            <div class="stat-value">{{ currentPower.toFixed(2) }}</div>
            <div class="stat-label">当前功率 (kW)</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon consumption-icon"></div>
          <div class="stat-content">
            <div class="stat-value">{{ todayConsumption.toFixed(2) }}</div>
            <div class="stat-label">今日能耗 (kWh)</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon efficiency-icon"></div>
          <div class="stat-content">
            <div class="stat-value">{{ efficiency.toFixed(1) }}%</div>
            <div class="stat-label">能效比</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon status-icon" :class="systemStatus"></div>
          <div class="stat-content">
            <div class="stat-value">{{ systemStatusText }}</div>
            <div class="stat-label">系统状态</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'RealtimeEnergyChart',
  data() {
    return {
      // 基础数据
      lines: [],
      stations: [],
      selectedLine: '',
      selectedStation: '',
      
      // 图表实例
      powerChartInstance: null,
      consumptionChartInstance: null,
      comparisonChartInstance: null,
      
      // 状态控制
      loading: false,
      autoRefresh: true,
      refreshInterval: null,
      
      // 实时数据
      realtimeData: [],
      currentPower: 0,
      todayConsumption: 0,
      efficiency: 85.6,
      systemStatus: 'normal',
      
      // 图表数据
      powerData: {
        times: [],
        values: []
      },
      consumptionData: {
        times: [],
        values: []
      },
      comparisonData: []
    }
  },
  computed: {
    systemStatusText() {
      const statusMap = {
        normal: '正常',
        warning: '警告',
        error: '故障',
        offline: '离线',
        '正常': '正常',
        '警告': '警告',
        '故障': '故障',
        '离线': '离线'
      }
      return statusMap[this.systemStatus] || this.systemStatus || '未知'
    }
  },
  mounted() {
    this.initCharts()
    this.loadLines()
    this.startAutoRefresh()
  },
  beforeUnmount() {
    this.stopAutoRefresh()
    this.destroyCharts()
  },
  methods: {
    // 初始化图表
    initCharts() {
      this.$nextTick(() => {
        if (this.$refs.powerChart) {
          this.powerChartInstance = echarts.init(this.$refs.powerChart)
          this.initPowerChart()
        }
        if (this.$refs.consumptionChart) {
          this.consumptionChartInstance = echarts.init(this.$refs.consumptionChart)
          this.initConsumptionChart()
        }
        if (this.$refs.comparisonChart) {
          this.comparisonChartInstance = echarts.init(this.$refs.comparisonChart)
          this.initComparisonChart()
        }
        
        // 响应式调整
        window.addEventListener('resize', this.handleResize)
      })
    },

    // 初始化功率图表
    initPowerChart() {
      const option = {
        title: {
          show: false
        },
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            return `${params[0].name}<br/>功率: ${params[0].value} kW`
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: this.powerData.times,
          axisLabel: {
            color: '#8c8c8c'
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            color: '#8c8c8c',
            formatter: '{value} kW'
          }
        },
        series: [{
          name: '功率',
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: {
            color: '#1890ff',
            width: 2
          },
          itemStyle: {
            color: '#1890ff'
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [{
                offset: 0, color: 'rgba(24, 144, 255, 0.3)'
              }, {
                offset: 1, color: 'rgba(24, 144, 255, 0.1)'
              }]
            }
          },
          data: this.powerData.values
        }]
      }
      this.powerChartInstance.setOption(option)
    },

    // 初始化能耗图表
    initConsumptionChart() {
      const option = {
        title: {
          show: false
        },
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            return `${params[0].name}<br/>能耗: ${params[0].value} kWh`
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: this.consumptionData.times,
          axisLabel: {
            color: '#8c8c8c'
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            color: '#8c8c8c',
            formatter: '{value} kWh'
          }
        },
        series: [{
          name: '能耗',
          type: 'bar',
          barWidth: '60%',
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [{
                offset: 0, color: '#52c41a'
              }, {
                offset: 1, color: '#73d13d'
              }]
            }
          },
          data: this.consumptionData.values
        }]
      }
      this.consumptionChartInstance.setOption(option)
    },

    // 初始化对比图表
    initComparisonChart() {
      const option = {
        title: {
          show: false
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: this.comparisonData.map(item => item.name),
          axisLabel: {
            color: '#8c8c8c',
            rotate: 45
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            color: '#8c8c8c',
            formatter: '{value} kWh'
          }
        },
        series: [{
          name: '能耗',
          type: 'bar',
          barWidth: '50%',
          itemStyle: {
            color: function(params) {
              const colors = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1']
              return colors[params.dataIndex % colors.length]
            }
          },
          data: this.comparisonData.map(item => item.value)
        }]
      }
      this.comparisonChartInstance.setOption(option)
    },

    // 加载线路数据
    async loadLines() {
      try {
        const response = await fetch('/api/energy-dashboard/stations')
        const data = await response.json()
        this.lines = data.lines || []
        if (this.lines.length > 0) {
          this.selectedLine = this.lines[0]
          await this.loadStations()
        }
      } catch (error) {
        console.error('加载线路数据失败:', error)
      }
    },

    // 加载站点数据
    async loadStations() {
      if (!this.selectedLine) {
        this.stations = []
        return
      }
      
      try {
        const response = await fetch(`/api/energy-dashboard/stations?line=${this.selectedLine}`)
        const data = await response.json()
        this.stations = data.stations || []
      } catch (error) {
        console.error('加载站点数据失败:', error)
      }
    },

    // 加载实时数据
    async loadRealtimeData() {
      this.loading = true
      try {
        const params = new URLSearchParams()
        if (this.selectedLine) params.append('line', this.selectedLine)
        if (this.selectedStation) params.append('station_ip', this.selectedStation)
        
        const response = await fetch(`http://localhost:8000/api/energy-dashboard/realtime?${params}`)
        const data = await response.json()
        
        if (data.success) {
          this.updateChartData(data.data)
          this.updateStats(data.data)
        } else {
          console.error('API返回错误:', data.error)
          this.useMockData()
        }
      } catch (error) {
        console.error('加载实时数据失败:', error)
        this.useMockData()
      } finally {
        this.loading = false
      }
    },

    // 更新图表数据
    updateChartData(data) {
      // 更新实时功率图表
      if (data.realtime_chart) {
        this.powerData.times = data.realtime_chart.map(item => item.time)
        this.powerData.values = data.realtime_chart.map(item => item.power)
        this.powerChartInstance?.setOption({
          xAxis: { data: this.powerData.times },
          series: [{ data: this.powerData.values }]
        })
      }

      // 更新能耗趋势图表（使用相同数据源的能耗字段）
      if (data.realtime_chart) {
        this.consumptionData.times = data.realtime_chart.map(item => item.time)
        this.consumptionData.values = data.realtime_chart.map(item => item.energy)
        this.consumptionChartInstance?.setOption({
          xAxis: { data: this.consumptionData.times },
          series: [{ data: this.consumptionData.values }]
        })
      }

      // 更新站点对比图表
      if (data.station_comparison && !this.selectedStation) {
        this.comparisonData = data.station_comparison
        this.comparisonChartInstance?.setOption({
          xAxis: { data: this.comparisonData.map(item => item.station) },
          series: [{ data: this.comparisonData.map(item => item.energy) }]
        })
      }
    },

    // 更新统计数据
    updateStats(data) {
      this.currentPower = data.current_power || 0
      this.todayConsumption = data.today_energy || 0
      this.efficiency = (data.efficiency_ratio * 100) || 85.6
      this.systemStatus = data.system_status || 'normal'
    },

    // 线路变更
    async onLineChange() {
      this.selectedStation = ''
      await this.loadStations()
      await this.loadRealtimeData()
    },

    // 站点变更
    async onStationChange() {
      await this.loadRealtimeData()
    },

    // 切换自动刷新
    toggleAutoRefresh() {
      this.autoRefresh = !this.autoRefresh
      if (this.autoRefresh) {
        this.startAutoRefresh()
      } else {
        this.stopAutoRefresh()
      }
    },

    // 开始自动刷新
    startAutoRefresh() {
      this.stopAutoRefresh()
      this.loadRealtimeData()
      this.refreshInterval = setInterval(() => {
        if (this.autoRefresh) {
          this.loadRealtimeData()
        }
      }, 5000) // 5秒刷新一次
    },

    // 停止自动刷新
    stopAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval)
        this.refreshInterval = null
      }
    },

    // 窗口大小调整
    handleResize() {
      this.powerChartInstance?.resize()
      this.consumptionChartInstance?.resize()
      this.comparisonChartInstance?.resize()
    },

    // 使用模拟数据
    useMockData() {
      const mockData = {
        current_power: 1050.5,
        today_consumption: 2100.8,
        efficiency: 89.2,
        system_status: 'normal',
        power_trend: this.generateMockPowerData(),
        consumption_trend: this.generateMockConsumptionData(),
        station_comparison: [
          { name: '振华路', value: 95.2 },
          { name: '五四广场', value: 108.7 },
          { name: '延安三路', value: 87.3 },
          { name: '青岛站', value: 125.6 }
        ]
      }
      this.updateChartData(mockData)
      this.updateStats(mockData)
    },

    // 生成模拟功率数据
    generateMockPowerData() {
      const data = []
      const now = new Date()
      for (let i = 23; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 60 * 60 * 1000)
        const value = 800 + Math.random() * 400
        data.push({
          time: time.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
          value: Math.round(value * 10) / 10
        })
      }
      return data
    },

    // 生成模拟能耗数据
    generateMockConsumptionData() {
      const data = []
      const now = new Date()
      for (let i = 6; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 24 * 60 * 60 * 1000)
        const value = 1500 + Math.random() * 1000
        data.push({
          time: time.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' }),
          value: Math.round(value * 10) / 10
        })
      }
      return data
    },

    // 销毁图表
    destroyCharts() {
      window.removeEventListener('resize', this.handleResize)
      this.powerChartInstance?.dispose()
      this.consumptionChartInstance?.dispose()
      this.comparisonChartInstance?.dispose()
    }
  }
}
</script>

<style scoped>
.realtime-energy-chart {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.chart-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-energy::before {
  content: "⚡";
  font-size: 20px;
}

.chart-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.line-selector,
.station-selector {
  padding: 6px 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 14px;
}

.line-selector option,
.station-selector option {
  color: #333;
}

.refresh-btn {
  padding: 6px 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.refresh-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.refresh-btn.active {
  background: rgba(255, 255, 255, 0.2);
}

.icon-refresh::before {
  content: "🔄";
}

.icon-refresh.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.chart-container {
  position: relative;
  padding: 24px;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 8px;
}

.chart-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.power-chart,
.consumption-chart,
.comparison-chart {
  background: #fafafa;
  border-radius: 6px;
  padding: 16px;
}

.comparison-chart {
  grid-column: 1 / -1;
}

.chart-content h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.chart-canvas {
  height: 200px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.power-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.power-icon::before {
  content: "⚡";
  color: white;
}

.consumption-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.consumption-icon::before {
  content: "📊";
  color: white;
}

.efficiency-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.efficiency-icon::before {
  content: "📈";
  color: white;
}

.status-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.status-icon.warning {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.status-icon.error {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
}

.status-icon.offline {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.status-icon::before {
  content: "✅";
  color: white;
}

.status-icon.warning::before {
  content: "⚠️";
}

.status-icon.error::before {
  content: "❌";
}

.status-icon.offline::before {
  content: "📴";
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .chart-controls {
    justify-content: center;
  }

  .chart-content {
    grid-template-columns: 1fr;
  }

  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>