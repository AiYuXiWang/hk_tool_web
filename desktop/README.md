# 环控平台维护工具 - 桌面版

桌面版应用，专注于数据导出和数据写值功能，与 Web 端功能完全一致。

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

- **Electron**: 跨平台桌面应用框架
- **Vue 3**: 前端界面（复用 Web 端代码）
- **Element Plus**: UI 组件库
- **Axios**: HTTP 请求库
- **Electron Store**: 本地配置存储

## 开发指南

### 环境要求
- Node.js 16+
- Python 3.10+ (后端服务)

### 安装依赖

```bash
cd desktop
npm install
```

### 开发模式

1. 启动后端服务：
```bash
cd ..
python main.py
```

2. 启动前端开发服务器：
```bash
cd ../frontend
npm run dev
```

3. 启动 Electron 开发模式：
```bash
cd ../desktop
npm run dev
```

### 构建打包

构建所有平台：
```bash
npm run build
```

构建 Windows 版本：
```bash
npm run build:win
```

构建 macOS 版本：
```bash
npm run build:mac
```

构建 Linux 版本：
```bash
npm run build:linux
```

打包文件将生成在 `desktop/dist` 目录中。

## 配置说明

应用配置存储在用户目录：
- Windows: `%APPDATA%\hk-tool-config\config.json`
- macOS: `~/Library/Application Support/hk-tool-config/config.json`
- Linux: `~/.config/hk-tool-config/config.json`

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

## 项目结构

```
desktop/
├── main.js              # Electron 主进程
├── preload.js           # 预加载脚本
├── package.json         # 项目配置
├── README.md            # 说明文档
├── assets/              # 应用资源
│   ├── icon.png         # Linux 图标
│   ├── icon.ico         # Windows 图标
│   └── icon.icns        # macOS 图标
└── renderer/            # 渲染进程文件（构建后）
    └── index.html
```

## 与 Web 端的区别

1. **部署方式**：
   - Web 端：浏览器访问
   - 桌面版：独立应用程序

2. **功能范围**：
   - Web 端：数据导出 + 数据写值 + 能源驾驶舱（已删除）
   - 桌面版：数据导出 + 数据写值

3. **技术实现**：
   - 桌面版使用 Electron IPC 进行进程间通信
   - 桌面版提供原生菜单、对话框、通知等
   - 桌面版支持本地配置持久化

## 快捷键

- `Ctrl/Cmd + E`: 打开数据导出
- `Ctrl/Cmd + R`: 重新加载
- `Ctrl/Cmd + Q`: 退出应用
- `Ctrl/Cmd + ,`: 打开设置
- `F11`: 切换全屏
- `Ctrl/Cmd + Shift + I`: 开发者工具

## 故障排除

### 1. 无法连接后端服务

确保后端服务已启动：
```bash
python main.py
```

检查配置中的 `apiBaseUrl` 是否正确。

### 2. 打包失败

清理缓存后重试：
```bash
npm run clean
npm install
npm run build
```

### 3. 应用无法启动

查看日志文件：
- Windows: `%APPDATA%\hk-tool-desktop\logs`
- macOS/Linux: `~/.config/hk-tool-desktop/logs`

## 更新日志

### v1.0.0 (2024)
- 初始版本
- 数据导出功能
- 数据写值功能
- 基本的桌面应用框架

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue。
