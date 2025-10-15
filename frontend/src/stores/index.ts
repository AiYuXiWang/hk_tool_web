import { createPinia } from 'pinia'

// 创建Pinia实例
export const pinia = createPinia()

// 导出所有stores
export { useEnergyStore } from './energy'
export { useDeviceStore } from './device'
export { useExportStore } from './export'
export { useAppStore } from './app'

export default pinia