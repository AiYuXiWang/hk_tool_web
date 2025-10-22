/**
 * Data Processor Service
 * 
 * 处理能源数据的工具函数集合，包括：
 * - 数据聚合与统计
 * - 数据格式化与验证
 * - 数据降采样
 * - 缓存管理
 */

export interface HistoryStatistics {
  total: number      // 总能耗 kWh
  average: number    // 平均功率 kW
  peak: number       // 峰值功率 kW
  min: number        // 最小功率 kW
  dataQuality: number // 数据质量 0-100%
}

export interface EnergyData {
  timestamp: string | number
  value: number
  [key: string]: any
}

/**
 * 计算历史数据统计指标
 * @param dataPoints 数据点数组
 * @returns 统计结果
 */
export function calculateStatistics(dataPoints: number[]): HistoryStatistics {
  if (!dataPoints || dataPoints.length === 0) {
    return { 
      total: 0, 
      average: 0, 
      peak: 0, 
      min: 0, 
      dataQuality: 0 
    }
  }
  
  // 过滤有效数据点
  const validPoints = dataPoints.filter(p => 
    p !== null && 
    p !== undefined && 
    isFinite(p) && 
    !isNaN(p)
  )
  
  if (validPoints.length === 0) {
    return { 
      total: 0, 
      average: 0, 
      peak: 0, 
      min: 0, 
      dataQuality: 0 
    }
  }
  
  // 计算数据质量（有效数据点占比）
  const dataQuality = (validPoints.length / dataPoints.length) * 100
  
  // 计算统计指标
  const total = validPoints.reduce((sum, val) => sum + val, 0)
  const average = total / validPoints.length
  const peak = Math.max(...validPoints)
  const min = Math.min(...validPoints)
  
  return {
    total: Number(total.toFixed(2)),
    average: Number(average.toFixed(2)),
    peak: Number(peak.toFixed(2)),
    min: Number(min.toFixed(2)),
    dataQuality: Number(dataQuality.toFixed(1))
  }
}

/**
 * 数据降采样（大数据集优化）
 * @param data 原始数据数组
 * @param maxPoints 最大数据点数（默认300）
 * @returns 降采样后的数据
 */
export function downsampleData<T>(data: T[], maxPoints: number = 300): T[] {
  if (!data || data.length <= maxPoints) {
    return data
  }
  
  const step = Math.ceil(data.length / maxPoints)
  const result: T[] = []
  
  for (let i = 0; i < data.length; i += step) {
    result.push(data[i])
  }
  
  // 确保包含最后一个数据点
  if (result[result.length - 1] !== data[data.length - 1]) {
    result.push(data[data.length - 1])
  }
  
  return result
}

/**
 * 规范化历史数据（添加统计信息和降采样）
 * @param rawData 原始数据
 * @returns 规范化后的数据
 */
export function normalizeHistoryData(rawData: any): any {
  if (!rawData) {
    return {
      values: [],
      timestamps: [],
      statistics: calculateStatistics([])
    }
  }
  
  const values = rawData.values || []
  const timestamps = rawData.timestamps || []
  
  // 计算统计信息
  const statistics = calculateStatistics(values)
  
  // 降采样处理（超过500个点）
  const shouldDownsample = values.length > 500
  const processedValues = shouldDownsample ? downsampleData(values) : values
  const processedTimestamps = shouldDownsample ? downsampleData(timestamps) : timestamps
  
  return {
    ...rawData,
    values: processedValues,
    timestamps: processedTimestamps,
    statistics,
    isDownsampled: shouldDownsample,
    originalLength: values.length,
    processedLength: processedValues.length
  }
}

/**
 * 验证能源数据有效性
 * @param data 能源数据
 * @returns 是否有效
 */
export function validateEnergyData(data: any): boolean {
  if (!data) return false
  
  // 检查必要字段
  if (!data.values || !Array.isArray(data.values)) return false
  if (!data.timestamps || !Array.isArray(data.timestamps)) return false
  
  // 检查数组长度一致性
  if (data.values.length !== data.timestamps.length) return false
  
  // 检查至少有一个有效数据点
  const hasValidData = data.values.some((v: any) => 
    v !== null && v !== undefined && isFinite(v)
  )
  
  return hasValidData
}

/**
 * 格式化能源数据显示
 * @param value 数值
 * @param unit 单位
 * @param decimals 小数位数
 * @returns 格式化后的字符串
 */
export function formatEnergyValue(
  value: number, 
  unit: string = 'kWh', 
  decimals: number = 1
): string {
  if (!isFinite(value) || isNaN(value)) {
    return '-- ' + unit
  }
  
  // 大数值添加千分位
  if (value >= 1000) {
    return value.toLocaleString('zh-CN', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }) + ' ' + unit
  }
  
  return value.toFixed(decimals) + ' ' + unit
}

/**
 * 缓存管理类
 */
export class DataCache<T> {
  private cache: Map<string, { data: T; timestamp: number }>
  private ttl: number // 缓存过期时间（毫秒）
  
  constructor(ttl: number = 30 * 60 * 1000) { // 默认30分钟
    this.cache = new Map()
    this.ttl = ttl
  }
  
  /**
   * 设置缓存
   */
  set(key: string, data: T): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    })
  }
  
  /**
   * 获取缓存
   */
  get(key: string): T | null {
    const cached = this.cache.get(key)
    
    if (!cached) {
      return null
    }
    
    // 检查是否过期
    if (this.isCacheExpired(cached.timestamp)) {
      this.cache.delete(key)
      return null
    }
    
    return cached.data
  }
  
  /**
   * 检查缓存是否过期
   */
  isCacheExpired(timestamp: number): boolean {
    return Date.now() - timestamp > this.ttl
  }
  
  /**
   * 清除指定缓存
   */
  delete(key: string): void {
    this.cache.delete(key)
  }
  
  /**
   * 清除所有缓存
   */
  clear(): void {
    this.cache.clear()
  }
  
  /**
   * 获取缓存大小
   */
  size(): number {
    return this.cache.size
  }
  
  /**
   * 检查缓存是否存在
   */
  has(key: string): boolean {
    const cached = this.cache.get(key)
    if (!cached) return false
    
    if (this.isCacheExpired(cached.timestamp)) {
      this.cache.delete(key)
      return false
    }
    
    return true
  }
}

/**
 * 计算KPI指标
 * @param data 实时数据
 * @returns KPI对象
 */
export function calculateKPI(data: any): any {
  if (!data) {
    return {
      current_kw: 0,
      total_kwh_today: 0,
      peak_kw: 0,
      efficiency: 0
    }
  }
  
  return {
    current_kw: data.current_kw || 0,
    total_kwh_today: data.total_kwh_today || 0,
    peak_kw: data.peak_kw || 0,
    efficiency: data.efficiency || 0
  }
}

/**
 * 数据平滑处理（移动平均）
 * @param data 原始数据
 * @param windowSize 窗口大小
 * @returns 平滑后的数据
 */
export function smoothData(data: number[], windowSize: number = 3): number[] {
  if (!data || data.length < windowSize) {
    return data
  }
  
  const result: number[] = []
  
  for (let i = 0; i < data.length; i++) {
    const start = Math.max(0, i - Math.floor(windowSize / 2))
    const end = Math.min(data.length, i + Math.ceil(windowSize / 2))
    const window = data.slice(start, end)
    const validWindow = window.filter(v => v !== null && v !== undefined && isFinite(v))
    
    if (validWindow.length > 0) {
      const average = validWindow.reduce((sum, val) => sum + val, 0) / validWindow.length
      result.push(average)
    } else {
      result.push(data[i])
    }
  }
  
  return result
}

// 导出全局数据缓存实例
export const historyDataCache = new DataCache<any>(30 * 60 * 1000) // 30分钟
export const realtimeDataCache = new DataCache<any>(60 * 1000) // 1分钟
