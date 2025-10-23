import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import EnergyPage from '@/views/EnergyPage.vue'
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