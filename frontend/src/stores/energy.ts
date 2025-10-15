import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ChartData } from '@/components/business/types'

export interface EnergyData {
  timestamp: string
  value: number
  unit: string
  deviceId: string
  deviceName: string
}

export interface EnergyKpi {
  totalConsumption: number
  currentPower: number
  efficiency: number
  cost: number
  trend: 'up' | 'down' | 'stable'
}

export interface EnergyDevice {
  id: string
  name: string
  type: string
  status: 'online' | 'offline' | 'error'
  currentPower: number
  totalConsumption: number
  efficiency: number
}

export const useEnergyStore = defineStore('energy', () => {
  // 状态定义
  const realtimeData = ref<ChartData[]>([])
  const historyData = ref<ChartData[]>([])
  const kpiData = ref<EnergyKpi>({
    totalConsumption: 0,
    currentPower: 0,
    efficiency: 0,
    cost: 0,
    trend: 'stable'
  })
  const devices = ref<EnergyDevice[]>([])
  const selectedDeviceId = ref<string>('')
  const timeRange = ref<string>('1h')
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const lastUpdateTime = ref<Date | null>(null)

  // 计算属性
  const selectedDevice = computed(() => 
    devices.value.find(device => device.id === selectedDeviceId.value)
  )

  const onlineDevicesCount = computed(() => 
    devices.value.filter(device => device.status === 'online').length
  )

  const totalPower = computed(() => 
    devices.value.reduce((sum, device) => sum + device.currentPower, 0)
  )

  const hasData = computed(() => 
    realtimeData.value.length > 0 || historyData.value.length > 0
  )

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

  const setTimeRange = (range: string) => {
    timeRange.value = range
  }

  const updateRealtimeData = (data: ChartData[]) => {
    realtimeData.value = data
    lastUpdateTime.value = new Date()
    error.value = null
  }

  const updateHistoryData = (data: ChartData[]) => {
    historyData.value = data
    error.value = null
  }

  const updateKpiData = (kpi: EnergyKpi) => {
    kpiData.value = kpi
  }

  const updateDevices = (deviceList: EnergyDevice[]) => {
    devices.value = deviceList
  }

  const updateDeviceStatus = (deviceId: string, status: EnergyDevice['status']) => {
    const device = devices.value.find(d => d.id === deviceId)
    if (device) {
      device.status = status
    }
  }

  // 模拟API调用
  const fetchRealtimeData = async (deviceId?: string) => {
    setLoading(true)
    setError(null)
    
    try {
      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // 模拟实时数据
      const now = new Date()
      const timestamps = Array.from({ length: 20 }, (_, i) => {
        const time = new Date(now.getTime() - (19 - i) * 60000)
        return time.toLocaleTimeString()
      })
      
      const mockData: ChartData[] = [{
        type: 'line',
        title: '实时功率',
        data: timestamps,
        xAxis: {
          type: 'category',
          data: timestamps
        },
        yAxis: {
          type: 'value',
          name: '功率 (kW)'
        },
        series: [{
          name: '当前功率',
          type: 'line',
          data: Array.from({ length: 20 }, () => Math.random() * 100 + 50),
          smooth: true,
          color: '#409EFF'
        }]
      }]
      
      updateRealtimeData(mockData)
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取实时数据失败')
    } finally {
      setLoading(false)
    }
  }

  const fetchHistoryData = async (deviceId?: string, range?: string) => {
    setLoading(true)
    setError(null)
    
    try {
      await new Promise(resolve => setTimeout(resolve, 800))
      
      // 模拟历史数据
      const dataPoints = range === '1d' ? 24 : range === '7d' ? 168 : 30
      const timestamps = Array.from({ length: dataPoints }, (_, i) => {
        const time = new Date(Date.now() - (dataPoints - 1 - i) * 3600000)
        return time.toLocaleDateString()
      })
      
      const mockData: ChartData[] = [{
        type: 'line',
        title: '历史趋势',
        data: timestamps,
        xAxis: {
          type: 'category',
          data: timestamps
        },
        yAxis: {
          type: 'value',
          name: '能耗 (kWh)'
        },
        series: [{
          name: '能耗',
          type: 'line',
          data: Array.from({ length: dataPoints }, () => Math.random() * 200 + 100),
          color: '#67C23A'
        }]
      }]
      
      updateHistoryData(mockData)
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取历史数据失败')
    } finally {
      setLoading(false)
    }
  }

  const fetchKpiData = async () => {
    try {
      // 模拟KPI数据
      const mockKpi: EnergyKpi = {
        totalConsumption: Math.random() * 10000 + 5000,
        currentPower: Math.random() * 500 + 200,
        efficiency: Math.random() * 30 + 70,
        cost: Math.random() * 5000 + 2000,
        trend: ['up', 'down', 'stable'][Math.floor(Math.random() * 3)] as EnergyKpi['trend']
      }
      
      updateKpiData(mockKpi)
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取KPI数据失败')
    }
  }

  const fetchDevices = async () => {
    try {
      // 模拟设备数据
      const mockDevices: EnergyDevice[] = [
        {
          id: 'device-1',
          name: '空调系统',
          type: 'HVAC',
          status: 'online',
          currentPower: 150.5,
          totalConsumption: 2450.8,
          efficiency: 85.2
        },
        {
          id: 'device-2',
          name: '照明系统',
          type: 'Lighting',
          status: 'online',
          currentPower: 45.2,
          totalConsumption: 890.3,
          efficiency: 92.1
        },
        {
          id: 'device-3',
          name: '电梯系统',
          type: 'Elevator',
          status: 'offline',
          currentPower: 0,
          totalConsumption: 1250.6,
          efficiency: 78.9
        }
      ]
      
      updateDevices(mockDevices)
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取设备数据失败')
    }
  }

  const refreshAllData = async () => {
    await Promise.all([
      fetchRealtimeData(selectedDeviceId.value),
      fetchHistoryData(selectedDeviceId.value, timeRange.value),
      fetchKpiData(),
      fetchDevices()
    ])
  }

  const clearData = () => {
    realtimeData.value = []
    historyData.value = []
    kpiData.value = {
      totalConsumption: 0,
      currentPower: 0,
      efficiency: 0,
      cost: 0,
      trend: 'stable'
    }
    devices.value = []
    selectedDeviceId.value = ''
    error.value = null
    lastUpdateTime.value = null
  }

  return {
    // 状态
    realtimeData,
    historyData,
    kpiData,
    devices,
    selectedDeviceId,
    timeRange,
    isLoading,
    error,
    lastUpdateTime,
    
    // 计算属性
    selectedDevice,
    onlineDevicesCount,
    totalPower,
    hasData,
    
    // Actions
    setLoading,
    setError,
    setSelectedDevice,
    setTimeRange,
    updateRealtimeData,
    updateHistoryData,
    updateKpiData,
    updateDevices,
    updateDeviceStatus,
    fetchRealtimeData,
    fetchHistoryData,
    fetchKpiData,
    fetchDevices,
    refreshAllData,
    clearData
  }
})