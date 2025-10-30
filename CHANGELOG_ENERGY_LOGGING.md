# 能源驾驶舱日志增强和模拟数据移除 - 变更日志

## 版本信息
- **日期**: 2024-10-30
- **分支**: `fix/energy-cockpit-remove-sim-fallback-add-detailed-logs`
- **类型**: 增强 + 修复

## 变更概述

移除了能源驾驶舱的模拟数据fallback机制，并添加了详细的日志输出，方便排查真实数据获取问题。

## 主要变更

### 1. 后端变更

#### `backend/app/services/realtime_energy_service.py`

**移除内容：**
- 不再返回模拟数据作为fallback
- 移除"使用模拟数据"的警告日志

**新增功能：**
- ✅ 详细的站点信息日志（站点名、IP、线路）
- 📋 节能配置解析详情（object_codes、data_codes数量及内容）
- 🔗 API调用地址日志
- 🌐 API请求详情（payload信息、时间范围）
- 📥 API响应详情（状态码、响应时间、数据条数）
- ❌ 详细的错误信息和可能原因
- 💡 具体的解决建议

**日志示例：**
```
INFO: 开始获取站点实时功率 - 站点: 振华路, IP: 192.168.1.100, 线路: M3
ERROR: ❌ [振华路] 站点没有节能数据配置。
       请在config_electricity.py中为线路'M3'的站点'振华路'配置'jienengfeijieneng'节点，
       包含object_codes和data_codes字段。
```

#### `backend/app/services/energy_service.py`

**移除内容：**
- 移除模拟功率生成逻辑（`base_power = device_count * 25 + random.uniform(-10, 10)`）
- 移除"使用模拟数据"的警告日志
- 移除 `simulated` 和 `mixed` 数据源标识

**新增功能：**
- 当获取失败时返回 `0.0` 而非模拟值
- 数据源标识更准确：`real`, `partial`, `unavailable`
- 详细的站点级日志
- 汇总级日志，显示可用/不可用站点统计
- 返回不可用站点列表及失败原因

**数据源语义变更：**
- `real` - 所有站点数据可用
- `partial` - 部分站点数据可用（取代 `mixed`）
- `unavailable` - 所有站点数据不可用（取代 `simulated`）

**新增响应字段：**
```json
{
  "data_source": "partial",
  "available_station_count": 8,
  "unavailable_stations": [
    {
      "station_name": "振华路",
      "station_ip": "192.168.1.100",
      "reason": "实时功率获取失败。请检查: 1) 节能数据配置 2) 站点API可达性 3) 是否存在实时数据"
    }
  ]
}
```

### 2. 前端变更

#### `frontend/src/views/EnergyCockpit.vue`

**数据源标识更新：**
```typescript
// 旧版本
const DATA_SOURCE_PRIORITY = {
  real: 3,
  mixed: 2,
  simulated: 1,
}

// 新版本
const DATA_SOURCE_PRIORITY = {
  real: 3,
  partial: 2,
  unavailable: 1,
}
```

**显示文本更新：**
```typescript
// 旧版本
{
  real: '真实数据',
  simulated: '模拟数据',
  mixed: '混合数据',
}

// 新版本
{
  real: '真实数据',
  partial: '部分数据缺失',
  unavailable: '数据不可用',
}
```

**样式类名更新：**
- `.data-source-simulated` → `.data-source-unavailable`
- `.data-source-mixed` → `.data-source-partial`

## 影响分析

### 向后兼容性

**不兼容变更：**
- API响应中的 `data_source` 字段值变更
  - `simulated` → `unavailable`
  - `mixed` → `partial`
- 不再返回模拟数据，数据不可用时返回 `0`

**兼容变更：**
- 新增响应字段不影响现有客户端
- API端点和参数保持不变

### 用户体验

**改进：**
- ✅ 数据更真实可靠，不会误导用户
- 📋 日志详细，问题排查更容易
- 💡 错误信息提供具体的解决建议

**注意事项：**
- ⚠️ 配置不正确的站点将显示为 `0`，需要及时修复配置
- ⚠️ 前端需要处理 `partial` 和 `unavailable` 状态

## 测试建议

### 1. 配置正确的站点
验证日志显示成功获取数据，数据源标识为 `real`

### 2. 配置缺失的站点
验证日志清晰说明配置问题和解决方法

### 3. 网络不可达的站点
验证日志说明连接失败原因（超时、连接拒绝等）

### 4. 部分站点失败
验证汇总日志显示可用/不可用站点统计

### 5. 前端显示
验证数据源指示器正确显示 `真实数据` / `部分数据缺失` / `数据不可用`

## 配置修复指南

如果看到 "站点没有节能数据配置" 错误，需要在 `config_electricity.py` 中添加配置：

```python
line_configs = {
    "M3": {
        "振华路": {
            "ip": "192.168.1.100",
            "jienengfeijieneng": {
                "object_codes": ["OBJ001", "OBJ002"],
                "data_codes": ["DC001", "DC002", "DC003"]
            }
        }
    }
}
```

## 相关文档

- [详细日志增强文档](docs/ENERGY_COCKPIT_LOGGING_ENHANCEMENT.md)
- [能源数据源更新](docs/ENERGY_DATA_SOURCE_UPDATE.md)

## 回滚说明

如需回滚此变更，请checkout到此分支之前的commit。注意：回滚后将恢复模拟数据fallback机制。

---

**审核者注意事项：**
- ✅ 已验证Python代码语法正确
- ✅ 日志使用结构化格式，便于监控和告警
- ✅ 错误信息提供可操作的解决建议
- ⚠️ 需要确保所有站点配置正确，否则将显示为数据不可用
