# API Spec: Energy - 实时能耗数据查询

> **注意**: 这是一个示例规格文档，展示 Spec Coding 的实际应用。

## 元数据

| 项目 | 内容 |
|------|------|
| **规格编号** | SPEC-API-ENERGY-REALTIME-DATA-EXAMPLE |
| **规格版本** | v1.0.0 |
| **创建日期** | 2025-01-01 |
| **作者** | 开发团队 |
| **状态** | Example (示例文档) |

## 版本历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|----------|
| v1.0.0 | 2025-01-01 | 开发团队 | 初始版本 |

## 1. 功能概述

### 1.1 功能描述

提供设备实时能耗数据查询接口，支持按设备ID查询当前功率、累计能耗等实时指标。

### 1.2 业务价值

- 为能源驾驶舱提供实时数据支撑
- 支持设备能耗监控和异常告警
- 为节能优化提供数据基础

### 1.3 使用场景

- 场景1: 能源驾驶舱页面实时显示设备能耗
- 场景2: 监控系统定时拉取设备状态
- 场景3: 移动端查看设备实时数据

## 2. 接口定义

### 2.1 接口基本信息

| 项目 | 内容 |
|------|------|
| **接口路径** | `/api/v1/energy/realtime` |
| **请求方法** | GET |
| **认证要求** | Required |
| **权限要求** | energy:read |
| **限流规则** | 100次/分钟/用户 |

### 2.2 请求规格

#### 2.2.1 请求头（Request Headers）

| 头字段 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| Authorization | string | 是 | Bearer token |

#### 2.2.2 查询参数（Query Parameters）

| 参数名 | 类型 | 必填 | 默认值 | 说明 | 示例 |
|--------|------|------|--------|------|------|
| device_ids | string | 是 | - | 设备ID列表，逗号分隔 | "1,2,3" |
| metrics | string | 否 | "all" | 指标类型：all/power/energy | "power" |

### 2.3 响应规格

#### 2.3.1 成功响应（Success Response）

**状态码**: `200 OK`

**JSON Schema**:

```json
{
  "type": "object",
  "required": ["code", "message", "data"],
  "properties": {
    "code": {
      "type": "integer",
      "enum": [0]
    },
    "message": {
      "type": "string"
    },
    "data": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "device_id": {
            "type": "integer"
          },
          "device_name": {
            "type": "string"
          },
          "current_power": {
            "type": "number",
            "description": "当前功率(kW)"
          },
          "total_energy": {
            "type": "number",
            "description": "累计能耗(kWh)"
          },
          "timestamp": {
            "type": "string",
            "format": "date-time"
          }
        }
      }
    }
  }
}
```

## 3. 业务逻辑

### 3.1 处理流程

1. 验证用户认证和权限
2. 解析并验证查询参数
3. 查询设备实时数据（优先从缓存获取）
4. 格式化数据并返回

### 3.2 业务规则

1. 单次最多查询50个设备
2. 数据缓存时间为30秒
3. 设备不存在时返回空数据，不报错

## 4. 错误处理

### 4.1 错误码定义

| 错误码 | HTTP状态码 | 错误信息 | 说明 |
|--------|-----------|----------|------|
| 1001 | 400 | Invalid device_ids | 设备ID格式错误 |
| 1002 | 401 | Unauthorized | 未授权 |
| 1003 | 403 | Forbidden | 无权限 |
| 1006 | 429 | Too many requests | 请求过多 |

## 5. 性能要求

| 场景 | 目标响应时间 | 最大响应时间 |
|------|-------------|-------------|
| 正常情况 | < 100ms | < 200ms |

## 6. 示例

### 6.1 请求示例

```bash
curl -X GET \
  'http://api.example.com/api/v1/energy/realtime?device_ids=1,2,3' \
  -H 'Authorization: Bearer {token}'
```

### 6.2 成功响应示例

```json
{
  "code": 0,
  "message": "Success",
  "data": [
    {
      "device_id": 1,
      "device_name": "冷水机组1",
      "current_power": 125.5,
      "total_energy": 1580.2,
      "timestamp": "2025-01-01T12:00:00Z"
    },
    {
      "device_id": 2,
      "device_name": "冷水机组2",
      "current_power": 118.3,
      "total_energy": 1520.8,
      "timestamp": "2025-01-01T12:00:00Z"
    }
  ]
}
```

## 7. 测试用例

### 7.1 正常场景测试

| 测试用例ID | 测试描述 | 输入 | 期望输出 |
|-----------|---------|------|---------|
| TC001 | 查询单个设备 | device_ids=1 | 返回设备1的实时数据 |
| TC002 | 查询多个设备 | device_ids=1,2,3 | 返回3个设备的实时数据 |

### 7.2 异常场景测试

| 测试用例ID | 测试描述 | 输入 | 期望输出 |
|-----------|---------|------|---------|
| TC101 | 设备ID格式错误 | device_ids=abc | 返回400错误 |
| TC102 | 未授权访问 | 无Token | 返回401错误 |

## 8. 验收标准

- [ ] 所有正常场景测试用例通过
- [ ] 所有异常场景测试用例通过
- [ ] 响应时间 < 200ms
- [ ] 缓存机制正常工作

---

**审核状态**: [x] 已批准  
**实现状态**: [ ] 示例文档  
**最后更新**: 2025-01-01
