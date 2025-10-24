# 重启脚本快速指南

## 一键运行 🚀

### 推荐方式（跨平台）
```bash
python scripts/restart_and_test.py
```

### Linux/macOS
```bash
./scripts/restart_and_test.sh
```

### Windows
```cmd
scripts\restart_and_test.bat
```

## 常用命令

### 完整重启（不运行测试）
```bash
python scripts/restart_and_test.py --no-tests
```

### 只重启后端
```bash
python scripts/restart_and_test.py --no-frontend --no-tests
```

### 只重启前端
```bash
python scripts/restart_and_test.py --no-backend --no-tests
```

## 服务地址

- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **前端应用**: http://localhost:5173

## 停止服务

### 方法1：使用PID文件
```bash
kill $(cat logs/backend.pid logs/frontend.pid)
```

### 方法2：重新运行脚本
脚本会自动停止现有服务并重启

### 方法3：手动停止端口
```bash
# Linux/macOS
lsof -ti:8000 | xargs kill -9  # 停止后端
lsof -ti:5173 | xargs kill -9  # 停止前端

# Windows
netstat -ano | findstr ":8000"
taskkill /F /PID <PID>
```

## 日志查看

```bash
# 查看后端日志
tail -f logs/backend.log

# 查看前端日志
tail -f logs/frontend.log

# 查看所有日志
tail -f logs/*.log
```

## 测试状态 ✅

- ✅ Shell脚本测试通过
- ✅ Python脚本测试通过
- ✅ 单独重启后端测试通过
- ✅ 单独重启前端测试通过
- ✅ 17个API测试全部通过
- ✅ 服务健康检查通过

## 更多信息

详细测试报告请查看：[RESTART_SCRIPTS_TEST_REPORT.md](RESTART_SCRIPTS_TEST_REPORT.md)
