# 工程结构优化共识文档

## 明确的需求描述

### 核心目标
对环控节能平台项目进行全面的结构规范化改造，建立符合企业级标准的工程架构，提升代码质量、可维护性和开发效率。

### 具体需求
1. **目录结构标准化**: 建立清晰的分层目录结构
2. **代码模块化重构**: 实现高内聚、低耦合的模块设计
3. **命名规范统一**: 建立并执行一致的命名标准
4. **配置管理集中化**: 统一配置文件管理和环境变量处理
5. **依赖管理优化**: 规范化依赖声明和版本管理
6. **开发工具链完善**: 建立代码质量检查和自动化构建流程

## 技术实现方案

### 1. 目录结构重组方案

#### 后端目录结构（目标）
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI应用入口
│   ├── core/                   # 核心配置和工具
│   │   ├── __init__.py
│   │   ├── config.py           # 配置管理
│   │   ├── database.py         # 数据库连接
│   │   ├── security.py         # 安全相关
│   │   └── exceptions.py       # 异常定义
│   ├── api/                    # API路由
│   │   ├── __init__.py
│   │   ├── deps.py             # 依赖注入
│   │   ├── v1/                 # API版本管理
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/      # 端点实现
│   │   │   │   ├── __init__.py
│   │   │   │   ├── control.py
│   │   │   │   ├── export.py
│   │   │   │   ├── energy.py
│   │   │   │   └── audit.py
│   │   │   └── api.py          # 路由聚合
│   ├── services/               # 业务服务层
│   │   ├── __init__.py
│   │   ├── control_service.py
│   │   ├── export_service.py
│   │   ├── audit_service.py
│   │   └── energy_service.py
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── control.py
│   │   ├── export.py
│   │   └── audit.py
│   ├── schemas/                # Pydantic模式
│   │   ├── __init__.py
│   │   ├── control.py
│   │   ├── export.py
│   │   └── audit.py
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       ├── datetime_utils.py
│       ├── file_utils.py
│       └── validation.py
├── tests/                      # 测试文件
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   ├── test_services/
│   └── test_utils/
├── config/                     # 配置文件
│   ├── __init__.py
│   ├── electricity_config.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py
│       ├── development.py
│       ├── production.py
│       └── testing.py
├── scripts/                    # 脚本文件
│   ├── start_server.py
│   └── init_db.py
├── requirements/               # 依赖管理
│   ├── base.txt
│   ├── development.txt
│   ├── production.txt
│   └── testing.txt
└── pyproject.toml             # 项目配置
```

#### 前端目录结构（优化）
```
frontend/
├── src/
│   ├── api/                    # API接口
│   │   ├── index.ts
│   │   ├── types.ts
│   │   ├── control.ts
│   │   ├── export.ts
│   │   ├── energy.ts
│   │   └── audit.ts
│   ├── components/             # 通用组件
│   │   ├── common/             # 基础组件
│   │   ├── business/           # 业务组件
│   │   └── layout/             # 布局组件
│   ├── views/                  # 页面组件
│   │   ├── device/
│   │   ├── energy/
│   │   └── export/
│   ├── router/                 # 路由配置
│   ├── stores/                 # 状态管理
│   ├── utils/                  # 工具函数
│   ├── styles/                 # 样式文件
│   ├── assets/                 # 静态资源
│   └── types/                  # TypeScript类型定义
├── public/                     # 公共资源
├── tests/                      # 测试文件
├── config/                     # 配置文件
└── docs/                       # 文档
```

### 2. 代码模块化重构方案

#### 服务层重构
- **单一职责原则**: 每个服务类只负责一个业务域
- **依赖注入**: 使用FastAPI的依赖注入系统
- **接口抽象**: 定义清晰的服务接口
- **错误处理**: 统一的异常处理机制

#### 数据层重构
- **模型分离**: 数据库模型与API模型分离
- **仓储模式**: 实现数据访问层抽象
- **连接管理**: 统一的数据库连接管理

### 3. 命名规范统一方案

#### Python命名规范
- **文件名**: snake_case（如：control_service.py）
- **类名**: PascalCase（如：ControlService）
- **函数名**: snake_case（如：get_device_tree）
- **变量名**: snake_case（如：device_list）
- **常量名**: UPPER_SNAKE_CASE（如：DEFAULT_TIMEOUT）

#### TypeScript命名规范
- **文件名**: kebab-case（如：control-service.ts）
- **类名**: PascalCase（如：ControlService）
- **接口名**: PascalCase，以I开头（如：IDeviceInfo）
- **函数名**: camelCase（如：getDeviceTree）
- **变量名**: camelCase（如：deviceList）
- **常量名**: UPPER_SNAKE_CASE（如：DEFAULT_TIMEOUT）

#### API路径命名
- **RESTful风格**: /api/v1/devices/{id}/controls
- **小写字母**: 使用小写字母和连字符
- **复数形式**: 资源名使用复数形式

### 4. 配置管理标准化方案

#### 环境配置分离
```python
# config/settings/base.py
class BaseSettings(BaseSettings):
    app_name: str = "HK Tool Web"
    debug: bool = False
    api_prefix: str = "/api/v1"
    
    # 数据库配置
    database_url: str
    
    # 外部服务配置
    hk_platform_token: str
    hk_login_user: str
    hk_login_pwd: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# config/settings/development.py
class DevelopmentSettings(BaseSettings):
    debug: bool = True
    log_level: str = "DEBUG"

# config/settings/production.py
class ProductionSettings(BaseSettings):
    debug: bool = False
    log_level: str = "INFO"
```

#### 配置加载机制
```python
from functools import lru_cache
from typing import Type

@lru_cache()
def get_settings() -> BaseSettings:
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()
```

### 5. 依赖管理优化方案

#### 后端依赖分层
```
requirements/
├── base.txt              # 基础依赖
├── development.txt       # 开发依赖
├── production.txt        # 生产依赖
└── testing.txt          # 测试依赖
```

#### 前端依赖管理
- **版本锁定**: 使用package-lock.json锁定版本
- **依赖分类**: 区分dependencies和devDependencies
- **安全检查**: 集成npm audit

### 6. 构建流程改进方案

#### 代码质量检查
```yaml
# .github/workflows/quality.yml
name: Code Quality
on: [push, pull_request]
jobs:
  backend-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10.11'
      - name: Install dependencies
        run: |
          pip install -r requirements/development.txt
      - name: Run linting
        run: |
          flake8 backend/
          black --check backend/
          isort --check-only backend/
      - name: Run tests
        run: pytest backend/tests/
  
  frontend-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: cd frontend && npm ci
      - name: Run linting
        run: cd frontend && npm run lint
      - name: Run tests
        run: cd frontend && npm run test
      - name: Build
        run: cd frontend && npm run build
```

## 技术约束和集成方案

### 兼容性约束
1. **API兼容性**: 保持现有API接口不变
2. **数据库兼容性**: 保持现有数据库结构
3. **部署兼容性**: 支持现有部署方式
4. **配置兼容性**: 支持现有配置文件格式

### 集成方案
1. **渐进式迁移**: 分模块逐步迁移，避免大爆炸式重构
2. **向后兼容**: 保留旧接口，逐步废弃
3. **文档同步**: 每个迁移步骤都有对应文档
4. **测试保障**: 每个迁移步骤都有完整测试

## 任务边界限制

### 包含范围
- ✅ 文件和目录重组
- ✅ 代码结构调整
- ✅ 配置文件整理
- ✅ 依赖管理优化
- ✅ 开发工具配置
- ✅ 文档更新

### 不包含范围
- ❌ 业务逻辑修改
- ❌ 数据库结构变更
- ❌ 第三方服务变更
- ❌ UI/UX改进

## 验收标准

### 结构验收标准
1. **目录结构**: 符合标准Python/Vue项目结构
2. **模块划分**: 职责清晰，依赖关系简单
3. **命名规范**: 100%符合制定的命名标准
4. **配置管理**: 环境配置完全分离
5. **依赖管理**: 依赖声明清晰，版本锁定

### 质量验收标准
1. **代码质量**: 通过所有linting检查
2. **测试覆盖**: 核心功能测试覆盖率>80%
3. **文档完整**: 所有变更都有对应文档
4. **部署成功**: 重构后系统可正常部署运行
5. **性能保持**: 重构不影响系统性能

### 可维护性验收标准
1. **新人上手**: 新开发者可在1天内理解项目结构
2. **功能扩展**: 新功能开发遵循既定模式
3. **问题定位**: 错误可快速定位到具体模块
4. **代码复用**: 通用功能可轻松复用

## 实施计划

### 阶段1: 基础结构搭建（1-2天）
- 创建新的目录结构
- 建立配置管理体系
- 设置开发工具链

### 阶段2: 后端重构（2-3天）
- 迁移服务文件到新结构
- 重构API路由
- 优化数据模型

### 阶段3: 前端优化（1-2天）
- 优化组件结构
- 完善TypeScript类型
- 统一样式管理

### 阶段4: 测试和文档（1天）
- 完善测试用例
- 更新项目文档
- 验证功能完整性

## 风险控制

### 主要风险
1. **功能回归**: 重构可能引入新bug
2. **部署问题**: 新结构可能影响部署
3. **学习成本**: 团队需要适应新结构

### 缓解措施
1. **分阶段实施**: 每阶段都验证功能完整性
2. **完整测试**: 每个变更都有对应测试
3. **文档支持**: 提供详细的迁移和使用文档
4. **回滚方案**: 每个阶段都可以快速回滚