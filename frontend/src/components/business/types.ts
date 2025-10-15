// 能源KPI数据类型
export interface KpiData {
  title: string
  subtitle?: string
  value: number | string
  unit?: string
  icon?: string
  trend?: 'up' | 'down' | 'stable'
  trendValue?: number
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  size?: 'small' | 'medium' | 'large'
  loading?: boolean
  formatter?: (value: number | string) => string
}

// 图表数据类型
export interface ChartData {
  type: 'line' | 'bar' | 'pie' | 'area' | 'scatter'
  title?: string
  data: any[]
  xAxis?: string[]
  yAxis?: any
  series?: any[]
  options?: any
}

// 优化建议类型
export interface OptimizationSuggestion {
  id: string
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  category: string
  estimatedSaving: number
  savingUnit: string
  difficulty: 'easy' | 'medium' | 'hard'
  roi: number
  implementationTime: string
  status: 'pending' | 'implementing' | 'completed' | 'rejected'
  detailDescription?: string
  implementationSteps?: string[]
  expectedResults?: string[]
  riskAssessment?: string[]
  createdAt: Date
  updatedAt?: Date
}

// 设备信息类型
export interface DeviceInfo {
  id: string
  name: string
  type: string
  location: string
  status: DeviceStatus
  power: number
  energyConsumption: number
  efficiency: number
  temperature: number
  alerts: DeviceAlert[]
  lastMaintenance?: Date
  nextMaintenance?: Date
  installDate: Date
  manufacturer?: string
  model?: string
  serialNumber?: string
}

// 设备状态类型
export type DeviceStatus = 'online' | 'offline' | 'warning' | 'error' | 'maintenance'

// 设备告警类型
export interface DeviceAlert {
  id: string
  type: 'warning' | 'error' | 'info'
  message: string
  timestamp: Date
  acknowledged: boolean
  severity: 'low' | 'medium' | 'high' | 'critical'
}

// 维护记录类型
export interface MaintenanceRecord {
  id: string
  date: Date
  type: 'routine' | 'repair' | 'upgrade' | 'inspection'
  description: string
  technician: string
  duration: number
  cost?: number
  parts?: string[]
  notes?: string
}

// 历史记录类型
export interface HistoryRecord {
  timestamp: Date
  power: number
  energyConsumption: number
  efficiency: number
  temperature: number
  status: DeviceStatus
}

// 导出参数类型
export interface ExportParams {
  lineId: string
  startTime: string
  endTime: string
  format?: 'csv' | 'excel' | 'json'
  compress?: boolean
  includeHeaders?: boolean
  dateFormat?: string
  encoding?: string
}

// 导出日志类型
export interface ExportLog {
  id?: string
  timestamp: number | Date
  level: 'info' | 'success' | 'warning' | 'error'
  message: string
  category?: string
  details?: any
  actions?: LogAction[]
  showDetails?: boolean
  highlight?: boolean
}

// 日志操作类型
export interface LogAction {
  key: string
  label: string
  icon?: string
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'outline'
  disabled?: boolean
}

// 线路配置类型
export interface LineConfig {
  id: number
  name: string
  stations: number
  length?: number
  status?: 'active' | 'inactive' | 'maintenance'
  description?: string
}

// 表单字段类型
export interface FormField {
  key: string
  label: string
  type: 'input' | 'select' | 'date' | 'datetime' | 'time' | 'number' | 'textarea' | 'switch' | 'checkbox' | 'radio'
  placeholder?: string
  required?: boolean
  options?: Array<{ label: string; value: any }>
  rules?: ValidationRule[]
  props?: any
}

// 验证规则类型
export interface ValidationRule {
  required?: boolean
  min?: number
  max?: number
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  validator?: (value: any) => boolean | string
  message?: string
}

// 数据预览类型
export interface DataPreview {
  headers: string[]
  rows: any[][]
  totalCount: number
  previewCount: number
}

// 导出进度类型
export interface ExportProgress {
  percentage: number
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
  message?: string
  startTime?: Date
  endTime?: Date
  estimatedTime?: number
}

// 导出统计类型
export interface ExportStats {
  totalExports: number
  successfulExports: number
  failedExports: number
  totalDataSize: number
  averageExportTime: number
  lastExportTime?: Date
}