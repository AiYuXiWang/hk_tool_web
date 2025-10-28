# Spec Coding 快速入门

本文档提供 Spec Coding 开发流程的快速入门指南。

## 快速开始

### 1. 创建新的 API 规格

```bash
# 使用工具创建 API 规格文档
python tools/create_spec.py --type api --module energy --name realtime-data --author "张三"

# 或使用 Make 命令（Windows 需要安装 Make 工具）
make spec-new-api
```

### 2. 编写规格文档

根据创建的模板，填写以下关键部分：

- **功能概述**：说明 API 的用途和业务价值
- **接口定义**：定义请求/响应格式、参数、错误码
- **业务逻辑**：描述处理流程和业务规则
- **验收标准**：明确可测试的验收条件

### 3. 提交规格评审

- 将规格文档提交到 Git
- 创建 Pull Request
- 标记相关评审人
- 等待评审通过

### 4. 按规格实现代码

评审通过后，开始编码：

```python
# Spec: SPEC-API-ENERGY-REALTIME-DATA-20250101.md#section-2.2
# 功能说明：获取设备实时能耗数据
@router.get("/api/v1/energy/realtime")
async def get_realtime_energy_data(
    device_id: int = Query(..., description="设备ID")
):
    """
    获取设备实时能耗数据
    
    Spec Reference: SPEC-API-ENERGY-REALTIME-DATA-20250101.md
    """
    # 实现代码
    pass
```

### 5. 编写测试用例

确保测试用例覆盖规格中的所有验收标准：

```python
def test_get_realtime_energy_data():
    """
    Test Spec: SPEC-API-ENERGY-REALTIME-DATA-20250101.md#section-9.1
    验证获取设备实时能耗数据接口
    """
    response = client.get("/api/v1/energy/realtime?device_id=1")
    assert response.status_code == 200
    assert response.json()["code"] == 0
```

### 6. 运行规格验证

```bash
# 验证 API 规格与实现的一致性
python tools/spec_validation/validate_api_spec.py

# 或使用 Make 命令
make spec-validate
```

## 目录结构示例

```
project/
├── specs/
│   ├── backend/
│   │   ├── api/
│   │   │   └── SPEC-API-ENERGY-REALTIME-DATA-20250101.md
│   │   ├── models/
│   │   │   └── SPEC-MODEL-ENERGY-DEVICE-20250101.md
│   │   └── services/
│   │       └── SPEC-SERVICE-ENERGY-CALCULATION-20250101.md
│   └── frontend/
│       ├── components/
│       │   └── SPEC-COMPONENT-ENERGY-CHART-20250101.md
│       └── views/
│           └── SPEC-VIEW-ENERGY-DASHBOARD-20250101.md
```

## 规格文档命名规范

| 类型 | 命名格式 | 示例 |
|------|----------|------|
| API | `SPEC-API-{模块}-{功能}-{日期}.md` | `SPEC-API-ENERGY-REALTIME-DATA-20250101.md` |
| 数据模型 | `SPEC-MODEL-{模块}-{模型}-{日期}.md` | `SPEC-MODEL-ENERGY-DEVICE-20250101.md` |
| 服务 | `SPEC-SERVICE-{模块}-{服务}-{日期}.md` | `SPEC-SERVICE-ENERGY-CALCULATION-20250101.md` |
| 组件 | `SPEC-COMPONENT-{模块}-{组件}-{日期}.md` | `SPEC-COMPONENT-ENERGY-CHART-20250101.md` |
| 页面 | `SPEC-VIEW-{模块}-{页面}-{日期}.md` | `SPEC-VIEW-ENERGY-DASHBOARD-20250101.md` |

## 常用命令

```bash
# 创建 API 规格
python tools/create_spec.py --type api --module {模块} --name {功能}

# 创建数据模型规格
python tools/create_spec.py --type model --module {模块} --name {模型}

# 创建组件规格
python tools/create_spec.py --type component --module {模块} --name {组件}

# 验证规格一致性
python tools/spec_validation/validate_api_spec.py
```

## 最佳实践

### 1. 规格编写

- ✅ 使用明确、无歧义的语言
- ✅ 提供完整的示例
- ✅ 包含所有边界情况
- ✅ 定义清晰的验收标准
- ❌ 避免使用模糊的描述
- ❌ 不要遗漏错误处理

### 2. 代码实现

- ✅ 严格遵循规格定义
- ✅ 添加规格引用注释
- ✅ 编写对应的测试用例
- ✅ 保持代码与规格同步
- ❌ 不要擅自偏离规格
- ❌ 不要跳过测试

### 3. 规格变更

如需变更规格，使用规格变更流程：

```bash
# 1. 创建变更请求文档
cp specs/templates/SPEC_CHANGE_TEMPLATE.md docs/changes/SPEC-CHANGE-001-20250101.md

# 2. 填写变更内容

# 3. 提交评审

# 4. 评审通过后更新规格文档（增加版本号）

# 5. 更新代码实现
```

## 规格评审检查清单

在提交规格评审前，请确保：

- [ ] 功能描述清晰完整
- [ ] API 接口定义明确（路径、方法、参数、响应）
- [ ] 数据模型设计合理
- [ ] 业务逻辑流程清晰
- [ ] 错误处理完善
- [ ] 验收标准可测试
- [ ] 性能要求明确
- [ ] 安全考虑充分
- [ ] 包含使用示例
- [ ] 文档格式规范

## 代码实现检查清单

在提交代码前，请确保：

- [ ] 严格按照规格实现
- [ ] 添加了规格引用注释
- [ ] 编写了对应的测试用例
- [ ] 测试用例引用了规格说明
- [ ] 通过了规格验证工具的检查
- [ ] 更新了相关文档
- [ ] 代码通过了所有测试
- [ ] 代码符合编码规范

## 常见问题

### Q: 小的 bug 修复也需要规格吗？

A: 简单的 bug 修复不需要完整的规格文档，但应该在相关规格文档中添加修订说明，或者在代码注释中说明修复的问题。

### Q: 规格文档太长，写不完怎么办？

A: 可以采用迭代的方式，先完成核心规格（接口定义、数据模型、验收标准），然后在实现过程中逐步完善细节。

### Q: 实现过程中发现规格有问题怎么办？

A: 应该暂停实现，提交规格变更请求，评审通过后再继续。不要在实现中擅自偏离规格。

### Q: 如何确保规格与代码保持一致？

A: 使用自动化验证工具，在 CI/CD 流程中强制执行，同时在代码评审时也要检查是否符合规格。

## 参考资源

- [Spec Coding 完整指南](./SPEC_CODING_GUIDE.md)
- [API 规格模板](../specs/templates/API_SPEC_TEMPLATE.md)
- [数据模型规格模板](../specs/templates/MODEL_SPEC_TEMPLATE.md)
- [组件规格模板](../specs/templates/COMPONENT_SPEC_TEMPLATE.md)
- [规格变更模板](../specs/templates/SPEC_CHANGE_TEMPLATE.md)

## 下一步

1. 阅读 [Spec Coding 完整指南](./SPEC_CODING_GUIDE.md)
2. 查看 [规格模板](../specs/templates/)
3. 尝试创建第一个规格文档
4. 按规格实现第一个功能

---

**需要帮助？**

如有任何问题，请查阅完整的 [Spec Coding 开发规范](./SPEC_CODING_GUIDE.md) 或联系团队负责人。
