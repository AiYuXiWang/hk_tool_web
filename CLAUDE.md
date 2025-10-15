# Claude Code 项目配置文件

## 项目概述

这是一个**环控节能平台设备点位运维与批量控制模块**的Web应用，基于 FastAPI + Vue 3 构建。

## 项目结构

```
hk_tool_web/
├── main.py                    # FastAPI 主应用入口
├── control_service.py         # 设备控制核心服务
├── export_service.py          # 数据导出服务
├── audit_service.py           # 审计服务
├── db_config.py              # 数据库配置
├── models.py                 # 数据模型定义
├── config_electricity.py     # 能源配置管理
├── backend/                   # 后端模块化代码
│   └── app/
│       ├── api/              # API 路由
│       ├── middleware/       # 中间件
│       ├── services/         # 业务服务
│       └── config/           # 配置管理
├── frontend/                  # Vue.js 前端
│   ├── src/
│   │   ├── App.vue           # 主应用组件
│   │   ├── views/            # 页面组件
│   │   ├── components/       # 业务组件
│   │   ├── api/              # API 封装
│   │   └── stores/           # 状态管理
├── docs/                      # 项目文档
└── requirements/             # 分环境依赖管理
```

## 技术栈

### 后端
- **FastAPI**: 现代化的 Python Web 框架
- **Python 3.10.11**: 编程语言
- **MySQL**: 数据库存储
- **pandas**: 数据处理
- **openpyxl**: Excel 文件生成

### 前端
- **Vue 3**: 渐进式 JavaScript 框架
- **Element Plus**: Vue 3 组件库
- **Vite**: 前端构建工具
- **Axios**: HTTP 客户端

## 核心功能

### 1. 设备控制模块
- 🌳 **设备树浏览**: 层级化展示设备结构，支持快速定位
- 📊 **点位实时查询**: 实时获取设备点位数据，支持批量查询
- ⚡ **批量写值控制**: 支持多点位批量控制，容错重试机制
- 📍 **多站点支持**: 支持按车站IP切换数据源

### 2. 能源管理驾驶舱
- 📈 **实时能耗监测**: 功率曲线、能耗趋势分析
- 🎯 **KPI指标**: 总能耗、当前功率、能效比、节能收益
- 🔍 **历史趋势**: 24h/7d/30d/90d多维度数据分析
- 💡 **优化建议**: AI驱动的节能优化建议

### 3. 数据导出功能
- 📋 **电耗数据导出**: 支持Excel/CSV格式
- 🌡️ **传感器数据导出**: 温度、湿度等环境数据
- ⏰ **时间范围选择**: 灵活的时间区间配置
- 📊 **多站点支持**: 按线路和站点批量导出

### 4. 操作审计系统
- 👁️ **实时监控**: 完整的操作日志记录
- 📝 **前后值对比**: 详细记录每次操作的变更
- 🔍 **可追溯性**: 支持操作者、时间、点位多维度查询

## 开发指南

### 环境要求
- Python 3.10.11
- Node.js 16+
- MySQL 数据库

### 快速启动

#### 1. 后端启动
```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量（创建 .env 文件）
# HK_PLATFORM_TOKEN=your_platform_token
# HK_PLATFORM_BASE_URL=your_platform_url

# 启动服务
python main.py
```

#### 2. 前端启动
```bash
cd frontend
npm install
npm run dev
```

### API 接口

主要接口地址：
- 后端 API: `http://localhost:8000`
- API 文档: `http://localhost:8000/docs`
- 前端界面: `http://localhost:5173`

#### 核心接口
- `GET /control/device-tree` - 获取设备树
- `POST /control/points/query` - 查询点位实时数据
- `POST /control/points/write` - 批量写值控制
- `POST /export/electricity` - 导出电耗数据
- `POST /export/sensor` - 导出传感器数据
- `GET /audit/logs` - 获取操作日志

## 代码规范

### Python 代码规范
- 使用 `black` 进行代码格式化
- 使用 `isort` 进行导入排序
- 使用 `flake8` 进行代码检查
- 使用 `mypy` 进行类型检查

### 前端代码规范
- 使用 ESLint 进行代码检查
- 使用 Prettier 进行代码格式化
- 组件命名使用 PascalCase
- 文件命名使用 kebab-case

## 测试

### 运行测试
```bash
# Python 测试
pytest

# 前端测试
cd frontend
npm run test
```

### 测试覆盖率
- 目标覆盖率：≥ 90%

## 部署

### 开发环境
```bash
# 一键启动（Windows）
start_all.bat

# 或手动启动
python main.py  # 后端
cd frontend && npm run dev  # 前端
```

### 生产环境
```bash
# 前端构建
cd frontend
npm run build

# 使用 Gunicorn 启动后端
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 配置说明

### 环境变量
创建 `.env` 文件：
```env
# 环控平台 API Token
HK_PLATFORM_TOKEN=your_token_here

# 环控平台 API 基础 URL
HK_PLATFORM_BASE_URL=https://your-platform-url

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database
```

## 故障排除

### 常见问题

1. **Token 认证失败**
   - 检查 `.env` 文件中的 `HK_PLATFORM_TOKEN` 配置
   - 确认 Token 有效性

2. **数据库连接失败**
   - 检查 `db_config.py` 中的数据库配置
   - 确认数据库服务正常运行

3. **前端无法访问后端**
   - 确认后端服务运行在 `http://localhost:8000`
   - 检查 CORS 配置

## 安全注意事项

- 不要在代码中硬编码敏感信息
- 使用环境变量管理配置
- 定期更新依赖包
- 启用 HTTPS（生产环境）
- 实施适当的访问控制

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请：
- 提交 [Issue](https://github.com/your-username/hk_tool_web/issues)
- 发送邮件至：your-email@example.com

---

**注意**：这是一个专业的环控平台运维工具，请确保在部署前正确配置所有必要的参数和环境。