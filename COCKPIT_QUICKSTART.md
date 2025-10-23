# 能源驾驶舱快速启动指南

## 📋 目录

- [快速启动](#快速启动)
- [服务管理](#服务管理)
- [功能测试](#功能测试)
- [访问地址](#访问地址)
- [API接口](#api接口)
- [故障排查](#故障排查)

---

## 🚀 快速启动

### 方式一：使用启动脚本（推荐）

```bash
cd /home/engine/project
./start_cockpit.sh
```

### 方式二：手动启动

**后端启动**:
```bash
cd /home/engine/project
source .venv/bin/activate
python main.py > backend.log 2>&1 &
```

**前端启动**:
```bash
cd /home/engine/project/frontend
npm run dev > ../frontend.log 2>&1 &
```

---

## 🎮 服务管理

### 启动服务
```bash
./start_cockpit.sh
```

### 停止服务
```bash
./stop_cockpit.sh
```

### 重启服务
```bash
./stop_cockpit.sh && ./start_cockpit.sh
```

### 查看服务状态
```bash
ps aux | grep -E "python main.py|vite" | grep -v grep
```

### 查看日志

**实时查看后端日志**:
```bash
tail -f backend.log
```

**实时查看前端日志**:
```bash
tail -f frontend.log
```

---

## 🧪 功能测试

### 运行完整测试
```bash
./test_cockpit.sh
```

### 手动测试API

**测试后端连接**:
```bash
curl http://localhost:8000/
```

**测试KPI接口**:
```bash
curl "http://localhost:8000/api/energy/kpi?line=M3" | python -m json.tool
```

**测试实时监测**:
```bash
curl "http://localhost:8000/api/energy/realtime?line=M3" | python -m json.tool
```

**测试历史趋势**:
```bash
curl "http://localhost:8000/api/energy/trend?line=M3&period=24h" | python -m json.tool
```

**测试节能建议**:
```bash
curl "http://localhost:8000/api/energy/suggestions?line=M3" | python -m json.tool
```

**测试能耗对比**:
```bash
curl "http://localhost:8000/api/energy/compare?line=M3&period=24h" | python -m json.tool
```

**测试分类分项**:
```bash
curl "http://localhost:8000/api/energy/classification?line=M3&period=24h" | python -m json.tool
```

---

## 🌐 访问地址

### 前端界面
- **主页**: http://localhost:5173/
- **能源驾驶舱**: http://localhost:5173/energy
- **能源管理驾驶舱**: http://localhost:5173/dashboard
- **数据导出**: http://localhost:5173/export

### 后端API
- **API根路径**: http://localhost:8000/
- **API文档（Swagger）**: http://localhost:8000/docs
- **API文档（ReDoc）**: http://localhost:8000/redoc

---

## 📡 API接口

### 基础接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/` | GET | API欢迎页面 |
| `/api/lines` | GET | 获取所有线路 |
| `/api/config/line_configs` | GET | 获取线路配置 |

### 能源驾驶舱接口

| 接口 | 方法 | 参数 | 描述 |
|------|------|------|------|
| `/api/energy/kpi` | GET | line, station_ip | 获取KPI指标 |
| `/api/energy/realtime` | GET | line, station_ip | 实时能耗监测 |
| `/api/energy/trend` | GET | line, station_ip, period | 历史趋势分析 |
| `/api/energy/suggestions` | GET | line, station_ip | 节能优化建议 |
| `/api/energy/compare` | GET | line, station_ip, period | 能耗对比分析 |
| `/api/energy/classification` | GET | line, station_ip, period | 分类分项分析 |

### 参数说明

**line**: 线路名称
- M3 - 3号线
- M8 - 8号线
- M11 - 11号线
- M1 - 1号线
- M2 - 2号线

**period**: 时间周期
- 24h - 24小时
- 7d - 7天
- 30d - 30天
- 90d - 90天

**station_ip**: 车站IP地址（可选）

---

## 🎯 核心功能

### 1. 实时监测
- 📊 实时功率曲线显示
- ⏱️ 5分钟数据刷新
- 🔄 多线路切换支持
- 📈 数据可视化展示

### 2. KPI指标
- 💡 总能耗统计
- ⚡ 当前功率显示
- 📈 峰值功率记录
- 🚉 站点数量统计

### 3. 历史趋势
- 📅 24小时趋势
- 📆 7天趋势
- 📊 30天趋势
- 📉 90天趋势

### 4. 智能建议
- 🤖 AI驱动的节能建议
- 💡 优化策略推荐
- 💰 预期收益估算

### 5. 能耗对比
- 📊 环比数据对比
- 📈 同比数据对比
- 📉 变化百分比计算

### 6. 分类分项
- 🏷️ 设备类别分类
- 📊 能耗占比统计
- 📈 多维度数据分析

---

## 🔧 故障排查

### 问题1: 后端无法启动

**症状**: 运行 `python main.py` 报错

**解决方案**:
```bash
# 1. 检查虚拟环境是否激活
source .venv/bin/activate

# 2. 重新安装依赖
python -m pip install -r requirements.txt

# 3. 检查端口是否被占用
lsof -i :8000
```

### 问题2: 前端无法启动

**症状**: 运行 `npm run dev` 报错

**解决方案**:
```bash
# 1. 重新安装依赖
cd frontend
rm -rf node_modules package-lock.json
npm install

# 2. 检查端口是否被占用
lsof -i :5173

# 3. 清理缓存
npm cache clean --force
```

### 问题3: API返回错误

**症状**: curl请求返回错误响应

**解决方案**:
```bash
# 1. 查看后端日志
tail -50 backend.log

# 2. 检查服务是否运行
ps aux | grep "python main.py"

# 3. 重启后端服务
./stop_cockpit.sh
./start_cockpit.sh
```

### 问题4: 数据库连接错误

**症状**: 日志中显示 MySQL 连接失败

**说明**: 
- 这是预期行为，审计日志功能需要数据库
- 核心功能不依赖数据库，使用配置文件数据
- 如需启用审计功能，请配置 .env 中的数据库参数

### 问题5: Token认证失败

**症状**: 日志中显示 HK_PLATFORM_TOKEN 缺失

**说明**:
- 这是预期行为，实时设备控制需要平台Token
- 当前使用配置文件中的模拟数据
- 如需连接实际平台，请在 .env 中配置 HK_PLATFORM_TOKEN

---

## 📊 性能指标

### 响应时间
- API平均响应: < 10ms
- 页面加载: < 1s
- 数据刷新: < 100ms

### 并发处理
- 默认限流: 100请求/分钟
- 能源API限流: 200请求/分钟
- 支持多用户同时访问

---

## 📝 配置说明

### 环境变量配置

编辑 `.env` 文件:
```bash
# 数据库配置（可选）
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=hk_tool_web

# 环控平台API配置（可选）
HK_API_BASE_URL=http://demo-platform-api.com
HK_API_TOKEN=demo_token_for_testing

# 服务配置
HOST=0.0.0.0
PORT=8000
DEBUG=false

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# 前端配置
FRONTEND_URL=http://localhost:5173
```

### 线路配置

线路配置在 `config_electricity.py` 中，包括：
- 线路名称
- 站点信息
- 设备列表
- 额定功率

---

## 📚 相关文档

- [完整测试报告](COCKPIT_TEST_REPORT.md)
- [项目README](README.md)
- [部署文档](DEPLOY.md)
- [集成指南](INTEGRATION_GUIDE_T045.md)

---

## 🔍 监控和日志

### 查看所有日志
```bash
# 后端日志
tail -f backend.log

# 前端日志  
tail -f frontend.log

# 查看最近的错误
grep ERROR backend.log | tail -20
```

### 监控服务状态
```bash
# 持续监控
watch -n 1 'ps aux | grep -E "python main.py|vite" | grep -v grep'

# 检查端口占用
netstat -tulpn | grep -E "8000|5173"
```

---

## 💡 开发提示

### 热重载
- 后端：修改代码后需要重启服务
- 前端：Vite自动热重载，无需重启

### 调试模式
```bash
# 后端调试
DEBUG=true python main.py

# 查看详细日志
LOG_LEVEL=DEBUG python main.py
```

---

## 📞 获取帮助

如有问题，请检查：
1. 服务是否正常运行：`ps aux | grep -E "python|vite"`
2. 端口是否被占用：`lsof -i :8000` 和 `lsof -i :5173`
3. 日志文件：`backend.log` 和 `frontend.log`
4. 运行测试脚本：`./test_cockpit.sh`

---

**最后更新**: 2025-10-23  
**版本**: 1.0.0
