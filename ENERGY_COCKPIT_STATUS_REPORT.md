# 能源驾驶舱功能状态报告

## 任务概述

本次任务包含两个主要需求：
1. ✅ **能源驾驶舱界面增加滑动栏** - 已完成
2. ❌ **能源驾驶舱后端接入真实数据** - 需要实施

---

## 1. 滑动栏功能实现状态 ✅

### 1.1 前端实现（已完成）

**文件**: `frontend/src/views/EnergyCockpit.vue`

已成功添加两个滑动栏控件：

#### 时间范围滑动栏（行 28-41）
```vue
<div class="control-group slider-group">
  <label>时间范围 (小时):</label>
  <el-slider 
    v-model="timeRangeHours" 
    :min="1" 
    :max="72" 
    :step="1"
    :show-tooltip="true"
    :format-tooltip="formatTooltip"
    @change="onTimeRangeChange"
    class="time-range-slider"
  />
  <span class="slider-value">{{ timeRangeHours }}h</span>
</div>
```

**功能特性**：
- 范围：1-72 小时
- 默认值：12 小时
- 实时显示当前选择的小时数
- 滑动时自动刷新实时数据

#### 刷新间隔滑动栏（行 43-56）
```vue
<div class="control-group slider-group">
  <label>刷新间隔 (秒):</label>
  <el-slider 
    v-model="refreshInterval" 
    :min="10" 
    :max="300" 
    :step="10"
    :show-tooltip="true"
    :format-tooltip="formatIntervalTooltip"
    @change="onRefreshIntervalChange"
    class="refresh-interval-slider"
  />
  <span class="slider-value">{{ refreshInterval }}s</span>
</div>
```

**功能特性**：
- 范围：10-300 秒
- 默认值：30 秒
- 实时显示当前刷新间隔
- 滑动时自动调整自动刷新定时器

### 1.2 前端API调用（已完成）

**文件**: `frontend/src/api/energy.ts`

```typescript
export async function fetchRealtimeEnergy(params: { 
  line: string; 
  station_ip?: string; 
  hours?: number  // ✅ 已添加 hours 参数
}) {
  const { data } = await http.get('/api/energy/realtime', { params })
  return unwrap(data)
}
```

### 1.3 后端API支持（已完成）

**文件**: `backend/app/api/energy_dashboard.py`

```python
@router.get("/realtime")
async def get_realtime_data(
    line: Optional[str] = Query(None, description="地铁线路，如M3、M8等"),
    station_ip: Optional[str] = Query(None, description="站点IP"),
    hours: int = Query(12, description="时间范围（小时），1-72", ge=1, le=72),  # ✅ 已添加
    x_station_ip: Optional[str] = Header(None, alias="X-Station-Ip"),
):
    # 生成指定时间范围的时间戳
    now = datetime.now()
    timestamps = []
    for i in range(hours):  # ✅ 使用 hours 参数
        time_point = now - timedelta(hours=hours - 1 - i)
        timestamps.append(time_point.strftime("%H:%M"))
    
    # ...生成数据逻辑
    
    return {
        "series": series,
        "timestamps": timestamps,
        "hours": hours,  # ✅ 返回 hours 参数
        "update_time": datetime.now().isoformat(),
    }
```

**结论**: ✅ 滑动栏功能已完整实现，前后端联动正常工作。

---

## 2. 后端真实数据接入状态 ❌

### 2.1 当前数据来源分析

#### 问题：所有能源接口都在使用模拟数据

##### 接口 1: `/api/energy/realtime` - 实时能耗监测
**位置**: `backend/app/api/energy_dashboard.py:58-127`
```python
# ❌ 使用随机数生成模拟数据
base_power = random.uniform(100, 200)
points = []
for i in range(hours):
    hour = (now - timedelta(hours=hours - 1 - i)).hour
    if 6 <= hour <= 22:  # 白天功率较高
        power = base_power * random.uniform(0.8, 1.2)
    else:  # 夜间功率较低
        power = base_power * random.uniform(0.5, 0.8)
    points.append(round(power, 1))
```

##### 接口 2: `/api/energy/trend` - 历史趋势
**位置**: `backend/app/api/energy_dashboard.py:269-344`
```python
# ❌ 使用随机数生成模拟数据
trend_factor = 1.0 - (i / data_points) * 0.1
random_factor = random.uniform(0.85, 1.15)
value = base_value * trend_factor * random_factor
```

##### 接口 3: `/api/energy/kpi` - KPI指标
**位置**: `backend/app/api/energy_dashboard.py:493-571`
```python
# ❌ 使用随机数生成模拟数据
kpi_data = {
    "total_kwh_today": station_count * 400 + random.uniform(-100, 100),
    "current_kw": station_count * 150 + random.uniform(-50, 50),
    "peak_kw": station_count * 200 + random.uniform(-30, 30),
    "station_count": station_count,
}
```

##### 接口 4: `/api/energy/compare` - 同比环比
**位置**: `backend/app/api/energy_dashboard.py:573-638`
```python
# ❌ 使用随机数生成模拟数据
yoy_percent = random.uniform(-20, 20)
mom_percent = random.uniform(-15, 15)
```

##### 接口 5: `/api/energy/classification` - 分类分项能耗
**位置**: `backend/app/api/energy_dashboard.py:640-736`
```python
# ❌ 使用固定分类和随机能耗值
classifications = {
    "冷机系统": random.uniform(0.35, 0.45),
    "水泵系统": random.uniform(0.15, 0.25),
    "冷却塔": random.uniform(0.08, 0.15),
    # ...
}
```

##### 接口 6: `/api/energy/equipment` - 设备状态
**位置**: `backend/app/api/energy_dashboard.py:346-415`
```python
# ❌ 使用随机数模拟设备状态
status_rand = random.random()
if status_rand > 0.9:
    status = "error"
elif status_rand > 0.7:
    status = "warning"
else:
    status = "normal"
```

##### 接口 7: `/api/energy/suggestions` - 优化建议
**位置**: `backend/app/api/energy_dashboard.py:417-491`
```python
# ❌ 使用硬编码的固定建议列表
suggestions = [
    {
        "id": 1,
        "title": "冷机运行时间优化",
        "description": "建议在非高峰时段降低冷机运行功率...",
        # ...
    },
    # ...
]
```

### 2.2 可用的真实数据源

项目中已经存在真实数据接口：

#### PlatformAPIService (control_service.py)
```python
class PlatformAPIService:
    """环控平台API服务类"""
    
    def __init__(self):
        self.base_url = "http://192.168.100.3"
        self.select_url = "http://192.168.100.3:9801/api/objectPointInfo/selectObjectPointValueByDataCode"
        
    def get_runtime_token(self) -> str:
        """获取运行时token"""
        # Token缓存和刷新逻辑
        
    def batch_query_realtime(self, station_ip, point_codes, object_codes):
        """批量查询实时点位数据"""
        # 调用真实平台API
```

#### ElectricityConfig (config_electricity.py)
包含完整的站点和设备配置：
- 13376行配置数据
- 包含所有地铁线路（M3, M8等）
- 每个站点的设备列表、IP、对象代码、数据代码
- 设备的额定功率、CT变比等信息

**示例配置**：
```python
"M3": {
    "振华路": {
        "ip": "192.168.100.3",
        "station": "振华路",
        "jienengfeijieneng": {"object_codes": ["PT_SDZ"], "data_codes": ["539"]},
        "data_list": [
            {
                "p1": "1",
                "p2": "B",
                "p3": "冷机LS01电表",
                "p5": "137KW",
                "p7": "400/5",  # CT变比
                # ...
            },
            # ...更多设备
        ]
    },
    # ...更多站点
}
```

### 2.3 需要实施的改造方案

#### 方案概述
将能源驾驶舱后端从模拟数据切换到真实的平台API数据。

#### 改造步骤

##### 步骤 1: 集成 PlatformAPIService
在 `EnergyService` 中注入平台API服务，用于查询真实点位数据。

##### 步骤 2: 实现真实数据查询
- 查询电表的实时功率值（通过点位代码）
- 查询电表的累计能耗值
- 使用CT变比进行功率和能耗计算

##### 步骤 3: 实现数据聚合
- 将单个设备数据聚合为站点级数据
- 将站点数据聚合为线路级数据
- 计算总能耗、平均功率、峰值功率等指标

##### 步骤 4: 实现时间序列数据
- 通过定期采样构建历史曲线
- 实现Redis缓存存储历史数据点
- 支持不同时间粒度的查询（小时/天）

##### 步骤 5: 实现分类能耗统计
- 根据设备名称（"冷机"、"水泵"、"冷却塔"等）进行分类
- 按分类汇总能耗数据
- 计算各分类的百分比

##### 步骤 6: 实现同比环比计算
- 从历史数据库查询去年同期数据
- 从历史数据库查询上一周期数据
- 计算变化百分比

##### 步骤 7: 实现智能建议生成
- 基于实时能耗数据分析
- 识别能耗异常的设备
- 基于规则引擎生成优化建议

#### 技术依赖

1. **PlatformAPIService**: 已存在，用于查询实时点位数据
2. **ElectricityConfig**: 已存在，提供设备配置信息
3. **Redis**: 需要配置，用于缓存历史时间序列数据
4. **MySQL**: 已存在（audit_service使用），可扩展用于存储能耗历史数据

#### 数据计算公式

```
实际功率(kW) = 点位读数 × CT变比 / 1000
实际能耗(kWh) = Σ(实时功率 × 采样间隔)
设备总功率 = Σ(各设备实际功率)
站点总能耗 = Σ(各设备实际能耗)
```

---

## 3. 实施优先级建议

### 高优先级（立即实施）
1. ✅ **实时能耗监测** (`/api/energy/realtime`)
   - 直接查询电表点位获取实时功率
   - 影响最大，用户最关注
   
2. ✅ **KPI指标** (`/api/energy/kpi`)
   - 计算总能耗、当前功率、峰值功率
   - 驾驶舱核心指标

### 中优先级（短期实施）
3. **历史趋势** (`/api/energy/trend`)
   - 需要历史数据采集机制
   - 可先使用近期采样数据

4. **分类分项能耗** (`/api/energy/classification`)
   - 基于设备名称分类
   - 聚合各分类能耗

### 低优先级（长期优化）
5. **同比环比对比** (`/api/energy/compare`)
   - 需要长期历史数据积累
   - 可保留模拟数据过渡

6. **设备状态监控** (`/api/energy/equipment`)
   - 需要设备状态点位映射
   - 逐步完善

7. **优化建议** (`/api/energy/suggestions`)
   - 需要规则引擎和AI分析
   - 作为长期功能演进

---

## 4. 风险和限制

### 数据可用性风险
- ⚠️ **点位数据完整性**: 部分站点可能缺失电表点位配置
- ⚠️ **网络连通性**: 平台API可能不稳定或超时
- ⚠️ **Token失效**: 需要健壮的Token刷新机制

### 性能风险
- ⚠️ **查询延迟**: 批量查询多个站点可能耗时较长
- ⚠️ **并发压力**: 多用户同时访问可能导致平台API压力
- ⚠️ **缓存策略**: 需要合理的缓存机制避免频繁查询

### 数据准确性风险
- ⚠️ **CT变比配置**: 配置错误会导致计算结果偏差
- ⚠️ **设备分类**: 自动分类可能不准确
- ⚠️ **历史数据**: 初期缺少历史数据

---

## 5. 推荐实施路径

### 阶段一：核心接口改造（1-2天）
1. 修改 `/api/energy/realtime` 接入真实功率数据
2. 修改 `/api/energy/kpi` 接入真实KPI计算

### 阶段二：历史数据支持（2-3天）
3. 实现Redis历史数据缓存
4. 修改 `/api/energy/trend` 使用历史数据
5. 修改 `/api/energy/classification` 使用真实分类

### 阶段三：高级功能（3-5天）
6. 实现历史数据库持久化
7. 实现同比环比计算
8. 实现智能建议引擎

---

## 6. 总结

| 功能模块 | 状态 | 数据来源 | 优先级 |
|---------|------|---------|--------|
| 滑动栏控件 | ✅ 已完成 | 前端交互 | - |
| 实时能耗监测 | ❌ 模拟数据 | random | 高 |
| KPI指标 | ❌ 模拟数据 | random | 高 |
| 历史趋势 | ❌ 模拟数据 | random | 中 |
| 分类分项能耗 | ❌ 模拟数据 | random | 中 |
| 同比环比对比 | ❌ 模拟数据 | random | 低 |
| 设备状态监控 | ❌ 模拟数据 | random | 低 |
| 优化建议 | ❌ 硬编码 | 固定列表 | 低 |

**关键发现**：
- ✅ 滑动栏功能已完整实现，工作正常
- ❌ 所有能源接口目前都使用模拟数据
- ✅ 项目已具备真实数据接口（PlatformAPIService）
- ✅ 配置数据完整（ElectricityConfig）
- ⚠️ 需要实施真实数据接入改造

**下一步行动**：
1. 确认是否立即开始真实数据接入改造
2. 选择实施的优先级接口
3. 准备必要的基础设施（Redis、历史数据库）
4. 逐步迁移各个接口到真实数据
