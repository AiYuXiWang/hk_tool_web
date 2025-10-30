# 能源驾驶舱滑动栏功能说明

## 功能概述

能源驾驶舱界面新增了三个可交互的滑动栏控件，用于动态调整数据展示参数和过滤条件，提供更灵活的数据查看和分析体验。

## 功能列表

### 1. 时间范围滑动栏

**功能描述：** 允许用户自定义查询历史数据的时间范围。

**参数范围：**
- 最小值：1 小时
- 最大值：72 小时
- 步进：1 小时
- 默认值：24 小时

**功能特性：**
- 拖动滑块即时调整时间范围
- 显示友好的时间格式（例如：1天、2天12小时）
- 自动刷新实时能耗和趋势数据
- 支持1-3天的历史数据回溯

**使用场景：**
- 查看最近几小时的短期能耗趋势
- 分析过去1-3天的中长期能耗变化
- 比较不同时间段的能耗模式

### 2. 刷新间隔滑动栏

**功能描述：** 动态调整数据自动刷新的时间间隔。

**参数范围：**
- 最小值：10 秒
- 最大值：300 秒（5 分钟）
- 步进：10 秒
- 默认值：30 秒

**功能特性：**
- 实时调整刷新频率
- 显示友好的时间格式（例如：30秒、1分钟、2分30秒）
- 立即生效，无需手动刷新
- 减少服务器负载，节省带宽

**使用场景：**
- 监控关键时段，设置更频繁的刷新（10-30秒）
- 日常监控，使用标准刷新间隔（30-60秒）
- 降低服务器压力，延长刷新间隔（1-5分钟）

### 3. 功率阈值滑动栏

**功能描述：** 根据设备功率筛选显示的设备列表。

**参数范围：**
- 最小值：0 W
- 最大值：5000 W
- 步进：100 W
- 默认值：0 W（不过滤）

**功能特性：**
- 实时筛选设备监控列表
- 只显示功率大于或等于阈值的设备
- 自动更新设备统计数据
- 帮助快速定位高功耗设备

**使用场景：**
- 筛选高功耗设备进行重点监控
- 过滤低功耗或待机设备
- 识别能耗异常的设备
- 优化设备列表显示，提高可读性

## 技术实现

### 前端实现

**组件位置：** `frontend/src/views/EnergyCockpit.vue`

**核心代码：**

```vue
<!-- 滑动栏控制面板 -->
<div class="slider-control-panel">
  <!-- 时间范围滑动栏 -->
  <div class="slider-group">
    <div class="slider-header">
      <label>时间范围: {{ timeRangeHours }}小时</label>
      <span class="slider-value">{{ timeRangeHours }}h</span>
    </div>
    <el-slider 
      v-model="timeRangeHours" 
      :min="1" 
      :max="72" 
      :step="1"
      :show-tooltip="true"
      :format-tooltip="formatTimeTooltip"
      @change="onTimeRangeChange"
    />
  </div>

  <!-- 刷新间隔滑动栏 -->
  <div class="slider-group">
    <div class="slider-header">
      <label>刷新间隔: {{ refreshIntervalSeconds }}秒</label>
      <span class="slider-value">{{ refreshIntervalSeconds }}s</span>
    </div>
    <el-slider 
      v-model="refreshIntervalSeconds" 
      :min="10" 
      :max="300" 
      :step="10"
      :show-tooltip="true"
      :format-tooltip="formatIntervalTooltip"
      @change="onRefreshIntervalChange"
    />
  </div>

  <!-- 功率阈值滑动栏 -->
  <div class="slider-group">
    <div class="slider-header">
      <label>功率阈值: {{ powerThreshold }} W</label>
      <span class="slider-value">{{ powerThreshold }} W</span>
    </div>
    <el-slider 
      v-model="powerThreshold" 
      :min="0" 
      :max="5000" 
      :step="100"
      :show-tooltip="true"
      :format-tooltip="formatPowerTooltip"
      @change="onPowerThresholdChange"
    />
  </div>
</div>
```

**响应式状态：**

```typescript
// 滑动栏状态
const timeRangeHours = ref<number>(24)
const refreshIntervalSeconds = ref<number>(30)
const powerThreshold = ref<number>(0)

// 工具提示格式化函数
const formatTimeTooltip = (value: number) => {
  if (value < 24) {
    return `${value} 小时`
  } else if (value === 24) {
    return '1 天'
  } else {
    const days = Math.floor(value / 24)
    const hours = value % 24
    return hours > 0 ? `${days} 天 ${hours} 小时` : `${days} 天`
  }
}

const formatIntervalTooltip = (value: number) => {
  if (value < 60) {
    return `${value} 秒`
  } else {
    const minutes = Math.floor(value / 60)
    const seconds = value % 60
    return seconds > 0 ? `${minutes} 分 ${seconds} 秒` : `${minutes} 分钟`
  }
}

const formatPowerTooltip = (value: number) => {
  return `≥ ${value} W`
}
```

**事件处理：**

```typescript
// 时间范围变化处理
const onTimeRangeChange = (value: number) => {
  console.log('时间范围变化:', value, '小时')
  toast.info(`时间范围已调整为 ${formatTimeTooltip(value)}`)
  refreshRealtime()
  refreshTrend()
}

// 刷新间隔变化处理
const onRefreshIntervalChange = (value: number) => {
  console.log('刷新间隔变化:', value, '秒')
  toast.info(`刷新间隔已调整为 ${formatIntervalTooltip(value)}`)
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
  startAutoRefresh()
}

// 功率阈值变化处理
const onPowerThresholdChange = (value: number) => {
  console.log('功率阈值变化:', value, 'W')
  toast.info(`功率阈值已设置为 ${value} W，设备列表已自动筛选`)
}
```

### 后端实现

**API 文件：** `backend/app/api/energy_dashboard.py`

#### 1. 实时能耗 API

```python
@router.get("/realtime")
async def get_realtime_data(
    line: Optional[str] = Query(None, description="地铁线路，如M3、M8等"),
    station_ip: Optional[str] = Query(None, description="站点IP"),
    hours: Optional[int] = Query(24, description="时间范围（小时数），默认24小时", ge=1, le=72),
    x_station_ip: Optional[str] = Header(None, alias="X-Station-Ip"),
    energy_service: EnergyService = Depends(get_energy_service),
):
    """
    获取实时能耗监控数据
    支持按线路或站点过滤，支持自定义时间范围（1-72小时）
    """
    # ... 实现代码
    return {
        "series": series,
        "timestamps": timestamps,
        "update_time": datetime.now().isoformat(),
        "time_range_hours": hours,
    }
```

#### 2. 设备监控 API

```python
@router.get("/equipment")
async def get_equipment_status(
    x_station_ip: Optional[str] = Header(None, alias="X-Station-Ip"),
    min_power: Optional[float] = Query(0, description="最小功率阈值(W)", ge=0),
    max_power: Optional[float] = Query(None, description="最大功率阈值(W)", ge=0),
):
    """
    获取设备运行状态数据
    支持按功率阈值筛选设备
    """
    # 根据功率阈值筛选设备
    filtered_device_powers = []
    for device_data in device_powers:
        power_w = device_data.get("power", 0)
        if min_power > 0 and power_w < min_power:
            continue
        if max_power and max_power > 0 and power_w > max_power:
            continue
        filtered_device_powers.append(device_data)
    
    # ... 返回筛选后的设备列表
```

### 样式设计

**设计理念：** 采用科技感设计风格，使用渐变色、发光效果和动画过渡。

**主要样式特点：**
1. 半透明背景 + 背景模糊（backdrop-filter）
2. 发光边框和动态渐变效果
3. 悬停时的视觉反馈
4. 流畅的过渡动画
5. 响应式布局，适配移动端

**关键 CSS 类：**
- `.slider-control-panel` - 滑动栏面板容器
- `.slider-group` - 单个滑动栏组
- `.slider-header` - 滑动栏标题区域
- `.slider-value` - 滑动栏数值显示

## 使用示例

### 场景 1：监控高峰时段能耗

1. 将时间范围设置为 **3 小时**，查看最近的短期趋势
2. 将刷新间隔设置为 **10 秒**，实时监控数据变化
3. 将功率阈值设置为 **2000 W**，关注高功耗设备

### 场景 2：日常能耗分析

1. 将时间范围设置为 **24 小时**，查看一天的能耗模式
2. 将刷新间隔设置为 **30 秒**，保持数据更新
3. 将功率阈值设置为 **0 W**，查看所有设备

### 场景 3：长期趋势对比

1. 将时间范围设置为 **72 小时**，分析3天的能耗变化
2. 将刷新间隔设置为 **120 秒**，减少数据刷新频率
3. 将功率阈值设置为 **1000 W**，筛选出主要能耗设备

## API 接口说明

### 实时能耗接口

**请求：**
```
GET /api/energy/realtime?line=M3&station_ip=10.188.100.1&hours=48
```

**响应：**
```json
{
  "series": [
    {
      "name": "站点1",
      "points": [100.5, 120.3, ...]
    }
  ],
  "timestamps": ["00:00", "01:00", ...],
  "update_time": "2024-01-15T10:30:00",
  "time_range_hours": 48
}
```

### 设备监控接口

**请求：**
```
GET /api/energy/equipment?min_power=1000&max_power=3000
Headers: X-Station-Ip: 10.188.100.1
```

**响应：**
```json
{
  "equipment_list": [
    {
      "id": "10.188.100.1_冷机1",
      "name": "冷机1",
      "location": "站点1",
      "power": 2500.5,
      "efficiency": 85.2,
      "status": "normal",
      "status_text": "正常运行"
    }
  ],
  "status_summary": {
    "normal": 5,
    "warning": 2,
    "error": 0
  },
  "update_time": "2024-01-15T10:30:00"
}
```

## 测试

### 单元测试

运行测试：
```bash
pytest tests/test_energy_slider_feature.py -v
```

### 测试覆盖

- ✅ 时间范围参数验证（1-72小时）
- ✅ 默认时间范围（24小时）
- ✅ 边界值测试（最小1小时，最大72小时）
- ✅ 无效参数处理（超出范围）
- ✅ 功率阈值筛选
- ✅ 最小功率阈值
- ✅ 默认不设置阈值

## 浏览器兼容性

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ⚠️ IE 不支持（已停止维护）

## 已知问题与限制

1. **时间范围限制：** 最大支持72小时（3天）的历史数据
2. **刷新间隔：** 过短的刷新间隔可能增加服务器负载
3. **功率阈值：** 只支持设置最小值，暂不支持同时设置最大值的前端界面（后端已支持）

## 未来优化方向

1. 添加预设时间范围快捷按钮（1h、6h、12h、24h、48h、72h）
2. 支持自定义起止时间的日期选择器
3. 添加功率范围双向滑动栏（最小值-最大值）
4. 保存用户偏好设置（本地存储或服务端）
5. 添加滑动栏数值输入框，支持精确输入
6. 导出当前筛选条件下的数据报表

## 版本历史

- **v1.0.0** (2024-01-15)
  - ✨ 新增时间范围滑动栏（1-72小时）
  - ✨ 新增刷新间隔滑动栏（10-300秒）
  - ✨ 新增功率阈值滑动栏（0-5000W）
  - 🎨 科技感UI设计
  - 📱 响应式布局支持
  - ✅ 后端API参数支持
  - 🧪 单元测试覆盖

## 相关文档

- [能源驾驶舱功能说明](./ENERGY_DASHBOARD.md)
- [API 接口文档](./API_REFERENCE.md)
- [前端组件开发指南](./FRONTEND_GUIDE.md)
- [后端服务开发指南](./BACKEND_GUIDE.md)
