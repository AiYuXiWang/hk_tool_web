# 能源驾驶舱能耗数据修复说明

## 问题描述

能源驾驶舱显示的能耗信息与实际不一致。导出功能（`export_service.py`）使用以下配置和逻辑计算能耗：

- 读取站点配置中的 `data_codes` 数组（包含所有电表的数据代码）
- 读取站点配置中的 `object_codes` 数组（包含所有设备对象代码）
- 调用 `/data/selectHisData` API 获取**所有设备**的电表起码、止码
- 计算耗电量 = 电表止码 - 电表起码

但能源驾驶舱使用的是**功率估算**方式：`日能耗 = 当前功率 × 20小时`，导致数据不一致。

## 修复方案

### 1. 在 `RealtimeEnergyService` 中添加能耗计算方法

**文件**: `backend/app/services/realtime_energy_service.py`

#### 新增方法：`get_station_energy_consumption`

```python
async def get_station_energy_consumption(
    self, station: Dict[str, Any], start_time: datetime, end_time: datetime
) -> Optional[float]:
    """
    获取单个站点在指定时间段的能耗
    
    使用与export_service.py中process_data函数相同的逻辑：
    1. 获取时间段开始时的电表读数（起码）
    2. 获取时间段结束时的电表读数（止码）
    3. 计算差值作为耗电量
    """
```

该方法：
- 使用站点的 `data_codes` 和 `object_codes` 配置
- 调用 `/data/selectHisData` API 获取电表读数
- 按照 `export_service.py` 的 `process_data` 函数完全相同的逻辑计算能耗

#### 新增方法：`_calculate_consumption_from_meter_readings`

```python
async def _calculate_consumption_from_meter_readings(
    self,
    api_url: str,
    object_codes: List[str],
    data_codes: List[str],
    start_time: datetime,
    end_time: datetime,
    station_name: str = "未知站点"
) -> Optional[float]:
    """
    根据电表起码和止码计算能耗
    
    这个方法完全复制export_service.py中process_data函数的逻辑
    """
```

该方法实现了与 `export_service.py` 完全一致的逻辑：

1. **获取结束时间的电表读数（止码）**
   ```python
   end_obj = {
       "dataCodes": data_codes,
       "endTime": end_timestamp,
       "fill": "0",
       "funcName": "mean",
       "funcTime": "",
       "measurement": "realData",
       "objectCodes": object_codes,
       "startTime": end_timestamp - 10 * 60000  # 10分钟前
   }
   ```

2. **获取开始时间的电表读数（起码）**
   ```python
   start_obj = {
       "dataCodes": data_codes,
       "endTime": start_timestamp + 3 * 60000,  # 3分钟后
       "fill": "0",
       "funcName": "mean",
       "funcTime": "",
       "measurement": "realData",
       "objectCodes": object_codes,
       "startTime": start_timestamp
   }
   ```

3. **计算每个设备的能耗并汇总**
   ```python
   for data_code in data_codes:
       for object_code in object_codes:
           # 查找匹配的起始和结束读数
           start_entry = next(...)
           end_entry = next(...)
           
           if start_entry and end_entry:
               start_reading = float(start_values[0].get("value"))
               end_reading = float(end_values[0].get("value"))
               
               # 计算能耗差值（参考export_service.py第226-229行）
               if end_reading - start_reading >= -1:
                   consumption = end_reading - start_reading
                   total_consumption += consumption
               else:
                   # 电表异常
                   logger.warning("电表异常")
   ```

### 2. 修改 `EnergyService` 使用新的能耗计算方法

**文件**: `backend/app/services/energy_service.py`

#### 修改方法：`_get_station_overview_data`

**修改前**（使用功率估算）：
```python
# 计算日能耗（基于当前功率的估算，不再叠加随机因素）
daily_consumption = current_power * 20  # 假设平均运行20小时/天
```

**修改后**（使用电表读数计算）：
```python
# 计算日能耗：使用与export_service相同的逻辑
# 获取当天的实际能耗（从当天00:00到现在的电表读数差值）
now = datetime.now()
start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

daily_consumption = await self.realtime_service.get_station_energy_consumption(
    station, start_of_day, now
)

# 如果无法获取真实能耗，使用功率估算（向后兼容）
if daily_consumption is None:
    daily_consumption = current_power * 20  # 假设平均运行20小时/天
    if data_source == "real":
        data_source = "partial"  # 有功率但无能耗数据
        self.logger.warning(
            "⚠️ [%s] 能耗数据获取失败，使用功率估算: %.2f kWh",
            station_name,
            daily_consumption,
        )
else:
    self.logger.info(
        "✅ [%s] 成功获取真实日能耗: %.2f kWh (使用电表读数计算)",
        station_name,
        daily_consumption,
    )
```

## 修复验证

### 测试文件

创建了全面的测试文件 `tests/test_energy_dashboard_consumption_fix.py`，验证：

1. ✅ 新增的能耗计算方法存在
2. ✅ 使用正确的配置（`data_codes` 和 `object_codes` 数组）
3. ✅ 能耗计算逻辑与 `export_service.py` 一致
4. ✅ 电表读数解析和异常处理正确
5. ✅ API请求格式与 `export_service` 一致
6. ✅ 配置与导出服务保持一致

### 测试结果

```bash
$ python tests/test_energy_dashboard_consumption_fix.py

======================================================================
能源驾驶舱能耗计算修复测试
======================================================================

✓ 能耗计算方法存在

✓ 能耗计算使用正确的配置（data_codes和object_codes数组）
  - data_codes数量: 17
  - object_codes数量: 13

✓ 能耗计算逻辑正确: 130.0 kWh
  - 使用电表起码、止码差值计算
  - LSA1_28: 50 kWh (1050 - 1000)
  - LSA2_28: 80 kWh (2080 - 2000)

✓ API请求payload与export_service一致
  - 第一次请求: 结束时间窗口 1704109800000 ~ 1704110400000
  - 第二次请求: 开始时间窗口 1704067200000 ~ 1704067380000

✓ 电表读数解析和异常处理正确

✓ API请求格式与export_service一致
  - 结束时间窗口: endTime 往前10分钟
  - 开始时间窗口: startTime 往后3分钟
  - funcName: mean
  - fill: 0

✓ 苗岭路: 配置与export_service一致
  - data_codes数量: 17
  - object_codes数量: 13

✓ 振华路: 配置与export_service一致
  - data_codes数量: 24
  - object_codes数量: 9

✓ 五四广场: 配置与export_service一致
  - data_codes数量: 28
  - object_codes数量: 5

======================================================================
✅ 所有测试通过！
======================================================================

修复总结：
1. ✓ 能源驾驶舱使用data_codes和object_codes配置
2. ✓ 使用电表起码、止码差值计算能耗
3. ✓ 与export_service.py的process_data函数逻辑一致
4. ✓ 调用/data/selectHisData API获取数据
5. ✓ 正确处理电表异常情况
```

## 数据一致性保证

### 相同的配置源

- **导出功能**: 从 `config_electricity.line_configs[line][station]` 读取 `data_codes` 和 `object_codes`
- **能源驾驶舱**: 从同一配置源读取相同的 `data_codes` 和 `object_codes`

### 相同的API调用

两者都调用相同的API：`http://{station_ip}:9898/data/selectHisData`

### 相同的计算逻辑

1. 获取结束时间的电表读数（在结束时间前10分钟窗口内取平均）
2. 获取开始时间的电表读数（在开始时间后3分钟窗口内取平均）
3. 对每个 `data_code`，遍历所有 `object_code` 找到匹配的数据
4. 计算差值（止码 - 起码）作为耗电量
5. 如果差值 < -1，认为是电表异常，跳过该设备

## 向后兼容性

如果无法获取电表读数（例如：API不可达、配置缺失、数据为空），系统会回退到功率估算方式：

```python
if daily_consumption is None:
    daily_consumption = current_power * 20  # 假设平均运行20小时/天
```

这确保了在特殊情况下系统仍能正常运行，只是数据精度会降低。

## 配置要求

每个站点的配置必须包含：

```python
line_configs = {
    "M11": {
        "苗岭路": {
            "ip": "192.168.1.100",
            "station": "苗岭路",
            "data_codes": [  # 所有电表的数据代码
                "LSA1_28", "LSA2_28", "LT/A1_7", "LT/A2_7",
                # ... 更多设备
            ],
            "object_codes": [  # 所有设备对象代码
                "OBJ001", "OBJ002", "OBJ003",
                # ... 更多对象
            ],
            "data_list": [  # 设备详细信息
                {"p1": 1, "p2": "站端区域", "p3": "设备名称", ...},
                # ... 更多设备
            ],
            "jienengfeijieneng": {  # 仅用于节能状态查询
                "data_codes": ["JNFJN_1"],
                "object_codes": ["OBJ_JNFJN"]
            }
        }
    }
}
```

**重要说明**：
- `data_codes` 和 `object_codes` 数组用于能耗计算（获取所有设备的电表读数）
- `jienengfeijieneng` 节点仅用于节能状态查询（1个data_code表示节能/非节能状态）

## 日志记录

修复后的代码提供详细的日志记录，便于调试和监控：

```
📊 [苗岭路] 开始获取总览数据 - 设备数量: 17
📊 [苗岭路] 开始获取站点能耗 - 站点: 苗岭路, IP: 192.168.1.100, 线路: M11, 时间段: 2024-01-01 00:00:00 ~ 2024-01-01 12:00:00
📊 [苗岭路] 设备 LSA1_28/OBJ001: 起码=1000.00, 止码=1050.00, 耗电=50.00 kWh
📊 [苗岭路] 设备 LSA2_28/OBJ001: 起码=2000.00, 止码=2080.00, 耗电=80.00 kWh
📊 [苗岭路] 能耗计算完成 - 有效设备数: 17/17, 总能耗: 1250.00 kWh
✅ [苗岭路] 成功获取真实日能耗: 1250.00 kWh (使用电表读数计算)
✅ [苗岭路] 总览数据获取成功 - 当前功率: 85.50 kW, 日能耗: 1250.00 kWh
```

## 总结

通过本次修复，能源驾驶舱的能耗数据计算逻辑与导出功能完全一致，确保了数据的准确性和一致性。主要改进包括：

1. **数据源一致**: 都使用 `data_codes` 和 `object_codes` 配置
2. **API调用一致**: 都调用 `/data/selectHisData` 接口
3. **计算逻辑一致**: 都使用电表起码、止码差值计算能耗
4. **异常处理一致**: 都正确处理电表异常情况（差值 < -1）
5. **向后兼容**: 在无法获取真实数据时回退到功率估算

这确保了能源驾驶舱显示的能耗数据与导出报表中的数据完全一致。
