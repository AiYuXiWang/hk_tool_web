import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ChartData } from '@/components/business/types'
import { DataCache, calculateStatistics, normalizeHistoryData, type HistoryStatistics } from '@/services/dataProcessor'

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

export interface CachedHistoryData {
  data: any
  statistics: HistoryStatistics
  timestamp: number
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
  
  // 历史数据缓存（按时间范围分组）
  const historyDataByRange = ref<Record<string, any>>({
    '24h': null,
    '7d': null,
    '30d': null,
    '90d': null
  })
  const historyStatistics = ref<HistoryStatistics>({
    total: 0,
    average: 0,
    peak: 0,
    min: 0,
    dataQuality: 100
  })
  const isLoadingHistory = ref(false)
  
  // 创建数据缓存实例（30分钟TTL）
  const historyCache = new DataCache<CachedHistoryData>(30 * 60 * 1000)

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
  
  // 获取历史数据（带缓存）
  const fetchHistoryWithCache = async (
    stationId: string, 
    timeRange: string,
    line?: string,
    fetchFn?: (params: any) => Promise<any>
  ) => {
    const cacheKey = `${stationId}_${timeRange}_${line || 'default'}`
    
    // 检查缓存
    const cached = historyCache.get(cacheKey)
    if (cached) {
      console.log(`[Cache Hit] 使用缓存数据: ${cacheKey}`)
      historyDataByRange.value[timeRange] = cached.data
      historyStatistics.value = cached.statistics
      return cached.data
    }
    
    // 缓存未命中，加载新数据
    console.log(`[Cache Miss] 从API加载数据: ${cacheKey}`)
    isLoadingHistory.value = true
    setError(null)
    
    try {
      // 调用提供的fetch函数或默认函数
      const rawData = fetchFn 
        ? await fetchFn({ line, station_ip: stationId, period: timeRange })
        : await fetchHistoryData(stationId, timeRange)
      
      // 规范化数据并计算统计
      const normalized = normalizeHistoryData(rawData)
      const stats = normalized.statistics || calculateStatistics(normalized.values || [])
      
      // 更新状态
      historyDataByRange.value[timeRange] = normalized
      historyStatistics.value = stats
      
      // 缓存数据
      historyCache.set(cacheKey, {
        data: normalized,
        statistics: stats,
        timestamp: Date.now()
      })
      
      return normalized
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取历史数据失败')
      throw err
    } finally {
      isLoadingHistory.value = false
    }
  }
  
  // 清除历史数据缓存
  const clearHistoryCache = (timeRange?: string) => {
    if (timeRange) {
      // 清除指定时间范围的缓存
      historyDataByRange.value[timeRange] = null
      // 清除相关的cache key
      // 注意：这里需要遍历所有可能的station_id，实际使用时可以优化
      historyCache.clear() // 简化处理，清除所有
    } else {
      // 清除所有历史数据缓存
      historyDataByRange.value = {
        '24h': null,
        '7d': null,
        '30d': null,
        '90d': null
      }
      historyCache.clear()
    }
  }
  
  // 更新历史统计数据
  const updateHistoryStatistics = (stats: HistoryStatistics) => {
    historyStatistics.value = stats
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
    
    // 历史数据缓存相关
    historyDataByRange,
    historyStatistics,
    isLoadingHistory,
    
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
    clearData,
    
    // 历史数据缓存相关方法
    fetchHistoryWithCache,
    clearHistoryCache,
    updateHistoryStatistics
  }
})