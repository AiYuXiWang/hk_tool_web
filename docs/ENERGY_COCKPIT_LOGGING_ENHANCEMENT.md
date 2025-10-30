# 能源驾驶舱日志增强和模拟数据移除

## 修改概述

本次更新移除了能源驾驶舱中的模拟数据fallback机制，并大幅增强了日志输出的详细程度，以便于排查真实数据获取问题。

## 修改文件

1. `backend/app/services/realtime_energy_service.py` - 真实能源数据服务
2. `backend/app/services/energy_service.py` - 能源管理服务

## 主要变更

### 1. 移除模拟数据Fallback

**之前的行为：**
- 当站点没有节能数据配置时，返回模拟数据
- 当实时功率获取失败时，使用模拟数据作为fallback
- 日志仅显示警告："站点 XXX 实时功率获取失败，使用模拟数据"

**现在的行为：**
- 当站点没有节能数据配置时，返回 `None` 并记录详细错误
- 当实时功率获取失败时，返回 `0.0` 并标记数据源为 `unavailable`
- 不再使用任何模拟数据，确保数据的真实性

### 2. 详细日志输出

#### 2.1 站点级别日志

**在 `realtime_energy_service.py` 中：**

```
开始获取站点实时功率 - 站点: 振华路, IP: 192.168.1.100, 线路: M3
```

**配置检查日志：**
- ❌ 表示错误
- ⚠️ 表示警告
- ✅ 表示成功
- 📋 表示配置信息
- 🔗 表示网络连接
- 🌐 表示API请求
- 📥 表示API响应

**示例日志输出：**

```
INFO: 开始获取站点实时功率 - 站点: 振华路, IP: 192.168.1.100, 线路: M3
ERROR: ❌ [振华路] 站点没有节能数据配置。
       请在config_electricity.py中为线路'M3'的站点'振华路'配置'jienengfeijieneng'节点，
       包含object_codes和data_codes字段。
```

**配置成功日志：**

```
INFO: 📋 [振华路] 节能配置解析成功 - object_codes数量: 10, data_codes数量: 15
DEBUG: 📋 [振华路] object_codes: ['OBJ001', 'OBJ002', 'OBJ003'], data_codes: ['DC001', 'DC002', 'DC003']
INFO: 🔗 [振华路] API地址: http://192.168.1.100:9898/data/selectHisData
```

#### 2.2 API请求详细日志

**请求日志：**

```
DEBUG: 🌐 发起API请求 - URL: http://192.168.1.100:9898/data/selectHisData, 
       payload: {'objectCodes数量': 10, 'dataCodes数量': 15, '时间范围': '1698653091000 - 1698653691000'}
```

**响应日志：**

```
DEBUG: 📥 API响应 - URL: http://192.168.1.100:9898/data/selectHisData, 
       状态码: 200, 响应时间: 0.35s
INFO: ✅ API请求成功 - URL: http://192.168.1.100:9898/data/selectHisData, 返回数据条数: 15
```

**错误日志示例：**

**超时：**
```
ERROR: ❌ API请求超时(>5s) - URL: http://192.168.1.100:9898/data/selectHisData, 
       可能原因: 1) 网络延迟 2) 站点服务响应慢 3) 数据量过大
```

**连接失败：**
```
ERROR: ❌ API连接失败 - URL: http://192.168.1.100:9898/data/selectHisData, 
       错误: Connection refused, 
       可能原因: 1) 站点IP不可达 2) 端口9898未开放 3) 网络故障
```

**空数据：**
```
WARNING: ⚠️ API返回空数据 - URL: http://192.168.1.100:9898/data/selectHisData, 
         完整响应: {'code': 200, 'data': [], 'message': 'success'}
```

#### 2.3 汇总级别日志

**总览指标：**

```
INFO: 📊 总览指标计算完成 - 总能耗: 12345.6 kWh, 当前功率: 567.8 kW, 可用站点: 8/10
WARNING: ⚠️ 以下站点总览数据不可用: 振华路, 人民广场
```

**实时数据：**

```
INFO: 📈 实时数据汇总完成 - 总功率: 567.8 kW, 可用站点: 8/10
WARNING: ⚠️ 以下站点实时数据不可用: 振华路, 人民广场
```

### 3. 数据源标识

**新增数据源状态：**

- `real` - 真实数据（所有站点数据可用）
- `partial` - 部分数据（部分站点数据不可用）
- `unavailable` - 数据不可用（所有站点数据均不可用）

**返回数据新增字段：**

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

## 排查指南

### 问题：站点没有节能数据配置

**日志示例：**
```
ERROR: ❌ [振华路] 站点没有节能数据配置。
       请在config_electricity.py中为线路'M3'的站点'振华路'配置'jienengfeijieneng'节点
```

**解决方法：**
1. 打开 `config_electricity.py`
2. 找到对应线路（如 M3）的配置
3. 找到对应站点（如 振华路）的配置
4. 添加 `jienengfeijieneng` 节点，示例：

```python
"振华路": {
    "ip": "192.168.1.100",
    "jienengfeijieneng": {
        "object_codes": ["OBJ001", "OBJ002"],
        "data_codes": ["DC001", "DC002", "DC003"]
    }
}
```

### 问题：API连接失败

**日志示例：**
```
ERROR: ❌ API连接失败 - URL: http://192.168.1.100:9898/data/selectHisData
       可能原因: 1) 站点IP不可达 2) 端口9898未开放 3) 网络故障
```

**排查步骤：**
1. 检查站点IP是否正确：`ping 192.168.1.100`
2. 检查端口是否开放：`telnet 192.168.1.100 9898`
3. 检查网络防火墙配置
4. 确认站点服务是否正常运行

### 问题：API返回空数据

**日志示例：**
```
WARNING: ⚠️ API返回空数据 - URL: http://192.168.1.100:9898/data/selectHisData
```

**排查步骤：**
1. 检查 `object_codes` 和 `data_codes` 是否正确
2. 确认时间范围内是否有数据（默认查询最近10分钟）
3. 检查站点数据采集服务是否正常
4. 使用Postman等工具直接调用API进行测试

### 问题：配置不完整

**日志示例：**
```
ERROR: ❌ [振华路] 节能配置不完整 - object_codes: 空, data_codes: 3个
```

**解决方法：**
确保配置中同时包含 `object_codes` 和 `data_codes` 数组，且不能为空。

## 日志级别配置

建议在开发和排查问题时使用 DEBUG 级别：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

生产环境使用 INFO 级别：

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 测试建议

1. **测试配置正确的站点** - 验证日志显示成功获取数据
2. **测试配置缺失的站点** - 验证日志清晰说明配置问题
3. **测试网络不可达的站点** - 验证日志说明连接失败原因
4. **测试部分站点失败的场景** - 验证汇总日志正确显示可用/不可用站点

## 向后兼容性

- API接口路径和参数保持不变
- 响应结构保持兼容，新增字段不影响现有功能
- 数据源标识从 `real/simulated/mixed` 变更为 `real/partial/unavailable`

## 相关文档

- [能源数据源更新](ENERGY_DATA_SOURCE_UPDATE.md)
- [能源实时数据集成](ENERGY_REALDATA_INTEGRATION.md)
- [数据源检测](data-source-detection.md)

## 更新日期

2024-10-30
