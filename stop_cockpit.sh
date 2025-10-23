#!/bin/bash

# 能源驾驶舱停止脚本
# 用于停止前后端服务

echo "======================================"
echo "  停止能源驾驶舱服务"
echo "======================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 停止后端服务
backend_pid=$(ps aux | grep "python main.py" | grep -v grep | awk '{print $2}')
if [ -n "$backend_pid" ]; then
    echo "停止后端服务 (PID: $backend_pid)..."
    kill $backend_pid
    sleep 2
    if ps -p $backend_pid > /dev/null 2>&1; then
        echo -e "${YELLOW}  ⚠ 后端服务未响应，强制停止...${NC}"
        kill -9 $backend_pid
    fi
    echo -e "${GREEN}  ✓ 后端服务已停止${NC}"
else
    echo -e "${YELLOW}  ⚠ 后端服务未运行${NC}"
fi

# 停止前端服务
frontend_pid=$(ps aux | grep "vite" | grep -v grep | awk '{print $2}')
if [ -n "$frontend_pid" ]; then
    echo "停止前端服务 (PID: $frontend_pid)..."
    kill $frontend_pid
    sleep 2
    # 检查是否还有残留进程
    remaining=$(ps aux | grep "vite" | grep -v grep | awk '{print $2}')
    if [ -n "$remaining" ]; then
        echo -e "${YELLOW}  ⚠ 前端服务未响应，强制停止...${NC}"
        kill -9 $remaining
    fi
    echo -e "${GREEN}  ✓ 前端服务已停止${NC}"
else
    echo -e "${YELLOW}  ⚠ 前端服务未运行${NC}"
fi

echo ""
echo "======================================"
echo -e "${GREEN}  服务已停止${NC}"
echo "======================================"
echo ""
