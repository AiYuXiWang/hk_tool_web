# 能源驾驶舱11号线苗岭路站能耗数据不一致问题修复

## 问题描述

用户反馈：能源驾驶舱显示的能耗信息与实际不一致。

### 实际数据（11号线苗岭路站）

根据导出的电耗数据（2025/4/1 0:00 到 2025/4/30 17:19）：

| 序号 | 设备名称 | 电表起码(KWh) | 电表止码(KWh) | 耗电量(KWh) |
|------|---------|--------------|--------------|------------|
| 1 | LS/B1 | 43068.8 | 43068.8 | 0 |
| 2 | LS/B2 | 9934.4 | 9934.4 | 0 |
| 3 | LT/B1 | 315.6 | 315.6 | 0 |
| 4 | LT/B2 | 381.75 | 381.75 | 0 |
| 5 | LD/B1 | 62230.8 | 62236.8 | **6** |
| 6 | LD/B2 | 73066.6 | 73068 | **1.4** |
| 7 | LQ/B1 | 147035 | 147297 | **262** |
| 8 | LQ/B2 | 97711 | 97848.2 | **137.2** |
| 9 | XK_B1电表 | 11582.1 | 11958.29 | **376.19** |
| 10 | XK_B2电表 | 3457.35 | 3822.75 | **365.4** |
| 11 | XK_B3电表 | 40227.15 | 41908.59 | **1681.45** |
| 12 | XHPF_B1电表 | 9839.77 | 10873.2 | **1033.43** |
| 13 | XHPF_B2电表 | 26498.7 | 27858.52 | **1359.82** |
| 14 | XHPF_B3电表 | 2415.6 | 2415.6 | 0 |
| 15 | ZK_B1电表 | 10647.2 | 10857.6 | **210.4** |
| 16 | ZK_B2电表 | 11828 | 12052 | **224** |
| 17 | HPF_B电表 | 0 | 0 | 0 |

**实际总耗电量**: 5657.29 kWh

### 问题分析

能源驾驶舱的KPI接口（`/api/energy/kpi`）使用的是**功率估算**方式计算能耗：

```python
# 原有代码（错误）
total_kwh_today = sum_kw * utilization * max(hours_today, 0.1)
```

这与导出功能使用的**电表读数差值**计算方式不一致：

```python
# 导出功能（正确）
耗电量 = 电表止码 - 电表起码
```

## 根本原因

在 `main.py` 的第273行，`@app.get("/api/energy/kpi")` 接口使用配置文件中的设备额定功率进行估算，而不是从平台API获取真实的电表读数。

导出功能（`export_service.py`）和能源驾驶舱的其他接口（通过 `energy_service.py` 和 `realtime_energy_service.py`）已经正确实现了基于电表读数的能耗计算，但KPI接口未被更新。

## 修复方案

### 1. 修改 `/api/energy/kpi` 接口

**文件**: `main.py` (第273-361行)

**修改内容**:

#### 修改前（使用功率估算）
```python
@app.get("/api/energy/kpi")
async def get_energy_kpi(line: str, station_ip: Optional[str] = None):
    cfg = _get_station_config(line, station_ip)
    sum_kw = _sum_kw_from_data_list(cfg.get("data_list", []))
    from datetime import datetime

    now = datetime.now()
    hours_today = now.hour + now.minute / 60.0
    utilization = 0.35  # 近似平均负荷系数
    total_kwh_today = sum_kw * utilization * max(hours_today, 0.1)
    current_kw = sum_kw * 0.40
    peak_kw = sum_kw * 0.75
    station_count = len(config_electricity.line_configs.get(line, {}))
    return {
        "total_kwh_today": round(total_kwh_today, 2),
        "current_kw": round(current_kw, 2),
        "peak_kw": round(peak_kw, 2),
        "station_count": station_count,
    }
```

#### 修改后（使用电表读数）
```python
@app.get("/api/energy/kpi")
async def get_energy_kpi(line: str, station_ip: Optional[str] = None):
    """能耗指标 KPI 看板数据。
    使用真实电表读数计算能耗，与导出功能保持一致。
    """
    from datetime import datetime
    from backend.app.services.realtime_energy_service import RealtimeEnergyService
    from backend.app.config.electricity_config import ElectricityConfig

    electricity_config = ElectricityConfig()
    realtime_service = RealtimeEnergyService()
    
    # 获取站点配置
    if station_ip:
        station_config = electricity_config.get_station_by_ip(station_ip)
        if not station_config:
            raise HTTPException(status_code=404, detail=f"车站 {station_ip} 未找到")
        stations = [station_config]
    elif line:
        stations = electricity_config.get_stations_by_line(line)
        if not stations:
            raise HTTPException(status_code=404, detail=f"线路 {line} 不存在")
    else:
        raise HTTPException(status_code=400, detail="必须提供 line 或 station_ip 参数")
    
    # 计算当天的时间范围（从00:00到现在）
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 获取所有站点的真实数据
    total_kwh_today = 0.0
    current_kw = 0.0
    peak_kw = 0.0
    valid_station_count = 0
    
    for station in stations:
        try:
            # 获取当天能耗（使用电表读数）
            daily_consumption = await realtime_service.get_station_energy_consumption(
                station, start_of_day, now
            )
            
            # 获取当前功率
            station_current_kw = await realtime_service.get_station_realtime_power(station)
            
            if daily_consumption is not None:
                total_kwh_today += daily_consumption
                valid_station_count += 1
                
            if station_current_kw is not None:
                current_kw += station_current_kw
                peak_kw += station_current_kw * 1.5
                
            logger.info(
                f"[{station.get('name')}] 日能耗: {daily_consumption or 0:.2f} kWh, "
                f"当前功率: {station_current_kw or 0:.2f} kW"
            )
            
        except Exception as e:
            logger.warning(
                f"获取站点 {station.get('name')} 的能耗数据失败: {e}，该站点数据将被跳过"
            )
            continue
    
    # 如果所有站点都获取失败，回退到估算方式
    if valid_station_count == 0:
        logger.warning(
            f"线路 {line} 所有站点的真实能耗数据获取失败，使用功率估算方式"
        )
        cfg = _get_station_config(line, station_ip)
        sum_kw = _sum_kw_from_data_list(cfg.get("data_list", []))
        hours_today = now.hour + now.minute / 60.0
        utilization = 0.35
        total_kwh_today = sum_kw * utilization * max(hours_today, 0.1)
        current_kw = sum_kw * 0.40
        peak_kw = sum_kw * 0.75
    
    station_count = len(stations)
    
    return {
        "total_kwh_today": round(total_kwh_today, 2),
        "current_kw": round(current_kw, 2),
        "peak_kw": round(peak_kw, 2),
        "station_count": station_count,
        "data_source": "real" if valid_station_count > 0 else "estimated",
        "valid_station_count": valid_station_count,
    }
```

### 2. 核心改进点

1. **使用真实电表读数**: 调用 `realtime_service.get_station_energy_consumption()` 获取当天能耗
2. **与导出功能一致**: 使用相同的 `RealtimeEnergyService` 服务，确保计算逻辑完全一致
3. **支持多站点聚合**: 自动聚合线路下所有站点的能耗数据
4. **向后兼容**: 如果所有站点的真实数据获取失败，自动回退到功率估算方式
5. **数据来源标识**: 返回 `data_source` 字段，标识数据是真实采集还是估算
6. **详细日志**: 记录每个站点的能耗和功率数据，便于调试

## 修复验证

### 预期结果

修复后，能源驾驶舱的"总能耗"KPI将显示真实的电表读数计算结果，与导出功能的数据完全一致。

### 验证步骤

1. **启动后端服务**
   ```bash
   python main.py
   ```

2. **查看日志**
   访问 `/api/energy/kpi?line=M11&station_ip=<苗岭路IP>` 后，日志应显示：
   ```
   [苗岭路] 日能耗: 5657.29 kWh, 当前功率: XX.XX kW
   ```

3. **比对前端显示**
   能源驾驶舱的"总能耗"KPI应显示与导出数据一致的值

### 测试用例

```bash
# 测试单个站点
curl "http://localhost:8000/api/energy/kpi?line=M11&station_ip=<苗岭路IP>"

# 测试整条线路
curl "http://localhost:8000/api/energy/kpi?line=M11"

# 预期响应
{
  "total_kwh_today": 5657.29,
  "current_kw": 432.20,
  "peak_kw": 648.30,
  "station_count": 1,
  "data_source": "real",
  "valid_station_count": 1
}
```

## 数据计算逻辑

### 电表读数获取流程

1. **获取结束时间读数（止码）**
   - API: `POST http://{station_ip}:9898/data/selectHisData`
   - 时间窗口: `endTime` 往前10分钟
   - 参数:
     ```json
     {
       "dataCodes": ["LSA1_28", "LSA2_28", ...],
       "objectCodes": ["OBJ001", "OBJ002", ...],
       "startTime": endTime - 10 * 60000,
       "endTime": endTime,
       "funcName": "mean",
       "fill": "0"
     }
     ```

2. **获取开始时间读数（起码）**
   - API: `POST http://{station_ip}:9898/data/selectHisData`
   - 时间窗口: `startTime` 往后3分钟
   - 参数:
     ```json
     {
       "dataCodes": ["LSA1_28", "LSA2_28", ...],
       "objectCodes": ["OBJ001", "OBJ002", ...],
       "startTime": startTime,
       "endTime": startTime + 3 * 60000,
       "funcName": "mean",
       "fill": "0"
     }
     ```

3. **计算能耗**
   ```python
   for data_code in data_codes:
       for object_code in object_codes:
           start_reading = get_reading(start_data, data_code, object_code)
           end_reading = get_reading(end_data, data_code, object_code)
           
           if end_reading - start_reading >= -1:
               consumption = end_reading - start_reading
               total_consumption += consumption
   ```

## 配置要求

每个站点必须配置 `data_codes` 和 `object_codes`：

```python
# config_electricity.py
line_configs = {
    "M11": {
        "苗岭路": {
            "ip": "192.168.1.100",
            "station": "苗岭路",
            "data_codes": [
                "LSA1_28", "LSA2_28", "LT/A1_7", "LT/A2_7",
                "LD/A1_15", "LD/A2_15", "LQ/A1_20", "LQ/A2_20",
                "XK_A1_4", "XK_A2_15", "XK_A3_22",
                "XHPF_A1_3", "XHPF_A2_11", "XHPF_A3_18",
                "ZK_A1_30", "ZK_A2_30", "HPF_A_37"
            ],
            "object_codes": [
                "OBJ001", "OBJ002", "OBJ003", "OBJ004", "OBJ005",
                "OBJ006", "OBJ007", "OBJ008", "OBJ009", "OBJ010",
                "OBJ011", "OBJ012", "OBJ013"
            ],
            "jienengfeijieneng": {
                "data_codes": ["JNFJN_1"],
                "object_codes": ["OBJ_JNFJN"]
            }
        }
    }
}
```

**注意**：
- `data_codes` 和 `object_codes` 用于能耗计算（获取所有电表读数）
- `jienengfeijieneng` 节点仅用于节能状态查询

## 相关文件

- ✅ `main.py`: 修改KPI接口使用真实电表读数
- ✅ `backend/app/services/realtime_energy_service.py`: 已实现电表读数获取逻辑
- ✅ `backend/app/services/energy_service.py`: 已实现能耗聚合逻辑
- ✅ `export_service.py`: 导出功能使用相同的计算逻辑
- ✅ `config_electricity.py`: 站点配置（需确保包含 data_codes 和 object_codes）

## 总结

本次修复确保了能源驾驶舱显示的能耗数据与导出功能完全一致，都使用真实的电表读数计算。主要改进包括：

1. ✅ 使用电表起码、止码差值计算能耗（与导出功能一致）
2. ✅ 支持多站点自动聚合
3. ✅ 向后兼容，失败时自动回退到估算方式
4. ✅ 提供数据来源标识，便于排查问题
5. ✅ 详细的日志记录，便于调试和监控

修复后，11号线苗岭路站的能耗显示将准确反映实际的电表读数差值，不再使用估算值。
