# 贡献指南

感谢您考虑为环控节能平台设备点位运维与批量控制模块做出贡献！

## 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发流程](#开发流程)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [测试要求](#测试要求)
- [文档要求](#文档要求)
- [代码审查](#代码审查)

## 行为准则

### 我们的承诺

为了营造开放和友好的环境，我们承诺：

- 使用包容和欢迎的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

### 不可接受的行为

- 使用性化语言或图像
- 人身攻击或侮辱性评论
- 公开或私下骚扰
- 未经明确许可发布他人的私人信息
- 其他在专业环境中被认为不适当的行为

## 如何贡献

### 报告 Bug

如果您发现 Bug，请通过 GitHub Issues 报告：

1. **使用清晰的标题**描述问题
2. **详细描述重现步骤**
3. **提供预期行为和实际行为**
4. **包含屏幕截图**（如果适用）
5. **提供环境信息**：
   - OS 版本
   - Python 版本
   - Node.js 版本
   - 浏览器版本（如果是前端问题）

### 建议新功能

我们欢迎新功能建议：

1. **检查是否已存在类似建议**
2. **清晰描述功能需求**
3. **解释为什么需要这个功能**
4. **提供使用场景示例**

### 提交代码

1. **Fork 项目**
2. **创建功能分支**：`git checkout -b feature/AmazingFeature`
3. **进行更改**
4. **添加测试**
5. **提交更改**：`git commit -m 'Add some AmazingFeature'`
6. **推送到分支**：`git push origin feature/AmazingFeature`
7. **创建 Pull Request**

## 开发流程

### 1. 设置开发环境

#### 后端开发环境

```bash
# 克隆仓库
git clone https://github.com/your-username/hk_tool_web.git
cd hk_tool_web

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装开发依赖
pip install -r requirements/development.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件填入实际配置

# 初始化数据库
python scripts/init_db.py
```

#### 前端开发环境

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 2. 创建功能分支

```bash
# 从 main 分支创建新分支
git checkout main
git pull origin main
git checkout -b feature/your-feature-name

# 或者修复 Bug
git checkout -b fix/bug-description
```

### 3. 进行开发

- 遵循代码规范
- 编写清晰的代码
- 添加必要的注释
- 编写单元测试
- 更新相关文档

### 4. 运行测试

```bash
# 运行所有测试
make test

# 运行后端测试
pytest

# 运行前端测试
cd frontend
npm run test

# 运行代码检查
make lint

# 格式化代码
make format
```

### 5. 提交代码

```bash
# 添加更改
git add .

# 提交更改（遵循提交规范）
git commit -m "feat: add new feature"

# 推送到远程
git push origin feature/your-feature-name
```

### 6. 创建 Pull Request

1. 访问 GitHub 仓库
2. 点击 "New Pull Request"
3. 选择您的分支
4. 填写 PR 描述：
   - 更改内容
   - 相关 Issue
   - 测试结果
   - 截图（如有）
5. 提交 PR

## 代码规范

### Python 代码规范

#### 格式化

使用 Black 格式化代码：

```bash
black .
```

#### 导入排序

使用 isort 排序导入：

```bash
isort .
```

#### 代码检查

使用 Flake8 检查代码：

```bash
flake8 .
```

#### 类型检查

使用 mypy 进行类型检查：

```bash
mypy .
```

#### 代码风格

- 遵循 PEP 8
- 最大行长：88 字符（Black 默认）
- 使用 4 个空格缩进
- 函数和类之间空两行
- 方法之间空一行

#### 命名约定

- 类名：PascalCase（`DeviceControlService`）
- 函数和变量：snake_case（`get_device_tree`）
- 常量：UPPER_CASE（`MAX_RETRIES`）
- 私有成员：前缀下划线（`_internal_method`）

#### 文档字符串

使用 Google 风格的文档字符串：

```python
def function_name(param1: str, param2: int) -> bool:
    """简短描述函数功能。

    详细描述函数的作用、使用方法等。

    Args:
        param1: 第一个参数的描述
        param2: 第二个参数的描述

    Returns:
        返回值的描述

    Raises:
        ValueError: 参数无效时抛出
        
    Example:
        >>> function_name("test", 42)
        True
    """
    pass
```

### JavaScript/Vue 代码规范

#### 格式化

使用 Prettier 格式化代码：

```bash
npm run format
```

#### 代码检查

使用 ESLint 检查代码：

```bash
npm run lint
```

#### 代码风格

- 使用 2 个空格缩进
- 使用单引号
- 语句末尾不加分号
- 使用尾逗号

#### 命名约定

- 组件名：PascalCase（`DeviceTree.vue`）
- 文件名：kebab-case（`device-tree.js`）
- 变量和函数：camelCase（`getDeviceList`）
- 常量：UPPER_CASE（`API_BASE_URL`）

#### Vue 组件结构

```vue
<template>
  <!-- 模板 -->
</template>

<script setup>
// 导入
import { ref, computed } from 'vue'

// Props
const props = defineProps({
  // ...
})

// Emits
const emit = defineEmits(['update'])

// 响应式数据
const data = ref(null)

// 计算属性
const computed Value = computed(() => {
  // ...
})

// 方法
function method() {
  // ...
}

// 生命周期
onMounted(() => {
  // ...
})
</script>

<style scoped>
/* 样式 */
</style>
```

## 提交规范

### Conventional Commits

我们使用 Conventional Commits 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type

- **feat**: 新功能
- **fix**: Bug 修复
- **docs**: 文档更新
- **style**: 代码格式（不影响代码运行）
- **refactor**: 重构（既不是新功能也不是 Bug 修复）
- **perf**: 性能优化
- **test**: 添加或修改测试
- **chore**: 构建过程或辅助工具的变动

#### Scope

可选，表示影响的范围：

- `api`: API 层
- `service`: 服务层
- `ui`: 前端界面
- `db`: 数据库
- `docs`: 文档
- `test`: 测试

#### Subject

- 使用祈使句，现在时态
- 首字母小写
- 不要以句号结束

#### 示例

```bash
# 添加新功能
git commit -m "feat(api): add device tree query endpoint"

# 修复 Bug
git commit -m "fix(ui): resolve button click issue in export page"

# 更新文档
git commit -m "docs: update API documentation"

# 性能优化
git commit -m "perf(service): optimize database query performance"
```

## 测试要求

### 测试覆盖率

- **总体覆盖率**: ≥ 80%
- **核心服务**: ≥ 90%
- **API 层**: ≥ 85%

### 编写测试

每个新功能或 Bug 修复都应该包含测试：

#### 后端测试

```python
import pytest
from fastapi.testclient import TestClient

def test_feature():
    """测试描述"""
    # Arrange
    client = TestClient(app)
    
    # Act
    response = client.get("/endpoint")
    
    # Assert
    assert response.status_code == 200
    assert "key" in response.json()
```

#### 前端测试

```javascript
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'

describe('Component', () => {
  it('renders properly', () => {
    const wrapper = mount(Component)
    expect(wrapper.text()).toContain('Expected text')
  })
})
```

### 运行测试

```bash
# 运行所有测试
make test

# 运行特定测试文件
pytest tests/test_specific.py

# 运行并查看覆盖率
pytest --cov=backend --cov-report=html
```

## 文档要求

### 代码文档

- 所有公共 API 必须有文档字符串
- 复杂逻辑需要内联注释
- 使用清晰的变量和函数名

### API 文档

- 使用 FastAPI 的自动文档功能
- 为每个端点添加描述
- 提供请求和响应示例

### 用户文档

更新以下文档（如需要）：

- `README.md`: 项目介绍和快速开始
- `docs/`: 详细文档
- `CHANGELOG.md`: 更改日志

## 代码审查

### 提交 Pull Request 前

- [ ] 代码符合规范
- [ ] 所有测试通过
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 提交信息符合规范
- [ ] 没有合并冲突

### 审查标准

审查者将关注：

1. **代码质量**
   - 是否遵循代码规范
   - 是否有明显的问题
   - 是否有性能问题

2. **测试**
   - 是否有足够的测试
   - 测试是否覆盖边界情况

3. **文档**
   - 是否有清晰的注释
   - 是否更新了相关文档

4. **设计**
   - 是否符合项目架构
   - 是否有更好的实现方式

### 响应审查意见

- 及时响应审查意见
- 清晰说明您的想法
- 虚心接受建设性批评
- 进行必要的修改

## 发布流程

### 版本号

遵循语义化版本（Semantic Versioning）：

- **主版本号**：不兼容的 API 更改
- **次版本号**：向后兼容的新功能
- **修订号**：向后兼容的 Bug 修复

### 更新日志

在 `CHANGELOG.md` 中记录更改：

```markdown
## [1.2.0] - 2024-01-15

### Added
- 新功能描述

### Changed
- 更改描述

### Fixed
- Bug 修复描述

### Deprecated
- 即将废弃的功能
```

## 获取帮助

如果您在贡献过程中遇到问题：

1. **查看文档**：阅读项目文档
2. **搜索 Issues**：查看是否有类似问题
3. **提问**：在 Issues 中提问
4. **联系维护者**：发送邮件

## 许可证

通过贡献代码，您同意您的贡献将遵循项目的 MIT 许可证。

## 致谢

感谢所有为项目做出贡献的人！

---

**Happy Contributing! 🎉**
