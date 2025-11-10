#!/bin/bash

# 环控平台维护工具 - 桌面版开发启动脚本

set -e

echo "================================"
echo "环控平台维护工具 - 开发模式"
echo "================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查后端是否运行
check_backend() {
    if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 启动后端
start_backend() {
    echo -e "${BLUE}启动后端服务...${NC}"
    cd ..
    
    # 检查虚拟环境
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    
    # 后台启动后端
    python main.py > desktop/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > desktop/backend.pid
    
    echo -e "${GREEN}✓${NC} 后端服务已启动 (PID: $BACKEND_PID)"
    echo "  日志文件: desktop/backend.log"
    
    # 等待后端启动
    echo -n "  等待后端就绪"
    for i in {1..30}; do
        if check_backend; then
            echo -e " ${GREEN}✓${NC}"
            return 0
        fi
        echo -n "."
        sleep 1
    done
    
    echo -e " ${RED}✗${NC}"
    echo -e "${RED}错误: 后端启动超时${NC}"
    return 1
}

# 启动前端
start_frontend() {
    echo -e "${BLUE}启动前端开发服务器...${NC}"
    cd ../frontend
    
    if [ ! -d "node_modules" ]; then
        echo "  安装前端依赖..."
        npm install
    fi
    
    # 后台启动前端
    npm run dev > ../desktop/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../desktop/frontend.pid
    
    echo -e "${GREEN}✓${NC} 前端服务已启动 (PID: $FRONTEND_PID)"
    echo "  访问地址: http://localhost:5173"
    echo "  日志文件: desktop/frontend.log"
}

# 启动 Electron
start_electron() {
    echo -e "${BLUE}启动 Electron 桌面应用...${NC}"
    cd ../desktop
    
    if [ ! -d "node_modules" ]; then
        echo "  安装桌面版依赖..."
        npm install
    fi
    
    # 前台启动 Electron（这样可以看到日志和关闭时能清理）
    npm run dev
}

# 清理函数
cleanup() {
    echo ""
    echo -e "${YELLOW}正在清理进程...${NC}"
    
    # 停止后端
    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid)
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            echo "  停止后端服务 (PID: $BACKEND_PID)"
            kill $BACKEND_PID 2>/dev/null || true
        fi
        rm -f backend.pid
    fi
    
    # 停止前端
    if [ -f "frontend.pid" ]; then
        FRONTEND_PID=$(cat frontend.pid)
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            echo "  停止前端服务 (PID: $FRONTEND_PID)"
            kill $FRONTEND_PID 2>/dev/null || true
        fi
        rm -f frontend.pid
    fi
    
    echo -e "${GREEN}✓${NC} 清理完成"
}

# 注册退出时的清理函数
trap cleanup EXIT INT TERM

# 主流程
main() {
    cd "$(dirname "$0")"
    
    # 检查后端是否已经在运行
    if check_backend; then
        echo -e "${GREEN}✓${NC} 后端服务已在运行"
    else
        start_backend || exit 1
    fi
    
    echo ""
    
    # 检查前端是否已经在运行
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} 前端服务已在运行"
    else
        start_frontend
        sleep 3  # 等待前端启动
    fi
    
    echo ""
    echo "================================"
    echo -e "${GREEN}✓ 所有服务已启动${NC}"
    echo "================================"
    echo ""
    echo "服务地址:"
    echo "  - 后端 API:  http://localhost:8000"
    echo "  - API 文档:  http://localhost:8000/docs"
    echo "  - 前端界面: http://localhost:5173"
    echo ""
    echo "按 Ctrl+C 退出并清理所有进程"
    echo ""
    
    # 启动 Electron
    start_electron
}

# 执行主流程
main
