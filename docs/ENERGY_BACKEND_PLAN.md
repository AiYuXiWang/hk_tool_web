# 能源驾驶舱后端开发方案

## 一、项目背景

根据前端需求，删除了能源管理驾驶舱（Dashboard）部分，保留并完善能源驾驶舱（Energy Cockpit）的后端实现。

## 二、前端功能分析

### 2.1 前端组件（EnergyCockpit.vue）

能源驾驶舱前端包含以下核心功能模块：

1. **控制栏**
   - 线路选择器
   - 车站选择器
   - 趋势周期选择器（24h/7d/30d）
   - 刷新按钮

2. **KPI看板**
   - 总能耗（total_kwh_today）
   - 实时功率（current_kw）
   - 峰值功率（peak_kw）
   - 监控车站数（station_count）
   - 同比变化（yoy_percent）
   - 环比变化（mom_percent）

3. **图表区域**
   - 实时能耗监测（折线图）
   - 历史数据趋势（柱状图）
   - 分类分项能耗（饼图）

4. **底部面板**
   - 设备监控
   - 智能节能建议

### 2.2 前端API调用

前端通过以下API接口获取数据：

```typescript
// frontend/src/api/energy.ts
- fetchRealtimeEnergy({ line, station_ip })
- fetchEnergyTrend({ line, station_ip, period })
- fetchEnergyKpi({ line, station_ip })
- fetchEnergyCompare({ line, station_ip, period })
- fetchEnergyClassification({ line, station_ip, period })
- fetchEnergySuggestions({ line, station_ip })
```

## 三、后端API设计

### 3.1 API路由前缀

所有能源相关API统一使用前缀：`/api/energy`

### 3.2 API接口列表

#### 3.2.1 KPI指标接口

**接口**: `GET /api/energy/kpi`

**请求参数**:
- `line` (可选): 地铁线路，如 M3、M8
- `station_ip` (可选): 站点IP
- `X-Station-Ip` (Header, 可选): 站点IP

**响应格式**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_kwh_today": 22449.7,
    "current_kw": 7062.8,
    "peak_kw": 9483.8,
    "station_count": 47,
    "update_time": "2025-10-23T03:54:03.000000"
  }
}
```

#### 3.2.2 实时能耗监测接口

**接口**: `GET /api/energy/realtime`

**请求参数**:
- `line` (可选): 地铁线路
- `station_ip` (可选): 站点IP
- `X-Station-Ip` (Header, 可选): 站点IP

**响应格式**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "series": [
      {
        "name": "振华路",
        "points": [116.3, 161.7, 125.5, ...]
      }
    ],
    "timestamps": ["16:54", "17:54", "18:54", ...],
    "update_time": "2025-10-23T03:54:03.000000"
  }
}
```

#### 3.2.3 历史趋势分析接口

**接口**: `GET /api/energy/trend`

**请求参数**:
- `line` (可选): 地铁线路
- `station_ip` (可选): 站点IP
- `period` (必需): 时间周期，可选值：24h, 7d, 30d
- `X-Station-Ip` (Header, 可选): 站点IP

**响应格式**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "values": [3500.0, 3200.5, 3800.3, ...],
    "timestamps": ["10-17", "10-18", "10-19", ...],
    "period": "7d",
    "station_count": 47,
    "update_time": "2025-10-23T03:54:04.000000"
  }
}
```

#### 3.2.4 同比环比对比接口

**接口**: `GET /api/energy/compare`

**请求参数**:
- `line` (可选): 地铁线路
- `station_ip` (可选): 站点IP
- `period` (必需): 对比周期，可选值：24h, 7d, 30d
- `X-Station-Ip` (Header, 可选): 站点IP

**响应格式**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "current_kwh": 172984.4,
    "yoy_percent": -12.3,
    "mom_percent": 5.6,
    "period": "7d",
    "station_count": 47,
    "update_time": "2025-10-23T03:54:04.000000"
  }
}
```

**说明**:
- `yoy_percent`: 同比变化百分比（Year-over-Year），正数表示增长，负数表示下降
- `mom_percent`: 环比变化百分比（Month-over-Month），正数表示增长，负数表示下降

#### 3.2.5 分类分项能耗接口

**接口**: `GET /api/energy/classification`

**请求参数**:
- `line` (可选): 地铁线路
- `station_ip` (可选): 站点IP
- `period` (必需): 统计周期，可选值：24h, 7d, 30d
- `X-Station-Ip` (Header, 可选): 站点IP

**响应格式**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "name": "冷机系统",
        "kwh": 71031.3,
        "percentage": 43.2
      },
      {
        "name": "水泵系统",
        "kwh": 27443.7,
        "percentage": 16.7
      }
    ],
    "total_kwh": 164500.0,
    "period": "24h",
    "station_count": 47,
    "update_time": "2025-10-23T03:54:04.000000"
  }
}
```

**设备分类**:
1. 冷机系统（35-45%）
2. 水泵系统（15-25%）
3. 冷却塔（8-15%）
4. 通风系统（10-18%）
5. 照明系统（5-12%）
6. 其他设备（3-8%）

#### 3.2.6 优化建议接口

**接口**: `GET /api/energy/suggestions`

**请求参数**:
- `X-Station-Ip` (Header, 可选): 站点IP

**响应格式**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "suggestions": [
      {
        "id": 1,
        "title": "冷机运行时间优化",
        "description": "建议在非高峰时段降低冷机运行功率，根据客流量动态调节",
        "priority": "high",
        "priority_text": "高优先级",
        "energy_saving": 2500,
        "cost_saving": 3750,
        "implementation_difficulty": "中等",
        "payback_period": "3个月"
      }
    ],
    "total_potential_saving": 5000,
    "total_cost_saving": 7500,
    "update_time": "2025-10-23T03:54:04.000000"
  }
}
```

## 四、技术实现

### 4.1 文件结构

```
backend/app/
├── api/
│   └── energy_dashboard.py    # 能源驾驶舱API路由
├── services/
│   └── energy_service.py      # 能源服务业务逻辑
├── models/
│   └── energy.py             # 能源数据模型
└── config/
    └── electricity_config.py # 电力配置管理
```

### 4.2 核心功能实现

#### 4.2.1 数据计算逻辑

1. **站点筛选**
   - 支持按线路（line）筛选
   - 支持按站点IP（station_ip）筛选
   - 未指定时返回所有站点数据

2. **能耗计算**
   - 基准功率：每站点150kW
   - 日均能耗：每站点3500kWh
   - 加入随机波动模拟真实场景

3. **时间序列生成**
   - 24h：24个数据点，按小时聚合
   - 7d：7个数据点，按天聚合
   - 30d：30个数据点，按天聚合

4. **同比环比计算**
   - 同比：与去年同期对比，模拟节能效果（通常为负值）
   - 环比：与上一周期对比，波动较小

### 4.3 中间件集成

所有API响应经过以下中间件处理：

1. **响应标准化中间件**: 统一响应格式为 `{code, message, data}`
2. **响应压缩中间件**: 压缩大型响应数据
3. **限流中间件**: `/api/energy` 路由限制为 200次/分钟
4. **日志中间件**: 记录所有请求和响应

## 五、测试方案

### 5.1 单元测试

测试文件：`tests/test_energy_api.py`

测试类：
1. `TestEnergyKpiAPI` - KPI接口测试
2. `TestEnergyRealtimeAPI` - 实时数据接口测试
3. `TestEnergyTrendAPI` - 趋势数据接口测试
4. `TestEnergyCompareAPI` - 对比数据接口测试
5. `TestEnergyClassificationAPI` - 分类能耗接口测试
6. `TestEnergySuggestionsAPI` - 优化建议接口测试
7. `TestEnergyIntegration` - 集成测试

### 5.2 测试覆盖

- 功能测试：验证所有API返回正确的数据结构
- 参数测试：验证不同参数组合的响应
- 数据一致性测试：验证计算结果的准确性
- 边界测试：验证异常参数的处理

### 5.3 运行测试

```bash
# 运行所有能源API测试
pytest tests/test_energy_api.py -v

# 运行特定测试类
pytest tests/test_energy_api.py::TestEnergyKpiAPI -v

# 查看测试覆盖率
pytest tests/test_energy_api.py --cov=backend/app/api/energy_dashboard
```

## 六、部署清单

### 6.1 代码变更

**删除的文件**:
- `frontend/src/views/EnergyDashboard.vue` - 能源管理驾驶舱页面

**修改的文件**:
- `frontend/src/router/index.js` - 删除dashboard路由
- `main.py` - 修改路由前缀从 `/api/energy-dashboard` 到 `/api/energy`
- `backend/app/api/energy_dashboard.py` - 新增3个API接口（kpi、compare、classification）

**新增的文件**:
- `tests/test_energy_api.py` - 能源API单元测试
- `docs/ENERGY_BACKEND_PLAN.md` - 后端开发方案文档

### 6.2 配置变更

**main.py 限流配置**:
```python
rate_limit_rules = {
    "/api/energy": "200/minute",  # 从 /api/energy-dashboard 改为 /api/energy
    ...
}
```

## 七、后续优化建议

### 7.1 数据持久化

当前实现使用模拟数据，建议后续：
1. 接入真实的能耗监测系统API
2. 建立能耗数据仓库
3. 实现历史数据缓存机制

### 7.2 性能优化

1. 实现Redis缓存，减少重复计算
2. 使用异步任务处理大数据量查询
3. 实现数据预聚合，提高查询效率

### 7.3 功能扩展

1. 支持自定义时间范围查询
2. 添加数据导出功能（Excel/CSV）
3. 实现告警阈值配置
4. 添加能效对比分析功能

### 7.4 监控告警

1. 实现API性能监控
2. 添加异常数据告警
3. 建立能耗异常检测机制

## 八、总结

本次开发完成了能源驾驶舱后端API的完整实现，包括：

✅ 删除了旧的Dashboard部分  
✅ 新增3个关键API接口（KPI、对比、分类能耗）  
✅ 修改2个现有接口（实时、趋势）以匹配前端需求  
✅ 编写17个单元测试，测试覆盖率达标  
✅ 更新路由配置和限流规则  
✅ 完善API文档和开发方案  

所有功能已经过测试验证，可以支持前端能源驾驶舱的正常运行。
