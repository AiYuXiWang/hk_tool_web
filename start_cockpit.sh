#!/bin/bash

# 能源驾驶舱启动脚本
# 用于快速启动前后端服务

echo "======================================"
echo "  启动能源驾驶舱服务"
echo "======================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="/home/engine/project"
cd "$PROJECT_ROOT"

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo -e "${RED}✗ 虚拟环境不存在，请先创建虚拟环境${NC}"
    exit 1
fi

# 检查是否已经在运行
backend_pid=$(ps aux | grep "python main.py" | grep -v grep | awk '{print $2}')
if [ -n "$backend_pid" ]; then
    echo -e "${YELLOW}⚠ 后端服务已在运行 (PID: $backend_pid)${NC}"
    echo "是否要重启服务? (y/n)"
    read -r answer
    if [ "$answer" = "y" ]; then
        echo "停止后端服务..."
        kill $backend_pid
        sleep 2
    else
        echo "保持现有服务运行"
    fi
fi

frontend_pid=$(ps aux | grep "vite" | grep -v grep | awk '{print $2}')
if [ -n "$frontend_pid" ]; then
    echo -e "${YELLOW}⚠ 前端服务已在运行 (PID: $frontend_pid)${NC}"
    echo "是否要重启服务? (y/n)"
    read -r answer
    if [ "$answer" = "y" ]; then
        echo "停止前端服务..."
        kill $frontend_pid
        sleep 2
    else
        echo "保持现有服务运行"
    fi
fi

echo ""
echo "正在启动服务..."
echo ""

# 激活虚拟环境并启动后端
echo -e "${GREEN}1. 启动后端服务...${NC}"
source .venv/bin/activate
nohup python main.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "   后端服务已启动 (PID: $BACKEND_PID)"
echo "   地址: http://localhost:8000"
echo "   日志: backend.log"

# 等待后端启动
echo "   等待后端服务启动..."
sleep 5

# 检查后端是否成功启动
if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}   ✓ 后端服务启动成功${NC}"
else
    echo -e "${RED}   ✗ 后端服务启动失败，请检查 backend.log${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}2. 启动前端服务...${NC}"
cd frontend
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   前端服务已启动 (PID: $FRONTEND_PID)"
echo "   地址: http://localhost:5173"
echo "   日志: frontend.log"

# 等待前端启动
echo "   等待前端服务启动..."
sleep 8

# 检查前端是否成功启动
if curl -s http://localhost:5173/ > /dev/null; then
    echo -e "${GREEN}   ✓ 前端服务启动成功${NC}"
else
    echo -e "${YELLOW}   ⚠ 前端服务可能未完全启动，请稍后访问${NC}"
fi

cd "$PROJECT_ROOT"

echo ""
echo "======================================"
echo -e "${GREEN}  服务启动完成！${NC}"
echo "======================================"
echo ""
echo "访问地址："
echo "  • 前端界面: http://localhost:5173"
echo "  • 后端API:  http://localhost:8000"
echo "  • API文档:  http://localhost:8000/docs"
echo ""
echo "驾驶舱页面："
echo "  • 能源驾驶舱:     http://localhost:5173/energy"
echo "  • 能源管理驾驶舱: http://localhost:5173/dashboard"
echo "  • 数据导出:       http://localhost:5173/export"
echo ""
echo "日志文件："
echo "  • 后端: $PROJECT_ROOT/backend.log"
echo "  • 前端: $PROJECT_ROOT/frontend.log"
echo ""
echo "停止服务："
echo "  • 运行: ./stop_cockpit.sh"
echo "  • 或手动: kill $BACKEND_PID (后端) / kill $FRONTEND_PID (前端)"
echo ""
echo "测试服务："
echo "  • 运行: ./test_cockpit.sh"
echo ""
