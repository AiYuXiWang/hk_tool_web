<template>
  <div class="kpi-dashboard">
    <!-- 主要KPI指标 -->
    <div class="kpi-main-section">
      <h3 class="section-title">
        <i class="icon-dashboard"></i>
        核心能耗指标
      </h3>
      <div class="kpi-grid">
        <div 
          v-for="kpi in mainKpis" 
          :key="kpi.id"
          class="kpi-card"
          :class="kpi.type"
        >
          <div class="kpi-header">
            <div class="kpi-icon">
              <i :class="kpi.icon"></i>
            </div>
            <div class="kpi-info">
              <h4 class="kpi-title">{{ kpi.title }}</h4>
              <span class="kpi-subtitle">{{ kpi.subtitle }}</span>
            </div>
          </div>
          <div class="kpi-value">
            <span class="value">{{ formatValue(kpi.value) }}</span>
            <span class="unit">{{ kpi.unit }}</span>
          </div>
          <div class="kpi-trend">
            <div class="trend-indicator" :class="kpi.trend.type">
              <i :class="getTrendIcon(kpi.trend.type)"></i>
              <span>{{ Math.abs(kpi.trend.value) }}%</span>
            </div>
            <span class="trend-period">{{ kpi.trend.period }}</span>
          </div>
          <div class="kpi-progress" v-if="kpi.target">
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: `${Math.min(100, (kpi.value / kpi.target) * 100)}%` }"
              ></div>
            </div>
            <span class="progress-text">目标: {{ formatValue(kpi.target) }}{{ kpi.unit }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 详细统计指标 -->
    <div class="kpi-detail-section">
      <h3 class="section-title">
        <i class="icon-chart"></i>
        详细统计数据
      </h3>
      <div class="detail-grid">
        <div class="detail-group" v-for="group in detailGroups" :key="group.name">
          <h4 class="group-title">{{ group.name }}</h4>
          <div class="detail-items">
            <div 
              v-for="item in group.items" 
              :key="item.id"
              class="detail-item"
            >
              <div class="item-header">
                <span class="item-label">{{ item.label }}</span>
                <span class="item-value">{{ formatValue(item.value) }}{{ item.unit }}</span>
              </div>
              <div class="item-bar">
                <div 
                  class="bar-fill" 
                  :style="{ 
                    width: `${item.percentage}%`,
                    backgroundColor: item.color 
                  }"
                ></div>
              </div>
              <div class="item-meta">
                <span class="item-change" :class="item.change.type">
                  <i :class="getTrendIcon(item.change.type)"></i>
                  {{ Math.abs(item.change.value) }}%
                </span>
                <span class="item-rank">排名 #{{ item.rank }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 性能指标雷达图 -->
    <div class="kpi-radar-section">
      <h3 class="section-title">
        <i class="icon-radar"></i>
        综合性能评估
      </h3>
      <div class="radar-container">
        <div class="radar-chart" ref="radarChart"></div>
        <div class="radar-legend">
          <div class="legend-item" v-for="metric in radarMetrics" :key="metric.name">
            <div class="legend-color" :style="{ backgroundColor: metric.color }"></div>
            <span class="legend-label">{{ metric.name }}</span>
            <span class="legend-score">{{ metric.score }}/100</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 实时告警和建议 -->
    <div class="kpi-alerts-section">
      <h3 class="section-title">
        <i class="icon-warning"></i>
        实时告警与建议
      </h3>
      <div class="alerts-container">
        <div class="alert-item" v-for="alert in alerts" :key="alert.id" :class="alert.level">
          <div class="alert-icon">
            <i :class="getAlertIcon(alert.level)"></i>
          </div>
          <div class="alert-content">
            <h5 class="alert-title">{{ alert.title }}</h5>
            <p class="alert-message">{{ alert.message }}</p>
            <div class="alert-meta">
              <span class="alert-time">{{ formatTime(alert.timestamp) }}</span>
              <span class="alert-source">{{ alert.source }}</span>
            </div>
          </div>
          <div class="alert-actions">
            <button class="action-btn primary" @click="handleAlert(alert)">
              处理
            </button>
            <button class="action-btn secondary" @click="dismissAlert(alert.id)">
              忽略
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

// 组件属性
const props = defineProps({
  refreshInterval: {
    type: Number,
    default: 30000 // 30秒刷新一次
  }
})

// 响应式数据
const radarChart = ref(null)
let radarChartInstance = null
let refreshTimer = null

// 主要KPI指标
const mainKpis = reactive([
  {
    id: 'total-energy',
    title: '总能耗',
    subtitle: '今日累计',
    icon: 'icon-energy',
    type: 'energy',
    value: 4347.5,
    unit: 'kWh',
    target: 5000,
    trend: {
      type: 'positive',
      value: 5.2,
      period: '较昨日'
    }
  },
  {
    id: 'avg-power',
    title: '平均功率',
    subtitle: '当前时段',
    icon: 'icon-power',
    type: 'power',
    value: 1375.2,
    unit: 'kW',
    target: 1500,
    trend: {
      type: 'negative',
      value: 2.1,
      period: '较上时'
    }
  },
  {
    id: 'efficiency',
    title: '系统能效',
    subtitle: 'COP值',
    icon: 'icon-efficiency',
    type: 'efficiency',
    value: 3.8,
    unit: '',
    target: 4.0,
    trend: {
      type: 'positive',
      value: 3.5,
      period: '较昨日'
    }
  },
  {
    id: 'cost-saving',
    title: '节能收益',
    subtitle: '本月累计',
    icon: 'icon-savings',
    type: 'savings',
    value: 28450,
    unit: '元',
    target: 30000,
    trend: {
      type: 'positive',
      value: 15.8,
      period: '较上月'
    }
  },
  {
    id: 'carbon-reduction',
    title: '碳减排量',
    subtitle: '今日累计',
    icon: 'icon-carbon',
    type: 'carbon',
    value: 2.1,
    unit: '吨CO₂',
    target: 2.5,
    trend: {
      type: 'positive',
      value: 8.3,
      period: '较昨日'
    }
  },
  {
    id: 'equipment-health',
    title: '设备健康度',
    subtitle: '综合评分',
    icon: 'icon-health',
    type: 'health',
    value: 92.5,
    unit: '%',
    target: 95,
    trend: {
      type: 'stable',
      value: 0.5,
      period: '较昨日'
    }
  }
])

// 详细统计分组
const detailGroups = reactive([
  {
    name: '线路能耗分布',
    items: [
      {
        id: 'line-m3',
        label: '3号线',
        value: 1580.3,
        unit: 'kWh',
        percentage: 85,
        color: '#00d4ff',
        change: { type: 'positive', value: 3.2 },
        rank: 1
      },
      {
        id: 'line-m8',
        label: '8号线',
        value: 1420.8,
        unit: 'kWh',
        percentage: 76,
        color: '#4ecdc4',
        change: { type: 'negative', value: 1.5 },
        rank: 2
      },
      {
        id: 'line-m11',
        label: '11号线',
        value: 1346.4,
        unit: 'kWh',
        percentage: 72,
        color: '#45b7d1',
        change: { type: 'positive', value: 2.8 },
        rank: 3
      }
    ]
  },
  {
    name: '设备类型能耗',
    items: [
      {
        id: 'chiller',
        label: '冷机系统',
        value: 2890.5,
        unit: 'kWh',
        percentage: 92,
        color: '#ff6b6b',
        change: { type: 'negative', value: 2.3 },
        rank: 1
      },
      {
        id: 'pump',
        label: '水泵系统',
        value: 890.2,
        unit: 'kWh',
        percentage: 58,
        color: '#ffa726',
        change: { type: 'positive', value: 4.1 },
        rank: 2
      },
      {
        id: 'fan',
        label: '风机系统',
        value: 566.8,
        unit: 'kWh',
        percentage: 38,
        color: '#66bb6a',
        change: { type: 'stable', value: 0.8 },
        rank: 3
      }
    ]
  }
])

// 雷达图指标
const radarMetrics = reactive([
  { name: '能效水平', score: 85, color: '#00d4ff' },
  { name: '设备健康', score: 92, color: '#4ecdc4' },
  { name: '运行稳定性', score: 88, color: '#45b7d1' },
  { name: '节能效果', score: 78, color: '#ffa726' },
  { name: '维护水平', score: 90, color: '#66bb6a' }
])

// 实时告警
const alerts = reactive([
  {
    id: 1,
    level: 'warning',
    title: '冷机效率偏低',
    message: '五四广场站冷机LS01效率降至88%，建议检查冷凝器清洁度',
    timestamp: Date.now() - 300000, // 5分钟前
    source: '五四广场站'
  },
  {
    id: 2,
    level: 'info',
    title: '节能机会识别',
    message: '检测到非高峰时段可优化运行策略，预计节能15%',
    timestamp: Date.now() - 600000, // 10分钟前
    source: 'AI分析引擎'
  },
  {
    id: 3,
    level: 'success',
    title: '优化效果显著',
    message: '延安三路站水泵变频调节效果良好，能效提升12%',
    timestamp: Date.now() - 900000, // 15分钟前
    source: '延安三路站'
  }
])

// 工具函数
const formatValue = (value) => {
  if (typeof value !== 'number') return value
  if (value >= 1000000) {
    return (value / 1000000).toFixed(1) + 'M'
  } else if (value >= 1000) {
    return (value / 1000).toFixed(1) + 'K'
  }
  return value.toLocaleString()
}

const getTrendIcon = (type) => {
  switch (type) {
    case 'positive': return 'icon-arrow-up'
    case 'negative': return 'icon-arrow-down'
    case 'stable': return 'icon-minus'
    default: return 'icon-minus'
  }
}

const getAlertIcon = (level) => {
  switch (level) {
    case 'error': return 'icon-error'
    case 'warning': return 'icon-warning'
    case 'info': return 'icon-info'
    case 'success': return 'icon-success'
    default: return 'icon-info'
  }
}

const formatTime = (timestamp) => {
  const now = Date.now()
  const diff = now - timestamp
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(minutes / 60)
  
  if (hours > 0) {
    return `${hours}小时前`
  } else if (minutes > 0) {
    return `${minutes}分钟前`
  } else {
    return '刚刚'
  }
}

// 初始化雷达图
const initRadarChart = () => {
  if (!radarChart.value) return
  
  radarChartInstance = echarts.init(radarChart.value)
  
  const option = {
    backgroundColor: 'transparent',
    radar: {
      indicator: radarMetrics.map(metric => ({
        name: metric.name,
        max: 100
      })),
      center: ['50%', '50%'],
      radius: '70%',
      axisName: {
        color: '#a0aec0',
        fontSize: 12
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.2)'
        }
      }
    },
    series: [{
      type: 'radar',
      data: [{
        value: radarMetrics.map(metric => metric.score),
        name: '当前性能',
        areaStyle: {
          color: 'rgba(0, 212, 255, 0.2)'
        },
        lineStyle: {
          color: '#00d4ff',
          width: 2
        },
        itemStyle: {
          color: '#00d4ff'
        }
      }]
    }]
  }
  
  radarChartInstance.setOption(option)
}

// 刷新数据
const refreshData = async () => {
  try {
    // 这里可以调用API获取最新数据
    console.log('刷新KPI数据...')
    
    // 模拟数据更新
    mainKpis.forEach(kpi => {
      const variation = (Math.random() - 0.5) * 0.1 // ±5%变化
      kpi.value = Math.max(0, kpi.value * (1 + variation))
    })
    
    // 更新雷达图
    if (radarChartInstance) {
      radarMetrics.forEach(metric => {
        const variation = (Math.random() - 0.5) * 0.1
        metric.score = Math.max(0, Math.min(100, metric.score * (1 + variation)))
      })
      
      const option = radarChartInstance.getOption()
      option.series[0].data[0].value = radarMetrics.map(metric => metric.score)
      radarChartInstance.setOption(option)
    }
  } catch (error) {
    console.error('刷新KPI数据失败:', error)
  }
}

// 处理告警
const handleAlert = (alert) => {
  console.log('处理告警:', alert)
  // 这里可以打开详细处理页面或执行相应操作
}

// 忽略告警
const dismissAlert = (alertId) => {
  const index = alerts.findIndex(alert => alert.id === alertId)
  if (index > -1) {
    alerts.splice(index, 1)
  }
}

// 生命周期
onMounted(() => {
  initRadarChart()
  refreshData()
  
  // 设置定时刷新
  refreshTimer = setInterval(refreshData, props.refreshInterval)
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    if (radarChartInstance) {
      radarChartInstance.resize()
    }
  })
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  if (radarChartInstance) {
    radarChartInstance.dispose()
  }
})
</script>

<style scoped>
.kpi-dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
}

.section-title i {
  color: #00d4ff;
}

/* 主要KPI指标 */
.kpi-main-section {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 24px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.kpi-card {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 212, 255, 0.15);
}

.kpi-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #00d4ff, #4ecdc4);
}

.kpi-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.kpi-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 212, 255, 0.2);
}

.kpi-icon i {
  font-size: 20px;
  color: #00d4ff;
}

.kpi-info {
  flex: 1;
}

.kpi-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
}

.kpi-subtitle {
  font-size: 12px;
  color: #a0aec0;
}

.kpi-value {
  margin-bottom: 12px;
}

.kpi-value .value {
  font-size: 32px;
  font-weight: bold;
  color: #ffffff;
}

.kpi-value .unit {
  font-size: 16px;
  color: #a0aec0;
  margin-left: 4px;
}

.kpi-trend {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.trend-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 600;
  font-size: 14px;
}

.trend-indicator.positive {
  color: #4ecdc4;
}

.trend-indicator.negative {
  color: #ff6b6b;
}

.trend-indicator.stable {
  color: #ffa726;
}

.trend-period {
  font-size: 12px;
  color: #a0aec0;
}

.kpi-progress {
  margin-top: 12px;
}

.progress-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 4px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00d4ff, #4ecdc4);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 11px;
  color: #a0aec0;
}

/* 详细统计 */
.kpi-detail-section {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 24px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
}

.detail-group {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 20px;
}

.group-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
}

.detail-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-item {
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.detail-item:last-child {
  border-bottom: none;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.item-label {
  font-size: 14px;
  color: #a0aec0;
}

.item-value {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
}

.item-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}

.bar-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-change {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
}

.item-change.positive {
  color: #4ecdc4;
}

.item-change.negative {
  color: #ff6b6b;
}

.item-change.stable {
  color: #ffa726;
}

.item-rank {
  font-size: 12px;
  color: #a0aec0;
}

/* 雷达图 */
.kpi-radar-section {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 24px;
}

.radar-container {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 24px;
  align-items: center;
}

.radar-chart {
  height: 300px;
}

.radar-legend {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-label {
  flex: 1;
  font-size: 14px;
  color: #a0aec0;
}

.legend-score {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

/* 告警和建议 */
.kpi-alerts-section {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 24px;
}

.alerts-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid;
}

.alert-item.error {
  background: rgba(255, 107, 107, 0.1);
  border-left-color: #ff6b6b;
}

.alert-item.warning {
  background: rgba(255, 167, 38, 0.1);
  border-left-color: #ffa726;
}

.alert-item.info {
  background: rgba(0, 212, 255, 0.1);
  border-left-color: #00d4ff;
}

.alert-item.success {
  background: rgba(102, 187, 106, 0.1);
  border-left-color: #66bb6a;
}

.alert-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.alert-content {
  flex: 1;
}

.alert-title {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

.alert-message {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #a0aec0;
  line-height: 1.4;
}

.alert-meta {
  display: flex;
  gap: 16px;
}

.alert-time,
.alert-source {
  font-size: 11px;
  color: #718096;
}

.alert-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn.primary {
  background: #00d4ff;
  color: #1a202c;
}

.action-btn.primary:hover {
  background: #00b8e6;
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #a0aec0;
}

.action-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }
  
  .radar-container {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .radar-chart {
    height: 250px;
  }
}

@media (max-width: 768px) {
  .kpi-dashboard {
    padding: 16px;
    gap: 16px;
  }
  
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .alert-item {
    flex-direction: column;
    gap: 12px;
  }
  
  .alert-actions {
    align-self: flex-start;
  }
}
</style>