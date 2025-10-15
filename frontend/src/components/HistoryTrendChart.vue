<template>
  <div class="history-trend-container">
    <div class="trend-header">
      <h3>📈 历史趋势分析</h3>
      <div class="time-range-selector">
        <button 
          v-for="range in timeRanges" 
          :key="range.value"
          :class="['time-btn', { active: selectedRange === range.value }]"
          @click="selectTimeRange(range.value)"
        >
          {{ range.label }}
        </button>
      </div>
    </div>

    <div class="trend-content">
      <!-- 统计卡片 -->
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon">⚡</div>
          <div class="stat-info">
            <div class="stat-value">{{ formatNumber(statistics.total_energy) }}</div>
            <div class="stat-label">总能耗 (kWh)</div>
            <div class="stat-change" :class="getChangeClass(statistics.energy_change)">
              {{ formatChange(statistics.energy_change) }}
            </div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">🔌</div>
          <div class="stat-info">
            <div class="stat-value">{{ formatNumber(statistics.avg_power) }}</div>
            <div class="stat-label">平均功率 (kW)</div>
            <div class="stat-change" :class="getChangeClass(statistics.power_change)">
              {{ formatChange(statistics.power_change) }}
            </div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.avg_efficiency }}%</div>
            <div class="stat-label">平均能效</div>
            <div class="stat-change" :class="getChangeClass(statistics.efficiency_change)">
              {{ formatChange(statistics.efficiency_change) }}
            </div>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="charts-container">
        <div class="chart-section">
          <h4>能耗趋势</h4>
          <div ref="energyChart" class="chart"></div>
        </div>

        <div class="chart-section">
          <h4>功率趋势</h4>
          <div ref="powerChart" class="chart"></div>
        </div>

        <div class="chart-section">
          <h4>能效趋势</h4>
          <div ref="efficiencyChart" class="chart"></div>
        </div>
      </div>
    </div>

    <div class="loading-overlay" v-if="loading">
      <div class="loading-spinner"></div>
      <div>加载中...</div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import axios from 'axios'

export default {
  name: 'HistoryTrendChart',
  data() {
    return {
      loading: false,
      selectedRange: '24h',
      timeRanges: [
        { value: '24h', label: '24小时' },
        { value: '7d', label: '7天' },
        { value: '30d', label: '30天' },
        { value: '90d', label: '90天' }
      ],
      historyData: [],
      statistics: {
        total_energy: 0,
        avg_power: 0,
        avg_efficiency: 0,
        energy_change: 0,
        power_change: 0,
        efficiency_change: 0
      },
      energyChartInstance: null,
      powerChartInstance: null,
      efficiencyChartInstance: null
    }
  },
  mounted() {
    this.initCharts()
    this.loadHistoryData()
  },
  beforeUnmount() {
    if (this.energyChartInstance) {
      this.energyChartInstance.dispose()
    }
    if (this.powerChartInstance) {
      this.powerChartInstance.dispose()
    }
    if (this.efficiencyChartInstance) {
      this.efficiencyChartInstance.dispose()
    }
  },
  methods: {
    async selectTimeRange(range) {
      this.selectedRange = range
      await this.loadHistoryData()
    },

    async loadHistoryData() {
      this.loading = true
      try {
        const response = await axios.get(`http://localhost:8000/api/energy-dashboard/history`, {
          params: {
            time_range: this.selectedRange
          }
        })
        
        if (response.data) {
          this.historyData = response.data.data_points || []
          this.statistics = response.data.statistics || {}
          this.updateCharts()
        }
      } catch (error) {
        console.error('加载历史数据失败:', error)
        // 使用模拟数据
        this.generateMockData()
      } finally {
        this.loading = false
      }
    },

    generateMockData() {
      const points = this.selectedRange === '24h' ? 24 : 
                   this.selectedRange === '7d' ? 7 : 
                   this.selectedRange === '30d' ? 30 : 30
      
      this.historyData = []
      for (let i = 0; i < points; i++) {
        const energy = 8000 + Math.random() * 4000
        const power = 600 + Math.random() * 400
        const efficiency = 75 + Math.random() * 20
        
        this.historyData.push({
          time: this.selectedRange === '24h' ? `${i}:00` : `${i + 1}`,
          energy: Math.round(energy),
          power: Math.round(power),
          efficiency: Math.round(efficiency * 10) / 10
        })
      }
      
      this.statistics = {
        total_energy: this.historyData.reduce((sum, item) => sum + item.energy, 0),
        avg_power: Math.round(this.historyData.reduce((sum, item) => sum + item.power, 0) / this.historyData.length),
        avg_efficiency: Math.round(this.historyData.reduce((sum, item) => sum + item.efficiency, 0) / this.historyData.length * 10) / 10,
        energy_change: (Math.random() - 0.5) * 30,
        power_change: (Math.random() - 0.5) * 20,
        efficiency_change: (Math.random() - 0.5) * 10
      }
      
      this.updateCharts()
    },

    initCharts() {
      this.energyChartInstance = echarts.init(this.$refs.energyChart)
      this.powerChartInstance = echarts.init(this.$refs.powerChart)
      this.efficiencyChartInstance = echarts.init(this.$refs.efficiencyChart)
    },

    updateCharts() {
      this.updateEnergyChart()
      this.updatePowerChart()
      this.updateEfficiencyChart()
    },

    updateEnergyChart() {
      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: '{b}<br/>能耗: {c} kWh'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: this.historyData.map(item => item.time),
          axisLabel: {
            color: '#666'
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            color: '#666',
            formatter: '{value} kWh'
          }
        },
        series: [{
          type: 'line',
          data: this.historyData.map(item => item.energy),
          smooth: true,
          lineStyle: {
            color: '#1890ff',
            width: 3
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
          }
        }]
      }
      this.energyChartInstance.setOption(option)
    },

    updatePowerChart() {
      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: '{b}<br/>功率: {c} kW'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: this.historyData.map(item => item.time),
          axisLabel: {
            color: '#666'
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            color: '#666',
            formatter: '{value} kW'
          }
        },
        series: [{
          type: 'line',
          data: this.historyData.map(item => item.power),
          smooth: true,
          lineStyle: {
            color: '#52c41a',
            width: 3
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [{
                offset: 0, color: 'rgba(82, 196, 26, 0.3)'
              }, {
                offset: 1, color: 'rgba(82, 196, 26, 0.1)'
              }]
            }
          }
        }]
      }
      this.powerChartInstance.setOption(option)
    },

    updateEfficiencyChart() {
      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: '{b}<br/>能效: {c}%'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: this.historyData.map(item => item.time),
          axisLabel: {
            color: '#666'
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            color: '#666',
            formatter: '{value}%'
          }
        },
        series: [{
          type: 'line',
          data: this.historyData.map(item => item.efficiency),
          smooth: true,
          lineStyle: {
            color: '#faad14',
            width: 3
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [{
                offset: 0, color: 'rgba(250, 173, 20, 0.3)'
              }, {
                offset: 1, color: 'rgba(250, 173, 20, 0.1)'
              }]
            }
          }
        }]
      }
      this.efficiencyChartInstance.setOption(option)
    },

    formatNumber(num) {
      if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M'
      } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K'
      }
      return num.toFixed(1)
    },

    formatChange(change) {
      const sign = change >= 0 ? '+' : ''
      return `${sign}${change.toFixed(1)}%`
    },

    getChangeClass(change) {
      return change >= 0 ? 'positive' : 'negative'
    }
  }
}
</script>

<style scoped>
.history-trend-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
}

.trend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.trend-header h3 {
  margin: 0;
  color: #1890ff;
  font-size: 18px;
}

.time-range-selector {
  display: flex;
  gap: 8px;
}

.time-btn {
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 12px;
}

.time-btn:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.time-btn.active {
  background: #1890ff;
  color: white;
  border-color: #1890ff;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #1890ff;
}

.stat-icon {
  font-size: 24px;
  margin-right: 12px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #262626;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #8c8c8c;
  margin-bottom: 4px;
}

.stat-change {
  font-size: 12px;
  font-weight: 500;
}

.stat-change.positive {
  color: #52c41a;
}

.stat-change.negative {
  color: #ff4d4f;
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.chart-section {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
}

.chart-section h4 {
  margin: 0 0 12px 0;
  color: #262626;
  font-size: 14px;
}

.chart {
  width: 100%;
  height: 200px;
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
  border-radius: 8px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .trend-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .charts-container {
    grid-template-columns: 1fr;
  }
}
</style>