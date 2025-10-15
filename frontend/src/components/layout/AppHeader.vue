<template>
  <header class="app-header">
    <div class="header-content">
      <div class="header-left">
        <div class="brand">
          <el-icon class="brand-icon">
            <Monitor />
          </el-icon>
          <h1 class="brand-title">环控平台维护工具</h1>
        </div>
      </div>
      
      <div class="header-center">
        <div class="breadcrumb">
          <span class="breadcrumb-item current">{{ currentPageTitle }}</span>
        </div>
      </div>
      
      <div class="header-right">
        <div class="user-info">
          <el-tag type="info" class="operator-tag">
            <el-icon><User /></el-icon>
            Operator: {{ operatorId }}
          </el-tag>
        </div>
        
        <div class="system-status">
          <el-tooltip content="系统状态" placement="bottom">
            <el-badge :value="connectionStatus === 'connected' ? '' : '!'" :type="connectionStatus === 'connected' ? 'success' : 'danger'">
              <el-icon class="status-icon" :class="connectionStatus">
                <Connection />
              </el-icon>
            </el-badge>
          </el-tooltip>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Monitor, User, Connection } from '@element-plus/icons-vue'

const props = defineProps({
  title: { type: String, default: '设备总览' }
})

const operatorId = ref('web-admin')
const connectionStatus = ref('connected') // connected, disconnected, error

const currentPageTitle = computed(() => props.title)
</script>

<style scoped>
.app-header {
  height: var(--header-height);
  background-color: var(--color-background-primary);
  border-bottom: 1px solid var(--color-border-secondary);
  box-shadow: var(--shadow-light);
  z-index: var(--z-index-sticky);
}

.header-content {
  height: 100%;
  padding: 0 var(--spacing-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1920px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  flex: none;
}

.brand {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
  transition: all var(--duration-base) var(--ease-out);
}

.brand:hover {
  opacity: 0.8;
}

.brand-icon {
  font-size: 24px;
  color: var(--color-primary);
}

.brand-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
  white-space: nowrap;
}

.header-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 var(--spacing-lg);
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.breadcrumb-item {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
}

.breadcrumb-item.current {
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  flex: none;
}

.operator-tag {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-weight: var(--font-weight-medium);
}

.system-status {
  display: flex;
  align-items: center;
}

.status-icon {
  font-size: 20px;
  transition: color var(--duration-base) var(--ease-out);
}

.status-icon.connected {
  color: var(--color-success);
}

.status-icon.disconnected {
  color: var(--color-error);
  animation: pulse 2s infinite;
}

.status-icon.error {
  color: var(--color-error);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    padding: 0 var(--spacing-md);
  }
  
  .brand-title {
    display: none;
  }
  
  .header-center {
    margin: 0 var(--spacing-sm);
  }
  
  .breadcrumb-item {
    font-size: var(--font-size-sm);
  }
}

@media (max-width: 480px) {
  .header-content {
    padding: 0 var(--spacing-sm);
  }
  
  .header-center {
    display: none;
  }
  
  .operator-tag :deep(.el-tag__content) {
    font-size: var(--font-size-xs);
  }
}
</style>