# 环控平台维护工具 - 桌面版

基于 PySide6 (Qt6) 的跨平台桌面应用，专注于数据导出和数据写值功能，与 Web 端功能完全一致。

## 功能特性

### 1. 数据导出
- 电耗数据导出（Excel/CSV格式）
- 传感器数据导出（温度、湿度等）
- 支持多站点批量导出
- 灵活的时间范围选择
- 导出进度实时反馈

### 2. 数据写值
- 设备树浏览与导航
- 点位实时查询
- 单点快速写值
- 批量写值控制
- 操作日志记录

## 技术栈

- **PySide6**: Qt6 的官方 Python 绑定
- **PyInstaller**: Python 应用打包工具
- **QWebEngineView**: 嵌入式 Web 浏览器
- **Vue 3**: 前端界面（复用 Web 端代码）
- **Element Plus**: UI 组件库

## 环境要求

- Python 3.10+
- Node.js 16+ (用于构建前端)
- Qt6 WebEngine (通过 PySide6-WebEngine 安装)

## 开发指南

### 1. 安装依赖

```bash
cd desktop

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate.bat  # Windows

# 安装 Python 依赖
pip install -r requirements.txt
```

### 2. 开发模式运行

**方式一：一键启动脚本（推荐）**

```bash
# Linux/macOS
./start-dev.sh

# Windows
start-dev.bat
```

脚本会自动：
1. 检查并启动后端服务（如果未运行）
2. 检查并启动前端开发服务器（如果未运行）
3. 启动 PySide6 桌面应用

**方式二：手动启动**

```bash
# 1. 启动后端（在项目根目录）
cd ..
python main.py

# 2. 启动前端（新终端）
cd frontend
npm run dev

# 3. 启动桌面应用（新终端）
cd desktop
python main.py --dev
```

### 3. 构建打包

**Linux/macOS:**

```bash
# 打包为目录格式（推荐，启动快）
./build.sh onedir

# 打包为单文件（体积大，启动慢）
./build.sh onefile
```

**Windows:**

```batch
REM 打包为目录格式（推荐）
build.bat onedir

REM 打包为单文件
build.bat onefile
```

打包产物位于 `desktop/dist/` 目录。

### 4. 运行打包后的应用

**目录格式:**
```bash
cd dist/hk-tool-desktop
./hk-tool-desktop  # Linux/macOS
hk-tool-desktop.exe  # Windows
```

**单文件格式:**
```bash
cd dist
./hk-tool-desktop  # Linux/macOS
hk-tool-desktop.exe  # Windows
```

## 项目结构

```
desktop/
├── main.py              # 主应用入口
├── dialogs.py           # 对话框模块（设置等）
├── requirements.txt     # Python 依赖
├── build.sh / .bat      # 构建脚本
├── start-dev.sh / .bat  # 开发启动脚本
├── README.md            # 本文档
├── .gitignore           # Git 忽略配置
├── assets/              # 应用资源
│   ├── icon.png         # Linux 图标
│   ├── icon.ico         # Windows 图标
│   └── icon.icns        # macOS 图标
├── venv/                # Python 虚拟环境（.gitignore）
├── renderer/            # 前端构建产物（.gitignore）
└── dist/                # 打包产物（.gitignore）
```

## 配置说明

应用配置存储在：
- **Linux**: `~/.hk-tool-desktop/config.json`
- **macOS**: `~/.hk-tool-desktop/config.json`
- **Windows**: `%USERPROFILE%\.hk-tool-desktop\config.json`

默认配置：
```json
{
  "apiBaseUrl": "http://localhost:8000",
  "windowBounds": {
    "width": 1400,
    "height": 900
  },
  "lastUsedLine": "",
  "lastUsedStation": ""
}
```

可以通过菜单 `文件 -> 设置` 修改配置。

## 功能说明

### 菜单栏

**文件菜单:**
- `导出数据 (Ctrl+E)`: 切换到数据导出页面
- `设置 (Ctrl+,)`: 打开设置对话框
- `退出 (Ctrl+Q)`: 退出应用

**视图菜单:**
- `重新加载 (Ctrl+R)`: 重新加载前端页面
- `全屏 (F11)`: 切换全屏模式
- `开发者工具 (Ctrl+Shift+I)`: 打开开发者工具（需要额外配置）

**帮助菜单:**
- `关于`: 显示应用信息
- `使用说明`: 显示功能说明

### 系统托盘

- 最小化到系统托盘
- 双击托盘图标显示/隐藏窗口
- 右键菜单：显示、退出

### 数据导出

1. 点击"数据导出"标签页
2. 选择线路和车站
3. 选择时间范围
4. 选择导出类型（电耗/传感器）
5. 点击导出，选择保存位置
6. 查看导出进度

### 数据写值

1. 点击"设备控制"标签页
2. 浏览设备树，选择设备
3. 查询点位实时值
4. 单点写值或批量写值
5. 查看操作日志

## 开发工具

### 启用 WebEngine 开发者工具

启动应用时添加参数：

```bash
python main.py --dev --remote-debugging-port=9222
```

然后在 Chrome 浏览器中访问 `http://localhost:9222`

### 查看 JavaScript 控制台

所有前端 JavaScript 日志会输出到终端。

## 与 Web 版的对比

| 特性 | Web 版 | 桌面版 (PySide6) |
|-----|--------|------------------|
| 跨平台 | ✅ 浏览器 | ✅ Windows/macOS/Linux |
| 安装 | ❌ 不需要 | ✅ 需要安装 |
| 原生UI | ❌ | ✅ Qt6 原生界面 |
| 系统集成 | ❌ | ✅ 系统托盘、菜单 |
| 离线使用 | ❌ | ✅ 可离线使用 |
| 自动更新 | ✅ | ❌ (计划中) |
| 文件操作 | 受限 | ✅ 原生文件对话框 |
| 通知 | 受限 | ✅ 系统通知 |
| 性能 | 中等 | 好 |
| 分发 | 简单 | 需要打包 |

## 优势

1. **原生体验**: Qt6 提供的原生界面和系统集成
2. **跨平台**: 一次开发，多平台运行
3. **代码复用**: 复用 Web 端的 Vue 3 前端代码
4. **功能一致**: 与 Web 端功能完全一致
5. **易于开发**: Python 开发，降低门槛

## 故障排除

### 1. 导入 PySide6 失败

```bash
pip install --upgrade PySide6 PySide6-WebEngine
```

### 2. 前端页面无法加载

- 确保后端服务已启动（http://localhost:8000）
- 确保前端开发服务器已启动（http://localhost:5173）
- 检查配置文件中的 `apiBaseUrl`

### 3. 打包失败

```bash
# 清理缓存
rm -rf build dist *.spec

# 重新打包
./build.sh onedir
```

### 4. 窗口显示异常

- 删除配置文件：`~/.hk-tool-desktop/config.json`
- 重新启动应用

### 5. WebEngine 相关错误

某些 Linux 发行版需要安装额外的依赖：

```bash
# Ubuntu/Debian
sudo apt-get install libxcb-xinerama0 libxcb-cursor0

# Fedora
sudo dnf install qt6-qtwebengine
```

## 已知问题

1. **开发者工具**: 需要额外配置才能使用
2. **自动更新**: 暂不支持（计划中）
3. **macOS 签名**: 打包后需要签名才能在 macOS 上运行

## 计划功能

- [ ] 自动更新功能
- [ ] 离线模式支持
- [ ] 主题切换
- [ ] 多语言支持
- [ ] 性能监控
- [ ] 崩溃报告

## 技术细节

### WebEngine 页面加载

桌面版使用 `QWebEngineView` 加载前端页面：

- **开发模式**: 加载 Vite 开发服务器 (http://localhost:5173)
- **生产模式**: 加载本地打包文件 (file://renderer/index.html)

### 配置持久化

使用 JSON 文件存储配置，确保跨平台兼容性。

### IPC 通信

桌面版不需要像 Electron 那样的 IPC 通信，Python 代码可以直接与 Qt 交互。

### 打包策略

- **onedir**: 打包为目录，包含所有依赖文件（推荐）
- **onefile**: 打包为单个可执行文件（体积大，启动慢）

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请提交 Issue 或联系开发团队。

---

**注意**: 桌面版应用需要后端服务支持，请确保后端服务已正确配置并运行。
