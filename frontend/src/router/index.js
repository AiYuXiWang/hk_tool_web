import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import EnergyPage from '@/views/EnergyPage.vue'
import EnergyDashboard from '@/views/EnergyDashboard.vue'
import DataExport from '@/views/DataExport.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: AppLayout,
    meta: { title: '设备总览' }
  },
  {
    path: '/energy',
    name: 'energy',
    component: EnergyPage,
    meta: { title: '能源驾驶舱' }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: EnergyDashboard,
    meta: { title: '能源管理驾驶舱' }
  },
  {
    // cockpit 已移除首页，不再提供独立路由，统一至 /energy
    // 若需兼容旧链接，可在此添加重定向：{ path: '/cockpit', redirect: '/energy' }
  },
  {
    path: '/export',
    name: 'export',
    component: DataExport,
    meta: { title: '数据导出' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router