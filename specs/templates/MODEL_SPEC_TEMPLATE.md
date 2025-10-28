# 数据模型规格: {模型名称}

## 元数据

| 项目 | 内容 |
|------|------|
| **规格编号** | SPEC-MODEL-{模块}-{模型}-{日期} |
| **规格版本** | v1.0.0 |
| **创建日期** | YYYY-MM-DD |
| **作者** | {作者姓名} |
| **状态** | Draft / Review / Approved / Implemented |

## 版本历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|----------|
| v1.0.0 | YYYY-MM-DD | {作者} | 初始版本 |

## 1. 模型概述

### 1.1 模型描述

{描述数据模型的用途、业务背景}

### 1.2 使用范围

- 场景1: {描述}
- 场景2: {描述}

### 1.3 关联规格

- [相关 API 规格](../api/SPEC-API-XXX.md)
- [相关服务规格](../services/SPEC-SERVICE-XXX.md)

## 2. 数据结构

### 2.1 字段定义

| 字段名 | 数据类型 | 必填 | 默认值 | 约束 | 描述 |
|--------|----------|------|--------|------|------|
| id | bigint | 是 | 自增 | 主键 | 唯一标识 |
| name | varchar(100) | 是 | - | 唯一 | 名称 |
| status | tinyint | 是 | 0 | 枚举[0-禁用,1-启用] | 状态 |
| created_at | datetime | 是 | CURRENT_TIMESTAMP | - | 创建时间 |
| updated_at | datetime | 是 | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

### 2.2 JSON Schema 描述（如适用）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "{模型名称}",
  "type": "object",
  "required": ["id", "name", "status"],
  "properties": {
    "id": {
      "type": "integer",
      "minimum": 1,
      "description": "唯一标识"
    },
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 100,
      "description": "名称"
    },
    "status": {
      "type": "integer",
      "enum": [0, 1],
      "description": "状态：0-禁用，1-启用"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "创建时间"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "更新时间"
    }
  }
}
```

### 2.3 索引设计

| 索引名称 | 类型 | 字段 | 唯一 | 说明 |
|----------|------|------|------|------|
| pk_{table} | 主键索引 | id | 是 | 主键索引 |
| uk_{table}_name | 唯一索引 | name | 是 | 名称唯一 |
| idx_{table}_status | 普通索引 | status | 否 | 状态查询 |

### 2.4 关系定义

| 关系类型 | 关联模型 | 关联字段 | Cardinality | 说明 |
|----------|----------|----------|-------------|------|
| OneToMany | {子模型} | parent_id -> id | 1:N | 一个父模型对应多个子模型 |
| ManyToMany | {关联模型} | {join_table} | N:M | 多对多关联 |

### 2.5 触发器 & 事件

| 触发器/事件 | 时机 | 条件 | 操作 |
|--------------|------|------|------|
| trg_update_timestamp | BEFORE UPDATE | - | 自动更新 updated_at |

## 3. 业务规则

### 3.1 数据约束

- 必须保证名称唯一
- 状态只能为0或1
- 删除时需检查是否存在引用

### 3.2 数据验证规则

| 场景 | 规则 | 错误码 | 错误信息 |
|------|------|--------|----------|
| 新增 | 名称不能为空 | 2001 | name is required |
| 新增 | 名称长度1-100 | 2002 | name length must be between 1 and 100 |
| 新增 | 状态必须合法 | 2003 | invalid status |

### 3.3 数据转换规则

- 保存前将名称去除首尾空格
- 状态字段存储为整数

## 4. 数据库表设计

### 4.1 表结构

```sql
CREATE TABLE `{table_name}` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name` VARCHAR(100) NOT NULL COMMENT '名称',
  `status` TINYINT NOT NULL DEFAULT 0 COMMENT '状态：0-禁用，1-启用',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_{table}_name` (`name`),
  KEY `idx_{table}_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='{模型描述}';
```

### 4.2 数据示例

| id | name | status | created_at | updated_at |
|----|------|--------|------------|------------|
| 1 | 示例数据 | 1 | 2025-01-01 10:00:00 | 2025-01-01 10:00:00 |

## 5. 接口契约

### 5.1 输入/输出契约

| 接口 | 场景 | 输入字段 | 输出字段 |
|------|------|----------|----------|
| POST /api/v1/{resource} | 新增 | name, status | id |
| GET /api/v1/{resource} | 查询 | id | id, name, status, created_at, updated_at |

### 5.2 DTO 定义

```python
class {Model}CreateRequest(BaseModel):
    name: constr(min_length=1, max_length=100)
    status: conint(ge=0, le=1) = 1

class {Model}Response(BaseModel):
    id: int
    name: str
    status: int
    created_at: datetime
    updated_at: datetime
```

## 6. 非功能性要求

### 6.1 性能要求

- 单表记录数：{预估数量}
- 读写比：读{比例} / 写{比例}
- 访问频率：{QPS/TPS}

### 6.2 安全要求

- 敏感字段存储加密（如适用）
- 数据访问权限控制

### 6.3 合规要求

- 数据保留时长：{保留期限}
- 法规要求：{如GDPR等}

## 7. 测试用例

### 7.1 单元测试

| 测试用例ID | 测试描述 | 输入 | 期望输出 |
|-----------|---------|------|---------|
| TC_MODEL_001 | 创建合法数据 | {合法数据} | 创建成功 |
| TC_MODEL_002 | 名称重复 | {重复名称} | 抛出唯一约束异常 |

### 7.2 集成测试

| 测试用例ID | 场景 | 步骤 | 期望结果 |
|-----------|------|------|---------|
| TC_MODEL_101 | CRUD操作 | 新增-查询-更新-删除 | 全部成功 |

### 7.3 数据一致性测试

- 验证索引有效性
- 验证外键约束
- 验证触发器执行

## 8. 监控与告警

### 8.1 监控指标

| 指标 | 说明 | 阈值 |
|------|------|------|
| 数据库错误数 | 数据库操作失败次数 | > 0 |
| 主键冲突 | 主键冲突次数 | > 0 |

### 8.2 告警策略

- 当数据库错误率超过1%时触发告警
- 当出现主键冲突时触发告警

## 9. 数据迁移

### 9.1 初始化脚本

```sql
INSERT INTO {table_name} (name, status)
VALUES ('默认数据', 1);
```

### 9.2 数据清理策略

- 定期归档历史数据
- 删除前备份

### 9.3 兼容性考虑

- 旧版本数据结构兼容方案
- 数据迁移风险评估

## 10. 附录

### 10.1 术语表

| 术语 | 定义 |
|------|------|
| {术语} | {定义} |

### 10.2 参考资料

- [数据建模最佳实践](https://example.com)
- [JSON Schema 文档](https://json-schema.org/)

---

**审核状态**: [ ] 待审核 / [ ] 已审核 / [ ] 已批准  
**实现状态**: [ ] 未实现 / [ ] 实现中 / [ ] 已完成 / [ ] 已上线  
**最后更新**: YYYY-MM-DD  
**维护者**: {维护者}
