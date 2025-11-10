#!/bin/bash

# 环控平台维护工具 - 桌面版构建脚本

set -e

echo "================================"
echo "环控平台维护工具 - 桌面版构建"
echo "================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}错误: 未安装 Node.js${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Node.js 版本: $(node --version)"

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}错误: 未安装 npm${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} npm 版本: $(npm --version)"

# 进入项目根目录
cd "$(dirname "$0")/.."

# 1. 构建前端
echo ""
echo "步骤 1/3: 构建前端..."
echo "-------------------"
cd frontend

if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

echo "构建前端应用..."
npm run build

echo -e "${GREEN}✓${NC} 前端构建完成"

# 2. 复制构建文件到桌面版
echo ""
echo "步骤 2/3: 准备桌面版资源..."
echo "-------------------"
cd ../desktop

# 创建 renderer 目录
rm -rf renderer
mkdir -p renderer

# 复制前端构建文件
cp -r ../frontend/dist/* renderer/

echo -e "${GREEN}✓${NC} 资源复制完成"

# 3. 安装桌面版依赖
echo ""
echo "步骤 3/3: 安装桌面版依赖..."
echo "-------------------"

if [ ! -d "node_modules" ]; then
    npm install
else
    echo "依赖已存在，跳过安装"
fi

echo -e "${GREEN}✓${NC} 依赖安装完成"

# 4. 构建桌面应用
echo ""
echo "构建桌面应用..."
echo "-------------------"

# 根据参数选择构建平台
PLATFORM=${1:-all}

case $PLATFORM in
    win|windows)
        echo "构建 Windows 版本..."
        npm run build:win
        ;;
    mac|macos)
        echo "构建 macOS 版本..."
        npm run build:mac
        ;;
    linux)
        echo "构建 Linux 版本..."
        npm run build:linux
        ;;
    all)
        echo "构建所有平台版本..."
        npm run build
        ;;
    *)
        echo -e "${RED}错误: 未知的平台 '$PLATFORM'${NC}"
        echo "支持的平台: win, mac, linux, all"
        exit 1
        ;;
esac

echo ""
echo "================================"
echo -e "${GREEN}✓ 构建完成！${NC}"
echo "================================"
echo ""
echo "输出目录: desktop/dist"
echo ""

# 列出构建产物
if [ -d "dist" ]; then
    echo "构建产物:"
    ls -lh dist/
fi

echo ""
echo "使用说明:"
echo "  - 运行开发模式: npm run dev"
echo "  - 构建 Windows: ./build.sh win"
echo "  - 构建 macOS:   ./build.sh mac"
echo "  - 构建 Linux:   ./build.sh linux"
echo "  - 构建全部:     ./build.sh all"
