# 重启前后端服务脚本

本项目包含三个跨平台的重启脚本，用于快速重启前后端服务并运行测试。

## 快速开始

### Python脚本（推荐 - 跨平台）
```bash
# 完整运行（重启服务并运行测试）
python scripts/restart_and_test.py

# 只重启服务，不运行测试
python scripts/restart_and_test.py --no-tests

# 只重启后端
python scripts/restart_and_test.py --no-frontend

# 只重启前端
python scripts/restart_and_test.py --no-backend
```

### Linux/Mac (Shell脚本)
```bash
chmod +x scripts/restart_and_test.sh
./scripts/restart_and_test.sh
```

### Windows (批处理脚本)
```cmd
scripts\restart_and_test.bat
```

## 功能特点

✅ **自动环境检测** - 自动检测并使用虚拟环境
✅ **智能进程管理** - 自动停止现有服务并重启
✅ **健康检查** - 等待服务完全启动后再继续
✅ **测试运行** - 自动运行后端和前端测试
✅ **彩色输出** - 友好的彩色终端输出
✅ **详细日志** - 记录所有操作和错误信息

## 服务信息

启动成功后，可以通过以下地址访问：

- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs  
- **前端应用**: http://localhost:5173

## 日志文件

脚本在`logs/`目录下生成日志文件：

- `logs/backend.log` - 后端服务日志
- `logs/frontend.log` - 前端服务日志
- `logs/backend.pid` - 后端进程ID
- `logs/frontend.pid` - 前端进程ID

## 停止服务

### 方法1：使用PID文件
```bash
kill $(cat logs/backend.pid)
kill $(cat logs/frontend.pid)
```

### 方法2：重新运行脚本
脚本会自动停止现有服务并重启

## 详细文档

更多信息请参阅：[scripts/README.md](scripts/README.md)

## 测试示例

脚本运行后的输出示例：

```
============================================================
重启前后端服务并运行测试
============================================================
ℹ 项目根目录: /home/engine/project

============================================================
步骤 1: 环境检查
============================================================
✓ Python环境检查通过
✓ Node.js环境检查通过

============================================================
步骤 2: 停止现有服务
============================================================
ℹ 正在停止 后端服务 (端口 8000)...
✓ 后端服务 已停止
ℹ 正在停止 前端服务 (端口 5173)...
✓ 前端服务 已停止

============================================================
步骤 3: 启动后端服务
============================================================
ℹ 启动后端服务...
ℹ 使用虚拟环境中的Python
ℹ 后端PID: 12345
ℹ 等待 后端服务 启动...
✓ 后端服务 已就绪
✓ 后端服务启动成功
ℹ 后端日志: /home/engine/project/logs/backend.log
ℹ API文档: http://localhost:8000/docs

============================================================
步骤 4: 启动前端服务
============================================================
ℹ 启动前端服务...
ℹ 前端PID: 12346
ℹ 等待 前端服务 启动...
✓ 前端服务 已就绪
✓ 前端服务启动成功
ℹ 前端日志: /home/engine/project/logs/frontend.log
ℹ 应用地址: http://localhost:5173

============================================================
步骤 5: 运行测试
============================================================
[测试输出...]

============================================================
完成
============================================================
✓ 前后端服务已重启并通过所有测试

服务信息:
  • 后端API: http://localhost:8000
  • 前端应用: http://localhost:5173
  • API文档: http://localhost:8000/docs

日志文件:
  • 后端日志: /home/engine/project/logs/backend.log
  • 前端日志: /home/engine/project/logs/frontend.log
```

## 故障排除

### 问题：虚拟环境不存在

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 问题：前端依赖未安装

```bash
cd frontend
npm install
```

### 问题：端口已被占用

```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9  # 停止后端
lsof -ti:5173 | xargs kill -9  # 停止前端

# Windows  
netstat -ano | findstr ":8000"
taskkill /F /PID <PID>
```

## 贡献

欢迎提交Issue和Pull Request来改进这些脚本！

---

**维护者**: 项目团队  
**最后更新**: 2024-01-20
