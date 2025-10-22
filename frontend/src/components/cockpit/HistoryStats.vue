<template>
  <div class="history-stats">
    <StatCard
      v-for="stat in stats"
      :key="stat.key"
      :title="stat.title"
      :value="stat.value"
      :unit="stat.unit"
      :icon="stat.icon"
      :trend="stat.trend"
      :variant="stat.variant"
    />
    
    <!-- 数据质量指示器 -->
    <div v-if="showDataQuality" class="data-quality-card stat-card">
      <div class="stat-header">
        <div class="stat-icon data-quality-icon">
          <i class="icon-check-circle"></i>
        </div>
        <div class="stat-title-group">
          <h3 class="stat-title">数据质量</h3>
          <p class="stat-subtitle">有效数据点比例</p>
        </div>
      </div>
      
      <div class="quality-content">
        <div class="quality-value">{{ dataQuality }}%</div>
        <div class="quality-bar">
          <div 
            class="quality-progress" 
            :style="{ width: dataQuality + '%' }"
            :class="getQualityClass(dataQuality)"
          ></div>
        </div>
        <div class="quality-label">{{ getQualityLabel(dataQuality) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import StatCard from './StatCard.vue'

export interface HistoryStatistics {
  total: number      // 总能耗 kWh
  average: number    // 平均功率 kW
  peak: number       // 峰值功率 kW
  min: number        // 最小功率 kW
  dataQuality?: number // 数据质量 0-100%
}

interface Props {
  statistics: HistoryStatistics
  showDataQuality?: boolean
  timeRange?: string
}

const props = withDefaults(defineProps<Props>(), {
  showDataQuality: true,
  timeRange: '24h'
})

const stats = computed(() => [
  {
    key: 'total',
    title: '总能耗',
    value: props.statistics.total || 0,
    unit: 'kWh',
    icon: 'icon-zap',
    variant: 'primary' as const,
    trend: undefined
  },
  {
    key: 'average',
    title: '平均功率',
    value: props.statistics.average || 0,
    unit: 'kW',
    icon: 'icon-activity',
    variant: 'success' as const,
    trend: undefined
  },
  {
    key: 'peak',
    title: '峰值功率',
    value: props.statistics.peak || 0,
    unit: 'kW',
    icon: 'icon-trending-up',
    variant: 'warning' as const,
    trend: undefined
  },
  {
    key: 'min',
    title: '最小功率',
    value: props.statistics.min || 0,
    unit: 'kW',
    icon: 'icon-trending-down',
    variant: 'info' as const,
    trend: undefined
  }
])

const dataQuality = computed(() => {
  return Math.round(props.statistics.dataQuality ?? 100)
})

const getQualityClass = (quality: number): string => {
  if (quality >= 90) return 'quality-excellent'
  if (quality >= 70) return 'quality-good'
  if (quality >= 50) return 'quality-fair'
  return 'quality-poor'
}

const getQualityLabel = (quality: number): string => {
  if (quality >= 90) return '优秀'
  if (quality >= 70) return '良好'
  if (quality >= 50) return '一般'
  return '较差'
}
</script>

<style scoped>
.history-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--spacing-md, 16px);
  margin-bottom: var(--spacing-lg, 24px);
}

/* 数据质量卡片 */
.data-quality-card {
  padding: var(--spacing-md, 16px);
  background: rgba(14, 23, 51, 0.65);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(0, 212, 255, 0.35);
  border-radius: var(--border-radius-lg, 12px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.data-quality-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 212, 255, 0.25);
  border-color: rgba(0, 255, 204, 0.5);
}

.stat-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm, 12px);
  margin-bottom: var(--spacing-md, 16px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius-md, 8px);
  font-size: 24px;
}

.data-quality-icon {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 255, 204, 0.2));
  color: var(--color-primary, #00D4FF);
}

.stat-title-group {
  flex: 1;
}

.stat-title {
  margin: 0;
  font-size: var(--font-size-md, 16px);
  font-weight: var(--font-weight-semibold, 600);
  color: var(--color-text-primary, #ffffff);
}

.stat-subtitle {
  margin: 4px 0 0 0;
  font-size: var(--font-size-xs, 12px);
  color: var(--color-text-tertiary, rgba(255, 255, 255, 0.6));
}

.quality-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm, 12px);
}

.quality-value {
  font-size: 32px;
  font-weight: var(--font-weight-bold, 700);
  color: var(--color-text-primary, #ffffff);
  line-height: 1;
}

.quality-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.quality-progress {
  height: 100%;
  border-radius: 4px;
  transition: width 1s ease, background 0.3s ease;
  position: relative;
  overflow: hidden;
}

.quality-progress::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.quality-excellent {
  background: linear-gradient(90deg, #10b981, #34d399);
}

.quality-good {
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
}

.quality-fair {
  background: linear-gradient(90deg, #f59e0b, #fbbf24);
}

.quality-poor {
  background: linear-gradient(90deg, #ef4444, #f87171);
}

.quality-label {
  font-size: var(--font-size-sm, 14px);
  font-weight: var(--font-weight-medium, 500);
  color: var(--color-text-secondary, rgba(255, 255, 255, 0.8));
}

/* 响应式设计 */
@media (max-width: 768px) {
  .history-stats {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: var(--spacing-sm, 12px);
  }
  
  .quality-value {
    font-size: 24px;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
}
</style>
