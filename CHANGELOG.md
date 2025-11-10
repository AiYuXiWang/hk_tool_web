# 更新日志 (Changelog)

## [v2.0.0] - 2024

### 重大变更 🚨

#### 删除能源驾驶舱功能
- **原因**：简化应用，专注核心功能
- **影响**：能源驾驶舱相关的所有功能已被移除
- **保留功能**：
  - ✅ 设备控制与点位管理
  - ✅ 数据导出（电耗、传感器）
  - ✅ 数据写值（单点、批量）
  - ✅ 操作审计日志

#### 删除的文件和功能

**前端 (Frontend)**
- 删除 `frontend/src/views/EnergyCockpit.vue` - 能源驾驶舱主页面
- 删除 `frontend/src/views/EnergyPage.vue` - 能源页面
- 删除 `frontend/src/stores/energy.ts` - 能源状态管理
- 删除 `frontend/src/api/energy.ts` - 能源 API 调用
- 删除 `frontend/src/components/` 中的能源相关组件：
  - `EnergyOptimizationSuggestions.vue`
  - `KpiDashboard.vue`
  - `HistoryTrendChart.vue`
  - `RealtimeEnergyChart.vue`
  - `business/EnergyChart.vue`
  - `business/EnergyDeviceMonitor.vue`
  - `business/EnergyOptimizationPanel.vue`
  - `business/EnergyKpiCard.vue`
  - `cockpit/` 目录（整个）

**后端 (Backend)**
- 删除 `backend/app/api/energy_dashboard.py` - 能源驾驶舱 API
- 删除 `backend/app/services/energy_service.py` - 能源服务
- 删除 `backend/app/services/realtime_energy_service.py` - 实时能源服务
- 删除 `backend/app/models/energy.py` - 能源数据模型
- 删除 `backend/app/config/energy_parameters.py` - 能源参数配置
- 从 `main.py` 中移除能源驾驶舱路由注册
- 从 `backend/app/core/dependencies.py` 中移除能源服务依赖

**测试文件 (Tests)**
- 删除 `test_energy_backend.py`
- 删除 `tests/test_energy_dashboard_consumption_fix.py`
- 删除 `tests/test_energy_api.py`
- 删除 `tests/test_energy_edge_cases.py`
- 删除 `tests/test_energy_dashboard_fix.py`
- 删除 `tests/test_energy_slider_feature.py`

**界面变更**
- 从主界面标签页中移除"能源驾驶舱"选项卡
- 默认显示"设备控制"页面（原为"能源驾驶舱"）

### 新增功能 ✨

#### 桌面版应用
- **技术栈**：Electron + Vue 3 + Element Plus
- **功能**：与 Web 端完全一致，专注于数据导出和数据写值
- **平台支持**：Windows、macOS、Linux
- **特性**：
  - 🖥️ 原生桌面应用体验
  - 📁 原生文件对话框
  - 🔔 系统通知支持
  - 💾 本地配置持久化
  - 📋 原生应用菜单
  - ⌨️ 快捷键支持

#### 桌面版文件结构
```
desktop/
├── main.js              # Electron 主进程
├── preload.js           # 预加载脚本（安全 IPC）
├── package.json         # 项目配置与依赖
├── README.md            # 详细使用说明
├── build.sh / .bat      # 构建脚本
├── start-dev.sh / .bat  # 开发启动脚本
├── assets/              # 应用图标资源
│   ├── icon.png         # Linux 图标
│   ├── icon.ico         # Windows 图标
│   └── icon.icns        # macOS 图标
└── .gitignore           # 桌面版忽略文件
```

#### 桌面版功能
1. **配置管理**
   - API 基础 URL 配置
   - 窗口大小和位置记忆
   - 最后使用的线路和车站记忆

2. **文件操作**
   - 选择保存路径对话框
   - 文件保存（支持 Excel/CSV）
   - 文件选择对话框

3. **API 请求**
   - 通过 IPC 代理所有 API 请求
   - 支持超时配置
   - 错误处理

4. **用户界面**
   - 消息对话框
   - 系统通知
   - 应用菜单（文件、编辑、视图、帮助）

5. **快捷键**
   - `Ctrl/Cmd + E`: 打开数据导出
   - `Ctrl/Cmd + R`: 重新加载
   - `Ctrl/Cmd + Q`: 退出应用
   - `Ctrl/Cmd + ,`: 打开设置
   - `F11`: 切换全屏
   - `Ctrl/Cmd + Shift + I`: 开发者工具

#### 构建脚本
- **Linux/macOS**: `./build.sh [win|mac|linux|all]`
- **Windows**: `build.bat [win|all]`
- 自动化流程：
  1. 构建前端应用
  2. 复制构建文件到桌面版
  3. 安装桌面版依赖
  4. 打包为可执行文件

#### 开发启动脚本
- **Linux/macOS**: `./start-dev.sh`
- **Windows**: `start-dev.bat`
- 功能：
  - 自动检查并启动后端服务
  - 自动检查并启动前端开发服务器
  - 启动 Electron 桌面应用
  - 退出时自动清理所有进程

### 改进 🔧

#### 代码简化
- 移除所有能源相关的依赖注入
- 简化路由配置
- 减少前端状态管理复杂度
- 清理未使用的导入和依赖

#### 文档更新
- 更新 `README.md` 添加桌面版说明
- 新增 `desktop/README.md` 详细文档
- 更新项目结构说明
- 添加快速启动指南

### 迁移指南 📖

如果您之前使用了能源驾驶舱功能，请注意：

1. **数据保留**：所有历史数据仍保留在数据库中
2. **API 变更**：`/api/energy/*` 相关的所有端点已被移除
3. **前端路由**：移除了 `cockpit` 路由
4. **默认页面**：应用启动时默认显示"设备控制"页面

### 升级步骤

#### Web 版
```bash
# 1. 更新代码
git pull

# 2. 安装/更新依赖
cd frontend
npm install

# 3. 重新构建
npm run build

# 4. 重启服务
cd ..
python main.py
```

#### 桌面版（新功能）
```bash
# 1. 进入桌面版目录
cd desktop

# 2. 安装依赖
npm install

# 3. 开发模式运行
npm run dev

# 或构建生产版本
./build.sh all  # Linux/macOS
build.bat all   # Windows
```

### 技术栈更新

#### 新增依赖
- `electron`: ^27.0.0 - 桌面应用框架
- `electron-builder`: ^24.6.4 - 打包工具
- `electron-store`: ^8.1.0 - 配置存储

#### 移除依赖
- 所有能源驾驶舱相关的前后端依赖

### 破坏性变更 ⚠️

1. **API 端点移除**
   - `GET /api/energy/overview` - 能源总览
   - `GET /api/energy/trends` - 能源趋势
   - `GET /api/energy/devices` - 设备能耗
   - `GET /api/energy/comparison` - 同比环比
   - `GET /api/energy/breakdown` - 分类分项

2. **前端组件移除**
   - `EnergyCockpit` 组件及其所有子组件
   - `energy` Store
   - `energy` API 模块

3. **配置变更**
   - 移除能源相关配置参数

### 已知问题

暂无

### 未来计划

- [ ] 桌面版自动更新功能
- [ ] 桌面版数据同步功能
- [ ] 桌面版离线模式支持
- [ ] 更多的主题和自定义选项

---

## [v1.x.x] - 以前版本

详见之前的更新日志文件。

---

**注意**：此版本包含破坏性变更，升级前请确保：
1. 导出所有需要的能源数据
2. 更新所有依赖能源 API 的客户端代码
3. 测试核心功能（数据导出、数据写值）正常运行
