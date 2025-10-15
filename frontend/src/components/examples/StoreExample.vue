<template>
  <div class="store-example">
    <h2>状态管理系统示例</h2>
    
    <!-- 应用状态示例 -->
    <div class="section">
      <h3>应用状态 (AppStore)</h3>
      <div class="info-grid">
        <div class="info-item">
          <label>当前用户:</label>
          <span>{{ appStore.user?.username || '未登录' }}</span>
        </div>
        <div class="info-item">
          <label>当前标签:</label>
          <span>{{ appStore.currentTab }}</span>
        </div>
        <div class="info-item">
          <label>连接状态:</label>
          <span :class="connectionStatusClass">{{ appStore.connectionStatus }}</span>
        </div>
        <div class="info-item">
          <label>未读通知:</label>
          <span>{{ appStore.unreadNotifications.length }}</span>
        </div>
      </div>
      
      <div class="actions">
        <el-button @click="handleLogin" :loading="appStore.loading">
          {{ appStore.isAuthenticated ? '退出登录' : '模拟登录' }}
        </el-button>
        <el-button @click="addTestNotification">添加测试通知</el-button>
        <el-button @click="appStore.setSidebarCollapsed(!appStore.sidebarCollapsed)">
          {{ appStore.sidebarCollapsed ? '展开' : '收起' }}侧边栏
        </el-button>
      </div>
    </div>

    <!-- 能源数据状态示例 -->
    <div class="section">
      <h3>能源数据状态 (EnergyStore)</h3>
      <div class="info-grid">
        <div class="info-item">
          <label>实时功率:</label>
          <span>{{ energyStore.realtimeData?.power || 0 }} kW</span>
        </div>
        <div class="info-item">
          <label>今日用电量:</label>
          <span>{{ energyStore.todayConsumption }} kWh</span>
        </div>
        <div class="info-item">
          <label>在线设备数:</label>
          <span>{{ energyStore.onlineDeviceCount }}</span>
        </div>
        <div class="info-item">
          <label>数据更新时间:</label>
          <span>{{ formatTime(energyStore.lastUpdateTime) }}</span>
        </div>
      </div>
      
      <div class="actions">
        <el-button @click="energyStore.fetchRealtimeData()" :loading="energyStore.loading">
          刷新实时数据
        </el-button>
        <el-button @click="energyStore.fetchHistoryData()">
          获取历史数据
        </el-button>
        <el-button @click="energyStore.startRealTimeUpdates()">
          开始实时更新
        </el-button>
        <el-button @click="energyStore.stopRealTimeUpdates()">
          停止实时更新
        </el-button>
      </div>
    </div>

    <!-- 设备状态示例 -->
    <div class="section">
      <h3>设备管理状态 (DeviceStore)</h3>
      <div class="info-grid">
        <div class="info-item">
          <label>设备总数:</label>
          <span>{{ deviceStore.totalDeviceCount }}</span>
        </div>
        <div class="info-item">
          <label>在线设备:</label>
          <span>{{ deviceStore.onlineDeviceCount }}</span>
        </div>
        <div class="info-item">
          <label>告警设备:</label>
          <span>{{ deviceStore.alertDeviceCount }}</span>
        </div>
        <div class="info-item">
          <label>选中设备:</label>
          <span>{{ deviceStore.selectedDevice?.name || '无' }}</span>
        </div>
      </div>
      
      <div class="actions">
        <el-button @click="deviceStore.fetchDeviceTree()" :loading="deviceStore.loading">
          刷新设备树
        </el-button>
        <el-button @click="deviceStore.fetchDeviceStatus()">
          获取设备状态
        </el-button>
        <el-button @click="selectRandomDevice">
          随机选择设备
        </el-button>
      </div>
    </div>

    <!-- 导出状态示例 -->
    <div class="section">
      <h3>导出管理状态 (ExportStore)</h3>
      <div class="info-grid">
        <div class="info-item">
          <label>任务总数:</label>
          <span>{{ exportStore.taskStats.total }}</span>
        </div>
        <div class="info-item">
          <label>进行中:</label>
          <span>{{ exportStore.taskStats.running }}</span>
        </div>
        <div class="info-item">
          <label>已完成:</label>
          <span>{{ exportStore.taskStats.completed }}</span>
        </div>
        <div class="info-item">
          <label>失败:</label>
          <span>{{ exportStore.taskStats.failed }}</span>
        </div>
      </div>
      
      <div class="actions">
        <el-button @click="startTestExport" :loading="exportStore.isExporting">
          开始测试导出
        </el-button>
        <el-button @click="exportStore.loadTemplates()">
          加载模板
        </el-button>
        <el-button @click="exportStore.clearCompletedTasks()">
          清理已完成任务
        </el-button>
      </div>
    </div>

    <!-- 通知列表 -->
    <div class="section" v-if="appStore.notifications.length > 0">
      <h3>通知列表</h3>
      <div class="notifications">
        <div 
          v-for="notification in appStore.notifications.slice(0, 5)" 
          :key="notification.id"
          class="notification-item"
          :class="notification.type"
        >
          <div class="notification-content">
            <h4>{{ notification.title }}</h4>
            <p>{{ notification.message }}</p>
            <small>{{ formatTime(notification.timestamp) }}</small>
          </div>
          <div class="notification-actions">
            <el-button 
              size="small" 
              @click="appStore.markNotificationAsRead(notification.id)"
              v-if="!notification.read"
            >
              标记已读
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="appStore.removeNotification(notification.id)"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'
import { useEnergyStore } from '@/stores/energy'
import { useDeviceStore } from '@/stores/device'
import { useExportStore } from '@/stores/export'

const appStore = useAppStore()
const energyStore = useEnergyStore()
const deviceStore = useDeviceStore()
const exportStore = useExportStore()

const connectionStatusClass = computed(() => ({
  'status-connected': appStore.connectionStatus === 'connected',
  'status-disconnected': appStore.connectionStatus === 'disconnected',
  'status-reconnecting': appStore.connectionStatus === 'reconnecting'
}))

const formatTime = (date: Date | null) => {
  if (!date) return '无'
  return date.toLocaleString('zh-CN')
}

const handleLogin = async () => {
  if (appStore.isAuthenticated) {
    await appStore.logout()
  } else {
    try {
      await appStore.login('admin', 'admin')
    } catch (error) {
      console.error('登录失败:', error)
    }
  }
}

const addTestNotification = () => {
  const types = ['info', 'success', 'warning', 'error'] as const
  const type = types[Math.floor(Math.random() * types.length)]
  
  appStore.addNotification({
    type,
    title: `测试通知 - ${type}`,
    message: `这是一个 ${type} 类型的测试通知，时间：${new Date().toLocaleTimeString()}`
  })
}

const selectRandomDevice = () => {
  const devices = deviceStore.flatDeviceList
  if (devices.length > 0) {
    const randomDevice = devices[Math.floor(Math.random() * devices.length)]
    deviceStore.setSelectedDevice(randomDevice)
  }
}

const startTestExport = async () => {
  const config = {
    format: 'excel' as const,
    dateRange: {
      start: new Date(Date.now() - 24 * 60 * 60 * 1000),
      end: new Date()
    },
    includeHeaders: true,
    compression: false
  }
  
  try {
    await exportStore.startExport(config, '测试导出任务', 'energy')
  } catch (error) {
    console.error('导出失败:', error)
  }
}

// 初始化数据
appStore.initializeApp()
energyStore.fetchRealtimeData()
deviceStore.fetchDeviceTree()
exportStore.loadTemplates()
</script>

<style scoped>
.store-example {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fff;
}

.section h3 {
  margin: 0 0 15px 0;
  color: #333;
  border-bottom: 2px solid #409eff;
  padding-bottom: 5px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
  margin-bottom: 15px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: #f5f5f5;
  border-radius: 4px;
}

.info-item label {
  font-weight: 500;
  color: #666;
}

.info-item span {
  color: #333;
}

.status-connected {
  color: #67c23a;
  font-weight: 500;
}

.status-disconnected {
  color: #f56c6c;
  font-weight: 500;
}

.status-reconnecting {
  color: #e6a23c;
  font-weight: 500;
}

.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.notifications {
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 6px;
  border-left: 4px solid;
}

.notification-item.info {
  background: #f0f9ff;
  border-left-color: #409eff;
}

.notification-item.success {
  background: #f0f9f0;
  border-left-color: #67c23a;
}

.notification-item.warning {
  background: #fdf6ec;
  border-left-color: #e6a23c;
}

.notification-item.error {
  background: #fef0f0;
  border-left-color: #f56c6c;
}

.notification-content h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 500;
}

.notification-content p {
  margin: 0 0 4px 0;
  font-size: 13px;
  color: #666;
}

.notification-content small {
  font-size: 12px;
  color: #999;
}

.notification-actions {
  display: flex;
  gap: 5px;
  flex-shrink: 0;
}
</style>