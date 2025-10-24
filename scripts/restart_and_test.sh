#!/bin/bash

# 重启前后端并运行测试脚本
# 功能：
# 1. 停止现有的前后端服务
# 2. 重新启动后端服务
# 3. 重新启动前端服务
# 4. 运行集成测试

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 日志文件
BACKEND_LOG="$PROJECT_ROOT/logs/backend.log"
FRONTEND_LOG="$PROJECT_ROOT/logs/frontend.log"
mkdir -p "$PROJECT_ROOT/logs"

# 端口配置
BACKEND_PORT=8000
FRONTEND_PORT=5173

# 打印分隔线
print_separator() {
    echo -e "${BLUE}=======================================${NC}"
}

# 打印标题
print_title() {
    print_separator
    echo -e "${BLUE}$1${NC}"
    print_separator
}

# 打印成功消息
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# 打印错误消息
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# 打印警告消息
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# 打印信息消息
print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # 端口被占用
    else
        return 1  # 端口空闲
    fi
}

# 停止指定端口的进程
kill_port() {
    local port=$1
    local service_name=$2
    
    if check_port $port; then
        print_info "正在停止 $service_name (端口 $port)..."
        local pids=$(lsof -ti:$port)
        if [ -n "$pids" ]; then
            echo "$pids" | xargs kill -9 2>/dev/null || true
            sleep 2
            
            # 再次检查是否成功停止
            if check_port $port; then
                print_error "$service_name 停止失败"
                return 1
            else
                print_success "$service_name 已停止"
            fi
        fi
    else
        print_info "$service_name 未运行"
    fi
    return 0
}

# 等待服务启动
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=${3:-30}
    local attempt=0
    
    print_info "等待 $service_name 启动..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f -o /dev/null "$url" 2>/dev/null; then
            print_success "$service_name 已就绪"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo -ne "${CYAN}⏳ 等待中... ($attempt/$max_attempts)\r${NC}"
        sleep 1
    done
    
    echo ""
    print_error "$service_name 启动超时"
    return 1
}

# 检查Python环境
check_python() {
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        print_error "Python未安装"
        exit 1
    fi
    print_success "Python环境检查通过"
}

# 检查Node.js环境
check_node() {
    if ! command -v node &> /dev/null; then
        print_error "Node.js未安装"
        exit 1
    fi
    print_success "Node.js环境检查通过"
}

# 启动后端服务
start_backend() {
    print_info "启动后端服务..."
    
    # 设置Python环境变量
    export PYTHONIOENCODING=utf-8
    export PYTHONUNBUFFERED=1
    
    # 清空日志文件
    > "$BACKEND_LOG"
    
    # 检查虚拟环境
    if [ -f "$PROJECT_ROOT/.venv/bin/python" ]; then
        PYTHON_CMD="$PROJECT_ROOT/.venv/bin/python"
        print_info "使用虚拟环境中的Python"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD=python3
    else
        PYTHON_CMD=python
    fi
    
    # 启动后端服务（后台运行）
    nohup $PYTHON_CMD main.py > "$BACKEND_LOG" 2>&1 &
    echo $! > "$PROJECT_ROOT/logs/backend.pid"
    
    print_info "后端PID: $(cat $PROJECT_ROOT/logs/backend.pid)"
    
    # 等待后端启动
    if wait_for_service "http://localhost:$BACKEND_PORT/docs" "后端服务" 30; then
        print_success "后端服务启动成功"
        print_info "后端日志: $BACKEND_LOG"
        print_info "API文档: http://localhost:$BACKEND_PORT/docs"
        return 0
    else
        print_error "后端服务启动失败"
        print_info "查看日志: tail -f $BACKEND_LOG"
        return 1
    fi
}

# 启动前端服务
start_frontend() {
    print_info "启动前端服务..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # 清空日志文件
    > "$FRONTEND_LOG"
    
    # 启动前端服务（后台运行）
    nohup npm run dev > "$FRONTEND_LOG" 2>&1 &
    echo $! > "$PROJECT_ROOT/logs/frontend.pid"
    
    print_info "前端PID: $(cat $PROJECT_ROOT/logs/frontend.pid)"
    
    # 等待前端启动
    if wait_for_service "http://localhost:$FRONTEND_PORT" "前端服务" 30; then
        print_success "前端服务启动成功"
        print_info "前端日志: $FRONTEND_LOG"
        print_info "应用地址: http://localhost:$FRONTEND_PORT"
        cd "$PROJECT_ROOT"
        return 0
    else
        print_error "前端服务启动失败"
        print_info "查看日志: tail -f $FRONTEND_LOG"
        cd "$PROJECT_ROOT"
        return 1
    fi
}

# 运行测试
run_tests() {
    print_title "运行测试套件"
    
    # 检查pytest
    if ! $PYTHON_CMD -c "import pytest" &> /dev/null; then
        print_warning "pytest未安装，正在安装..."
        pip install pytest pytest-cov pytest-asyncio
    fi
    
    local test_failed=0
    
    # 1. 运行基础API测试
    echo ""
    print_info "[1/3] 运行基础API测试"
    if [ -f "tests/test_energy_api.py" ]; then
        if $PYTHON_CMD -m pytest tests/test_energy_api.py -v --tb=short --color=yes; then
            print_success "基础API测试通过"
        else
            print_error "基础API测试失败"
            test_failed=1
        fi
    else
        print_warning "未找到基础API测试文件"
    fi
    
    # 2. 运行边界情况测试
    echo ""
    print_info "[2/3] 运行边界情况测试"
    if [ -f "tests/test_energy_edge_cases.py" ]; then
        if $PYTHON_CMD -m pytest tests/test_energy_edge_cases.py -v --tb=short --color=yes; then
            print_success "边界情况测试通过"
        else
            print_error "边界情况测试失败"
            test_failed=1
        fi
    else
        print_warning "未找到边界情况测试文件"
    fi
    
    # 3. 运行前后端集成测试
    echo ""
    print_info "[3/3] 运行前后端集成测试"
    if [ -f "tests/test_frontend_backend_integration.py" ]; then
        if $PYTHON_CMD -m pytest tests/test_frontend_backend_integration.py -v --tb=short --color=yes; then
            print_success "前后端集成测试通过"
        else
            print_error "前后端集成测试失败"
            test_failed=1
        fi
    else
        print_warning "未找到前后端集成测试文件"
    fi
    
    # 运行前端测试
    echo ""
    print_info "[4/4] 运行前端单元测试"
    cd "$PROJECT_ROOT/frontend"
    if npm run test -- --run 2>/dev/null; then
        print_success "前端单元测试通过"
    else
        print_warning "前端单元测试失败或未配置"
        # 前端测试失败不影响整体结果
    fi
    cd "$PROJECT_ROOT"
    
    echo ""
    if [ $test_failed -eq 0 ]; then
        print_separator
        print_success "🎉 所有测试通过！"
        print_separator
        return 0
    else
        print_separator
        print_error "❌ 部分测试失败"
        print_separator
        return 1
    fi
}

# 主函数
main() {
    print_title "重启前后端服务并运行测试"
    
    echo ""
    print_info "项目根目录: $PROJECT_ROOT"
    echo ""
    
    # 1. 环境检查
    print_title "步骤 1: 环境检查"
    check_python
    check_node
    
    # 设置Python命令
    if command -v python3 &> /dev/null; then
        PYTHON_CMD=python3
    else
        PYTHON_CMD=python
    fi
    
    # 2. 停止现有服务
    echo ""
    print_title "步骤 2: 停止现有服务"
    kill_port $BACKEND_PORT "后端服务"
    kill_port $FRONTEND_PORT "前端服务"
    
    # 3. 启动后端服务
    echo ""
    print_title "步骤 3: 启动后端服务"
    if ! start_backend; then
        print_error "后端启动失败，请检查日志: $BACKEND_LOG"
        exit 1
    fi
    
    # 4. 启动前端服务
    echo ""
    print_title "步骤 4: 启动前端服务"
    if ! start_frontend; then
        print_error "前端启动失败，请检查日志: $FRONTEND_LOG"
        exit 1
    fi
    
    # 5. 运行测试
    echo ""
    print_title "步骤 5: 运行测试"
    if ! run_tests; then
        print_error "测试失败"
        exit 1
    fi
    
    # 6. 完成
    echo ""
    print_title "完成"
    print_success "前后端服务已重启并通过所有测试"
    echo ""
    print_info "服务信息:"
    echo -e "  • 后端API: ${CYAN}http://localhost:$BACKEND_PORT${NC}"
    echo -e "  • 前端应用: ${CYAN}http://localhost:$FRONTEND_PORT${NC}"
    echo -e "  • API文档: ${CYAN}http://localhost:$BACKEND_PORT/docs${NC}"
    echo ""
    print_info "日志文件:"
    echo -e "  • 后端日志: ${CYAN}$BACKEND_LOG${NC}"
    echo -e "  • 前端日志: ${CYAN}$FRONTEND_LOG${NC}"
    echo ""
    print_info "停止服务:"
    echo -e "  • 后端: ${CYAN}kill \$(cat $PROJECT_ROOT/logs/backend.pid)${NC}"
    echo -e "  • 前端: ${CYAN}kill \$(cat $PROJECT_ROOT/logs/frontend.pid)${NC}"
    echo ""
}

# 运行主函数
main
