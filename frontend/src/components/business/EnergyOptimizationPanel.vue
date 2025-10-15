<template>
  <BaseCard title="能源优化建议" class="optimization-panel">
    <div class="panel-content">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>正在分析能源数据...</p>
      </div>
      
      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
        <el-button @click="$emit('retry')" type="primary" size="small">
          重新分析
        </el-button>
      </div>
      
      <div v-else class="suggestions-container">
        <div v-if="!suggestions.length" class="empty-state">
          <p>暂无优化建议</p>
          <el-button @click="$emit('analyze')" type="primary">
            开始分析
          </el-button>
        </div>
        
        <div v-else class="suggestions-list">
          <div 
            v-for="suggestion in suggestions" 
            :key="suggestion.id"
            class="suggestion-item"
            :class="[`priority-${suggestion.priority}`, { 'implemented': suggestion.implemented }]"
          >
            <div class="suggestion-header">
              <div class="suggestion-title">
                <span class="priority-badge" :class="`priority-${suggestion.priority}`">
                  {{ getPriorityText(suggestion.priority) }}
                </span>
                <h4>{{ suggestion.title }}</h4>
              </div>
              <div class="suggestion-actions">
                <el-button 
                  v-if="!suggestion.implemented"
                  @click="handleImplement(suggestion)"
                  type="primary"
                  size="small"
                >
                  实施
                </el-button>
                <el-button 
                  @click="handleDismiss(suggestion)"
                  text
                  size="small"
                >
                  忽略
                </el-button>
              </div>
            </div>
            
            <div class="suggestion-content">
              <p class="description">{{ suggestion.description }}</p>
              
              <div class="metrics">
                <div class="metric">
                  <span class="label">预计节能：</span>
                  <span class="value energy-saving">{{ suggestion.energySaving }}%</span>
                </div>
                <div class="metric">
                  <span class="label">预计节省：</span>
                  <span class="value cost-saving">¥{{ suggestion.costSaving }}</span>
                </div>
                <div class="metric">
                  <span class="label">实施难度：</span>
                  <span class="value difficulty">{{ getDifficultyText(suggestion.difficulty) }}</span>
                </div>
              </div>
              
              <div v-if="suggestion.steps?.length" class="implementation-steps">
                <h5>实施步骤：</h5>
                <ol>
                  <li v-for="step in suggestion.steps" :key="step">{{ step }}</li>
                </ol>
              </div>
            </div>
          </div>
        </div>
        
        <div class="panel-footer">
          <div class="summary">
            <span>共 {{ suggestions.length }} 条建议</span>
            <span>已实施 {{ implementedCount }} 条</span>
            <span>预计总节能 {{ totalEnergySaving }}%</span>
          </div>
          <el-button @click="$emit('refresh')" plain>
            刷新建议
          </el-button>
        </div>
      </div>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { BaseCard } from '../common'
import type { OptimizationSuggestion } from './types'

interface Props {
  suggestions?: OptimizationSuggestion[]
  loading?: boolean
  error?: string
}

interface Emits {
  (e: 'retry'): void
  (e: 'analyze'): void
  (e: 'refresh'): void
  (e: 'implement', suggestion: OptimizationSuggestion): void
  (e: 'dismiss', suggestion: OptimizationSuggestion): void
}

const props = withDefaults(defineProps<Props>(), {
  suggestions: () => [],
  loading: false,
  error: ''
})

const emit = defineEmits<Emits>()

// 计算属性
const implementedCount = computed(() => 
  props.suggestions.filter(s => s.implemented).length
)

const totalEnergySaving = computed(() => 
  props.suggestions.reduce((total, s) => total + s.energySaving, 0)
)

// 方法
const getPriorityText = (priority: 'high' | 'medium' | 'low'): string => {
  const map = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return map[priority]
}

const getDifficultyText = (difficulty: 'easy' | 'medium' | 'hard'): string => {
  const map = {
    easy: '简单',
    medium: '中等',
    hard: '困难'
  }
  return map[difficulty]
}

const handleImplement = (suggestion: OptimizationSuggestion) => {
  emit('implement', suggestion)
}

const handleDismiss = (suggestion: OptimizationSuggestion) => {
  emit('dismiss', suggestion)
}
</script>

<style scoped>
.optimization-panel {
  height: 100%;
}

.panel-content {
  min-height: 400px;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: var(--text-color-secondary);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-color);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.suggestion-item {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  background: var(--bg-color);
  transition: all 0.3s ease;
}

.suggestion-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.suggestion-item.implemented {
  opacity: 0.7;
  background: var(--bg-color-light);
}

.suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.suggestion-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.priority-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  color: white;
}

.priority-badge.priority-high {
  background: #f56565;
}

.priority-badge.priority-medium {
  background: #ed8936;
}

.priority-badge.priority-low {
  background: #48bb78;
}

.suggestion-title h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color);
}

.suggestion-actions {
  display: flex;
  gap: 8px;
}

.suggestion-content .description {
  margin: 0 0 16px 0;
  color: var(--text-color-secondary);
  line-height: 1.5;
}

.metrics {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metric .label {
  font-size: 12px;
  color: var(--text-color-secondary);
}

.metric .value {
  font-size: 14px;
  font-weight: 600;
}

.metric .value.energy-saving {
  color: #48bb78;
}

.metric .value.cost-saving {
  color: #3182ce;
}

.metric .value.difficulty {
  color: var(--text-color);
}

.implementation-steps {
  margin-top: 16px;
}

.implementation-steps h5 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-color);
}

.implementation-steps ol {
  margin: 0;
  padding-left: 20px;
}

.implementation-steps li {
  margin-bottom: 4px;
  color: var(--text-color-secondary);
  font-size: 14px;
  line-height: 1.4;
}

.panel-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.summary {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: var(--text-color-secondary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .suggestion-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .suggestion-actions {
    align-self: flex-end;
  }
  
  .metrics {
    gap: 16px;
  }
  
  .panel-footer {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .summary {
    flex-direction: column;
    gap: 8px;
  }
}

/* 深色模式 */
@media (prefers-color-scheme: dark) {
  .suggestion-item {
    background: var(--bg-color-dark);
    border-color: var(--border-color-dark);
  }
  
  .suggestion-item.implemented {
    background: var(--bg-color-darker);
  }
}
</style>