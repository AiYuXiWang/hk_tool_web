import axios, { AxiosInstance } from 'axios'

const OPERATOR_ID = 'web-admin' // 可按登录态动态赋值

export const http: AxiosInstance = axios.create({
  baseURL: '',
  timeout: 8000,
  headers: {
    'X-Operator-Id': OPERATOR_ID,
  },
})

export type DefaultPointItem = {
  object_code: string
  data_code: string
  point_key: string
  data_type: string
  unit: string | null
  is_writable: boolean
  border_min: number | null
  border_max: number | null
  warn_min: number | null
  warn_max: number | null
  error_min: number | null
  error_max: number | null
}

export async function fetchDefaultPoints(objectCodes: string[]): Promise<{
  items: DefaultPointItem[]
  count: number
}> {
  const params = { object_codes: objectCodes.join(',') }
  const { data } = await http.get('/control/points/default', { params })
  return data
}

export async function fetchDeviceTree(opts?: { forceTest?: boolean; station_ip?: string }): Promise<{
  tree: DeviceTreeNode[]
  count: number
}> {
  function normalize(resp: any): { tree: DeviceTreeNode[]; count: number } {
    try {
      let obj = resp
      // 解包常见形态：{data:{tree,count}} / {result:{tree,count}}
      if (obj && typeof obj === 'object' && ('data' in obj) && obj.data && typeof obj.data === 'object') {
        obj = obj.data
      }
      if (obj && typeof obj === 'object' && ('result' in obj) && obj.result && typeof obj.result === 'object') {
        obj = obj.result
      }
      // 直接数组
      if (Array.isArray(obj)) {
        if (import.meta.env.DEV) console.debug('[dev] device-tree shape=array len=', obj.length)
        return { tree: obj as DeviceTreeNode[], count: obj.length }
      }
      // 标准对象
      const arr = Array.isArray(obj?.tree) ? (obj.tree as DeviceTreeNode[]) : []
      const cnt = typeof obj?.count === 'number' ? obj.count : arr.length
      if (import.meta.env.DEV) {
        const keys = obj && typeof obj === 'object' ? Object.keys(obj) : []
        console.debug('[dev] device-tree shape=obj keys=', keys, 'len=', arr.length, 'count=', cnt)
      }
      return { tree: arr, count: cnt }
    } catch {
      // 防御：异常时按空树处理
      if (import.meta.env.DEV) console.debug('[dev] device-tree normalize error, fallback empty')
      return { tree: [], count: 0 }
    }
  }

  // 强制测试树
  if (opts?.forceTest) {
    const { data: demo } = await http.get('/control/device-tree-test', { params: opts?.station_ip ? { station_ip: opts.station_ip } : undefined })
    return normalize(demo)
  }

  try {
    const { data } = await http.get('/control/device-tree', { params: opts?.station_ip ? { station_ip: opts.station_ip } : undefined })
    const norm = normalize(data)
    // 无条件：空结果则回退测试树（联调期保障可视化）
    if (norm.tree.length === 0) {
      const { data: demo } = await http.get('/control/device-tree-test', { params: opts?.station_ip ? { station_ip: opts.station_ip } : undefined })
      return normalize(demo)
    }
    return norm
  } catch {
    // 异常亦回退测试树
    const { data: demo } = await http.get('/control/device-tree-test', { params: opts?.station_ip ? { station_ip: opts.station_ip } : undefined })
    return normalize(demo)
  }
}

export type DeviceTreeNode = {
  id: string
  label: string
  children?: DeviceTreeNode[]
  meta: {
    object_code: string
    object_name?: string
    object_type?: string
    data_code?: string
    data_name?: string
    unit?: string
    is_writable?: boolean
    point_key?: string
    data_type?: string
    border_min?: number | null
    border_max?: number | null
    warn_min?: number | null
    warn_max?: number | null
    error_min?: number | null
    error_max?: number | null
    point_count?: number
    total_points?: number
  }
}

export async function fetchRealtimeValue(
  objectCode: string,
  dataCode: string
): Promise<{
  object_code: string
  data_code: string
  value: number | string | boolean | null
  unit: string | null
  ts: string
  raw: any
}> {
  const params = { object_code: objectCode, data_code: dataCode }
  const { data } = await http.get('/control/points/real-time', { params })
  return data
}

export async function batchWritePoints(commands: Array<{
  point_key: string
  data_source: 1 | 2 | 3
  control_value: number | string | boolean
  object_code?: string
  data_code?: string
}>): Promise<{
  total: number
  success: number
  failed: number
  items: Array<{
    point_key: string
    status: 'ok' | 'failed'
    message: string | null
    duration_ms: number
    before: any
    after: any
    retries: number
  }>
}> {
  const { data } = await http.post('/control/points/write', commands)
  return data
}

// UI 辅助
export function isBooleanType(dataType: string) {
  return dataType === '2'
}

export function normalizeSetValue(dataType: string, v: any) {
  if (isBooleanType(dataType)) {
    if (v === true || v === 'true' || v === 1 || v === '1') return 1
    return 0
  }
  const n = Number(v)
  return Number.isNaN(n) ? v : n
}

export function getSeverityColor(
  value: number | null,
  warnMin: number | null,
  warnMax: number | null,
  errMin: number | null,
  errMax: number | null
): 'ok' | 'warn' | 'error' {
  if (value == null) return 'ok'
  if ((errMin != null && value < errMin) || (errMax != null && value > errMax)) return 'error'
  if ((warnMin != null && value < warnMin) || (warnMax != null && value > warnMax)) return 'warn'
  return 'ok'
}

// 数据导出相关接口
export type ExportRequest = {
  line: string
  start_time: string
  end_time: string
}

export type ExportResult = {
  success: boolean
  message: string
  file_path?: string
  details?: {
    total_count: number
    success_count: number
    fail_count: number
    results: Array<{
      station_name: string
      station_ip: string
      success: boolean
      message: string
      file_path?: string
    }>
  }
}

export async function exportElectricityData(request: ExportRequest): Promise<ExportResult> {
  const { data } = await http.post('/api/export/electricity', request)
  return data
}

export async function exportSensorData(request: ExportRequest): Promise<ExportResult> {
  const { data } = await http.post('/api/export/sensor', request)
  return data
}

export type LineConfigs = {
  [line: string]: Array<{ station_name: string; station_ip: string }>
}

/** 线路-车站配置获取 */
export async function fetchLineConfigs(): Promise<LineConfigs> {
  const { data } = await http.get('/api/config/line_configs')
  return data
}
// 设备控制与批量写值 API 封装
export type DeviceTreeNode = {
  id: string
  label: string
  children?: DeviceTreeNode[]
  meta?: Record<string, any>
}

export type DeviceTreeResponse = {
  tree: DeviceTreeNode[]
  count: number
}