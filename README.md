# 环控节能平台设备点位运维与批量控制模块

一个基于 FastAPI + Vue 3 的环控平台维护工具，提供设备点位运维、批量控制、数据导出和实时监控功能。

## 🚀 功能特性

### 核心功能
- 🌳 **设备树浏览**：层级化展示设备结构，支持快速定位
- 📊 **点位实时查询**：实时获取设备点位数据，支持批量查询
- ⚡ **批量写值控制**：支持多点位批量控制，容错重试机制
- 📈 **数据导出**：电耗数据、传感器数据导出，支持 Excel/CSV 格式
- 🔍 **操作审计**：完整的操作日志记录，包含前后值对比

### 技术亮点
- ✅ **智能模糊匹配**：自动处理不完整的 point_key 格式
- ✅ **异步并发处理**：高性能的批量操作处理
- ✅ **容错重试机制**：指数退避重试，确保操作可靠性
- ✅ **实时状态同步**：前后端状态实时同步
- ✅ **中文本地化**：完整的中文界面支持

## 🛠 技术栈

### 后端
- **FastAPI**: 现代化的 Python Web 框架
- **Python 3.10.11**: 编程语言
- **MySQL**: 数据库存储
- **aiohttp**: 异步 HTTP 客户端
- **pandas**: 数据处理
- **openpyxl**: Excel 文件生成

### 前端
- **Vue 3**: 渐进式 JavaScript 框架
- **Element Plus**: Vue 3 组件库
- **Vite**: 前端构建工具
- **Axios**: HTTP 客户端

## 📁 项目结构

```
hk_tool_web/
├── frontend/                    # Vue.js 前端应用
│   ├── src/
│   │   ├── App.vue             # 主应用组件
│   │   ├── DeviceOverview.vue  # 设备总览组件
│   │   └── main.js             # 应用入口
│   ├── index.html              # HTML 模板
│   ├── package.json            # 前端依赖
│   └── vite.config.js          # Vite 配置
├── docs/                       # 项目文档
│   ├── openapi/               # API 文档
│   └── *.md                   # 各种说明文档
├── templates/                  # 模板文件
├── main.py                     # FastAPI 主应用
├── control_service.py          # 设备控制服务
├── export_service.py           # 数据导出服务
├── audit_service.py            # 审计服务
├── db_config.py               # 数据库配置
├── models.py                  # 数据模型
├── logger_config.py           # 日志配置
├── requirements.txt           # Python 依赖
├── .env                       # 环境变量（需要创建）
├── start_all.bat             # 一键启动脚本
└── README.md                 # 项目说明
```

## 🚀 快速开始

### 环境要求
- Python 3.10.11
- Node.js 16+
- MySQL 数据库

### 一键启动（推荐）
```bash
# Windows 用户
start_all.bat

# 或者手动启动
start_simple.bat
```

### 手动部署

#### 1. 后端部署

```bash
# 1. 安装 Python 依赖
pip install -r requirements.txt

# 2. 配置环境变量
# 创建 .env 文件，添加以下配置：
# HK_PLATFORM_TOKEN=your_platform_token
# HK_PLATFORM_BASE_URL=your_platform_url

# 3. 配置数据库连接（修改 db_config.py）

# 4. 启动后端服务
python main.py
```

#### 2. 前端部署

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev

# 4. 构建生产版本
npm run build
```

## 📖 使用说明

### 设备点位运维
1. **设备树浏览**：左侧设备树展示设备层级结构
2. **点位查询**：选择设备后查看实时点位数据
3. **实时写值**：选中点位后可进行实时控制
4. **批量操作**：支持多点位批量写值控制

### 数据导出
1. **选择线路**：从下拉菜单选择地铁线路
2. **设置时间范围**：配置导出的时间区间
3. **选择类型**：电耗数据或传感器数据
4. **执行导出**：实时显示导出进度
5. **下载文件**：导出完成后下载 Excel/CSV 文件

### 批量控制
1. **添加点位**：通过"加入批量"按钮添加点位
2. **配置参数**：设置控制值和参数
3. **执行控制**：批量执行控制命令
4. **查看结果**：实时查看执行状态和结果

## 🔧 配置说明

### 环境变量配置
创建 `.env` 文件：
```env
# 环控平台 API Token
HK_PLATFORM_TOKEN=your_token_here

# 环控平台 API 基础 URL
HK_PLATFORM_BASE_URL=https://your-platform-url

# 数据库配置（可选，默认使用 db_config.py）
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database
```

### 数据库配置
修改 `db_config.py` 文件中的数据库连接参数。

## 🔍 API 文档

启动后端服务后，访问以下地址查看 API 文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📊 主要接口

### 设备控制
- `GET /control/devices/tree` - 获取设备树
- `POST /control/points/query` - 查询点位实时数据
- `POST /control/points/write` - 批量写值控制

### 数据导出
- `POST /export/electricity` - 导出电耗数据
- `POST /export/sensor` - 导出传感器数据
- `GET /export/status` - 获取导出状态

### 审计日志
- `GET /audit/logs` - 获取操作日志
- `POST /audit/logs` - 记录操作日志

## 🐛 故障排除

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

4. **点位写值失败**
   - 检查 `point_key` 格式是否正确
   - 确认 `data_source` 参数正确

## 📝 开发说明

- 后端 API 服务：`http://localhost:8000`
- 前端开发服务器：`http://localhost:5173`
- 日志文件：`logs/` 目录，按日期命名
- 测试覆盖率要求：≥ 90%

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

如有问题或建议，请：
- 提交 [Issue](https://github.com/your-username/hk_tool_web/issues)
- 发送邮件至：your-email@example.com

---

**注意**：首次使用前请确保正确配置环境变量和数据库连接。