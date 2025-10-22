# T045: 集成历史数据组件到 EnergyCockpit.vue

**目标**: 将新创建的 TimeRangeSelector、HistoryStats 组件集成到主页面
**预计时间**: 30-45分钟

---

## 步骤 1: 导入新组件

在 `frontend/src/views/EnergyCockpit.vue` 的 `<script setup>` 部分添加导入:

```typescript
// 在现有导入后添加
import TimeRangeSelector from '@/components/cockpit/TimeRangeSelector.vue'
import HistoryStats from '@/components/cockpit/HistoryStats.vue'
import { useEnergyStore } from '@/stores/energy'
```

---

## 步骤 2: 初始化 Store 和状态

```typescript
const energyStore = useEnergyStore()
const currentHistoryRange = ref('24h') // 当前历史数据时间范围
```

---

## 步骤 3: 修改现有的 trendPeriod 选择器

**选项 A: 替换为 TimeRangeSelector 组件**

找到现有的趋势周期选择器代码（约21-26行）:

```vue
<!-- 旧代码 -->
<div class="control-group">
  <label>趋势周期:</label>
  <el-select v-model="trendPeriod" placeholder="趋势周期" size="small" @change="refreshTrend">
    <el-option label="24小时" value="24h" />
    <el-option label="7天" value="7d" />
    <el-option label="30天" value="30d" />
  </el-select>
</div>
```

**替换为**:

```vue
<!-- 新代码 -->
<div class="control-group time-range-group">
  <label>趋势周期:</label>
  <TimeRangeSelector 
    v-model="trendPeriod" 
    :ranges="[
      { label: '24小时', value: '24h' },
      { label: '7天', value: '7d' },
      { label: '30天', value: '30d' },
      { label: '90天', value: '90d' }
    ]"
    @change="onHistoryRangeChange"
  />
</div>
```

**选项 B: 保留现有选择器，添加90d选项**

```vue
<div class="control-group">
  <label>趋势周期:</label>
  <el-select v-model="trendPeriod" placeholder="趋势周期" size="small" @change="refreshTrend">
    <el-option label="24小时" value="24h" />
    <el-option label="7天" value="7d" />
    <el-option label="30天" value="30d" />
    <el-option label="90天" value="90d" /> <!-- 新增 -->
  </el-select>
</div>
```

---

## 步骤 4: 添加历史统计区域

在图表区域前（约106行）添加历史统计部分:

```vue
<!-- 历史数据统计区域 -->
<div v-if="energyStore.historyStatistics && energyStore.historyStatistics.total > 0" class="history-stats-section">
  <div class="section-header">
    <h3 class="section-title">历史数据统计 - {{ getTrendPeriodLabel(trendPeriod) }}</h3>
    <span class="data-timestamp">数据更新: {{ new Date().toLocaleString('zh-CN') }}</span>
  </div>
  
  <HistoryStats 
    :statistics="energyStore.historyStatistics"
    :time-range="trendPeriod"
    :show-data-quality="true"
  />
</div>
```

---

## 步骤 5: 添加加载状态

在 HistoryStats 前添加骨架屏:

```vue
<div v-if="energyStore.isLoadingHistory" class="history-stats-skeleton">
  <div class="skeleton-card" v-for="i in 5" :key="i">
    <div class="skeleton-header"></div>
    <div class="skeleton-value"></div>
    <div class="skeleton-bar"></div>
  </div>
</div>
```

---

## 步骤 6: 实现历史数据加载逻辑

修改 `refreshTrend` 函数使用缓存:

```typescript
async function refreshTrend() {
  if (!selectedLine.value || !selectedStation.value) return
  
  energyStore.isLoadingHistory = true
  
  try {
    // 使用缓存加载历史数据
    const cached = await energyStore.fetchHistoryWithCache(
      selectedStation.value,
      trendPeriod.value,
      selectedLine.value,
      fetchEnergyTrend
    )
    
    // 如果有缓存数据，同时更新图表
    if (cached && cached.values) {
      historyData.value = [{
        type: 'bar',
        title: '历史趋势',
        data: cached.values || [],
        xAxis: cached.timestamps || [],
        series: [{
          name: '耗电量',
          type: 'bar',
          data: cached.values || [],
          color: '#67C23A'
        }]
      }]
      
      // 更新统计信息
      if (cached.statistics) {
        energyStore.updateHistoryStatistics(cached.statistics)
      }
    }
  } catch (error) {
    console.error('加载历史趋势失败:', error)
    ElMessage.warning('趋势数据获取失败')
    
    // 降级：显示示例数据（原有逻辑）
    historyData.value = [{
      type: 'bar',
      title: '历史趋势',
      data: Array.from({ length: 24 }, () => Math.round(50 + Math.random() * 30)),
      xAxis: Array.from({ length: 24 }, (_, i) => `${i}:00`),
      series: [{
        name: '耗电量',
        type: 'bar',
        data: Array.from({ length: 24 }, () => Math.round(50 + Math.random() * 30)),
        color: '#67C23A'
      }]
    }]
  } finally {
    energyStore.isLoadingHistory = false
  }
}
```

---

## 步骤 7: 添加时间范围变更处理

```typescript
function onHistoryRangeChange(newRange: string) {
  console.log(`时间范围切换: ${trendPeriod.value} → ${newRange}`)
  trendPeriod.value = newRange
  refreshTrend()
}

function getTrendPeriodLabel(period: string): string {
  const labels: Record<string, string> = {
    '24h': '24小时',
    '7d': '7天',
    '30d': '30天',
    '90d': '90天'
  }
  return labels[period] || period
}
```

---

## 步骤 8: 添加样式

在 `<style scoped>` 中添加:

```css
/* 历史统计区域 */
.history-stats-section {
  margin: var(--spacing-lg, 24px) 0;
  padding: var(--spacing-md, 16px);
  background: rgba(14, 23, 51, 0.4);
  border-radius: var(--border-radius-lg, 12px);
  border: 1px solid rgba(0, 212, 255, 0.2);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md, 16px);
  padding-bottom: var(--spacing-sm, 12px);
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
}

.section-title {
  margin: 0;
  font-size: var(--font-size-lg, 18px);
  font-weight: var(--font-weight-semibold, 600);
  color: var(--color-text-primary, #ffffff);
  background: linear-gradient(90deg, #00D4FF, #00FFCC);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.data-timestamp {
  font-size: var(--font-size-xs, 12px);
  color: var(--color-text-tertiary, rgba(255, 255, 255, 0.6));
}

/* 时间范围选择器组 */
.time-range-group {
  flex-direction: column;
  align-items: flex-start;
  gap: var(--spacing-xs, 8px);
  min-width: auto;
}

.time-range-group label {
  margin-bottom: var(--spacing-xs, 4px);
}

/* 骨架屏 */
.history-stats-skeleton {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--spacing-md, 16px);
  margin-bottom: var(--spacing-lg, 24px);
}

.skeleton-card {
  padding: var(--spacing-md, 16px);
  background: rgba(14, 23, 51, 0.65);
  border: 1px solid rgba(0, 212, 255, 0.35);
  border-radius: var(--border-radius-lg, 12px);
  animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.skeleton-header {
  width: 60%;
  height: 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  margin-bottom: var(--spacing-sm, 12px);
}

.skeleton-value {
  width: 80%;
  height: 32px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 4px;
  margin-bottom: var(--spacing-sm, 12px);
}

.skeleton-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 4px;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm, 12px);
  }
  
  .time-range-group {
    width: 100%;
  }
}
```

---

## 步骤 9: 测试缓存功能

### 测试步骤:
1. 打开浏览器开发者工具 Console
2. 打开能源驾驶舱页面
3. 点击"7天"按钮
4. 观察 Console 输出: `[Cache Miss] 从API加载数据: {station}_7d_{line}`
5. 点击其他时间范围，再点回"7天"
6. 观察 Console 输出: `[Cache Hit] 使用缓存数据: {station}_7d_{line}`
7. 等待30分钟后再次点击"7天"，应该看到 `[Cache Miss]`（缓存过期）

### 期望结果:
- ✅ 首次加载显示骨架屏 → 2秒内显示数据
- ✅ 切换回已加载的时间范围 → 立即显示（无网络请求）
- ✅ HistoryStats 显示正确的统计数据
- ✅ 数据质量指示器显示

---

## 步骤 10: 清理站点切换时的缓存

在 `onLineChange` 和 `refreshAll` 中添加缓存清理:

```typescript
function onLineChange() {
  const stations = stationsOfSelectedLine.value
  selectedStation.value = stations.length > 0 ? stations[0].station_ip : ''
  
  // 清理历史数据缓存（站点变更）
  energyStore.clearHistoryCache()
  
  refreshAll()
}
```

---

## 验收清单

完成集成后，确认以下功能:

- [ ] ✅ TimeRangeSelector 显示正常（4个按钮或下拉菜单）
- [ ] ✅ 选中状态高亮正确
- [ ] ✅ 点击时间范围，HistoryStats 显示对应数据
- [ ] ✅ 统计数据正确（总能耗/平均/峰值/最小值）
- [ ] ✅ 数据质量指示器正常工作
- [ ] ✅ 缓存功能工作（Console日志）
- [ ] ✅ 站点切换时缓存被清空
- [ ] ✅ 骨架屏加载动画流畅
- [ ] ✅ 响应式布局正常 (desktop/tablet/mobile)
- [ ] ✅ 无控制台错误

---

## 可选优化

### 添加 Vue Transition 动画:

```vue
<Transition name="fade" mode="out-in">
  <div v-if="energyStore.isLoadingHistory" class="history-stats-skeleton" key="skeleton">
    <!-- 骨架屏 -->
  </div>
  <HistoryStats 
    v-else-if="energyStore.historyStatistics"
    :statistics="energyStore.historyStatistics"
    :time-range="trendPeriod"
    key="stats"
  />
</Transition>
```

```css
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
```

---

## 故障排查

### 问题1: 组件导入失败
**错误**: `Cannot find module '@/components/cockpit/TimeRangeSelector.vue'`
**解决**: 检查文件路径和 `@/` 别名配置

### 问题2: Store 方法未定义
**错误**: `energyStore.fetchHistoryWithCache is not a function`
**解决**: 确认 `energy.ts` store 已正确导出新方法

### 问题3: 缓存未生效
**症状**: 每次切换都发起网络请求
**解决**: 
1. 检查 Console 日志是否有缓存相关输出
2. 检查 `DataCache` 是否正确初始化
3. 检查缓存键是否一致

### 问题4: 统计数据为0
**症状**: HistoryStats 显示全为0
**解决**:
1. 检查 API 返回的数据格式
2. 检查 `calculateStatistics` 是否正确处理数据
3. 添加 Console.log 调试数据流

---

## 完成后

完成集成后，运行以下命令:

```bash
# 1. 构建验证
npm run build

# 2. 提交代码
git add .
git commit -m "feat: 集成历史数据统计组件 (T045)

- 添加 TimeRangeSelector 时间范围选择器
- 集成 HistoryStats 统计卡片
- 实现30分钟缓存机制
- 添加骨架屏加载状态
- 支持 24h/7d/30d/90d 时间维度
"

# 3. 运行验收测试 (T049)
# 参考 ACCEPTANCE_T049.md 执行完整测试流程
```

---

**预计完成时间**: 30-45分钟
**前置条件**: Phase 4 组件已创建 (T042-T044, T046, T048 ✅)
**后续任务**: T049 验收测试
