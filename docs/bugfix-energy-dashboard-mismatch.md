# Bug Fix: 能源驾驶舱数据与导出数据不一致

## 问题描述

能源驾驶舱显示的能耗信息与实际导出的电耗数据不一致。用户反馈11号线苗岭路站的数据存在明显差异。

## 根本原因分析

### 1. 导出功能的数据获取方式

导出功能（`export_service.py`）使用以下配置：
- 读取站点配置中的 `data_codes` 数组（包含所有电表的数据代码）
- 读取站点配置中的 `object_codes` 数组（包含所有设备对象代码）
- 调用 `/data/selectHisData` API 获取**所有设备**的电表起码、止码，计算耗电量

示例（苗岭路站）：
```python
"data_codes": [
    "LSA1_28",   # 冷机LS/B1
    "LSA2_28",   # 冷机LS/B2
    "LT/A1_7",   # 冷却塔LT/B1
    # ... 共17个电表数据代码
]
"object_codes": [
    "S_LS_1", "S_LS_2", "S_LQTFJ_1",
    # ... 共13个对象代码
]
```

### 2. 能源驾驶舱的数据获取方式（修复前）

能源驾驶舱（`realtime_energy_service.py`）使用以下配置：
- 读取站点配置中的 `jienengfeijieneng` 节点
- 该节点仅包含**节能状态**的配置，只有1个data_code

示例（苗岭路站修复前）：
```python
"jienengfeijieneng": {
    "object_codes": ["PT_SDZ"],
    "data_codes": ["296"]  # 仅用于获取节能状态，不是设备功率
}
```

### 3. 问题所在

能源驾驶舱只获取了**节能状态**的数据（1个数据点），而不是所有设备的功率数据（17个数据点），导致：
- 能源驾驶舱显示的功率数据**不完整**
- 总能耗计算**严重偏低**
- 与导出功能使用不同的数据源，造成**数据不一致**

## 修复方案

修改 `backend/app/services/realtime_energy_service.py` 中的 `_get_jieneng_config` 方法：

### 修改前
```python
def _get_jieneng_config(self, line_code: str, station_name: str) -> Optional[Dict[str, Any]]:
    """从config_electricity.py获取站点的节能配置"""
    try:
        from config_electricity import line_configs

        line_config = line_configs.get(line_code)
        if not line_config:
            return None

        station_config = line_config.get(station_name)
        if not station_config:
            return None

        return station_config.get("jienengfeijieneng")  # ❌ 只获取节能状态配置

    except Exception as exc:
        logger.error("获取节能配置失败: %s", exc)
        return None
```

### 修改后
```python
def _get_jieneng_config(self, line_code: str, station_name: str) -> Optional[Dict[str, Any]]:
    """从config_electricity.py获取站点的节能配置
    
    注意：这里应该使用data_codes和object_codes数组来获取所有设备的能耗数据，
    而不是jienengfeijieneng节点（该节点仅用于获取节能状态）
    """
    try:
        from config_electricity import line_configs

        line_config = line_configs.get(line_code)
        if not line_config:
            return None

        station_config = line_config.get(station_name)
        if not station_config:
            return None

        # ✅ 使用data_codes和object_codes数组，而不是jienengfeijieneng节点
        # 这样可以与导出功能保持一致，获取所有设备的实时功率
        data_codes = station_config.get("data_codes", [])
        object_codes = station_config.get("object_codes", [])
        
        if not data_codes or not object_codes:
            logger.warning(
                "站点 %s (线路 %s) 缺少data_codes或object_codes配置",
                station_name, line_code
            )
            return None
        
        return {
            "data_codes": data_codes,
            "object_codes": object_codes
        }

    except Exception as exc:
        logger.error("获取节能配置失败: %s", exc)
        return None
```

## 修复效果

### 修复前（苗岭路站）
- data_codes数量: 1（仅节能状态）
- object_codes数量: 1
- 获取的数据：只有节能状态，无设备功率

### 修复后（苗岭路站）
- data_codes数量: 17（所有电表）
- object_codes数量: 13（所有设备对象）
- 获取的数据：所有设备的实时功率，与导出功能一致

## 影响范围

1. **能源驾驶舱（Energy Dashboard）**
   - `/api/energy/overview` - 能源总览数据
   - `/api/energy/realtime` - 实时能耗监控
   - `/api/energy/equipment` - 设备运行状态
   
2. **受影响站点**
   - 所有配置了 `data_codes` 和 `object_codes` 的站点
   - 特别是11号线苗岭路站（用户反馈的站点）

## 测试验证

```bash
# 测试配置读取
python -c "
from backend.app.services.realtime_energy_service import RealtimeEnergyService

service = RealtimeEnergyService()
config = service._get_jieneng_config('M11', '苗岭路')

print(f'data_codes数量: {len(config[\"data_codes\"])}')  # 应为17
print(f'object_codes数量: {len(config[\"object_codes\"])}')  # 应为13
print(f'data_codes前3个: {config[\"data_codes\"][:3]}')
print(f'object_codes前3个: {config[\"object_codes\"][:3]}')
"
```

## 相关文件

- `backend/app/services/realtime_energy_service.py` - 修改的主文件
- `backend/app/services/energy_service.py` - 调用方
- `export_service.py` - 参考的导出服务
- `config_electricity.py` - 站点配置文件

## 注意事项

1. **配置要求**：所有站点必须在 `config_electricity.py` 中配置 `data_codes` 和 `object_codes` 数组
2. **向后兼容**：如果站点缺少这些配置，会记录警告日志并返回 `None`
3. **数据一致性**：修复后，能源驾驶舱和导出功能使用相同的数据源，确保数据一致
4. **性能影响**：获取的数据点从1个增加到17个（以苗岭路为例），API调用时间可能略有增加

## 后续优化建议

1. 考虑添加缓存机制，减少API调用频率
2. 在前端显示数据来源（真实数据 vs 模拟数据）
3. 添加配置验证工具，确保所有站点配置完整
4. 考虑将 `jienengfeijieneng` 节点用途明确化，仅用于节能状态展示
