import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface User {
  id: string
  username: string
  email: string
  role: 'admin' | 'operator' | 'viewer'
  avatar?: string
  permissions: string[]
  lastLoginTime?: Date
  preferences: UserPreferences
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto'
  language: 'zh-CN' | 'en-US'
  timezone: string
  dateFormat: string
  refreshInterval: number
  notifications: {
    email: boolean
    browser: boolean
    sound: boolean
  }
  dashboard: {
    layout: 'grid' | 'list'
    autoRefresh: boolean
    showAnimations: boolean
  }
}

export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  timestamp: Date
  read: boolean
  persistent?: boolean
  actions?: NotificationAction[]
}

export interface NotificationAction {
  label: string
  action: () => void
  type?: 'primary' | 'secondary'
}

export interface AppConfig {
  version: string
  buildTime: string
  apiBaseUrl: string
  wsUrl: string
  features: {
    realTimeMonitoring: boolean
    dataExport: boolean
    deviceManagement: boolean
    alertSystem: boolean
    reporting: boolean
  }
  limits: {
    maxDevices: number
    maxExportSize: number
    dataRetentionDays: number
  }
}

export interface SystemStatus {
  online: boolean
  lastHeartbeat: Date
  serverTime: Date
  uptime: number
  performance: {
    cpu: number
    memory: number
    disk: number
    network: number
  }
  services: {
    database: 'online' | 'offline' | 'degraded'
    messageQueue: 'online' | 'offline' | 'degraded'
    fileStorage: 'online' | 'offline' | 'degraded'
    monitoring: 'online' | 'offline' | 'degraded'
  }
}

export const useAppStore = defineStore('app', () => {
  // 状态定义
  const user = ref<User | null>(null)
  const isAuthenticated = ref(false)
  const notifications = ref<Notification[]>([])
  const config = ref<AppConfig | null>(null)
  const systemStatus = ref<SystemStatus | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const sidebarCollapsed = ref(false)
  const currentTab = ref('monitor')
  const lastActivity = ref<Date>(new Date())
  const connectionStatus = ref<'connected' | 'disconnected' | 'reconnecting'>('disconnected')

  // 计算属性
  const unreadNotifications = computed(() => 
    notifications.value.filter(n => !n.read)
  )

  const criticalNotifications = computed(() => 
    notifications.value.filter(n => n.type === 'error' && !n.read)
  )

  const hasPermission = computed(() => (permission: string) => {
    return user.value?.permissions.includes(permission) || user.value?.role === 'admin'
  })

  const isAdmin = computed(() => user.value?.role === 'admin')

  const isOperator = computed(() => 
    user.value?.role === 'admin' || user.value?.role === 'operator'
  )

  const currentTheme = computed(() => {
    if (!user.value) return 'light'
    
    const theme = user.value.preferences.theme
    if (theme === 'auto') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    return theme
  })

  const systemHealth = computed(() => {
    if (!systemStatus.value) return 'unknown'
    
    const services = Object.values(systemStatus.value.services)
    const offlineServices = services.filter(s => s === 'offline').length
    const degradedServices = services.filter(s => s === 'degraded').length
    
    if (offlineServices > 0) return 'critical'
    if (degradedServices > 0) return 'warning'
    return 'healthy'
  })

  const isSessionExpired = computed(() => {
    if (!user.value?.lastLoginTime) return false
    
    const sessionTimeout = 8 * 60 * 60 * 1000 // 8小时
    const now = new Date().getTime()
    const lastLogin = user.value.lastLoginTime.getTime()
    
    return (now - lastLogin) > sessionTimeout
  })

  // Actions
  const setLoading = (isLoading: boolean) => {
    loading.value = isLoading
  }

  const setError = (errorMessage: string | null) => {
    error.value = errorMessage
  }

  const setUser = (userData: User) => {
    user.value = userData
    isAuthenticated.value = true
    updateLastActivity()
  }

  const clearUser = () => {
    user.value = null
    isAuthenticated.value = false
  }

  const updateUserPreferences = (preferences: Partial<UserPreferences>) => {
    if (user.value) {
      user.value.preferences = { ...user.value.preferences, ...preferences }
      // 在实际应用中，这里会调用API保存偏好设置
    }
  }

  const setSidebarCollapsed = (collapsed: boolean) => {
    sidebarCollapsed.value = collapsed
  }

  const setCurrentTab = (tab: string) => {
    currentTab.value = tab
    updateLastActivity()
  }

  const updateLastActivity = () => {
    lastActivity.value = new Date()
  }

  const setConnectionStatus = (status: typeof connectionStatus.value) => {
    connectionStatus.value = status
  }

  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    const newNotification: Notification = {
      ...notification,
      id: `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
      read: false
    }
    
    notifications.value.unshift(newNotification)
    
    // 限制通知数量
    if (notifications.value.length > 100) {
      notifications.value = notifications.value.slice(0, 100)
    }
    
    // 如果启用了浏览器通知
    if (user.value?.preferences.notifications.browser && 'Notification' in window) {
      if (Notification.permission === 'granted') {
        new Notification(notification.title, {
          body: notification.message,
          icon: '/favicon.ico'
        })
      }
    }
    
    return newNotification
  }

  const markNotificationAsRead = (notificationId: string) => {
    const notification = notifications.value.find(n => n.id === notificationId)
    if (notification) {
      notification.read = true
    }
  }

  const markAllNotificationsAsRead = () => {
    notifications.value.forEach(n => n.read = true)
  }

  const removeNotification = (notificationId: string) => {
    const index = notifications.value.findIndex(n => n.id === notificationId)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clearNotifications = () => {
    notifications.value = []
  }

  const loadConfig = async () => {
    try {
      setLoading(true)
      
      // 模拟加载配置
      const mockConfig: AppConfig = {
        version: '1.0.0',
        buildTime: new Date().toISOString(),
        apiBaseUrl: '/api',
        wsUrl: 'ws://localhost:8000/ws',
        features: {
          realTimeMonitoring: true,
          dataExport: true,
          deviceManagement: true,
          alertSystem: true,
          reporting: true
        },
        limits: {
          maxDevices: 1000,
          maxExportSize: 100 * 1024 * 1024, // 100MB
          dataRetentionDays: 365
        }
      }
      
      config.value = mockConfig
      
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载配置失败')
    } finally {
      setLoading(false)
    }
  }

  const loadSystemStatus = async () => {
    try {
      // 模拟加载系统状态
      const mockStatus: SystemStatus = {
        online: true,
        lastHeartbeat: new Date(),
        serverTime: new Date(),
        uptime: Math.floor(Math.random() * 1000000),
        performance: {
          cpu: Math.floor(Math.random() * 100),
          memory: Math.floor(Math.random() * 100),
          disk: Math.floor(Math.random() * 100),
          network: Math.floor(Math.random() * 100)
        },
        services: {
          database: 'online',
          messageQueue: 'online',
          fileStorage: 'online',
          monitoring: 'online'
        }
      }
      
      systemStatus.value = mockStatus
      setConnectionStatus('connected')
      
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载系统状态失败')
      setConnectionStatus('disconnected')
    }
  }

  const login = async (username: string, password: string) => {
    try {
      setLoading(true)
      setError(null)
      
      // 模拟登录
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      if (username === 'admin' && password === 'admin') {
        const userData: User = {
          id: 'user-1',
          username: 'admin',
          email: 'admin@example.com',
          role: 'admin',
          avatar: '/avatars/admin.png',
          permissions: ['*'],
          lastLoginTime: new Date(),
          preferences: {
            theme: 'light',
            language: 'zh-CN',
            timezone: 'Asia/Shanghai',
            dateFormat: 'YYYY-MM-DD HH:mm:ss',
            refreshInterval: 30000,
            notifications: {
              email: true,
              browser: true,
              sound: false
            },
            dashboard: {
              layout: 'grid',
              autoRefresh: true,
              showAnimations: true
            }
          }
        }
        
        setUser(userData)
        addNotification({
          type: 'success',
          title: '登录成功',
          message: `欢迎回来，${userData.username}！`
        })
        
        return userData
      } else {
        throw new Error('用户名或密码错误')
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '登录失败'
      setError(errorMessage)
      addNotification({
        type: 'error',
        title: '登录失败',
        message: errorMessage
      })
      throw err
    } finally {
      setLoading(false)
    }
  }

  const logout = async () => {
    try {
      setLoading(true)
      
      // 模拟登出
      await new Promise(resolve => setTimeout(resolve, 500))
      
      clearUser()
      clearNotifications()
      setConnectionStatus('disconnected')
      
      addNotification({
        type: 'info',
        title: '已退出登录',
        message: '您已安全退出系统'
      })
      
    } catch (err) {
      setError(err instanceof Error ? err.message : '退出登录失败')
    } finally {
      setLoading(false)
    }
  }

  const requestNotificationPermission = async () => {
    if ('Notification' in window && Notification.permission === 'default') {
      const permission = await Notification.requestPermission()
      return permission === 'granted'
    }
    return Notification.permission === 'granted'
  }

  const checkSessionValidity = () => {
    if (isSessionExpired.value) {
      addNotification({
        type: 'warning',
        title: '会话即将过期',
        message: '请重新登录以继续使用系统',
        persistent: true,
        actions: [
          {
            label: '重新登录',
            action: logout,
            type: 'primary'
          }
        ]
      })
    }
  }

  const initializeApp = async () => {
    try {
      setLoading(true)
      
      await Promise.all([
        loadConfig(),
        loadSystemStatus()
      ])
      
      // 检查会话有效性
      if (isAuthenticated.value) {
        checkSessionValidity()
      }
      
      // 请求通知权限
      await requestNotificationPermission()
      
    } catch (err) {
      setError(err instanceof Error ? err.message : '应用初始化失败')
    } finally {
      setLoading(false)
    }
  }

  const clearData = () => {
    clearUser()
    notifications.value = []
    config.value = null
    systemStatus.value = null
    loading.value = false
    error.value = null
    sidebarCollapsed.value = false
    currentTab.value = 'monitor'
    lastActivity.value = new Date()
    connectionStatus.value = 'disconnected'
  }

  return {
    // 状态
    user,
    isAuthenticated,
    notifications,
    config,
    systemStatus,
    loading,
    error,
    sidebarCollapsed,
    currentTab,
    lastActivity,
    connectionStatus,
    
    // 计算属性
    unreadNotifications,
    criticalNotifications,
    hasPermission,
    isAdmin,
    isOperator,
    currentTheme,
    systemHealth,
    isSessionExpired,
    
    // Actions
    setLoading,
    setError,
    setUser,
    clearUser,
    updateUserPreferences,
    setSidebarCollapsed,
    setCurrentTab,
    updateLastActivity,
    setConnectionStatus,
    addNotification,
    markNotificationAsRead,
    markAllNotificationsAsRead,
    removeNotification,
    clearNotifications,
    loadConfig,
    loadSystemStatus,
    login,
    logout,
    requestNotificationPermission,
    checkSessionValidity,
    initializeApp,
    clearData
  }
})