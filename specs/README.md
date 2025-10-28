# Spec 文档目录

此目录用于存放所有基于 Spec Coding 流程编写的规格说明文档。目录结构如下：

```
specs/
├── backend/           # 后端规格
│   ├── api/           # API 规格
│   ├── services/      # 服务规格
│   └── models/        # 数据模型规格
├── frontend/          # 前端规格
│   ├── views/         # 页面规格
│   ├── components/    # 组件规格
│   └── stores/        # 状态管理规格
├── integration/       # 集成与跨域规格
└── templates/         # 规格模板（勿直接修改）
```

## 使用说明

1. **创建规格文档**
   - 在对应目录下创建新的规格文档
   - 命名格式：`SPEC-{类型}-{模块}-{功能}-{日期}.md`
   - 例如：`SPEC-API-ENERGY-REALTIME-DATA-20250101.md`

2. **引用模板**
   - 所有规格文档都应基于 `templates/` 目录中的模板创建
   - 如需新增模板，请先进行讨论并更新 `SPEC_CODING_GUIDE.md`

3. **版本管理**
   - 每个规格文档必须包含版本历史表格
   - 变更需通过 `templates/SPEC_CHANGE_TEMPLATE.md`

4. **审核流程**
   - Spec 文档创建后需提交评审
   - 评审结论和状态需记录在文档头部元数据中

5. **实现要求**
   - 代码实现必须严格遵循规格说明
   - 关键代码处需添加 `Spec:` 引用注释，指向对应规格文档

6. **验证工具**
   - 使用 `tools/spec_validation/validate_api_spec.py` 验证 API 规格
   - 后续将补充更多自动化验证工具

---

如对规范有疑问，请参考 `docs/SPEC_CODING_GUIDE.md`。
