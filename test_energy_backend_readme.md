# 能源驾驶舱后端测试脚本使用说明

## 📋 概述

`test_energy_backend.py` 是一个完整的后端测试脚本，用于验证能源驾驶舱是否能正常通过环控API获取真实数据。

## 🎯 测试内容

脚本会依次执行以下测试：

### 1. 配置完整性检查
- 检查 `config_electricity.py` 中的站点配置
- 验证每个站点是否包含必需的字段：
  - `ip`: 站点IP地址
  - `line`: 线路代码
  - `data_codes`: 数据代码数组
  - `object_codes`: 对象代码数组
- 统计配置完整和不完整的站点数量

### 2. 站点API连通性测试
- 测试前3个站点的API可达性
- 验证 `http://{站点IP}:9898` 是否可访问
- 超时设置: 5秒

### 3. 实时功率数据获取测试
- 测试前3个配置完整的站点
- 调用 `realtime_service.get_station_realtime_power()` 方法
- 验证是否能从环控API获取实时功率数据

### 4. 能耗数据获取测试
- 测试前3个配置完整的站点
- 获取当天（00:00到现在）的能耗数据
- 调用 `realtime_service.get_station_energy_consumption()` 方法
- 验证电表起码/止码计算逻辑

### 5. 能源总览接口测试
- 测试 `energy_service.get_energy_overview()` 接口
- 验证返回的KPI指标：
  - 总能耗 (kWh)
  - 当前功率 (kW)
  - 能效比
  - 节能收益 (元)
- 检查数据来源标识 (`real`, `partial`, `unavailable`)

### 6. 实时数据接口测试
- 测试 `energy_service.get_realtime_data()` 接口
- 验证返回的站点数据和24小时功率曲线

### 7. 趋势数据接口测试
- 测试 `energy_service.get_trend_series()` 接口
- 获取最近24小时的趋势数据
- 验证数据点数量和时间粒度

## 🚀 使用方法

### 环境依赖

请确保已安装以下 Python 依赖：

```bash
pip install requests
```

> **注意**: 实际后端服务也依赖 `requests` 与环控API交互，如缺少该库脚本将无法运行。

### 基础使用

```bash
# 进入项目根目录
cd /path/to/hk_tool_web

# 运行测试脚本
python test_energy_backend.py
```

### 输出示例

```
================================================================================
  能源驾驶舱后端API测试
================================================================================
测试时间: 2024-01-15 10:30:00
Python版本: 3.10.11

================================================================================
  1. 配置完整性检查
================================================================================
ℹ️  配置文件中总共有 15 个站点
ℹ️  配置文件中总共有 2 条线路: M3, M8
ℹ️  配置完整的站点数: 12
ℹ️  配置不完整的站点数: 3
✅ 配置完整性检查通过

================================================================================
  2. 站点API连通性测试
================================================================================
ℹ️  测试站点 '振华路' (http://192.168.100.3:9898)...
✅ 站点 '振华路' API可访问 (状态码: 200)
...

================================================================================
  测试总结报告
================================================================================

总测试数: 7
通过: 5
失败: 2

详细结果:
1. 配置完整性: ✅ 通过
2. API连通性: ✅ 通过
3. 实时功率获取: ❌ 失败
...
```

## 📊 测试报告

测试完成后会生成 `energy_backend_test_report.json` 文件，包含：

- **summary**: 测试汇总统计
  - `total`: 总测试数
  - `passed`: 通过数量
  - `failed`: 失败数量
  
- **results**: 详细测试结果数组
  - `test_name`: 测试名称
  - `passed`: 是否通过
  - `message`: 结果消息
  - `data`: 详细数据
  - `timestamp`: 测试时间

示例：

```json
{
  "summary": {
    "total": 7,
    "passed": 5,
    "failed": 2
  },
  "results": [
    {
      "test_name": "配置完整性",
      "passed": true,
      "message": "找到 12 个配置完整的站点",
      "data": {
        "total_stations": 15,
        "valid_stations": 12,
        "invalid_stations": 3
      },
      "timestamp": "2024-01-15T10:30:15.123456"
    }
  ]
}
```

## 🔍 故障诊断

### 配置完整性检查失败

**现象**: 站点被标记为"配置不完整"

**可能原因**:
1. 站点缺少 `ip` 字段
2. 站点缺少 `data_codes` 或 `object_codes` 数组
3. `data_codes` 或 `object_codes` 为空数组

**解决方法**:
检查 `config_electricity.py` 中的站点配置，确保包含以下字段：

```python
"站点名称": {
    "ip": "192.168.100.X",
    "station": "站点名称",
    "data_codes": ["code1", "code2", ...],
    "object_codes": ["obj1", "obj2", ...],
    "data_list": [...]
}
```

### API连通性测试失败

**现象**: 站点API无法访问，显示"连接超时"或"无法连接"

**可能原因**:
1. 站点IP地址不可达
2. 端口9898未开放或被防火墙拦截
3. 站点服务未启动
4. 网络问题

**解决方法**:
1. 使用 `ping` 命令测试站点IP可达性
2. 使用 `telnet {ip} 9898` 测试端口连通性
3. 检查站点服务状态
4. 检查防火墙和网络配置

### 实时功率获取失败

**现象**: API调用成功但未能获取有效功率数据

**可能原因**:
1. API返回空数据
2. 数据格式无法解析
3. 时间范围内无数据
4. `data_codes` 或 `object_codes` 配置错误

**解决方法**:
1. 检查后端日志，查看详细错误信息
2. 使用 Postman 等工具直接调用站点API，验证返回数据格式
3. 检查 `config_electricity.py` 中的配置是否与实际API匹配

示例API请求：

```bash
curl -X POST http://192.168.100.3:9898/data/selectHisData \
  -H "Content-Type: application/json" \
  -d '{
    "dataCodes": ["LS01_26"],
    "objectCodes": ["S_D_ZJ"],
    "startTime": 1705302000000,
    "endTime": 1705302600000,
    "measurement": "realData",
    "funcName": "mean",
    "fill": "0",
    "funcTime": ""
  }'
```

### 能耗数据获取失败

**现象**: 无法计算能耗差值

**可能原因**:
1. 起码或止码获取失败
2. 电表读数异常（止码小于起码）
3. API响应超时
4. 数据代码配置错误

**解决方法**:
1. 检查时间范围设置（建议至少1小时以上）
2. 验证电表读数是否正常累计
3. 检查日志中的详细错误信息
4. 确认配置的 `data_codes` 对应的是累计电量而非瞬时功率

### 能源驾驶舱接口测试失败

**现象**: 接口返回 `success: false` 或抛出异常

**可能原因**:
1. 所有站点数据获取都失败
2. 服务层异常
3. 数据聚合计算错误

**解决方法**:
1. 先确保前面的测试（实时功率、能耗数据）通过
2. 检查后端服务日志
3. 验证 `EnergyService` 和 `RealtimeEnergyService` 的初始化

## 🔧 高级配置

### 修改测试站点数量

编辑 `test_energy_backend.py`，修改 `run_all_tests()` 方法中的参数：

```python
# 测试前5个站点而不是3个
self.test_api_connectivity(max_stations=5)
await self.test_realtime_power(max_stations=5)
await self.test_energy_consumption(max_stations=5)
```

### 修改日志级别

在脚本开头修改：

```python
logging.basicConfig(
    level=logging.DEBUG,  # 改为 DEBUG 查看更详细的日志
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
```

### 自定义测试

可以单独运行某个测试：

```python
import asyncio
from test_energy_backend import EnergyBackendTester

async def test_single():
    tester = EnergyBackendTester()
    
    # 只测试配置完整性
    tester.test_config_integrity()
    
    # 只测试实时功率
    await tester.test_realtime_power(max_stations=1)
    
    # 生成报告
    tester.generate_test_report()

asyncio.run(test_single())
```

## 📝 日志说明

脚本运行时会产生详细的日志输出，帮助诊断问题：

| 符号 | 含义 | 示例 |
|------|------|------|
| ✅ | 成功 | `✅ 站点 '振华路' 实时功率: 245.50 kW` |
| ❌ | 错误 | `❌ 站点 '五四广场' 未能获取实时功率` |
| ⚠️ | 警告 | `⚠️ 站点 '某站点' 缺少节能数据配置` |
| ℹ️ | 信息 | `ℹ️ 配置文件中总共有 15 个站点` |
| 📊 | 数据 | `📊 [振华路] 总览数据获取成功` |
| 🌐 | API请求 | `🌐 发起API请求 - URL: http://...` |

## 🆘 常见问题

### Q: 所有测试都失败怎么办？

A: 按以下顺序检查：
1. 确认 `config_electricity.py` 配置正确
2. 确认网络连接正常
3. 确认站点服务可访问
4. 查看详细日志输出
5. 检查后端服务是否正常启动

### Q: 测试显示"数据不可用"怎么办？

A: 这是正常现象，说明：
- 配置正确
- API可访问
- 但当前时间段内没有实际数据

可以检查：
1. 站点设备是否在运行
2. 数据采集系统是否正常
3. 时间范围是否合理

### Q: 如何判断是真实数据还是模拟数据？

A: 查看测试输出中的 `data_source` 字段：
- `real`: 真实数据
- `partial`: 部分真实，部分估算
- `unavailable`: 数据不可用
- `simulated`: 模拟数据（已弃用）

### Q: 测试通过后前端仍显示数据不可用？

A: 可能原因：
1. 前端未正确配置 API 地址
2. 前端缓存问题，需要清除浏览器缓存
3. 前端与后端版本不匹配
4. 跨域（CORS）配置问题

解决方法：
1. 检查前端 `.env` 文件中的 API 地址
2. 清除浏览器缓存并刷新
3. 检查浏览器控制台的网络请求
4. 查看后端 CORS 中间件配置

## 📞 技术支持

如果遇到无法解决的问题，请提供以下信息：

1. 测试报告 JSON 文件 (`energy_backend_test_report.json`)
2. 完整的控制台输出
3. 后端服务日志
4. 站点配置信息（脱敏后）
5. 网络拓扑说明

## 🔄 更新日志

- v1.0 (2024-01-15): 初始版本
  - 实现7项核心测试
  - 支持配置完整性检查
  - 支持API连通性测试
  - 支持真实数据获取验证
  - 生成JSON格式测试报告
