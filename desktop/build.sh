#!/bin/bash

# 环控平台维护工具 - 桌面版构建脚本（PySide6）

set -e

echo "================================"
echo "环控平台维护工具 - 桌面版构建"
echo "================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未安装 Python3${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 版本: $(python3 --version)"

# 进入项目根目录
cd "$(dirname "$0")/.."

# 1. 构建前端
echo ""
echo "步骤 1/4: 构建前端..."
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
echo "步骤 2/4: 准备桌面版资源..."
echo "-------------------"
cd ../desktop

# 创建 renderer 目录
rm -rf renderer
mkdir -p renderer

# 复制前端构建文件
cp -r ../frontend/dist/* renderer/

echo -e "${GREEN}✓${NC} 资源复制完成"

# 3. 创建虚拟环境并安装依赖
echo ""
echo "步骤 3/4: 安装桌面版依赖..."
echo "-------------------"

if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

echo "激活虚拟环境..."
source venv/bin/activate

echo "安装依赖..."
pip install -r requirements.txt
pip install pyinstaller

echo -e "${GREEN}✓${NC} 依赖安装完成"

# 4. 使用 PyInstaller 打包
echo ""
echo "步骤 4/4: 打包桌面应用..."
echo "-------------------"

# 根据参数选择打包选项
PLATFORM=${1:-onedir}

# 创建 spec 文件（如果不存在）
if [ ! -f "hk-tool.spec" ]; then
    echo "创建 PyInstaller spec 文件..."
    cat > hk-tool.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('renderer', 'renderer'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='hk-tool-desktop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.png',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='hk-tool-desktop',
)

# macOS App Bundle
app = BUNDLE(
    coll,
    name='环控平台维护工具.app',
    icon='assets/icon.icns',
    bundle_identifier='com.hk.tool.desktop',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'LSUIElement': False,
    },
)
EOF
fi

case $PLATFORM in
    onedir)
        echo "打包为目录格式..."
        pyinstaller hk-tool.spec --distpath dist --clean
        ;;
    onefile)
        echo "打包为单文件格式..."
        pyinstaller main.py --onefile --windowed \
            --name hk-tool-desktop \
            --add-data "renderer:renderer" \
            --add-data "assets:assets" \
            --hidden-import PySide6.QtWebEngineCore \
            --hidden-import PySide6.QtWebEngineWidgets \
            --distpath dist --clean
        ;;
    *)
        echo -e "${RED}错误: 未知的打包模式 '$PLATFORM'${NC}"
        echo "支持的模式: onedir, onefile"
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
echo "  - 运行开发模式: python3 main.py --dev"
echo "  - 打包为目录:   ./build.sh onedir"
echo "  - 打包为单文件: ./build.sh onefile"
