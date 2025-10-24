# 重启前后端并运行测试脚本

这个目录包含用于重启前后端服务并运行测试的脚本。

## 脚本列表

### 1. `restart_and_test.py` (推荐)
跨平台的Python脚本，支持Windows、Linux和macOS。

**使用方法：**
```bash
# 完整运行（重启前后端并运行所有测试）
python scripts/restart_and_test.py

# 或使用python3
python3 scripts/restart_and_test.py

# 只重启后端
python scripts/restart_and_test.py --no-frontend

# 只重启前端
python scripts/restart_and_test.py --no-backend

# 重启服务但不运行测试
python scripts/restart_and_test.py --no-tests
```

**功能特点：**
- ✅ 自动检测并使用虚拟环境中的Python
- ✅ 智能端口检测和进程清理
- ✅ 服务启动健康检查
- ✅ 彩色输出（支持终端颜色）
- ✅ 详细的日志记录
- ✅ 支持命令行参数

### 2. `restart_and_test.sh`
Linux/Unix shell脚本版本。

**使用方法：**
```bash
# 添加执行权限（首次使用）
chmod +x scripts/restart_and_test.sh

# 运行脚本
./scripts/restart_and_test.sh

# 或直接使用bash
bash scripts/restart_and_test.sh
```

**功能特点：**
- ✅ 彩色终端输出
- ✅ 自动检测虚拟环境
- ✅ 端口检测和进程管理
- ✅ 服务健康检查
- ✅ 详细的运行日志

### 3. `restart_and_test.bat`
Windows批处理脚本版本。

**使用方法：**
```cmd
REM 直接双击运行，或在命令行中执行
scripts\restart_and_test.bat
```

**功能特点：**
- ✅ Windows原生支持
- ✅ 自动端口检测
- ✅ 进程管理（使用netstat和taskkill）
- ✅ 服务健康检查
- ✅ 友好的中文界面

## 脚本执行流程

所有脚本都按以下步骤执行：

1. **环境检查**
   - 检查Python环境
   - 检查Node.js环境
   - 验证必要的工具是否可用

2. **停止现有服务**
   - 检测并停止运行在端口8000的后端服务
   - 检测并停止运行在端口5173的前端服务

3. **启动后端服务**
   - 使用虚拟环境中的Python（如果存在）
   - 启动FastAPI应用（main.py）
   - 等待服务就绪（健康检查）
   - 记录PID和日志位置

4. **启动前端服务**
   - 进入frontend目录
   - 启动Vite开发服务器
   - 等待服务就绪（健康检查）
   - 记录PID和日志位置

5. **运行测试**
   - 检查并安装pytest（如果需要）
   - 运行基础API测试
   - 运行边界情况测试
   - 运行前后端集成测试
   - 运行前端单元测试

6. **输出结果**
   - 显示服务访问地址
   - 显示日志文件位置
   - 显示测试结果摘要

## 日志文件

脚本运行后会在`logs/`目录下生成以下文件：

```
logs/
├── backend.log      # 后端服务日志
├── frontend.log     # 前端服务日志
├── backend.pid      # 后端进程ID
└── frontend.pid     # 前端进程ID
```

**查看日志：**
```bash
# 查看后端日志
tail -f logs/backend.log

# 查看前端日志
tail -f logs/frontend.log
```

## 服务地址

启动成功后，可以通过以下地址访问服务：

- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **前端应用**: http://localhost:5173

## 停止服务

### 方法1：使用PID文件
```bash
# 停止后端
kill $(cat logs/backend.pid)

# 停止前端
kill $(cat logs/frontend.pid)
```

### 方法2：使用端口号
```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9  # 停止后端
lsof -ti:5173 | xargs kill -9  # 停止前端

# Windows
netstat -ano | findstr ":8000" | findstr "LISTENING"  # 查找后端PID
taskkill /F /PID <PID>  # 停止后端
```

### 方法3：重新运行脚本
脚本会自动停止已运行的服务并重新启动。

## 故障排除

### 1. 后端启动失败

**问题**: `ModuleNotFoundError: No module named 'xxx'`

**解决方案**:
```bash
# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 前端启动失败

**问题**: `npm: command not found` 或 `Module not found`

**解决方案**:
```bash
# 安装Node.js依赖
cd frontend
npm install
```

### 3. 端口被占用

**问题**: `Address already in use`

**解决方案**:
```bash
# 手动停止占用端口的进程
# Linux/Mac
lsof -ti:8000 | xargs kill -9
lsof -ti:5173 | xargs kill -9

# Windows
netstat -ano | findstr ":8000"
taskkill /F /PID <PID>
```

### 4. pytest未安装

**问题**: `ModuleNotFoundError: No module named 'pytest'`

**解决方案**:
```bash
# 在虚拟环境中安装pytest
source .venv/bin/activate
pip install pytest pytest-cov pytest-asyncio
```

### 5. 虚拟环境不存在

**问题**: `.venv` 目录不存在

**解决方案**:
```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

## 开发建议

### 日常开发工作流

1. **启动开发环境**
   ```bash
   python scripts/restart_and_test.py --no-tests
   ```

2. **修改代码**
   - 后端代码会自动重载（FastAPI支持热重载）
   - 前端代码会自动重载（Vite HMR）

3. **运行测试**
   ```bash
   # 使用虚拟环境中的pytest
   .venv/bin/pytest tests/ -v
   
   # 或运行完整的测试套件
   python scripts/restart_and_test.py
   ```

4. **停止服务**
   ```bash
   kill $(cat logs/backend.pid) $(cat logs/frontend.pid)
   ```

### CI/CD集成

脚本可以集成到CI/CD流程中：

```yaml
# GitHub Actions示例
- name: 重启服务并运行测试
  run: |
    python scripts/restart_and_test.py
  timeout-minutes: 10
```

## 环境要求

### 必需
- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 可选
- 虚拟环境（推荐）
- pytest（脚本会自动安装）
- colorama（用于Windows彩色输出，可选）

## 配置文件

脚本使用项目中的以下配置：

- `.env` - 环境变量配置
- `requirements.txt` - Python依赖
- `frontend/package.json` - Node.js依赖

## 更多信息

- [项目README](../README.md)
- [API文档](http://localhost:8000/docs)
- [部署指南](../DEPLOY.md)

## 贡献

如果你发现问题或有改进建议，请：
1. 提交Issue
2. 创建Pull Request
3. 联系维护者

---

**最后更新**: 2024-01-20
**维护者**: 项目团队
