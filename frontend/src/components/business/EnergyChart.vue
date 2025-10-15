<template>
  <BaseCard :title="title" class="energy-chart">
    <div class="chart-container">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
        <el-button @click="$emit('retry')" type="primary" size="small">
          重试
        </el-button>
      </div>
      <div v-else ref="chartRef" class="chart" :style="{ height: height }"></div>
    </div>
    
    <div v-if="showControls" class="chart-controls">
      <div class="time-range">
        <label>时间范围：</label>
        <select v-model="selectedTimeRange" @change="handleTimeRangeChange">
          <option value="1h">最近1小时</option>
          <option value="24h">最近24小时</option>
          <option value="7d">最近7天</option>
          <option value="30d">最近30天</option>
        </select>
      </div>
      
      <div class="chart-type">
        <label>图表类型：</label>
        <select v-model="selectedChartType" @change="handleChartTypeChange">
          <option value="line">折线图</option>
          <option value="bar">柱状图</option>
          <option value="area">面积图</option>
        </select>
      </div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { BaseCard } from '../common'
import type { ChartData } from './types'

interface Props {
  title?: string
  data?: ChartData[]
  loading?: boolean
  error?: string
  height?: string
  showControls?: boolean
  chartType?: 'line' | 'bar' | 'area'
  timeRange?: string
}

interface Emits {
  (e: 'retry'): void
  (e: 'timeRangeChange', value: string): void
  (e: 'chartTypeChange', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  title: '能源图表',
  data: () => [],
  loading: false,
  error: '',
  height: '400px',
  showControls: true,
  chartType: 'line',
  timeRange: '24h'
})

const emit = defineEmits<Emits>()

const chartRef = ref<HTMLElement>()
const selectedTimeRange = ref(props.timeRange)
const selectedChartType = ref(props.chartType)
let chartInstance: any = null

// 模拟图表库（实际项目中应该使用 ECharts 或其他图表库）
const initChart = async () => {
  if (!chartRef.value || !props.data?.length) return
  
  // 这里应该初始化真实的图表库
  // 例如：chartInstance = echarts.init(chartRef.value)
  console.log('初始化图表:', {
    type: selectedChartType.value,
    data: props.data,
    timeRange: selectedTimeRange.value
  })
}

const updateChart = () => {
  if (!chartInstance) return
  
  // 更新图表数据
  console.log('更新图表数据:', props.data)
}

const handleTimeRangeChange = () => {
  emit('timeRangeChange', selectedTimeRange.value)
}

const handleChartTypeChange = () => {
  emit('chartTypeChange', selectedChartType.value)
  // 重新初始化图表
  nextTick(() => {
    initChart()
  })
}

// 监听数据变化
watch(() => props.data, () => {
  updateChart()
}, { deep: true })

// 监听加载状态
watch(() => props.loading, (newVal) => {
  if (!newVal && props.data?.length) {
    nextTick(() => {
      initChart()
    })
  }
})

onMounted(() => {
  if (!props.loading && props.data?.length) {
    initChart()
  }
})

onUnmounted(() => {
  if (chartInstance) {
    // 销毁图表实例
    chartInstance.dispose?.()
    chartInstance = null
  }
})
</script>

<style scoped>
.energy-chart {
  height: 100%;
}

.chart-container {
  position: relative;
  min-height: 300px;
}

.chart {
  width: 100%;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: var(--text-color-secondary);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-color);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.chart-controls {
  display: flex;
  gap: 24px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.time-range,
.chart-type {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-range label,
.chart-type label {
  font-size: 14px;
  color: var(--text-color-secondary);
  white-space: nowrap;
}

.time-range select,
.chart-type select {
  padding: 4px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--bg-color);
  color: var(--text-color);
  font-size: 14px;
}

.time-range select:focus,
.chart-type select:focus {
  outline: none;
  border-color: var(--primary-color);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chart-controls {
    flex-direction: column;
    gap: 12px;
  }
  
  .time-range,
  .chart-type {
    justify-content: space-between;
  }
}

/* 深色模式 */
@media (prefers-color-scheme: dark) {
  .time-range select,
  .chart-type select {
    background: var(--bg-color-dark);
    border-color: var(--border-color-dark);
    color: var(--text-color-dark);
  }
}
</style>