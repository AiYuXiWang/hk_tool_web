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
  color: rgba(255, 255, 255, 0.7);
  text-align: center;
  gap: 12px;
}

.loading-state p,
.error-state p,
.empty-state p {
  margin: 0;
  font-size: 15px;
  letter-spacing: 0.05em;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 212, 255, 0.15);
  border-top: 4px solid rgba(0, 212, 255, 0.85);
  border-radius: 50%;
  animation: spin 1s linear infinite, glowPulse 1.8s ease-in-out infinite;
  margin-bottom: 12px;
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
  border: 1px solid rgba(0, 212, 255, 0.25);
  border-radius: 16px;
  padding: 20px;
  background: linear-gradient(135deg, rgba(14, 23, 51, 0.7) 0%, rgba(18, 32, 58, 0.6) 100%);
  backdrop-filter: blur(14px);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.3);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.suggestion-item:hover {
  box-shadow: 0 12px 40px rgba(0, 212, 255, 0.25);
  border-color: rgba(0, 212, 255, 0.5);
  transform: translateY(-3px) scale(1.01);
}

.suggestion-item.implemented {
  opacity: 0.65;
  background: linear-gradient(135deg, rgba(14, 23, 51, 0.6) 0%, rgba(18, 32, 58, 0.5) 100%);
  border-color: rgba(82, 196, 26, 0.3);
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
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  color: rgba(15, 25, 45, 0.95);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(8px);
}

.priority-badge.priority-high {
  background: linear-gradient(135deg, rgba(255, 77, 79, 0.85) 0%, rgba(255, 138, 141, 0.95) 100%);
  box-shadow: 0 8px 24px rgba(255, 77, 79, 0.35);
}

.priority-badge.priority-medium {
  background: linear-gradient(135deg, rgba(250, 173, 20, 0.85) 0%, rgba(255, 214, 102, 0.95) 100%);
  box-shadow: 0 8px 24px rgba(250, 173, 20, 0.35);
}

.priority-badge.priority-low {
  background: linear-gradient(135deg, rgba(82, 196, 26, 0.85) 0%, rgba(143, 239, 123, 0.95) 100%);
  box-shadow: 0 8px 24px rgba(82, 196, 26, 0.35);
}

.suggestion-title h4 {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  letter-spacing: 0.03em;
}

.suggestion-actions {
  display: flex;
  gap: 10px;
}

.suggestion-actions :deep(.el-button) {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2) 0%, rgba(18, 32, 58, 0.7) 100%);
  border-color: rgba(0, 212, 255, 0.35);
  color: rgba(255, 255, 255, 0.9);
  box-shadow: 0 8px 20px rgba(0, 212, 255, 0.18);
  transition: all 0.3s ease;
}

.suggestion-actions :deep(.el-button:hover) {
  border-color: rgba(0, 212, 255, 0.65);
  color: #fff;
  box-shadow: 0 12px 28px rgba(0, 212, 255, 0.25);
}

.suggestion-actions :deep(.el-button.is-text),
.suggestion-actions :deep(.el-button.el-button--text) {
  background: transparent;
  border-color: transparent;
  color: rgba(0, 212, 255, 0.85);
  box-shadow: none;
}

.suggestion-actions :deep(.el-button.is-text:hover),
.suggestion-actions :deep(.el-button.el-button--text:hover) {
  color: rgba(0, 255, 204, 0.95);
}

.suggestion-content .description {
  margin: 0 0 16px 0;
  color: rgba(255, 255, 255, 0.75);
  line-height: 1.6;
}

.metrics {
  display: flex;
  gap: 24px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 16px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(13, 25, 47, 0.65) 0%, rgba(16, 32, 60, 0.5) 100%);
  border: 1px solid rgba(0, 212, 255, 0.15);
  min-width: 140px;
}

.metric .label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.55);
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.metric .value {
  font-size: 15px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.metric .value.energy-saving {
  color: rgba(82, 196, 26, 0.95);
}

.metric .value.cost-saving {
  color: rgba(24, 144, 255, 0.95);
}

.metric .value.difficulty {
  color: rgba(0, 212, 255, 0.9);
}

.implementation-steps {
  margin-top: 20px;
  padding: 16px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(13, 25, 47, 0.6) 0%, rgba(16, 32, 60, 0.45) 100%);
  border: 1px solid rgba(0, 212, 255, 0.12);
}

.implementation-steps h5 {
  margin: 0 0 8px 0;
  font-size: 15px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  letter-spacing: 0.04em;
}

.implementation-steps ol {
  margin: 0;
  padding-left: 20px;
}

.implementation-steps li {
  margin-bottom: 6px;
  color: rgba(255, 255, 255, 0.65);
  font-size: 14px;
  line-height: 1.5;
}

.panel-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 28px;
  padding-top: 18px;
  border-top: 1px solid rgba(0, 212, 255, 0.18);
}

.panel-footer :deep(.el-button) {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.25) 0%, rgba(0, 255, 204, 0.45) 100%);
  color: #0b2432;
  border-color: transparent;
  box-shadow: 0 10px 30px rgba(0, 212, 255, 0.25);
}

.summary {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 0.04em;
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