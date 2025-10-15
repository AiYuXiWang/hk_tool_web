import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface DeviceNode {
  id: string
  name: string
  type: 'building' | 'floor' | 'room' | 'device'
  parentId?: string
  children?: DeviceNode[]
  status?: 'online' | 'offline' | 'error' | 'maintenance'
  properties?: Record<string, any>
  location?: {
    building?: string
    floor?: string
    room?: string
  }
}

export interface DeviceStatus {
  id: string
  name: string
  status: 'online' | 'offline' | 'error' | 'maintenance'
  lastSeen: Date
  temperature?: number
  humidity?: number
  power?: number
  alerts?: string[]
}

export interface DeviceConfig {
  id: string
  name: string
  type: string
  settings: Record<string, any>
  thresholds: {
    temperature?: { min: number; max: number }
    humidity?: { min: number; max: number }
    power?: { max: number }
  }
}

export const useDeviceStore = defineStore('device', () => {
  // 状态定义
  const deviceTree = ref<DeviceNode[]>([])
  const deviceStatuses = ref<DeviceStatus[]>([])
  const deviceConfigs = ref<DeviceConfig[]>([])
  const selectedDeviceId = ref<string>('')
  const expandedNodes = ref<string[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const lastUpdateTime = ref<Date | null>(null)

  // 计算属性
  const selectedDevice = computed(() => {
    const findDevice = (nodes: DeviceNode[]): DeviceNode | undefined => {
      for (const node of nodes) {
        if (node.id === selectedDeviceId.value) return node
        if (node.children) {
          const found = findDevice(node.children)
          if (found) return found
        }
      }
      return undefined
    }
    return findDevice(deviceTree.value)
  })

  const selectedDeviceStatus = computed(() => 
    deviceStatuses.value.find(status => status.id === selectedDeviceId.value)
  )

  const selectedDeviceConfig = computed(() => 
    deviceConfigs.value.find(config => config.id === selectedDeviceId.value)
  )

  const onlineDevices = computed(() => 
    deviceStatuses.value.filter(device => device.status === 'online')
  )

  const offlineDevices = computed(() => 
    deviceStatuses.value.filter(device => device.status === 'offline')
  )

  const errorDevices = computed(() => 
    deviceStatuses.value.filter(device => device.status === 'error')
  )

  const deviceCount = computed(() => ({
    total: deviceStatuses.value.length,
    online: onlineDevices.value.length,
    offline: offlineDevices.value.length,
    error: errorDevices.value.length,
    maintenance: deviceStatuses.value.filter(d => d.status === 'maintenance').length
  }))

  const devicesWithAlerts = computed(() => 
    deviceStatuses.value.filter(device => device.alerts && device.alerts.length > 0)
  )

  const flatDeviceList = computed(() => {
    const flatten = (nodes: DeviceNode[]): DeviceNode[] => {
      const result: DeviceNode[] = []
      for (const node of nodes) {
        if (node.type === 'device') {
          result.push(node)
        }
        if (node.children) {
          result.push(...flatten(node.children))
        }
      }
      return result
    }
    return flatten(deviceTree.value)
  })

  // Actions
  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }

  const setError = (errorMessage: string | null) => {
    error.value = errorMessage
  }

  const setSelectedDevice = (deviceId: string) => {
    selectedDeviceId.value = deviceId
  }

  const toggleNodeExpansion = (nodeId: string) => {
    const index = expandedNodes.value.indexOf(nodeId)
    if (index > -1) {
      expandedNodes.value.splice(index, 1)
    } else {
      expandedNodes.value.push(nodeId)
    }
  }

  const expandNode = (nodeId: string) => {
    if (!expandedNodes.value.includes(nodeId)) {
      expandedNodes.value.push(nodeId)
    }
  }

  const collapseNode = (nodeId: string) => {
    const index = expandedNodes.value.indexOf(nodeId)
    if (index > -1) {
      expandedNodes.value.splice(index, 1)
    }
  }

  const expandAll = () => {
    const getAllNodeIds = (nodes: DeviceNode[]): string[] => {
      const ids: string[] = []
      for (const node of nodes) {
        ids.push(node.id)
        if (node.children) {
          ids.push(...getAllNodeIds(node.children))
        }
      }
      return ids
    }
    expandedNodes.value = getAllNodeIds(deviceTree.value)
  }

  const collapseAll = () => {
    expandedNodes.value = []
  }

  const updateDeviceTree = (tree: DeviceNode[]) => {
    deviceTree.value = tree
    lastUpdateTime.value = new Date()
    error.value = null
  }

  const updateDeviceStatuses = (statuses: DeviceStatus[]) => {
    deviceStatuses.value = statuses
    lastUpdateTime.value = new Date()
  }

  const updateDeviceStatus = (deviceId: string, status: DeviceStatus['status']) => {
    const device = deviceStatuses.value.find(d => d.id === deviceId)
    if (device) {
      device.status = status
      device.lastSeen = new Date()
    }
  }

  const updateDeviceConfig = (config: DeviceConfig) => {
    const index = deviceConfigs.value.findIndex(c => c.id === config.id)
    if (index > -1) {
      deviceConfigs.value[index] = config
    } else {
      deviceConfigs.value.push(config)
    }
  }

  const addDeviceAlert = (deviceId: string, alert: string) => {
    const device = deviceStatuses.value.find(d => d.id === deviceId)
    if (device) {
      if (!device.alerts) device.alerts = []
      device.alerts.push(alert)
    }
  }

  const clearDeviceAlerts = (deviceId: string) => {
    const device = deviceStatuses.value.find(d => d.id === deviceId)
    if (device) {
      device.alerts = []
    }
  }

  // 模拟API调用
  const fetchDeviceTree = async () => {
    setLoading(true)
    setError(null)
    
    try {
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // 模拟设备树数据
      const mockTree: DeviceNode[] = [
        {
          id: 'building-1',
          name: '主楼',
          type: 'building',
          children: [
            {
              id: 'floor-1-1',
              name: '1楼',
              type: 'floor',
              parentId: 'building-1',
              children: [
                {
                  id: 'room-1-1-1',
                  name: '机房A',
                  type: 'room',
                  parentId: 'floor-1-1',
                  children: [
                    {
                      id: 'device-1',
                      name: '空调-01',
                      type: 'device',
                      parentId: 'room-1-1-1',
                      status: 'online',
                      properties: { type: 'HVAC', model: 'AC-2000' }
                    },
                    {
                      id: 'device-2',
                      name: '温度传感器-01',
                      type: 'device',
                      parentId: 'room-1-1-1',
                      status: 'online',
                      properties: { type: 'Sensor', model: 'TEMP-100' }
                    }
                  ]
                },
                {
                  id: 'room-1-1-2',
                  name: '办公室A',
                  type: 'room',
                  parentId: 'floor-1-1',
                  children: [
                    {
                      id: 'device-3',
                      name: '照明-01',
                      type: 'device',
                      parentId: 'room-1-1-2',
                      status: 'offline',
                      properties: { type: 'Lighting', model: 'LED-500' }
                    }
                  ]
                }
              ]
            },
            {
              id: 'floor-1-2',
              name: '2楼',
              type: 'floor',
              parentId: 'building-1',
              children: [
                {
                  id: 'room-1-2-1',
                  name: '会议室B',
                  type: 'room',
                  parentId: 'floor-1-2',
                  children: [
                    {
                      id: 'device-4',
                      name: '投影仪-01',
                      type: 'device',
                      parentId: 'room-1-2-1',
                      status: 'error',
                      properties: { type: 'AV', model: 'PROJ-300' }
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
      
      updateDeviceTree(mockTree)
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取设备树失败')
    } finally {
      setLoading(false)
    }
  }

  const fetchDeviceStatuses = async () => {
    try {
      await new Promise(resolve => setTimeout(resolve, 300))
      
      // 模拟设备状态数据
      const mockStatuses: DeviceStatus[] = [
        {
          id: 'device-1',
          name: '空调-01',
          status: 'online',
          lastSeen: new Date(),
          temperature: 22.5,
          humidity: 45,
          power: 150.5,
          alerts: []
        },
        {
          id: 'device-2',
          name: '温度传感器-01',
          status: 'online',
          lastSeen: new Date(),
          temperature: 23.1,
          humidity: 48,
          alerts: []
        },
        {
          id: 'device-3',
          name: '照明-01',
          status: 'offline',
          lastSeen: new Date(Date.now() - 300000),
          alerts: ['设备离线超过5分钟']
        },
        {
          id: 'device-4',
          name: '投影仪-01',
          status: 'error',
          lastSeen: new Date(),
          alerts: ['温度过高', '风扇故障']
        }
      ]
      
      updateDeviceStatuses(mockStatuses)
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取设备状态失败')
    }
  }

  const fetchDeviceConfigs = async () => {
    try {
      await new Promise(resolve => setTimeout(resolve, 200))
      
      // 模拟设备配置数据
      const mockConfigs: DeviceConfig[] = [
        {
          id: 'device-1',
          name: '空调-01',
          type: 'HVAC',
          settings: {
            targetTemperature: 22,
            mode: 'auto',
            fanSpeed: 'medium'
          },
          thresholds: {
            temperature: { min: 18, max: 28 },
            power: { max: 200 }
          }
        }
      ]
      
      deviceConfigs.value = mockConfigs
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取设备配置失败')
    }
  }

  const refreshAllData = async () => {
    await Promise.all([
      fetchDeviceTree(),
      fetchDeviceStatuses(),
      fetchDeviceConfigs()
    ])
  }

  const clearData = () => {
    deviceTree.value = []
    deviceStatuses.value = []
    deviceConfigs.value = []
    selectedDeviceId.value = ''
    expandedNodes.value = []
    error.value = null
    lastUpdateTime.value = null
  }

  return {
    // 状态
    deviceTree,
    deviceStatuses,
    deviceConfigs,
    selectedDeviceId,
    expandedNodes,
    isLoading,
    error,
    lastUpdateTime,
    
    // 计算属性
    selectedDevice,
    selectedDeviceStatus,
    selectedDeviceConfig,
    onlineDevices,
    offlineDevices,
    errorDevices,
    deviceCount,
    devicesWithAlerts,
    flatDeviceList,
    
    // Actions
    setLoading,
    setError,
    setSelectedDevice,
    toggleNodeExpansion,
    expandNode,
    collapseNode,
    expandAll,
    collapseAll,
    updateDeviceTree,
    updateDeviceStatuses,
    updateDeviceStatus,
    updateDeviceConfig,
    addDeviceAlert,
    clearDeviceAlerts,
    fetchDeviceTree,
    fetchDeviceStatuses,
    fetchDeviceConfigs,
    refreshAllData,
    clearData
  }
})