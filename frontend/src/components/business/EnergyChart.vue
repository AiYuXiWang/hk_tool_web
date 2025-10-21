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
          <option value="pie">饼图</option>
        </select>
      </div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { BaseCard } from '../common'
import type { ChartData } from './types'
import * as echarts from 'echarts'

interface Props {
  title?: string
  data?: ChartData[]
  loading?: boolean
  error?: string
  height?: string
  showControls?: boolean
  chartType?: 'line' | 'bar' | 'area' | 'pie'
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

// 主题：根据 CSS 变量构建并注册 Tech 主题
const getCssVar = (name: string, fallback?: string) => {
  const val = getComputedStyle(document.documentElement).getPropertyValue(name)?.trim()
  return val || (fallback ?? '')
}

const buildTechTheme = () => {
  const bg = getCssVar('--color-background-primary', '#0b1020')
  const text = getCssVar('--color-text-primary', '#cfe9ff')
  const textSecondary = getCssVar('--color-text-secondary', '#9bb3c6')
  const border = getCssVar('--color-border-primary', '#1e2a3a')
  const borderSecondary = getCssVar('--color-border-secondary', '#142033')
  const primary = getCssVar('--color-primary', '#00d4ff')
  const success = getCssVar('--color-success', '#4ecdc4')
  const warning = getCssVar('--color-warning', '#ffd166')
  const danger = getCssVar('--color-danger', '#ff6b6b')
  const info = getCssVar('--color-info', primary || '#00d4ff')

  return {
    color: [primary, info, success, warning, danger, '#a29bfe'],
    backgroundColor: 'transparent',
    textStyle: {
      color: text,
      fontFamily: getCssVar('--font-family-sans', 'Inter, system-ui, -apple-system, Helvetica, Arial, sans-serif'),
      fontSize: 12
    },
    title: { textStyle: { color: text, fontWeight: 600 } },
    legend: { textStyle: { color: textSecondary } },
    tooltip: {
      backgroundColor: getCssVar('--color-background-elevated', bg),
      borderColor: border,
      borderWidth: 1,
      textStyle: { color: textSecondary }
    },
    axisPointer: {
      lineStyle: { color: primary },
      crossStyle: { color: primary }
    },
    categoryAxis: {
      axisLine: { lineStyle: { color: border } },
      axisTick: { lineStyle: { color: border } },
      axisLabel: { color: textSecondary },
      splitLine: { show: false }
    },
    valueAxis: {
      axisLine: { lineStyle: { color: border } },
      axisTick: { lineStyle: { color: border } },
      axisLabel: { color: textSecondary },
      splitLine: { lineStyle: { color: borderSecondary } }
    }
  }
}

const ensureTechTheme = () => {
  try {
    // 重复注册同名主题在 ECharts 中是安全的
    echarts.registerTheme('tech', buildTechTheme())
  } catch (e) {
    // 忽略注册异常
  }
}

const handleResize = () => {
  chartInstance?.resize()
}

// 构建 ECharts 配置
const buildOption = (chartDataList: ChartData[]) => {
  const cd = chartDataList?.[0]
  const type = selectedChartType.value

  if (!cd) {
    return {
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'value' },
      series: []
    }
  }

  if (type === 'pie') {
    const categories = cd.xAxis || []
    const values = cd.data || []
    const pieData = categories.map((name, idx) => ({ name, value: values[idx] ?? 0 }))
    return {
      tooltip: { trigger: 'item' },
      legend: { top: 'bottom' },
      series: [{
        name: cd.title || '分类分项能耗',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 1 },
        label: { show: true, formatter: '{b}: {d}%' },
        data: pieData
      }]
    }
  }

  // 线/柱/面积图
  const option: any = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: cd.xAxis || [] },
    yAxis: { type: 'value' },
    series: []
  }

  if (cd.series && cd.series.length) {
    option.series = cd.series.map((s: any) => ({
      ...s,
      type: type === 'area' ? 'line' : type, // 面积图用line + areaStyle
      areaStyle: type === 'area' ? { opacity: 0.2 } : undefined,
      stack: (s.stack || cd.options?.stacked) ? 'total' : undefined
    }))
  } else {
    option.series = [{
      name: cd.title || '数据',
      type: type === 'area' ? 'line' : type,
      data: cd.data || [],
      areaStyle: type === 'area' ? { opacity: 0.2 } : undefined
    }]
  }
  return option
}

// 初始化图表
const initChart = async () => {
  if (!chartRef.value || !props.data?.length) return
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  ensureTechTheme()
  chartInstance = echarts.init(chartRef.value, 'tech')
  const option = buildOption(props.data)
  chartInstance.setOption(option)
}

// 更新图表
const updateChart = () => {
  if (!chartInstance || !props.data?.length) return
  const option = buildOption(props.data)
  chartInstance.setOption(option, true)
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
  window.addEventListener('resize', handleResize)
  const darkMedia = window.matchMedia?.('(prefers-color-scheme: dark)')
  darkMedia && darkMedia.addEventListener?.('change', () => {
    // 令牌颜色变化时，重建主题并重绘
    nextTick(() => {
      initChart()
    })
  })
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  window.removeEventListener('resize', handleResize)
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
  color: var(--color-text-secondary);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-border-primary);
  border-top: 3px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.chart-controls {
  display: flex;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-secondary);
}

.time-range,
.chart-type {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.time-range label,
.chart-type label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.time-range select,
.chart-type select {
  padding: 4px 8px;
  border: 1px solid var(--color-border-primary);
  border-radius: var(--border-radius-sm);
  background: var(--color-background-primary);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
}

.time-range select:focus,
.chart-type select:focus {
  outline: none;
  border-color: var(--color-primary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chart-controls {
    flex-direction: column;
    gap: var(--spacing-sm);
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
    background: var(--color-background-primary);
    border-color: var(--color-border-primary);
    color: var(--color-text-primary);
  }
}
</style>