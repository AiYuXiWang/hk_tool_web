<template>
  <BaseCard
    :title="title"
    :shadow="shadow"
    :hover="hover"
    :loading="loading"
    class="energy-device-monitor"
  >
    <template #header-extra>
      <div class="monitor-controls">
        <el-button
          plain
          size="small"
          @click="toggleAutoRefresh"
          :class="{ 'active': autoRefresh }"
        >
          {{ autoRefresh ? '停止自动刷新' : '自动刷新' }}
        </el-button>
        <el-button
          plain
          size="small"
          @click="refreshDevices"
          :loading="refreshing"
        >
          刷新
        </el-button>
      </div>
    </template>

    <div class="monitor-content">
      <!-- 设备概览 -->
      <div class="device-overview">
        <div class="overview-stats">
          <div class="stat-item">
            <div class="stat-value">{{ totalDevices }}</div>
            <div class="stat-label">总设备数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value online">{{ onlineDevices }}</div>
            <div class="stat-label">在线</div>
          </div>
          <div class="stat-item">
            <div class="stat-value warning">{{ warningDevices }}</div>
            <div class="stat-label">告警</div>
          </div>
          <div class="stat-item">
            <div class="stat-value offline">{{ offlineDevices }}</div>
            <div class="stat-label">离线</div>
          </div>
        </div>
      </div>

      <!-- 设备列表 -->
      <div class="device-list">
        <BaseTable
          :columns="deviceColumns"
          :data="filteredDevices"
          :loading="loading"
          row-key="id"
          @row-click="handleDeviceClick"
        >
          <template #status="{ row }">
            <span :class="['status-badge', row.status]">
              {{ getStatusText(row.status) }}
            </span>
          </template>
          <template #power="{ row }">
            {{ formatPower(row.power) }}
          </template>
          <template #energy="{ row }">
            {{ formatEnergy(row.energy) }}
          </template>
        </BaseTable>
      </div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import BaseCard from '../common/BaseCard.vue'
import BaseTable from '../common/BaseTable.vue'

// Props
interface Props {
  title?: string
  shadow?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
  hover?: boolean
  autoRefreshInterval?: number
}

const props = withDefaults(defineProps<Props>(), {
  title: '设备监控',
  shadow: 'md',
  hover: true,
  autoRefreshInterval: 30000
})

// Emits
interface Emits {
  (e: 'device-click', device: any): void
  (e: 'refresh'): void
}

const emit = defineEmits<Emits>()

// 响应式数据
const loading = ref(false)
const refreshing = ref(false)
const autoRefresh = ref(false)
const devices = ref<any[]>([])
const refreshTimer = ref<NodeJS.Timeout | null>(null)

// 计算属性
const totalDevices = computed(() => devices.value.length)
const onlineDevices = computed(() => devices.value.filter(d => d.status === 'online').length)
const offlineDevices = computed(() => devices.value.filter(d => d.status === 'offline').length)
const warningDevices = computed(() => devices.value.filter(d => d.status === 'warning').length)

const filteredDevices = computed(() => devices.value)

// 表格列定义
const deviceColumns = [
  { key: 'name', title: '设备名称', width: 200 },
  { key: 'type', title: '设备类型', width: 120 },
  { key: 'status', title: '状态', width: 100, slot: 'status' },
  { key: 'power', title: '功率', width: 120, slot: 'power' },
  { key: 'energy', title: '能耗', width: 120, slot: 'energy' },
  { key: 'location', title: '位置', width: 150 },
  { key: 'lastUpdate', title: '最后更新', width: 180 }
]

// 方法
const fetchDevices = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    devices.value = [
      {
        id: 1,
        name: '空调设备-01',
        type: '空调',
        status: 'online',
        power: 2500,
        energy: 125.5,
        location: '办公区A',
        lastUpdate: new Date().toLocaleString()
      },
      {
        id: 2,
        name: '照明设备-02',
        type: '照明',
        status: 'warning',
        power: 800,
        energy: 45.2,
        location: '办公区B',
        lastUpdate: new Date().toLocaleString()
      }
    ]
  } catch (error) {
    console.error('获取设备数据失败:', error)
  } finally {
    loading.value = false
  }
}

const refreshDevices = async () => {
  refreshing.value = true
  try {
    await fetchDevices()
    emit('refresh')
  } finally {
    refreshing.value = false
  }
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const startAutoRefresh = () => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
  }
  refreshTimer.value = setInterval(() => {
    refreshDevices()
  }, props.autoRefreshInterval)
}

const stopAutoRefresh = () => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
    refreshTimer.value = null
  }
}

const handleDeviceClick = (device: any) => {
  emit('device-click', device)
}

const getStatusText = (status: string) => {
  const statusMap = {
    online: '在线',
    offline: '离线',
    warning: '告警'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const formatPower = (power: number) => {
  return `${power.toFixed(1)} W`
}

const formatEnergy = (energy: number) => {
  return `${energy.toFixed(1)} kWh`
}

// 生命周期
onMounted(() => {
  fetchDevices()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.energy-device-monitor {
  height: 100%;
}

.monitor-controls {
  display: flex;
  gap: 8px;
}

.monitor-controls .active {
  background-color: var(--primary-color);
  color: white;
}

.monitor-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

.device-overview {
  background: var(--bg-color-light);
  border-radius: 8px;
  padding: 16px;
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 12px;
  background: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 4px;
}

.stat-value.online {
  color: var(--success-color);
}

.stat-value.warning {
  color: var(--warning-color);
}

.stat-value.offline {
  color: var(--error-color);
}

.stat-label {
  font-size: 12px;
  color: var(--text-color-secondary);
}

.device-list {
  flex: 1;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.online {
  background-color: var(--success-color-light);
  color: var(--success-color);
}

.status-badge.warning {
  background-color: var(--warning-color-light);
  color: var(--warning-color);
}

.status-badge.offline {
  background-color: var(--error-color-light);
  color: var(--error-color);
}
</style>