# 在 cto.new 中使用 Spec Coding 的工作流程

本文档说明如何在 cto.new 平台创建任务时，充分利用本项目搭建的 Spec Coding 基础设施。

## 概述

Spec Coding 是一种"规格先行、实现跟随"的开发方法论。在 cto.new 创建任务时，应该遵循以下原则：

1. **任务分为两阶段**：规格编写阶段 + 实现阶段
2. **规格是代码的前置条件**：没有规格文档，不能开始编码
3. **规格即是合约**：规格文档是 AI 和人类开发者之间的明确约定

## 工作流程

### 阶段 1: 规格编写任务（Specification Task）

#### 任务标题格式
```
[Spec] {功能模块} - {功能描述}
```

**示例**：
- `[Spec] 能源模块 - 实时能耗数据查询 API`
- `[Spec] 设备控制 - 批量写值接口优化`
- `[Spec] 前端组件 - 能源趋势图表`

#### 任务描述模板

```markdown
## 任务目标
编写 {功能名称} 的完整规格文档

## 功能概述
{简要描述功能的业务背景、目标和价值}

## 规格类型
- [ ] API 规格
- [ ] 数据模型规格
- [ ] 服务规格
- [ ] 前端组件规格
- [ ] 前端页面规格
- [ ] 集成规格

## 规格要求

### 必须包含的内容
1. **功能概述**
   - 功能描述
   - 业务价值
   - 使用场景

2. **技术规格**
   - 接口定义（API 规格）/ 组件接口（组件规格）/ 数据结构（数据模型）
   - 请求/响应格式 或 Props/Events/Slots
   - 业务逻辑流程
   - 错误处理机制

3. **非功能性需求**
   - 性能要求
   - 安全要求
   - 可用性要求

4. **测试用例**
   - 正常场景测试用例
   - 异常场景测试用例
   - 边界场景测试用例

5. **验收标准**
   - 明确的、可测试的验收条件

## 参考资料
- [Spec Coding 开发规范](docs/SPEC_CODING_GUIDE.md)
- [Spec Coding 快速入门](docs/SPEC_CODING_QUICKSTART.md)
- [API 规格模板](specs/templates/API_SPEC_TEMPLATE.md)
- [组件规格模板](specs/templates/COMPONENT_SPEC_TEMPLATE.md)
- [数据模型规格模板](specs/templates/MODEL_SPEC_TEMPLATE.md)
- [示例规格](specs/backend/api/SPEC-API-ENERGY-REALTIME-DATA-20250101-EXAMPLE.md)

## 输出要求
1. 在 `specs/` 目录下创建规格文档
2. 使用工具创建文档草稿：
   ```bash
   python tools/create_spec.py --type {api|model|component} --module {模块} --name {功能}
   ```
3. 按照模板填写完整的规格内容
4. 确保文档格式规范、内容完整
5. 提交规格文档供评审

## 验收标准
- [ ] 规格文档已创建并位于正确的目录
- [ ] 文档命名符合规范：`SPEC-{类型}-{模块}-{功能}-{日期}.md`
- [ ] 包含所有必需章节
- [ ] 接口定义 / 数据模型 / 组件接口明确
- [ ] 业务逻辑描述清晰
- [ ] 错误处理完善
- [ ] 测试用例完整
- [ ] 验收标准可测试
- [ ] 文档可通过人工评审
```

#### 任务示例

**任务标题**：`[Spec] 能源模块 - 设备实时能耗数据查询 API`

**任务描述**：
```markdown
## 任务目标
编写设备实时能耗数据查询 API 的完整规格文档

## 功能概述
能源驾驶舱需要实时显示设备的功率和能耗数据。该 API 提供按设备 ID 查询实时能耗指标的能力，支持批量查询多个设备。

## 规格类型
- [x] API 规格

## 规格要求

### 必须包含的内容
1. **功能概述**
   - 查询设备实时能耗数据（功率、累计能耗）
   - 支持能源驾驶舱实时监控
   - 批量查询多个设备

2. **技术规格**
   - 接口路径：`/api/v1/energy/realtime`
   - 请求方法：GET
   - 查询参数：device_ids（设备ID列表）
   - 响应格式：JSON（设备列表 + 能耗指标）
   - 错误处理：参数验证、权限检查、限流

3. **非功能性需求**
   - 响应时间：< 200ms
   - 并发支持：100 QPS
   - 数据缓存：30秒

4. **测试用例**
   - 单设备查询
   - 多设备批量查询
   - 参数错误处理
   - 设备不存在处理

5. **验收标准**
   - 接口定义完整
   - 包含完整的请求/响应示例
   - 错误码定义清晰
   - 性能要求明确

## 参考资料
- [API 规格模板](specs/templates/API_SPEC_TEMPLATE.md)
- [示例规格](specs/backend/api/SPEC-API-ENERGY-REALTIME-DATA-20250101-EXAMPLE.md)

## 输出要求
1. 使用工具创建规格文档：
   ```bash
   python tools/create_spec.py --type api --module energy --name realtime-data
   ```
2. 填写完整的规格内容
3. 文件位置：`specs/backend/api/SPEC-API-ENERGY-REALTIME-DATA-{日期}.md`

## 验收标准
- [x] 规格文档已创建
- [x] 接口路径、方法、参数定义明确
- [x] 请求/响应 JSON Schema 完整
- [x] 错误码定义完善
- [x] 包含至少 5 个测试用例
- [x] 性能要求明确（响应时间、QPS）
- [x] 包含 cURL/Python/JavaScript 请求示例
```

---

### 阶段 2: 实现任务（Implementation Task）

只有在规格文档评审通过后，才能创建实现任务。

#### 任务标题格式
```
[Impl] {功能模块} - {功能描述}
```

**示例**：
- `[Impl] 能源模块 - 实时能耗数据查询 API`
- `[Impl] 设备控制 - 批量写值接口优化`
- `[Impl] 前端组件 - 能源趋势图表`

#### 任务描述模板

```markdown
## 任务目标
按照规格文档实现 {功能名称}

## 规格文档
**必须严格遵循以下规格文档**：
- [SPEC-{类型}-{模块}-{功能}-{日期}.md](specs/{路径}/SPEC-{类型}-{模块}-{功能}-{日期}.md)

## 实现要求

### 1. 代码实现
- 严格按照规格文档实现
- 不得偏离规格定义
- 如发现规格问题，先提出规格变更请求

### 2. 代码注释
在关键代码处添加规格引用注释：

**Python 示例**：
```python
# Spec: SPEC-API-ENERGY-REALTIME-DATA-20250101.md#section-2.2
# 功能说明：获取设备实时能耗数据
@router.get("/api/v1/energy/realtime")
async def get_realtime_energy_data(
    device_ids: str = Query(..., description="设备ID列表，逗号分隔")
):
    # 实现代码
    pass
```

**TypeScript 示例**：
```typescript
// Spec: SPEC-COMPONENT-ENERGY-CHART-20250101.md#section-2.1
// 组件说明：能源趋势图表组件
export default defineComponent({
  name: 'EnergyChart',
  props: {
    // Props 定义
  }
})
```

### 3. 测试用例
编写对应的测试用例，并引用规格说明：

```python
def test_get_realtime_energy_data():
    """
    Test Spec: SPEC-API-ENERGY-REALTIME-DATA-20250101.md#section-8.1
    验证获取设备实时能耗数据接口
    """
    response = client.get("/api/v1/energy/realtime?device_ids=1,2,3")
    assert response.status_code == 200
    assert response.json()["code"] == 0
```

### 4. 规格验证
完成实现后，运行规格验证工具：

```bash
# 验证 API 规格一致性
python tools/spec_validation/validate_api_spec.py

# 或使用 Make 命令
make spec-validate
```

## 开发流程

1. **阅读规格文档**
   - 仔细阅读规格文档的所有章节
   - 理解功能需求、业务逻辑、接口定义
   - 明确验收标准

2. **实现代码**
   - 按照规格定义实现功能
   - 添加规格引用注释
   - 遵循现有代码风格

3. **编写测试**
   - 为每个测试用例编写测试代码
   - 测试代码中引用规格章节
   - 确保测试覆盖率

4. **运行验证**
   - 运行规格验证工具
   - 运行单元测试
   - 运行集成测试

5. **提交代码**
   - 确保所有测试通过
   - 确保规格验证通过
   - 提交 Pull Request

## 验收标准
- [ ] 代码实现严格遵循规格文档
- [ ] 所有关键代码添加了规格引用注释
- [ ] 测试用例完整，覆盖规格中定义的所有场景
- [ ] 测试用例引用了规格章节
- [ ] 规格验证工具检查通过
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 代码符合编码规范
- [ ] 满足规格中定义的所有验收标准
```

#### 任务示例

**任务标题**：`[Impl] 能源模块 - 设备实时能耗数据查询 API`

**任务描述**：
```markdown
## 任务目标
按照规格文档实现设备实时能耗数据查询 API

## 规格文档
**必须严格遵循以下规格文档**：
- [SPEC-API-ENERGY-REALTIME-DATA-20250101.md](specs/backend/api/SPEC-API-ENERGY-REALTIME-DATA-20250101.md)

## 实现要求

### 1. 后端实现
在 `backend/app/api/energy.py` 或 `main.py` 中实现：

```python
# Spec: SPEC-API-ENERGY-REALTIME-DATA-20250101.md#section-2.2
# 功能说明：获取设备实时能耗数据
@router.get("/api/v1/energy/realtime")
async def get_realtime_energy_data(
    device_ids: str = Query(..., description="设备ID列表，逗号分隔"),
    metrics: str = Query("all", description="指标类型：all/power/energy")
):
    """
    获取设备实时能耗数据
    
    Spec Reference: SPEC-API-ENERGY-REALTIME-DATA-20250101.md
    """
    # 1. 解析设备ID列表
    # 2. 验证参数（最多50个设备）
    # 3. 查询实时数据（优先从缓存）
    # 4. 格式化响应
    pass
```

### 2. 测试用例
在 `tests/test_energy_api.py` 中添加：

```python
def test_get_realtime_energy_data_single_device():
    """
    Test Spec: SPEC-API-ENERGY-REALTIME-DATA-20250101.md#section-8.1.TC001
    验证查询单个设备
    """
    response = client.get("/api/v1/energy/realtime?device_ids=1")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert len(data["data"]) == 1

def test_get_realtime_energy_data_multiple_devices():
    """
    Test Spec: SPEC-API-ENERGY-REALTIME-DATA-20250101.md#section-8.1.TC002
    验证查询多个设备
    """
    response = client.get("/api/v1/energy/realtime?device_ids=1,2,3")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert len(data["data"]) == 3

def test_get_realtime_energy_data_invalid_ids():
    """
    Test Spec: SPEC-API-ENERGY-REALTIME-DATA-20250101.md#section-8.2.TC101
    验证设备ID格式错误
    """
    response = client.get("/api/v1/energy/realtime?device_ids=abc")
    assert response.status_code == 400
```

### 3. 运行验证
```bash
# 验证规格一致性
make spec-validate

# 运行测试
pytest tests/test_energy_api.py -v
```

## 验收标准
- [x] 接口路径为 `/api/v1/energy/realtime`
- [x] 支持 `device_ids` 和 `metrics` 查询参数
- [x] 响应格式符合规格定义
- [x] 实现了缓存机制（30秒）
- [x] 限制最多查询50个设备
- [x] 错误处理完善（参数验证、设备不存在）
- [x] 添加了规格引用注释
- [x] 测试用例覆盖所有场景
- [x] 规格验证通过
- [x] 所有测试通过
- [x] 响应时间 < 200ms
```

---

## 任务创建最佳实践

### 1. 任务粒度
- **规格任务**：一个规格任务对应一个独立的功能模块
- **实现任务**：一个实现任务对应一个规格文档

### 2. 任务依赖
- 实现任务必须依赖于规格任务
- 在规格任务完成并评审通过之前，不要创建实现任务

### 3. 任务标签
建议为任务添加标签：
- `spec` - 规格编写任务
- `impl` - 实现任务
- `api` - API 相关
- `frontend` - 前端相关
- `backend` - 后端相关

### 4. 任务优先级
- **P0**: 核心功能的规格和实现
- **P1**: 重要功能的规格和实现
- **P2**: 优化和改进

### 5. 规格变更
如果在实现过程中发现规格有问题，应该：
1. 暂停实现任务
2. 创建新的规格变更任务：`[Spec Change] {功能} - {变更说明}`
3. 使用 `specs/templates/SPEC_CHANGE_TEMPLATE.md` 模板
4. 评审通过后更新规格文档
5. 继续实现任务

---

## 完整示例：能源模块开发

### 任务 1: [Spec] 能源模块 - 实时能耗数据查询 API
- 创建规格文档
- 定义接口、参数、响应格式
- 编写测试用例和验收标准
- 提交评审

### 任务 2: [Impl] 能源模块 - 实时能耗数据查询 API（依赖任务1）
- 阅读规格文档
- 实现 API 接口
- 编写测试用例
- 运行规格验证
- 提交代码

### 任务 3: [Spec] 能源模块 - 能源趋势图表组件
- 创建组件规格文档
- 定义 Props、Events、Slots
- 编写使用示例
- 提交评审

### 任务 4: [Impl] 能源模块 - 能源趋势图表组件（依赖任务3）
- 阅读规格文档
- 实现 Vue 组件
- 编写组件测试
- 验证组件接口
- 提交代码

### 任务 5: [Impl] 能源模块 - 驾驶舱页面集成（依赖任务2、任务4）
- 集成 API 和组件
- 实现完整的页面功能
- 端到端测试
- 提交代码

---

## 常见问题

### Q1: 每个功能都需要规格文档吗？
A: 是的。所有新功能和重要变更都需要规格文档。简单的 bug 修复可以不需要完整规格，但应在代码注释中说明。

### Q2: 规格任务和实现任务可以合并吗？
A: 不建议。规格编写和代码实现是两个不同的阶段，分开可以确保：
- 规格文档得到充分的讨论和评审
- 实现者能够专注于按规格编码
- 规格文档可以作为独立的交付物

### Q3: 如何处理规格与实现不一致的情况？
A: 
1. 如果是规格问题，创建规格变更任务
2. 如果是实现偏离，修改代码使其符合规格
3. 使用规格验证工具检测不一致

### Q4: AI 能否同时完成规格和实现？
A: 可以，但建议分两个任务：
1. 第一个任务：让 AI 编写规格文档
2. 人工评审规格文档
3. 第二个任务：让 AI 按规格实现代码

这样可以确保规格文档的质量，避免 AI 自说自话。

---

## 总结

使用 Spec Coding 在 cto.new 创建任务时：

✅ **分阶段创建任务**：规格任务 → 评审 → 实现任务  
✅ **使用明确的任务标题**：`[Spec]` 和 `[Impl]` 前缀  
✅ **提供完整的任务描述**：包含目标、要求、验收标准  
✅ **引用规格文档**：实现任务必须明确引用规格文档  
✅ **使用验证工具**：确保规格与实现一致  

这样可以确保：
- 功能需求明确
- 实现质量可控
- 代码可维护
- 文档完整

---

**更多资源**：
- [Spec Coding 开发规范](./SPEC_CODING_GUIDE.md)
- [Spec Coding 快速入门](./SPEC_CODING_QUICKSTART.md)
- [规格基础设施说明](../SPEC_CODING_INFRASTRUCTURE.md)
