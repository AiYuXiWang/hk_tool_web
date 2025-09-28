# 部署指南

## 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/AiYuXiWang/hk_tool_web.git
cd hk_tool_web
```

### 2. 后端部署
```bash
# 安装Python依赖
pip install -r requirements.txt

# 启动后端服务
python main.py
```

### 3. 前端部署
```bash
# 进入前端目录
cd frontend

# 安装Node.js依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用
- 后端API: http://localhost:8000
- 前端界面: http://localhost:3000

## 生产环境部署

### 前端构建
```bash
cd frontend
npm run build
```

### 服务器配置
建议使用 Nginx 作为反向代理，配置前后端服务。

## 注意事项
- 确保MySQL数据库配置正确
- 检查防火墙设置，确保端口可访问
- 生产环境请修改默认密码和配置