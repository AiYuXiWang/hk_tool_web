#!/bin/bash

# 环控平台维护工具 - 桌面版开发启动脚本（PySide6 原生版）

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

# 启动桌面应用
start_desktop() {
    echo -e "${BLUE}启动 PySide6 桌面应用...${NC}"
    cd ../desktop
    
    # 检查 Python 虚拟环境
    if [ ! -d "venv" ]; then
        echo "  创建虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    if [ ! -f "venv/.installed" ]; then
        echo "  安装桌面版依赖..."
        pip install -r requirements.txt
        touch venv/.installed
    fi
    
    # 启动桌面应用
    python3 main.py
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
    echo "================================"
    echo -e "${GREEN}✓ 后端服务已就绪${NC}"
    echo "================================"
    echo ""
    echo "服务地址:"
    echo "  - 后端 API:  http://localhost:8000"
    echo "  - API 文档:  http://localhost:8000/docs"
    echo ""
    echo "桌面应用使用 PySide6（Qt6）原生界面"
    echo "按 Ctrl+C 退出并清理所有进程"
    echo ""
    
    # 启动桌面应用
    start_desktop
}

# 执行主流程
main
