@echo off
REM 环控平台维护工具 - 桌面版构建脚本 (Windows/PySide6)

setlocal enabledelayedexpansion

echo ================================
echo 环控平台维护工具 - 桌面版构建
echo ================================

REM 检查 Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未安装 Python
    exit /b 1
)

echo [✓] Python 版本:
python --version

REM 进入项目根目录
cd /d "%~dp0\.."

REM 1. 构建前端
echo.
echo 步骤 1/4: 构建前端...
echo -------------------
cd frontend

if not exist "node_modules" (
    echo 安装前端依赖...
    call npm install
)

echo 构建前端应用...
call npm run build

if %ERRORLEVEL% NEQ 0 (
    echo [错误] 前端构建失败
    exit /b 1
)

echo [✓] 前端构建完成

REM 2. 复制构建文件到桌面版
echo.
echo 步骤 2/4: 准备桌面版资源...
echo -------------------
cd ..\desktop

REM 创建 renderer 目录
if exist "renderer" rd /s /q renderer
mkdir renderer

REM 复制前端构建文件
xcopy /E /I /Y "..\frontend\dist\*" "renderer\"

echo [✓] 资源复制完成

REM 3. 创建虚拟环境并安装依赖
echo.
echo 步骤 3/4: 安装桌面版依赖...
echo -------------------

if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 安装依赖...
pip install -r requirements.txt
pip install pyinstaller

echo [✓] 依赖安装完成

REM 4. 使用 PyInstaller 打包
echo.
echo 步骤 4/4: 打包桌面应用...
echo -------------------

set PACKAGE_MODE=%1
if "%PACKAGE_MODE%"=="" set PACKAGE_MODE=onedir

REM 创建 spec 文件（如果不存在）
if not exist "hk-tool.spec" (
    echo 创建 PyInstaller spec 文件...
    (
        echo # -*- mode: python ; coding: utf-8 -*-
        echo.
        echo block_cipher = None
        echo.
        echo a = Analysis(
        echo     ['main.py'],
        echo     pathex=[],
        echo     binaries=[],
        echo     datas=[
        echo         ('renderer', 'renderer'^),
        echo         ('assets', 'assets'^),
        echo     ],
        echo     hiddenimports=[
        echo         'PySide6.QtWebEngineCore',
        echo         'PySide6.QtWebEngineWidgets',
        echo     ],
        echo     hookspath=[],
        echo     hooksconfig={},
        echo     runtime_hooks=[],
        echo     excludes=[],
        echo     win_no_prefer_redirects=False,
        echo     win_private_assemblies=False,
        echo     cipher=block_cipher,
        echo     noarchive=False,
        echo ^)
        echo.
        echo pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher^)
        echo.
        echo exe = EXE(
        echo     pyz,
        echo     a.scripts,
        echo     [],
        echo     exclude_binaries=True,
        echo     name='hk-tool-desktop',
        echo     debug=False,
        echo     bootloader_ignore_signals=False,
        echo     strip=False,
        echo     upx=True,
        echo     console=False,
        echo     disable_windowed_traceback=False,
        echo     argv_emulation=False,
        echo     target_arch=None,
        echo     codesign_identity=None,
        echo     entitlements_file=None,
        echo     icon='assets/icon.ico',
        echo ^)
        echo.
        echo coll = COLLECT(
        echo     exe,
        echo     a.binaries,
        echo     a.zipfiles,
        echo     a.datas,
        echo     strip=False,
        echo     upx=True,
        echo     upx_exclude=[],
        echo     name='hk-tool-desktop',
        echo ^)
    ) > hk-tool.spec
)

if "%PACKAGE_MODE%"=="onedir" (
    echo 打包为目录格式...
    pyinstaller hk-tool.spec --distpath dist --clean
) else if "%PACKAGE_MODE%"=="onefile" (
    echo 打包为单文件格式...
    pyinstaller main.py --onefile --windowed ^
        --name hk-tool-desktop ^
        --add-data "renderer;renderer" ^
        --add-data "assets;assets" ^
        --hidden-import PySide6.QtWebEngineCore ^
        --hidden-import PySide6.QtWebEngineWidgets ^
        --icon assets\icon.ico ^
        --distpath dist --clean
) else (
    echo [错误] 未知的打包模式 '%PACKAGE_MODE%'
    echo 支持的模式: onedir, onefile
    exit /b 1
)

if %ERRORLEVEL% NEQ 0 (
    echo [错误] 桌面应用打包失败
    exit /b 1
)

echo.
echo ================================
echo [✓] 构建完成！
echo ================================
echo.
echo 输出目录: desktop\dist
echo.

REM 列出构建产物
if exist "dist" (
    echo 构建产物:
    dir /B dist
)

echo.
echo 使用说明:
echo   - 运行开发模式: python main.py --dev
echo   - 打包为目录:   build.bat onedir
echo   - 打包为单文件: build.bat onefile
echo.

endlocal
