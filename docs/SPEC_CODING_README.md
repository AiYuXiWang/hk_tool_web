# Spec Coding 文档导航

本目录包含完整的 Spec Coding 开发规范和指南。

## 📚 文档列表

### 核心文档

1. **[Spec Coding 开发规范](SPEC_CODING_GUIDE.md)** ⭐️
   - 完整的开发流程和规范
   - 规格文档编写指南
   - 实现和验证流程
   - 质量保证和最佳实践
   - **适合**：需要深入了解 Spec Coding 全流程的开发者

2. **[Spec Coding 快速入门](SPEC_CODING_QUICKSTART.md)** 🚀
   - 快速上手指南
   - 常用命令和工具
   - 实践示例
   - 常见问题解答
   - **适合**：希望快速开始使用 Spec Coding 的开发者

3. **[cto.new 任务创建指南](CTO_NEW_SPEC_CODING_WORKFLOW.md)** 💡
   - 如何在 cto.new 平台创建 Spec Coding 任务
   - 规格任务和实现任务的模板
   - 任务创建最佳实践
   - 完整的任务示例
   - **适合**：使用 cto.new 平台进行项目管理的团队

### 基础设施文档

4. **[Spec Coding 基础设施说明](../SPEC_CODING_INFRASTRUCTURE.md)** 🏗️
   - 已搭建的基础设施概览
   - 目录结构说明
   - 开发工具使用
   - 命名规范和流程
   - **适合**：需要了解项目 Spec Coding 基础设施的开发者

## 🎯 快速选择

### 我是新手，如何开始？
1. 先阅读 [Spec Coding 快速入门](SPEC_CODING_QUICKSTART.md)
2. 查看示例规格文档 [SPEC-API-ENERGY-REALTIME-DATA-20250101-EXAMPLE.md](../specs/backend/api/SPEC-API-ENERGY-REALTIME-DATA-20250101-EXAMPLE.md)
3. 使用工具创建第一个规格文档：
   ```bash
   python tools/create_spec.py --type api --module test --name hello
   ```

### 我要在 cto.new 创建任务
直接查看 [cto.new 任务创建指南](CTO_NEW_SPEC_CODING_WORKFLOW.md)，里面有详细的任务模板。

### 我需要了解完整的规范
阅读 [Spec Coding 开发规范](SPEC_CODING_GUIDE.md)，这是最完整的参考文档。

### 我想了解项目的 Spec Coding 基础设施
查看 [Spec Coding 基础设施说明](../SPEC_CODING_INFRASTRUCTURE.md)。

## 📁 相关资源

### 规格模板
- [API 规格模板](../specs/templates/API_SPEC_TEMPLATE.md)
- [数据模型规格模板](../specs/templates/MODEL_SPEC_TEMPLATE.md)
- [组件规格模板](../specs/templates/COMPONENT_SPEC_TEMPLATE.md)
- [规格变更模板](../specs/templates/SPEC_CHANGE_TEMPLATE.md)

### 示例文档
- [API 规格示例](../specs/backend/api/SPEC-API-ENERGY-REALTIME-DATA-20250101-EXAMPLE.md)

### 工具
- 规格创建工具：`tools/create_spec.py`
- 规格验证工具：`tools/spec_validation/validate_api_spec.py`

## 🔄 典型工作流程

```
1. 需求分析
   ↓
2. 创建规格任务（在 cto.new）
   ↓
3. 编写规格文档
   - 使用工具: python tools/create_spec.py
   - 填写模板内容
   ↓
4. 提交规格评审
   ↓
5. 创建实现任务（在 cto.new）
   ↓
6. 按规格实现代码
   - 添加规格引用注释
   - 编写测试用例
   ↓
7. 运行规格验证
   - make spec-validate
   ↓
8. 提交代码
   ↓
9. 代码评审和验收
```

## ❓ 常见问题

### Q: 必须使用 Spec Coding 吗？
A: 是的。对于所有新功能和重要变更，必须先编写规格文档。

### Q: 规格文档写不完怎么办？
A: 可以采用迭代方式，先完成核心部分（接口定义、数据模型、验收标准），再逐步完善。

### Q: 发现规格有问题怎么办？
A: 使用规格变更流程，创建变更请求，评审通过后更新规格。

### Q: 如何验证规格与代码一致？
A: 使用规格验证工具：`make spec-validate`

## 📞 需要帮助？

1. 查阅相关文档
2. 查看示例规格
3. 联系团队负责人
4. 在项目中搜索类似的规格文档作为参考

---

**最后更新**: 2025-01-01  
**维护者**: 开发团队
