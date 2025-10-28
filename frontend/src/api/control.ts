import axios, { AxiosInstance } from 'axios'

const OPERATOR_ID = 'web-admin' // 可按登录态动态赋值

export const http: AxiosInstance = axios.create({
  baseURL: import.meta.env.DEV ? '' : 'http://localhost:8000', // 开发环境使用代理，生产环境直接指向后端
  timeout: 60000, // 60秒超时，适应多站点导出（M2线路6个站点，每站点15秒）
  headers: {
    'X-Operator-Id': OPERATOR_ID,
  },
})

// 统一解包后端标准响应 { code, message, data, ... }
function unwrap<T = any>(resp: any): T {
  try {
    if (resp && typeof resp === 'object') {
      if ('data' in resp && ('code' in resp || 'message' in resp)) {
        return resp.data as T
      }
      // 某些接口可能直接返回目标对象
      return resp as T
    }
    return resp as T
  } catch {
    return resp as T
  }
}

// 动态设置站点头，便于在站点切换时统一生效
export function setStationIp(ip: string) {
  const v = (ip || '').trim()
  if (v) {
    http.defaults.headers['X-Station-Ip'] = v
  } else {
    // 清理无效值，避免误用默认
    delete (http.defaults.headers as any)['X-Station-Ip']
  }
}

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
  // 后端返回的点位数据源，范围为 1 | 2 | 3
  data_source?: 1 | 2 | 3
}

export async function fetchDefaultPoints(objectCodes: string[]): Promise<{
  items: DefaultPointItem[]
  count: number
}> {
  const params = { object_codes: objectCodes.join(',') }
  const { data } = await http.get('/control/points/default', { params })
  // 统一解包，适配后端标准响应或直接对象
  return unwrap(data)
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
} | Array<{
  object_code: string
  data_code: string
  value: number | string | boolean | null
  unit: string | null
  ts: string
  raw: any
}>> {
  const params = { object_code: objectCode, data_code: dataCode }
  const { data } = await http.get('/control/points/real-time', { params })
  // 后端可能返回多种形态，进行健壮解包与规范化
  let obj: any
  try {
    obj = unwrap(data)
  } catch {
    obj = data
  }
  if (obj && typeof obj === 'object' && 'result' in obj && obj.result) {
    obj = obj.result
  }
  const normalizeRow = (r: any) => {
    if (!r || typeof r !== 'object') return r
    const value = ('value' in r) ? r.value : (('current_value' in r) ? r.current_value : (('val' in r) ? r.val : null))
    const unit = (r.unit != null) ? r.unit : (r.meta?.unit ?? null)
    const object_code = r.object_code ?? r.objectCode ?? r.object ?? r.meta?.object_code ?? ''
    const data_code = r.data_code ?? r.dataCode ?? r.data ?? r.meta?.data_code ?? ''
    const ts = r.ts ?? r.timestamp ?? r.time ?? ''
    return { object_code, data_code, value, unit, ts, raw: r }
  }
  if (Array.isArray(obj)) return obj.map(normalizeRow)
  return normalizeRow(obj)
}

export async function batchWritePoints(commands: Array<{
  point_key: string
  data_source: 1 | 2 | 3
  control_value: number | string | boolean
  object_code?: string
  data_code?: string
}>, stationIp?: string, options?: { timeoutMs?: number }): Promise<{
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
  // 默认请求头：跳过写前读取，加路由层超时（3~60s）
  const routeTimeoutMs = Math.min(Math.max(options?.timeoutMs ?? 10000, 3000), 60000)
  const headers: Record<string, string> = {
    'X-Timeout-Ms': String(routeTimeoutMs),
    'X-Skip-Before': '1',
    ...(stationIp ? { 'X-Station-Ip': stationIp } : {}),
  }
  // Axios 自身的请求超时，留出一定余量
  const timeout = options?.timeoutMs ?? 12000
  const { data } = await http.post('/control/points/write', commands, { headers, timeout })
  // 统一解包，确保返回的是 { total, success, failed, items }
  return unwrap(data)
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
  task_id?: string
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

// 任务状态类型
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

export type TaskProgress = {
  task_id: string
  status: TaskStatus
  progress: number
  current_step: string
  total_steps: number
  completed_steps: number
  start_time: string
  end_time?: string
  result?: any
  error?: string
}

export async function exportElectricityData(request: ExportRequest): Promise<ExportResult> {
  const { data } = await http.post('/api/export/electricity', request)
  return unwrap<ExportResult>(data)
}

export async function exportSensorData(request: ExportRequest): Promise<ExportResult> {
  const { data } = await http.post('/api/export/sensor', request)
  return unwrap<ExportResult>(data)
}

// 获取任务状态
export async function getTaskStatus(taskId: string): Promise<TaskProgress> {
  const { data } = await http.get(`/api/tasks/${taskId}`)
  const raw = unwrap<any>(data)
  // 规范化进度对象到UI期望字段
  const p = raw?.progress
  const normalized: TaskProgress = {
    task_id: String(raw?.task_id || taskId),
    status: (raw?.status || 'pending') as TaskStatus,
    progress: typeof p === 'number' ? p : (typeof p?.percentage === 'number' ? p.percentage : 0),
    current_step: typeof p === 'object' && p ? (p.message || '') : (raw?.current_step || ''),
    total_steps: typeof p === 'object' && p ? (p.total ?? (raw?.total_steps ?? 0)) : (raw?.total_steps ?? 0),
    completed_steps: typeof p === 'object' && p ? (p.current ?? (raw?.completed_steps ?? 0)) : (raw?.completed_steps ?? 0),
    start_time: raw?.created_at || raw?.start_time || new Date().toISOString(),
    end_time: raw?.updated_at || raw?.end_time,
    result: raw?.result,
    error: raw?.error,
  }
  return normalized
}

// 获取所有任务列表
export async function getAllTasks(): Promise<TaskProgress[]> {
  const { data } = await http.get('/api/tasks')
  const arr = unwrap<any[]>(data) || []
  return arr.map((raw: any) => {
    const p = raw?.progress
    const tp: TaskProgress = {
      task_id: String(raw?.task_id || ''),
      status: (raw?.status || 'pending') as TaskStatus,
      progress: typeof p === 'number' ? p : (typeof p?.percentage === 'number' ? p.percentage : 0),
      current_step: typeof p === 'object' && p ? (p.message || '') : (raw?.current_step || ''),
      total_steps: typeof p === 'object' && p ? (p.total ?? (raw?.total_steps ?? 0)) : (raw?.total_steps ?? 0),
      completed_steps: typeof p === 'object' && p ? (p.current ?? (raw?.completed_steps ?? 0)) : (raw?.completed_steps ?? 0),
      start_time: raw?.created_at || raw?.start_time || new Date().toISOString(),
      end_time: raw?.updated_at || raw?.end_time,
      result: raw?.result,
      error: raw?.error,
    }
    return tp
  })
}

// 取消任务
export async function cancelTask(taskId: string): Promise<{ success: boolean; message: string }> {
  const { data } = await http.delete(`/api/tasks/${taskId}`)
  return unwrap<{ success: boolean; message: string }>(data)
}

export type LineConfigs = {
  [line: string]: Array<{ station_name: string; station_ip: string }>
}

/** 线路-车站配置获取 */
export async function fetchLineConfigs(): Promise<LineConfigs> {
  const { data } = await http.get('/api/config/line_configs')
  return unwrap<LineConfigs>(data)
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