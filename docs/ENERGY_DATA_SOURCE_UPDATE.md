# 能源驾驶舱数据来源更新说明

## 更新概述

能源驾驶舱后端的真实数据获取方式已更新，现在使用与 `export_service` 相同的API调用方式，确保数据一致性和可靠性。

## 主要变更

### 1. API端点变更

**之前**:
- 端口: 9801
- 接口: `/api/objectPointInfo/selectObjectPointValueByDataCode`
- 方式: 使用 `PlatformAPIService` 封装

**现在**:
- 端口: **9898**
- 接口: **/data/selectHisData**
- 方式: 直接使用 `requests` 库调用

### 2. 数据查询方式

参考 `export_service.py` 的成熟实现：

```python
# 查询最近10分钟的数据作为"实时"功率
obj = {
    "dataCodes": ["data_code1", "data_code2"],
    "objectCodes": ["object_code1", "object_code2"],
    "startTime": end_timestamp - 10 * 60000,  # 10分钟前
    "endTime": end_timestamp,
    "fill": "0",
    "funcName": "mean",  # 使用平均值
    "funcTime": "",
    "measurement": "realData"
}

response = requests.post(
    f"http://{station_ip}:9898/data/selectHisData",
    json=obj,
    timeout=5.0
)
```

### 3. 数据解析方式

**API响应格式**:
```json
{
  "data": [
    {
      "tags": {
        "dataCode": "LS01_26",
        "objectCode": "S_D_ZJ"
      },
      "values": [
        {
          "time": "2025-01-15 10:00:00.000",
          "value": 123.45
        },
        {
          "time": "2025-01-15 10:05:00.000",
          "value": 125.30
        }
      ]
    }
  ]
}
```

**解析逻辑**:
- 遍历返回的 `data` 数组
- 取每个数据项的 `values` 数组中的最后一个值（最新值）
- 累加所有有效数据点的值

### 4. 配置数据来源

从 `config_electricity.py` 获取站点配置：

```python
line_configs = {
    "M3": {
        "振华路": {
            "ip": "192.168.100.3",
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

## 优势

### 1. 一致性
- 与电耗数据导出功能使用完全相同的API
- 数据来源统一，避免差异

### 2. 可靠性
- 参考了经过实战验证的 `export_service` 实现
- 包含完善的超时处理和错误处理机制

### 3. 可维护性
- 不依赖 `PlatformAPIService` 和 Token 管理
- 直接使用 `requests` 库，代码更简洁

### 4. 准确性
- 查询最近10分钟的平均值作为实时功率
- 更加平滑和稳定，减少瞬时波动影响

## 代码文件

### 修改的文件

1. **backend/app/services/realtime_energy_service.py**
   - 完全重写数据查询逻辑
   - 使用 `/data/selectHisData` 接口
   - 端口从 9801 改为 9898

2. **backend/app/services/energy_service.py**
   - 继续使用 `RealtimeEnergyService` 获取真实数据
   - 保持原有的降级机制

3. **backend/app/api/energy_dashboard.py**
   - API端点逻辑保持不变
   - 数据来源自动切换到新的查询方式

4. **docs/ENERGY_REALDATA_INTEGRATION.md**
   - 更新API调用说明
   - 更新请求/响应格式示例

## 测试验证

所有测试均通过：

```bash
# 能源API测试
pytest tests/test_energy_api.py -v

# 前后端集成测试
pytest tests/test_frontend_backend_integration.py -v
```

## 使用方式

### 获取单个站点实时功率

```python
from backend.app.services.realtime_energy_service import RealtimeEnergyService

service = RealtimeEnergyService()
station = {
    "name": "振华路",
    "ip": "192.168.100.3",
    "line": "M3"
}

power = await service.get_station_realtime_power(station)
print(f"实时功率: {power} kW")
```

### 批量获取多个站点功率

```python
stations = [
    {"name": "振华路", "ip": "192.168.100.3", "line": "M3"},
    {"name": "五四广场", "ip": "192.168.100.4", "line": "M3"}
]

power_map = await service.get_multiple_stations_power(stations)
for station_name, power in power_map.items():
    print(f"{station_name}: {power} kW")
```

## 注意事项

1. **端口配置**: 确保站点的9898端口可访问
2. **配置完整性**: 需要在 `config_electricity.py` 中配置 `jienengfeijieneng` 字段
3. **超时设置**: 单次API请求超时为5秒，确保网络稳定
4. **数据时效性**: 查询最近10分钟的数据，确保数据新鲜度

## 未来改进方向

1. **历史数据接入**: 
   - 目前历史趋势仍使用估算
   - 可使用 `/data/selectHisData` 接口查询更长时间范围的数据

2. **缓存优化**:
   - 接入Redis缓存
   - 减少API调用频率

3. **数据聚合**:
   - 定时任务预计算常用指标
   - 提高响应速度

4. **监控告警**:
   - 根据真实功率数据触发告警
   - 异常功率值自动通知

## 参考资料

- `export_service.py`: 电耗数据导出服务（数据查询方式参考）
- `export_data.py`: 原始数据导出实现
- `config_electricity.py`: 站点和设备配置
