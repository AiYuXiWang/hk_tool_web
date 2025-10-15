<template>
  <div class="optimization-suggestions">
    <!-- 建议概览 -->
    <div class="suggestions-overview">
      <h3 class="section-title">
        <i class="icon-lightbulb"></i>
        智能节能优化建议
      </h3>
      <div class="overview-stats">
        <div class="stat-item">
          <div class="stat-value">{{ totalSuggestions }}</div>
          <div class="stat-label">优化建议</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ potentialSavings }}%</div>
          <div class="stat-label">预计节能</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ implementedCount }}</div>
          <div class="stat-label">已实施</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ estimatedROI }}个月</div>
          <div class="stat-label">投资回收期</div>
        </div>
      </div>
    </div>

    <!-- 建议分类标签 -->
    <div class="suggestion-filters">
      <div class="filter-tabs">
        <button 
          v-for="category in categories" 
          :key="category.id"
          class="filter-tab"
          :class="{ active: activeCategory === category.id }"
          @click="setActiveCategory(category.id)"
        >
          <i :class="category.icon"></i>
          <span>{{ category.name }}</span>
          <span class="count">{{ category.count }}</span>
        </button>
      </div>
      <div class="filter-controls">
        <el-select v-model="priorityFilter" placeholder="优先级" size="small" class="filter-select">
          <el-option label="全部" value="all" />
          <el-option label="高优先级" value="high" />
          <el-option label="中优先级" value="medium" />
          <el-option label="低优先级" value="low" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="状态" size="small" class="filter-select">
          <el-option label="全部" value="all" />
          <el-option label="待实施" value="pending" />
          <el-option label="进行中" value="in_progress" />
          <el-option label="已完成" value="completed" />
          <el-option label="已忽略" value="ignored" />
        </el-select>
      </div>
    </div>

    <!-- 建议列表 -->
    <div class="suggestions-list">
      <div 
        v-for="suggestion in filteredSuggestions" 
        :key="suggestion.id"
        class="suggestion-card"
        :class="[suggestion.priority, suggestion.status]"
      >
        <div class="suggestion-header">
          <div class="suggestion-meta">
            <div class="suggestion-category">
              <i :class="getCategoryIcon(suggestion.category)"></i>
              <span>{{ suggestion.category }}</span>
            </div>
            <div class="suggestion-priority" :class="suggestion.priority">
              {{ getPriorityText(suggestion.priority) }}
            </div>
          </div>
          <div class="suggestion-actions">
            <el-dropdown @command="handleAction">
              <el-button type="text" size="small">
                <i class="icon-more"></i>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="{ action: 'implement', id: suggestion.id }">
                    实施建议
                  </el-dropdown-item>
                  <el-dropdown-item :command="{ action: 'schedule', id: suggestion.id }">
                    计划实施
                  </el-dropdown-item>
                  <el-dropdown-item :command="{ action: 'ignore', id: suggestion.id }">
                    忽略建议
                  </el-dropdown-item>
                  <el-dropdown-item :command="{ action: 'details', id: suggestion.id }">
                    查看详情
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>

        <div class="suggestion-content">
          <h4 class="suggestion-title">{{ suggestion.title }}</h4>
          <p class="suggestion-description">{{ suggestion.description }}</p>
          
          <!-- 建议详情 -->
          <div class="suggestion-details">
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">影响设备</span>
                <span class="detail-value">{{ suggestion.affectedEquipment.join(', ') }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">预计节能</span>
                <span class="detail-value energy-saving">{{ suggestion.energySaving }}%</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">实施难度</span>
                <span class="detail-value" :class="suggestion.difficulty">
                  {{ getDifficultyText(suggestion.difficulty) }}
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-label">预计成本</span>
                <span class="detail-value">{{ formatCost(suggestion.estimatedCost) }}</span>
              </div>
            </div>
          </div>

          <!-- 实施步骤 -->
          <div class="implementation-steps" v-if="suggestion.steps && suggestion.steps.length > 0">
            <h5 class="steps-title">实施步骤</h5>
            <div class="steps-list">
              <div 
                v-for="(step, index) in suggestion.steps" 
                :key="index"
                class="step-item"
                :class="{ completed: step.completed }"
              >
                <div class="step-number">{{ index + 1 }}</div>
                <div class="step-content">
                  <div class="step-title">{{ step.title }}</div>
                  <div class="step-description">{{ step.description }}</div>
                  <div class="step-meta">
                    <span class="step-duration">预计耗时: {{ step.duration }}</span>
                    <span class="step-responsible">负责人: {{ step.responsible }}</span>
                  </div>
                </div>
                <div class="step-status">
                  <i :class="step.completed ? 'icon-check' : 'icon-clock'"></i>
                </div>
              </div>
            </div>
          </div>

          <!-- 效果预测 -->
          <div class="effect-prediction">
            <h5 class="prediction-title">效果预测</h5>
            <div class="prediction-chart" :data-chart-id="suggestion.id"></div>
            <div class="prediction-summary">
              <div class="summary-item">
                <span class="summary-label">月节能量</span>
                <span class="summary-value">{{ suggestion.monthlyEnergySaving }} kWh</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">月节约成本</span>
                <span class="summary-value">{{ formatCost(suggestion.monthlyCostSaving) }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">年化收益</span>
                <span class="summary-value">{{ formatCost(suggestion.annualBenefit) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="suggestion-footer">
          <div class="suggestion-timestamp">
            <i class="icon-time"></i>
            <span>{{ formatTime(suggestion.createdAt) }}</span>
          </div>
          <div class="suggestion-source">
            <i class="icon-robot"></i>
            <span>{{ suggestion.source }}</span>
          </div>
          <div class="suggestion-confidence">
            <span class="confidence-label">置信度</span>
            <div class="confidence-bar">
              <div 
                class="confidence-fill" 
                :style="{ width: `${suggestion.confidence}%` }"
              ></div>
            </div>
            <span class="confidence-value">{{ suggestion.confidence }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredSuggestions.length === 0" class="empty-state">
      <i class="icon-empty"></i>
      <h4>暂无优化建议</h4>
      <p>系统正在分析能耗数据，稍后将为您提供个性化的节能建议</p>
      <el-button type="primary" @click="refreshSuggestions">
        <i class="icon-refresh"></i>
        刷新建议
      </el-button>
    </div>

    <!-- 建议详情弹窗 -->
    <el-dialog 
      v-model="showDetailDialog" 
      title="建议详情" 
      width="800px"
      :before-close="closeDetailDialog"
    >
      <div v-if="selectedSuggestion" class="suggestion-detail-dialog">
        <!-- 详情内容 -->
        <div class="detail-content">
          <h3>{{ selectedSuggestion.title }}</h3>
          <p>{{ selectedSuggestion.description }}</p>
          
          <!-- 技术分析 -->
          <div class="technical-analysis">
            <h4>技术分析</h4>
            <div class="analysis-content">
              <p>{{ selectedSuggestion.technicalAnalysis }}</p>
            </div>
          </div>

          <!-- 风险评估 -->
          <div class="risk-assessment">
            <h4>风险评估</h4>
            <div class="risk-items">
              <div 
                v-for="risk in selectedSuggestion.risks" 
                :key="risk.id"
                class="risk-item"
                :class="risk.level"
              >
                <div class="risk-level">{{ risk.level }}</div>
                <div class="risk-description">{{ risk.description }}</div>
                <div class="risk-mitigation">缓解措施: {{ risk.mitigation }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="closeDetailDialog">关闭</el-button>
        <el-button type="primary" @click="implementSuggestion(selectedSuggestion)">
          实施建议
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'

// 组件属性
const props = defineProps({
  refreshInterval: {
    type: Number,
    default: 60000 // 1分钟刷新一次
  }
})

// 响应式数据
const activeCategory = ref('all')
const priorityFilter = ref('all')
const statusFilter = ref('all')
const showDetailDialog = ref(false)
const selectedSuggestion = ref(null)
let refreshTimer = null
const chartInstances = new Map()

// 建议分类
const categories = reactive([
  { id: 'all', name: '全部', icon: 'icon-all', count: 0 },
  { id: 'equipment', name: '设备优化', icon: 'icon-equipment', count: 0 },
  { id: 'schedule', name: '运行策略', icon: 'icon-schedule', count: 0 },
  { id: 'maintenance', name: '维护建议', icon: 'icon-maintenance', count: 0 },
  { id: 'upgrade', name: '升级改造', icon: 'icon-upgrade', count: 0 }
])

// 模拟建议数据
const suggestions = reactive([
  {
    id: 1,
    category: 'equipment',
    priority: 'high',
    status: 'pending',
    title: '冷机运行参数优化',
    description: '根据实时负荷调整冷机冷冻水出水温度，在保证舒适度的前提下提升系统能效',
    affectedEquipment: ['冷机LS01', '冷机LS02'],
    energySaving: 12.5,
    difficulty: 'easy',
    estimatedCost: 5000,
    monthlyEnergySaving: 15600,
    monthlyCostSaving: 12480,
    annualBenefit: 149760,
    confidence: 92,
    createdAt: Date.now() - 1800000, // 30分钟前
    source: 'AI能效分析引擎',
    technicalAnalysis: '通过分析历史运行数据发现，当前冷机出水温度设定偏低，在满足末端需求的情况下，可适当提高出水温度1-2℃，从而降低冷机功耗。',
    risks: [
      {
        id: 1,
        level: 'low',
        description: '可能影响部分区域舒适度',
        mitigation: '分阶段调整，实时监控温度反馈'
      }
    ],
    steps: [
      {
        title: '数据收集与分析',
        description: '收集近30天冷机运行数据和末端温度反馈',
        duration: '2小时',
        responsible: '运维工程师',
        completed: true
      },
      {
        title: '参数调整方案制定',
        description: '制定分阶段调整方案，确定最优出水温度',
        duration: '4小时',
        responsible: '技术主管',
        completed: false
      },
      {
        title: '试运行与监控',
        description: '实施调整并监控系统响应',
        duration: '1周',
        responsible: '运维团队',
        completed: false
      }
    ]
  },
  {
    id: 2,
    category: 'schedule',
    priority: 'high',
    status: 'pending',
    title: '水泵变频控制策略优化',
    description: '基于实时流量需求动态调整水泵转速，避免过度运行造成的能耗浪费',
    affectedEquipment: ['冷冻水泵P01', '冷冻水泵P02', '冷却水泵P03'],
    energySaving: 18.3,
    difficulty: 'medium',
    estimatedCost: 15000,
    monthlyEnergySaving: 22800,
    monthlyCostSaving: 18240,
    annualBenefit: 218880,
    confidence: 88,
    createdAt: Date.now() - 3600000, // 1小时前
    source: 'AI能效分析引擎',
    technicalAnalysis: '当前水泵运行策略较为保守，存在过度运行现象。通过优化变频控制算法，可以更精确地匹配实际需求。',
    risks: [
      {
        id: 1,
        level: 'medium',
        description: '控制算法调整可能影响系统稳定性',
        mitigation: '采用渐进式调整，保留原有控制逻辑作为备份'
      }
    ],
    steps: [
      {
        title: '现有控制策略分析',
        description: '分析当前变频控制逻辑和运行效果',
        duration: '1天',
        responsible: '自控工程师',
        completed: false
      },
      {
        title: '优化算法开发',
        description: '开发基于负荷预测的智能控制算法',
        duration: '1周',
        responsible: '算法工程师',
        completed: false
      }
    ]
  },
  {
    id: 3,
    category: 'maintenance',
    priority: 'medium',
    status: 'in_progress',
    title: '冷却塔清洗维护',
    description: '定期清洗冷却塔填料和水盘，提高换热效率，降低冷机冷凝温度',
    affectedEquipment: ['冷却塔CT01', '冷却塔CT02'],
    energySaving: 8.5,
    difficulty: 'easy',
    estimatedCost: 8000,
    monthlyEnergySaving: 10600,
    monthlyCostSaving: 8480,
    annualBenefit: 101760,
    confidence: 95,
    createdAt: Date.now() - 7200000, // 2小时前
    source: '设备健康监测系统',
    technicalAnalysis: '冷却塔填料积垢严重，影响换热效率，导致冷凝温度偏高，增加冷机能耗。',
    risks: [
      {
        id: 1,
        level: 'low',
        description: '清洗期间需要停机',
        mitigation: '安排在低负荷时段进行，使用备用设备'
      }
    ],
    steps: [
      {
        title: '制定清洗计划',
        description: '确定清洗时间和方案',
        duration: '2小时',
        responsible: '维护主管',
        completed: true
      },
      {
        title: '执行清洗作业',
        description: '专业清洗团队执行清洗作业',
        duration: '1天',
        responsible: '外包清洗队',
        completed: false
      }
    ]
  },
  {
    id: 4,
    category: 'upgrade',
    priority: 'low',
    status: 'pending',
    title: 'LED照明系统升级',
    description: '将传统荧光灯更换为LED灯具，降低照明能耗并改善照明质量',
    affectedEquipment: ['站厅照明', '站台照明', '设备房照明'],
    energySaving: 45.0,
    difficulty: 'medium',
    estimatedCost: 120000,
    monthlyEnergySaving: 8500,
    monthlyCostSaving: 6800,
    annualBenefit: 81600,
    confidence: 98,
    createdAt: Date.now() - 10800000, // 3小时前
    source: '能耗审计报告',
    technicalAnalysis: '现有照明系统能耗较高，LED技术成熟，投资回收期约18个月，具有良好的经济效益。',
    risks: [
      {
        id: 1,
        level: 'low',
        description: '初期投资较大',
        mitigation: '分期实施，优先更换高使用频率区域'
      }
    ],
    steps: [
      {
        title: '照明现状调研',
        description: '统计现有灯具数量和功率',
        duration: '3天',
        responsible: '电气工程师',
        completed: false
      },
      {
        title: 'LED选型与采购',
        description: '选择合适的LED产品并进行采购',
        duration: '2周',
        responsible: '采购部门',
        completed: false
      }
    ]
  }
])

// 计算属性
const totalSuggestions = computed(() => suggestions.length)
const potentialSavings = computed(() => {
  const total = suggestions.reduce((sum, s) => sum + s.energySaving, 0)
  return (total / suggestions.length).toFixed(1)
})
const implementedCount = computed(() => 
  suggestions.filter(s => s.status === 'completed').length
)
const estimatedROI = computed(() => {
  const totalCost = suggestions.reduce((sum, s) => sum + s.estimatedCost, 0)
  const totalBenefit = suggestions.reduce((sum, s) => sum + s.annualBenefit, 0)
  return totalBenefit > 0 ? Math.round((totalCost / totalBenefit) * 12) : 0
})

const filteredSuggestions = computed(() => {
  let filtered = suggestions

  // 按分类过滤
  if (activeCategory.value !== 'all') {
    filtered = filtered.filter(s => s.category === activeCategory.value)
  }

  // 按优先级过滤
  if (priorityFilter.value !== 'all') {
    filtered = filtered.filter(s => s.priority === priorityFilter.value)
  }

  // 按状态过滤
  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(s => s.status === statusFilter.value)
  }

  return filtered
})

// 方法
const setActiveCategory = (categoryId) => {
  activeCategory.value = categoryId
}

const getCategoryIcon = (category) => {
  const categoryMap = {
    equipment: 'icon-equipment',
    schedule: 'icon-schedule',
    maintenance: 'icon-maintenance',
    upgrade: 'icon-upgrade'
  }
  return categoryMap[category] || 'icon-default'
}

const getPriorityText = (priority) => {
  const priorityMap = {
    high: '高优先级',
    medium: '中优先级',
    low: '低优先级'
  }
  return priorityMap[priority] || priority
}

const getDifficultyText = (difficulty) => {
  const difficultyMap = {
    easy: '简单',
    medium: '中等',
    hard: '困难'
  }
  return difficultyMap[difficulty] || difficulty
}

const formatCost = (cost) => {
  if (cost >= 10000) {
    return `${(cost / 10000).toFixed(1)}万元`
  }
  return `${cost.toLocaleString()}元`
}

const formatTime = (timestamp) => {
  const now = Date.now()
  const diff = now - timestamp
  const hours = Math.floor(diff / 3600000)
  const minutes = Math.floor((diff % 3600000) / 60000)
  
  if (hours > 0) {
    return `${hours}小时前`
  } else if (minutes > 0) {
    return `${minutes}分钟前`
  } else {
    return '刚刚'
  }
}

const handleAction = (command) => {
  const { action, id } = command
  const suggestion = suggestions.find(s => s.id === id)
  
  switch (action) {
    case 'implement':
      implementSuggestion(suggestion)
      break
    case 'schedule':
      scheduleSuggestion(suggestion)
      break
    case 'ignore':
      ignoreSuggestion(suggestion)
      break
    case 'details':
      showSuggestionDetails(suggestion)
      break
  }
}

const implementSuggestion = async (suggestion) => {
  try {
    await ElMessageBox.confirm(
      `确定要实施建议"${suggestion.title}"吗？`,
      '确认实施',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    suggestion.status = 'in_progress'
    ElMessage.success('建议已开始实施')
  } catch {
    // 用户取消
  }
}

const scheduleSuggestion = (suggestion) => {
  ElMessage.info('建议已加入实施计划')
  // 这里可以打开计划设置对话框
}

const ignoreSuggestion = async (suggestion) => {
  try {
    await ElMessageBox.confirm(
      `确定要忽略建议"${suggestion.title}"吗？`,
      '确认忽略',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    suggestion.status = 'ignored'
    ElMessage.success('建议已忽略')
  } catch {
    // 用户取消
  }
}

const showSuggestionDetails = (suggestion) => {
  selectedSuggestion.value = suggestion
  showDetailDialog.value = true
}

const closeDetailDialog = () => {
  showDetailDialog.value = false
  selectedSuggestion.value = null
}

const refreshSuggestions = () => {
  ElMessage.info('正在刷新建议...')
  // 这里可以调用API刷新建议
}

// 更新分类计数
const updateCategoryCounts = () => {
  categories.forEach(category => {
    if (category.id === 'all') {
      category.count = suggestions.length
    } else {
      category.count = suggestions.filter(s => s.category === category.id).length
    }
  })
}

// 初始化效果预测图表
const initPredictionCharts = () => {
  nextTick(() => {
    suggestions.forEach(suggestion => {
      const chartRef = `chart-${suggestion.id}`
      const chartElement = document.querySelector(`[data-chart-id="${suggestion.id}"]`)
      
      if (chartElement && !chartInstances.has(suggestion.id)) {
        const chart = echarts.init(chartElement)
        
        const option = {
          backgroundColor: 'transparent',
          grid: {
            left: 10,
            right: 10,
            top: 10,
            bottom: 10
          },
          xAxis: {
            type: 'category',
            data: ['当前', '实施后'],
            axisLine: { show: false },
            axisTick: { show: false },
            axisLabel: {
              color: '#a0aec0',
              fontSize: 10
            }
          },
          yAxis: {
            type: 'value',
            show: false
          },
          series: [{
            type: 'bar',
            data: [100, 100 - suggestion.energySaving],
            itemStyle: {
              color: (params) => {
                return params.dataIndex === 0 ? '#ff6b6b' : '#4ecdc4'
              }
            },
            barWidth: '60%'
          }]
        }
        
        chart.setOption(option)
        chartInstances.set(suggestion.id, chart)
      }
    })
  })
}

// 生命周期
onMounted(() => {
  updateCategoryCounts()
  initPredictionCharts()
  
  // 设置定时刷新
  refreshTimer = setInterval(() => {
    // 这里可以调用API刷新数据
    updateCategoryCounts()
  }, props.refreshInterval)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  
  // 销毁图表实例
  chartInstances.forEach(chart => {
    chart.dispose()
  })
  chartInstances.clear()
})
</script>

<style scoped>
.optimization-suggestions {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 20px;
}

/* 建议概览 */
.suggestions-overview {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
}

.section-title i {
  color: #00d4ff;
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #00d4ff;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #a0aec0;
}

/* 过滤器 */
.suggestion-filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px 24px;
}

.filter-tabs {
  display: flex;
  gap: 8px;
}

.filter-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #a0aec0;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-tab:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.filter-tab.active {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
  color: #00d4ff;
}

.filter-tab .count {
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 12px;
}

.filter-controls {
  display: flex;
  gap: 12px;
}

.filter-select {
  width: 120px;
}

/* 建议列表 */
.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.suggestion-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 24px;
  transition: all 0.3s ease;
}

.suggestion-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 212, 255, 0.15);
}

.suggestion-card.high {
  border-left: 4px solid #ff6b6b;
}

.suggestion-card.medium {
  border-left: 4px solid #ffa726;
}

.suggestion-card.low {
  border-left: 4px solid #4ecdc4;
}

.suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.suggestion-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}

.suggestion-category {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  font-size: 12px;
  color: #a0aec0;
}

.suggestion-priority {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.suggestion-priority.high {
  background: rgba(255, 107, 107, 0.2);
  color: #ff6b6b;
}

.suggestion-priority.medium {
  background: rgba(255, 167, 38, 0.2);
  color: #ffa726;
}

.suggestion-priority.low {
  background: rgba(78, 205, 196, 0.2);
  color: #4ecdc4;
}

.suggestion-content {
  margin-bottom: 20px;
}

.suggestion-title {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
}

.suggestion-description {
  margin: 0 0 16px 0;
  color: #a0aec0;
  line-height: 1.5;
}

.suggestion-details {
  margin-bottom: 20px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
}

.detail-label {
  font-size: 13px;
  color: #a0aec0;
}

.detail-value {
  font-size: 13px;
  font-weight: 600;
  color: #ffffff;
}

.detail-value.energy-saving {
  color: #4ecdc4;
}

.detail-value.easy {
  color: #4ecdc4;
}

.detail-value.medium {
  color: #ffa726;
}

.detail-value.hard {
  color: #ff6b6b;
}

/* 实施步骤 */
.implementation-steps {
  margin-bottom: 20px;
}

.steps-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
}

.step-item.completed {
  background: rgba(78, 205, 196, 0.1);
}

.step-number {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  color: #ffffff;
  flex-shrink: 0;
}

.step-item.completed .step-number {
  background: #4ecdc4;
  color: #1a202c;
}

.step-content {
  flex: 1;
}

.step-title {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 4px;
}

.step-description {
  font-size: 13px;
  color: #a0aec0;
  margin-bottom: 6px;
}

.step-meta {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #718096;
}

.step-status {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.step-status i {
  color: #4ecdc4;
}

/* 效果预测 */
.effect-prediction {
  margin-bottom: 20px;
}

.prediction-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

.prediction-chart {
  height: 80px;
  margin-bottom: 12px;
}

.prediction-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.summary-label {
  font-size: 11px;
  color: #a0aec0;
  margin-bottom: 2px;
}

.summary-value {
  font-size: 13px;
  font-weight: 600;
  color: #4ecdc4;
}

/* 建议底部 */
.suggestion-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.suggestion-timestamp,
.suggestion-source {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #718096;
}

.suggestion-confidence {
  display: flex;
  align-items: center;
  gap: 8px;
}

.confidence-label {
  font-size: 12px;
  color: #a0aec0;
}

.confidence-bar {
  width: 60px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, #ffa726, #4ecdc4);
  transition: width 0.3s ease;
}

.confidence-value {
  font-size: 12px;
  font-weight: 600;
  color: #ffffff;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.empty-state i {
  font-size: 48px;
  color: #4a5568;
  margin-bottom: 16px;
}

.empty-state h4 {
  margin: 0 0 8px 0;
  color: #a0aec0;
}

.empty-state p {
  margin: 0 0 20px 0;
  color: #718096;
}

/* 详情对话框 */
.suggestion-detail-dialog {
  max-height: 600px;
  overflow-y: auto;
}

.technical-analysis,
.risk-assessment {
  margin-bottom: 20px;
}

.technical-analysis h4,
.risk-assessment h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #ffffff;
}

.analysis-content {
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  color: #a0aec0;
  line-height: 1.6;
}

.risk-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.risk-item {
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid;
}

.risk-item.low {
  background: rgba(78, 205, 196, 0.1);
  border-left-color: #4ecdc4;
}

.risk-item.medium {
  background: rgba(255, 167, 38, 0.1);
  border-left-color: #ffa726;
}

.risk-item.high {
  background: rgba(255, 107, 107, 0.1);
  border-left-color: #ff6b6b;
}

.risk-level {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 4px;
}

.risk-description {
  font-size: 14px;
  color: #ffffff;
  margin-bottom: 8px;
}

.risk-mitigation {
  font-size: 13px;
  color: #a0aec0;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .suggestion-filters {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .filter-tabs {
    flex-wrap: wrap;
  }
  
  .filter-controls {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .optimization-suggestions {
    padding: 16px;
    gap: 16px;
  }
  
  .overview-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .prediction-summary {
    grid-template-columns: 1fr;
  }
  
  .suggestion-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>