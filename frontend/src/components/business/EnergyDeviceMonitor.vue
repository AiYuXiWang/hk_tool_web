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
  gap: 12px;
  align-items: center;
  justify-content: flex-end;
}

.monitor-controls :deep(.el-button) {
  background: linear-gradient(135deg, rgba(14, 23, 51, 0.7) 0%, rgba(18, 32, 58, 0.6) 100%);
  border-color: rgba(0, 212, 255, 0.3);
  color: rgba(255, 255, 255, 0.9);
  box-shadow: 0 8px 20px rgba(0, 212, 255, 0.2);
  transition: all 0.3s ease;
}

.monitor-controls :deep(.el-button:hover) {
  border-color: rgba(0, 255, 204, 0.6);
  color: #fff;
  box-shadow: 0 10px 28px rgba(0, 212, 255, 0.25);
}

.monitor-controls :deep(.el-button.active) {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.75) 0%, rgba(0, 255, 204, 0.6) 100%);
  border-color: rgba(0, 255, 204, 0.8);
  color: #0a1528;
  box-shadow: 0 12px 32px rgba(0, 212, 255, 0.35);
}

.monitor-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
}

.device-overview {
  background: linear-gradient(135deg, rgba(14, 23, 51, 0.7) 0%, rgba(18, 32, 58, 0.6) 100%);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(0, 212, 255, 0.25);
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(14px);
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 18px 12px;
  background: linear-gradient(135deg, rgba(13, 25, 47, 0.8) 0%, rgba(16, 32, 60, 0.6) 100%);
  border-radius: 18px;
  border: 1px solid rgba(0, 212, 255, 0.18);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08), 0 8px 24px rgba(0, 212, 255, 0.12);
  color: rgba(255, 255, 255, 0.95);
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 6px;
  text-shadow: 0 0 18px rgba(0, 212, 255, 0.45);
}

.stat-value.online {
  color: rgba(82, 196, 26, 0.95);
  text-shadow: 0 0 18px rgba(82, 196, 26, 0.4);
}

.stat-value.warning {
  color: rgba(250, 173, 20, 0.95);
  text-shadow: 0 0 18px rgba(250, 173, 20, 0.45);
}

.stat-value.offline {
  color: rgba(255, 77, 79, 0.95);
  text-shadow: 0 0 18px rgba(255, 77, 79, 0.45);
}

.stat-label {
  font-size: 13px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.6);
}

.device-list {
  flex: 1;
  background: linear-gradient(135deg, rgba(14, 23, 51, 0.7) 0%, rgba(18, 32, 58, 0.6) 100%);
  border-radius: 16px;
  border: 1px solid rgba(0, 212, 255, 0.25);
  overflow: hidden;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(14px);
}

.device-list :deep(.el-table) {
  background-color: transparent;
  color: rgba(255, 255, 255, 0.92);
}

.device-list :deep(.el-table__header-wrapper) {
  background-color: rgba(0, 212, 255, 0.08);
}

.device-list :deep(.el-table__row:hover) {
  background-color: rgba(0, 212, 255, 0.08);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
}

.status-badge.online {
  background: linear-gradient(135deg, rgba(82, 196, 26, 0.3) 0%, rgba(143, 239, 123, 0.6) 100%);
  color: #0f2a05;
}

.status-badge.warning {
  background: linear-gradient(135deg, rgba(250, 173, 20, 0.3) 0%, rgba(255, 221, 132, 0.6) 100%);
  color: #402b04;
}

.status-badge.offline {
  background: linear-gradient(135deg, rgba(255, 77, 79, 0.3) 0%, rgba(255, 155, 157, 0.6) 100%);
  color: #3f0e11;
}
</style>