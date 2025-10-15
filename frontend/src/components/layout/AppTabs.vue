<template>
  <div class="app-tabs">
    <div class="tabs-container">
      <div class="tabs-wrapper">
        <button
          v-for="tab in tabs"
          :key="tab.name"
          class="tab-item"
          :class="{ active: modelValue === tab.name }"
          @click="handleTabClick(tab.name)"
          :aria-selected="modelValue === tab.name"
          role="tab"
        >
          <el-icon class="tab-icon">
            <component :is="tab.icon" />
          </el-icon>
          <span class="tab-label">{{ tab.label }}</span>
          <span v-if="tab.badge" class="tab-badge">{{ tab.badge }}</span>
        </button>
      </div>
      
      <div class="tabs-actions">
        <el-tooltip content="刷新当前页面" placement="bottom">
          <el-button size="small" text @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </el-tooltip>
        
        <el-tooltip content="全屏显示" placement="bottom">
          <el-button size="small" text @click="toggleFullscreen">
            <el-icon><FullScreen /></el-icon>
          </el-button>
        </el-tooltip>
      </div>
    </div>
    
    <div class="tab-content">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, markRaw } from 'vue'
import { 
  Monitor, 
  Download, 
  DataAnalysis,
  TrendCharts,
  Refresh, 
  FullScreen 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Props
const props = defineProps({
  modelValue: {
    type: String,
    default: 'device'
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'change', 'refresh'])

// 标签页定义
const tabs = ref([
  {
    name: 'device',
    label: '设备总览',
    icon: markRaw(Monitor),
    badge: null
  },
  {
    name: 'export',
    label: '数据导出',
    icon: markRaw(Download),
    badge: null
  }
])

// Methods
const handleTabClick = (tabName) => {
  if (tabName !== props.modelValue) {
    emit('update:modelValue', tabName)
    emit('change', tabName)
  }
}

const handleRefresh = () => {
  emit('refresh')
  ElMessage.success('页面已刷新')
}

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(err => {
      ElMessage.error('无法进入全屏模式')
    })
  } else {
    document.exitFullscreen()
  }
}

// 键盘导航支持
const handleKeydown = (event) => {
  const currentIndex = tabs.value.findIndex(tab => tab.name === props.modelValue)
  
  if (event.key === 'ArrowLeft' && currentIndex > 0) {
    event.preventDefault()
    handleTabClick(tabs.value[currentIndex - 1].name)
  } else if (event.key === 'ArrowRight' && currentIndex < tabs.value.length - 1) {
    event.preventDefault()
    handleTabClick(tabs.value[currentIndex + 1].name)
  }
}

// 添加键盘事件监听
if (typeof window !== 'undefined') {
  window.addEventListener('keydown', handleKeydown)
}
</script>

<style scoped>
.app-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tabs-container {
  height: var(--tab-height);
  background-color: var(--color-background-primary);
  border-bottom: 1px solid var(--color-border-secondary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-lg);
}

.tabs-wrapper {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  flex: 1;
}

.tab-item {
  height: 44px;
  padding: 0 var(--spacing-md);
  border: none;
  background: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  border-radius: var(--border-radius-md);
  transition: all var(--duration-base) var(--ease-out);
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-normal);
  position: relative;
  user-select: none;
}

.tab-item:hover {
  background-color: var(--color-background-tertiary);
  color: var(--color-text-primary);
}

.tab-item:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.tab-item.active {
  background-color: var(--color-primary);
  color: #ffffff;
  font-weight: var(--font-weight-medium);
  box-shadow: var(--shadow-light);
}

.tab-item.active:hover {
  background-color: var(--color-primary-dark);
}

.tab-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.tab-label {
  white-space: nowrap;
  flex-shrink: 0;
}

.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 6px;
  background-color: var(--color-error);
  color: #ffffff;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  border-radius: var(--border-radius-round);
  line-height: 1;
}

.tab-item.active .tab-badge {
  background-color: rgba(255, 255, 255, 0.8);
  color: var(--color-primary);
}

.tabs-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  flex-shrink: 0;
}

.tab-content {
  flex: 1;
  overflow: hidden;
  background-color: var(--color-background-secondary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .tabs-container {
    padding: 0 var(--spacing-md);
  }
  
  .tab-item {
    padding: 0 var(--spacing-sm);
  }
  
  .tab-label {
    display: none;
  }
  
  .tabs-actions {
    gap: var(--spacing-xs);
  }
}

@media (max-width: 480px) {
  .tabs-container {
    padding: 0 var(--spacing-sm);
  }
  
  .tab-item {
    height: 32px;
    padding: 0 var(--spacing-xs);
  }
  
  .tab-icon {
    font-size: 14px;
  }
  
  .tabs-actions {
    display: none;
  }
}

/* 动画效果 */
.tab-item::before {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: var(--color-primary);
  transform: scaleX(0);
  transition: transform var(--duration-base) var(--ease-out);
}

.tab-item.active::before {
  transform: scaleX(1);
}
</style>