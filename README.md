# 环控平台维护工具Web版

这是一个基于FastAPI和Vue.js的环控平台维护工具，用于导出电耗数据和传感器数据。

## 功能特性

- 🔋 **电耗数据导出**：支持按线路和时间范围导出电耗统计数据
- 🌡️ **传感器数据导出**：支持导出温湿度传感器、风机频率等数据
- 🌐 **Web界面**：现代化的Web用户界面，支持中文本地化
- 📊 **实时状态**：显示导出进度和详细的操作日志
- 🚀 **批量处理**：支持多站点批量数据导出

## 技术栈

### 后端
- **FastAPI**: 现代化的Python Web框架
- **Python 3.8+**: 编程语言
- **MySQL**: 数据库连接
- **aiohttp**: 异步HTTP客户端
- **pandas**: 数据处理
- **openpyxl**: Excel文件生成

### 前端
- **Vue 3**: 渐进式JavaScript框架
- **Element Plus**: Vue 3组件库
- **Vite**: 前端构建工具
- **Axios**: HTTP客户端

## 项目结构

```
hk_tool_web/
├── frontend/                 # Vue.js前端应用
│   ├── src/
│   │   ├── App.vue          # 主应用组件
│   │   └── main.js          # 应用入口
│   ├── index.html           # HTML模板
│   ├── package.json         # 前端依赖
│   └── vite.config.js       # Vite配置
├── app.py                   # FastAPI主应用
├── export_service.py        # 数据导出服务
├── db_config.py            # 数据库配置
├── requirements.txt         # Python依赖
├── logs/                   # 日志目录
└── README.md              # 项目说明
```

## 安装和运行

### 环境要求
- Python 3.8+
- Node.js 16+
- MySQL数据库

### 后端部署

1. 安装Python依赖：
```bash
pip install -r requirements.txt
```

2. 配置数据库连接（修改db_config.py）

3. 启动后端服务：
```bash
python app.py
```

### 前端部署

1. 进入前端目录并安装依赖：
```bash
cd frontend
npm install
```

2. 启动开发服务器：
```bash
npm run dev
```

3. 构建生产版本：
```bash
npm run build
```

## 使用说明

1. **选择线路**：从下拉菜单中选择要导出的地铁线路
2. **设置时间范围**：
   - 开始时间：自动初始化为当日00:00:00
   - 结束时间：自动初始化为当前小时00:00:00
3. **选择导出类型**：电耗数据或传感器数据
4. **执行导出**：点击导出按钮，系统会显示实时进度
5. **下载文件**：导出完成后可直接下载生成的Excel/CSV文件

## 功能亮点

- ✅ **中文本地化**：时间选择器完全中文化显示
- ✅ **智能时间初始化**：自动设置合理的默认时间范围
- ✅ **实时状态同步**：前后端状态实时同步，避免状态异常
- ✅ **详细日志记录**：完整的操作日志和错误信息
- ✅ **紧急停止功能**：支持强制重置导出状态

## 开发说明

- 后端API服务运行在 `http://localhost:8000`
- 前端开发服务器运行在 `http://localhost:3000`
- 日志文件保存在 `logs/` 目录下，按日期命名

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

MIT License