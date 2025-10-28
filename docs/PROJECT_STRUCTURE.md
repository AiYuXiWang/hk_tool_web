# 项目结构说明

## 概述

本项目是一个基于 FastAPI + Vue 3 的环控节能平台设备点位运维与批量控制模块，采用前后端分离架构。

## 目录结构

```
hk_tool_web/
├── .github/                           # GitHub 配置文件
│   └── workflows/                     # CI/CD 工作流
├── backend/                           # 后端模块化代码
│   ├── app/                          # 应用核心代码
│   │   ├── api/                      # API 路由模块
│   │   │   ├── energy_dashboard.py  # 能源驾驶舱 API
│   │   │   ├── data_upload.py       # 数据上传 API
│   │   │   └── v1/                   # API v1 版本
│   │   ├── config/                   # 配置模块
│   │   │   └── electricity_config.py # 电力配置
│   │   ├── core/                     # 核心功能
│   │   │   ├── dependencies.py       # 依赖注入
│   │   │   └── exceptions.py         # 异常处理
│   │   ├── middleware/               # 中间件
│   │   │   ├── error_handler.py      # 错误处理
│   │   │   ├── response_formatter.py # 响应格式化
│   │   │   ├── compression.py        # 压缩中间件
│   │   │   ├── validation.py         # 验证中间件
│   │   │   ├── rate_limiter.py       # 限流中间件
│   │   │   └── logging.py            # 日志中间件
│   │   ├── models/                   # 数据模型
│   │   │   ├── energy.py             # 能源模型
│   │   │   ├── device.py             # 设备模型
│   │   │   └── response.py           # 响应模型
│   │   ├── services/                 # 业务服务层
│   │   │   ├── energy_service.py     # 能源服务
│   │   │   └── data_service.py       # 数据服务
│   │   └── utils/                    # 工具函数
│   ├── config/                       # 环境配置
│   │   └── environments/             # 环境配置文件
│   └── tests/                        # 后端测试
│       ├── __init__.py
│       └── test_energy_service.py
├── config/                           # 配置文件目录
│   ├── database/                     # 数据库配置
│   └── stations/                     # 站点配置
├── docs/                             # 项目文档
│   ├── openapi/                      # OpenAPI 文档
│   ├── 工程结构优化/                  # 工程优化文档
│   ├── 线路配置修复/                  # 线路配置文档
│   ├── 界面功能修复/                  # 界面修复文档
│   ├── 异步导出功能/                  # 异步导出文档
│   ├── data_source_fix/              # 数据源修复文档
│   ├── PROJECT_STRUCTURE.md          # 项目结构说明（本文件）
│   ├── TESTING.md                    # 测试文档
│   ├── CONTRIBUTING.md               # 贡献指南
│   └── *.md                          # 其他文档
├── frontend/                         # Vue.js 前端应用
│   ├── public/                       # 静态资源
│   ├── src/                          # 源代码
│   │   ├── api/                      # API 封装
│   │   │   ├── device.js             # 设备 API
│   │   │   ├── energy.js             # 能源 API
│   │   │   ├── export.js             # 导出 API
│   │   │   └── http.js               # HTTP 客户端
│   │   ├── components/               # 组件
│   │   │   ├── common/               # 通用组件
│   │   │   ├── cockpit/              # 驾驶舱组件
│   │   │   ├── enhanced/             # 增强组件
│   │   │   ├── feedback/             # 反馈组件
│   │   │   └── layout/               # 布局组件
│   │   ├── composables/              # 组合式函数
│   │   ├── router/                   # 路由配置
│   │   ├── stores/                   # 状态管理
│   │   │   ├── app.js                # 应用状态
│   │   │   ├── device.js             # 设备状态
│   │   │   ├── energy.js             # 能源状态
│   │   │   └── export.js             # 导出状态
│   │   ├── utils/                    # 工具函数
│   │   ├── views/                    # 页面视图
│   │   │   ├── DataExport.vue        # 数据导出
│   │   │   ├── DeviceOverview.vue    # 设备总览
│   │   │   ├── EnergyCockpit.vue     # 能源驾驶舱
│   │   │   └── EnhancedDataExport.vue # 增强导出
│   │   ├── App.vue                   # 根组件
│   │   └── main.js                   # 入口文件
│   ├── tests/                        # 前端测试
│   │   ├── unit/                     # 单元测试
│   │   └── e2e/                      # E2E 测试
│   ├── index.html                    # HTML 模板
│   ├── package.json                  # 依赖配置
│   ├── vite.config.js                # Vite 配置
│   └── vitest.config.js              # 测试配置
├── logs/                             # 日志目录
├── requirements/                     # Python 依赖管理
│   ├── base.txt                      # 基础依赖
│   ├── development.txt               # 开发依赖
│   ├── production.txt                # 生产依赖
│   └── testing.txt                   # 测试依赖
├── scripts/                          # 脚本工具
│   ├── restart_and_test.py           # 重启测试脚本
│   ├── restart_and_test.sh           # Linux 重启脚本
│   ├── restart_and_test.bat          # Windows 重启脚本
│   └── uv_setup.ps1                  # uv 环境设置脚本
├── templates/                        # HTML 模板
├── tests/                            # 主要测试目录
│   ├── __init__.py
│   ├── conftest.py                   # pytest 配置
│   ├── test_energy_api.py            # 能源 API 测试
│   ├── test_energy_edge_cases.py     # 边界测试
│   ├── test_frontend_backend_integration.py # 集成测试
│   ├── test_control_service.py       # 控制服务测试
│   ├── test_export_service.py        # 导出服务测试
│   ├── test_audit_service.py         # 审计服务测试
│   └── test_main_api.py              # 主 API 测试
├── .env.example                      # 环境变量示例
├── .flake8                           # Flake8 配置
├── .gitignore                        # Git 忽略文件
├── .pre-commit-config.yaml           # Pre-commit 配置
├── .prettierrc                       # Prettier 配置
├── .python-version                   # Python 版本
├── audit_service.py                  # 审计服务
├── config_electricity.py             # 电力配置
├── control_service.py                # 控制服务
├── db_config.py                      # 数据库配置
├── export_service.py                 # 导出服务
├── logger_config.py                  # 日志配置
├── main.py                           # FastAPI 主应用
├── models.py                         # 数据模型
├── Makefile                          # Make 命令
├── pyproject.toml                    # Python 项目配置
├── README.md                         # 项目说明
└── requirements.txt                  # Python 依赖（兼容）
```

## 模块说明

### 1. 后端模块 (Backend)

#### 1.1 API 层 (`backend/app/api/`)
- **energy_dashboard.py**: 能源驾驶舱 API，提供 KPI、实时数据、趋势分析等接口
- **data_upload.py**: 数据上传 API，处理文件上传和数据验证
- **v1/**: API v1 版本路由

#### 1.2 配置层 (`backend/app/config/`)
- **electricity_config.py**: 电力和站点配置管理
- **environments/**: 环境特定配置（开发、测试、生产）

#### 1.3 核心层 (`backend/app/core/`)
- **dependencies.py**: FastAPI 依赖注入
- **exceptions.py**: 自定义异常类

#### 1.4 中间件层 (`backend/app/middleware/`)
- **error_handler.py**: 全局错误处理
- **response_formatter.py**: 统一响应格式化
- **compression.py**: 响应压缩
- **validation.py**: 请求验证
- **rate_limiter.py**: API 限流
- **logging.py**: 请求日志记录

#### 1.5 服务层 (`backend/app/services/`)
- **energy_service.py**: 能源数据业务逻辑
- **data_service.py**: 数据处理业务逻辑

#### 1.6 模型层 (`backend/app/models/`)
- **energy.py**: 能源数据模型
- **device.py**: 设备数据模型
- **response.py**: API 响应模型

### 2. 前端模块 (Frontend)

#### 2.1 API 封装 (`frontend/src/api/`)
- **device.js**: 设备相关 API
- **energy.js**: 能源相关 API
- **export.js**: 导出相关 API
- **http.js**: HTTP 客户端配置

#### 2.2 组件 (`frontend/src/components/`)
- **common/**: 通用基础组件（按钮、表单、表格等）
- **cockpit/**: 能源驾驶舱专用组件
- **enhanced/**: 增强功能组件
- **feedback/**: 用户反馈组件（加载、错误等）
- **layout/**: 布局组件（头部、标签页等）

#### 2.3 视图 (`frontend/src/views/`)
- **DeviceOverview.vue**: 设备总览页面
- **DataExport.vue**: 数据导出页面
- **EnergyCockpit.vue**: 能源驾驶舱页面
- **EnhancedDataExport.vue**: 增强导出页面

#### 2.4 状态管理 (`frontend/src/stores/`)
- **app.js**: 应用全局状态
- **device.js**: 设备状态管理
- **energy.js**: 能源数据状态
- **export.js**: 导出任务状态

### 3. 根目录服务文件

#### 3.1 核心服务
- **main.py**: FastAPI 主应用入口，路由配置和中间件设置
- **control_service.py**: 设备控制核心服务，处理点位查询和写值
- **export_service.py**: 数据导出服务，支持 Excel 和 CSV
- **audit_service.py**: 操作审计服务，记录用户操作日志

#### 3.2 配置文件
- **db_config.py**: 数据库连接配置
- **logger_config.py**: 日志配置
- **config_electricity.py**: 电力系统配置
- **models.py**: 共享数据模型

### 4. 配置目录 (config/)

#### 4.1 数据库配置 (`config/database/`)
多站点数据库连接配置

#### 4.2 站点配置 (`config/stations/`)
地铁线路和站点配置信息

### 5. 测试目录 (tests/)

#### 5.1 API 测试
- **test_energy_api.py**: 能源 API 测试
- **test_main_api.py**: 主 API 测试

#### 5.2 服务测试
- **test_control_service.py**: 控制服务单元测试
- **test_export_service.py**: 导出服务单元测试
- **test_audit_service.py**: 审计服务单元测试

#### 5.3 集成测试
- **test_frontend_backend_integration.py**: 前后端集成测试
- **test_energy_edge_cases.py**: 边界情况测试

### 6. 文档目录 (docs/)

#### 6.1 技术文档
- **PROJECT_STRUCTURE.md**: 项目结构说明
- **TESTING.md**: 测试文档
- **CONTRIBUTING.md**: 贡献指南
- **ENERGY_BACKEND_PLAN.md**: 能源后端规划
- **INTEGRATION_TEST_PLAN.md**: 集成测试计划

#### 6.2 功能文档
- **工程结构优化/**: 工程结构优化记录
- **线路配置修复/**: 线路配置修复文档
- **界面功能修复/**: UI 修复文档
- **异步导出功能/**: 异步导出实现文档

## 技术架构

### 后端技术栈
- **FastAPI**: 高性能 Python Web 框架
- **Python 3.10**: 编程语言
- **MySQL**: 关系型数据库
- **aiohttp**: 异步 HTTP 客户端
- **pandas**: 数据处理
- **openpyxl**: Excel 文件操作

### 前端技术栈
- **Vue 3**: 渐进式 JavaScript 框架
- **Vite**: 前端构建工具
- **Element Plus**: Vue 3 组件库
- **Pinia**: 状态管理
- **Axios**: HTTP 客户端
- **ECharts**: 数据可视化

### 开发工具
- **pytest**: Python 测试框架
- **Vitest**: Vue 测试框架
- **ESLint**: JavaScript 代码检查
- **Prettier**: 代码格式化
- **Black**: Python 代码格式化
- **isort**: Python 导入排序
- **mypy**: Python 类型检查

## 数据流

### 1. 设备控制流程
```
前端 → API Gateway → Control Service → Platform API → 设备
     ← Response    ← Audit Service   ← Database     ←
```

### 2. 数据导出流程
```
前端 → Export API → Export Service → Database → Excel/CSV
     ← Task ID    ← Progress       ← Query    ← File
```

### 3. 能源监控流程
```
前端 → Energy API → Energy Service → Platform API/Database → 数据
     ← KPI/Chart  ← Aggregation    ← Raw Data            ←
```

## 环境变量

必需的环境变量（在 `.env` 文件中配置）：

```env
# 环控平台 API
HK_PLATFORM_TOKEN=your_token_here
HK_PLATFORM_BASE_URL=https://your-platform-url

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database

# 应用配置
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5173
```

## 部署架构

### 开发环境
- 后端: `http://localhost:8000`
- 前端: `http://localhost:5173`

### 生产环境
- 使用 Nginx 作为反向代理
- 使用 Gunicorn + Uvicorn 运行 FastAPI
- 前端静态文件由 Nginx 直接服务

## 依赖管理

### 后端依赖
使用 `uv` 或 `pip` 管理依赖：
- `requirements/base.txt`: 基础依赖
- `requirements/development.txt`: 开发依赖
- `requirements/production.txt`: 生产依赖
- `requirements/testing.txt`: 测试依赖

### 前端依赖
使用 `npm` 管理依赖，配置在 `frontend/package.json`

## 代码规范

### Python 代码规范
- 遵循 PEP 8
- 使用 Black 格式化（行长 88）
- 使用 isort 排序导入
- 使用 mypy 进行类型检查
- 使用 flake8 进行代码检查

### JavaScript 代码规范
- 遵循 ESLint 规则
- 使用 Prettier 格式化
- 组件命名: PascalCase
- 文件命名: kebab-case

## 日志管理

日志按日期存储在 `logs/` 目录：
- `app_YYYY-MM-DD.log`: 应用日志
- `error_YYYY-MM-DD.log`: 错误日志
- `access_YYYY-MM-DD.log`: 访问日志

## 性能优化

### 后端优化
- 使用异步 I/O (aiohttp)
- 数据库连接池
- 响应压缩
- API 缓存

### 前端优化
- 组件懒加载
- 虚拟滚动
- 图片压缩
- CDN 加速

## 安全措施

1. **认证授权**: Token 认证
2. **输入验证**: Pydantic 模型验证
3. **SQL 注入防护**: 使用参数化查询
4. **XSS 防护**: 输出转义
5. **CSRF 防护**: CSRF Token
6. **限流**: API 限流中间件

## 监控与告警

- 应用日志监控
- 性能监控
- 错误追踪
- 资源使用监控

## 相关文档

- [测试文档](TESTING.md)
- [贡献指南](CONTRIBUTING.md)
- [API 文档](../README.md#-api-文档)
- [部署文档](../DEPLOY.md)
