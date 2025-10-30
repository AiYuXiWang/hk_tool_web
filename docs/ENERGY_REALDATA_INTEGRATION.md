# 能源驾驶舱真实数据接入文档

## 概述

能源驾驶舱后端已接入真实数据源，通过平台API获取实时能耗数据，替代了原有的模拟数据生成逻辑。

## 核心改进

### 1. 新增 RealtimeEnergyService

**文件路径**: `backend/app/services/realtime_energy_service.py`

**功能**:
- 从平台API获取站点实时功率数据
- 支持批量查询多个站点
- 获取站点所有设备的功率详情
- 自动处理数据解析和错误

**主要方法**:

```python
# 获取单个站点的实时总功率
async def get_station_realtime_power(station: Dict[str, Any]) -> Optional[float]

# 批量获取多个站点的实时功率
async def get_multiple_stations_power(stations: List[Dict[str, Any]]) -> Dict[str, Optional[float]]

# 获取站点所有设备的实时功率
async def get_station_device_powers(station: Dict[str, Any]) -> List[Dict[str, Any]]
```

### 2. 修改 EnergyService

**文件路径**: `backend/app/services/energy_service.py`

**改进点**:
- 集成 `RealtimeEnergyService` 获取真实功率数据
- 保留降级机制：真实数据获取失败时使用估算值
- 优化数据计算逻辑，基于真实功率进行能耗估算

**修改的方法**:
- `_get_station_overview_data`: 使用真实功率数据
- `_get_station_realtime_data`: 使用真实功率数据

### 3. 更新 API 端点

**文件路径**: `backend/app/api/energy_dashboard.py`

**修改的端点**:

#### `/api/energy/realtime`
- 使用 `EnergyService.get_realtime_data()` 获取真实数据
- 返回格式保持不变，保证前端兼容性

#### `/api/energy/equipment`
- 使用 `RealtimeEnergyService.get_station_device_powers()` 获取设备功率
- 根据真实功率判断设备状态（在线/离线/效率偏低）

#### `/api/energy/overview`
- 使用 `EnergyService.get_energy_overview()` 获取总览数据
- 基于真实功率计算能耗趋势

## 数据来源

### 平台API

使用 `PlatformAPIService` 调用环控平台的实时数据接口：

```
POST http://{station_ip}:9801/api/objectPointInfo/selectObjectPointValueByDataCode
```

**请求参数**:
- `object_code`: 对象代码（从配置中获取）
- `data_code`: 数据代码（从配置中获取）
- `token`: 认证令牌

**响应格式**:
```json
{
  "code": 1,
  "data": [{
    "property_num_value": 123.45,
    "property_value": "123.45"
  }]
}
```

### 配置文件

站点和设备配置来自 `config_electricity.py`:

```python
line_configs = {
    "M3": {
        "振华路": {
            "ip": "192.168.100.3",
            "station": "振华路",
            "jienengfeijieneng": {
                "object_codes": ["PT_SDZ"],
                "data_codes": ["539"]
            },
            "object_codes": ["S_D_ZJ", "S_X_ZJ", ...],
            "data_codes": ["LS01_26", "LS02_26", ...]
        }
    }
}
```

## 数据流程

```
前端请求
    ↓
API 端点 (energy_dashboard.py)
    ↓
EnergyService (energy_service.py)
    ↓
RealtimeEnergyService (realtime_energy_service.py)
    ↓
PlatformAPIService (control_service.py)
    ↓
环控平台 API
    ↓
返回实时功率数据
```

## 容错机制

### 1. 数据获取失败降级
如果平台API调用失败，系统会：
- 记录警告日志
- 使用基于设备数量的估算值
- 保证服务不中断

### 2. Token 自动刷新
- 使用缓存机制，避免频繁登录
- Token过期时自动重新登录
- 登录失败时使用兜底Token

### 3. 并发控制
- 使用 `asyncio.gather` 并行查询多个站点
- 异常捕获，单个站点失败不影响其他站点
- 返回异常标记，便于问题定位

## 性能优化

### 1. 缓存策略
```python
@service_method(cache_timeout=60)  # 能源总览缓存60秒
@service_method(cache_timeout=30)  # 实时数据缓存30秒
@service_method(cache_timeout=300) # 历史趋势缓存5分钟
```

### 2. 查询限制
- 设备功率查询限制在20个以内
- 站点列表限制在5个以内（显示）
- 避免过多的API请求

### 3. 异步并发
- 使用异步IO提高响应速度
- 并行查询多个站点和设备
- 减少等待时间

## 数据格式

### 站点功率数据
```python
{
    "station_ip": "192.168.100.3",
    "station_name": "振华路",
    "current_power": 1234.5,  # kW，真实值
    "daily_consumption": 24690.0,  # kWh，基于功率估算
    "device_count": 24
}
```

### 设备功率数据
```python
{
    "device_name": "冷机LS01",
    "data_code": "LS01_26",
    "object_code": "S_D_ZJ",
    "power": 137.8,  # kW，真实值
    "status": "online"  # online/offline
}
```

## 测试验证

### API 测试
```bash
# 测试能源总览
curl http://localhost:8000/api/energy/overview

# 测试实时数据
curl http://localhost:8000/api/energy/realtime

# 测试设备状态
curl http://localhost:8000/api/energy/equipment
```

### 单元测试
```bash
# 运行能源API测试
pytest tests/test_energy_api.py -v
```

## 注意事项

1. **网络连接**: 确保后端服务器能够访问各站点的环控平台API（端口9801）

2. **认证配置**: 需要正确配置环境变量：
   ```bash
   HK_LOGIN_USER=aitest
   HK_LOGIN_PWD=your_password
   ```

3. **数据准确性**: 
   - 实时功率为当前时刻的瞬时值
   - 日能耗为基于当前功率的估算值
   - 历史数据暂时仍使用估算模式（可后续接入历史数据库）

4. **错误处理**: 
   - 查看日志文件了解API调用详情
   - 关注 WARNING 级别日志，了解降级情况

## 后续优化建议

1. **历史数据接入**: 
   - 对接MySQL历史数据库
   - 提供真实的历史趋势分析

2. **数据缓存优化**:
   - 接入Redis缓存
   - 减少API调用频率

3. **数据聚合**:
   - 定时任务定期聚合数据
   - 预计算常用指标

4. **告警集成**:
   - 根据真实功率数据触发告警
   - 异常功率值自动通知

5. **数据可视化增强**:
   - 实时功率曲线
   - 设备能效排名
   - 能耗趋势预测
