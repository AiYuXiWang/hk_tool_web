@echo off
REM 环控平台维护工具 - 桌面版构建脚本 (Windows)

setlocal enabledelayedexpansion

echo ================================
echo 环控平台维护工具 - 桌面版构建
echo ================================

REM 检查 Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未安装 Node.js
    exit /b 1
)

echo [✓] Node.js 版本:
node --version

REM 检查 npm
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未安装 npm
    exit /b 1
)

echo [✓] npm 版本:
npm --version

REM 进入项目根目录
cd /d "%~dp0\.."

REM 1. 构建前端
echo.
echo 步骤 1/3: 构建前端...
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
echo 步骤 2/3: 准备桌面版资源...
echo -------------------
cd ..\desktop

REM 创建 renderer 目录
if exist "renderer" rd /s /q renderer
mkdir renderer

REM 复制前端构建文件
xcopy /E /I /Y "..\frontend\dist\*" "renderer\"

echo [✓] 资源复制完成

REM 3. 安装桌面版依赖
echo.
echo 步骤 3/3: 安装桌面版依赖...
echo -------------------

if not exist "node_modules" (
    call npm install
) else (
    echo 依赖已存在，跳过安装
)

echo [✓] 依赖安装完成

REM 4. 构建桌面应用
echo.
echo 构建桌面应用...
echo -------------------

set PLATFORM=%1
if "%PLATFORM%"=="" set PLATFORM=win

if "%PLATFORM%"=="win" (
    echo 构建 Windows 版本...
    call npm run build:win
) else if "%PLATFORM%"=="all" (
    echo 构建所有平台版本...
    call npm run build
) else (
    echo [错误] Windows 环境仅支持构建 Windows 版本
    echo 使用方式: build.bat [win^|all]
    exit /b 1
)

if %ERRORLEVEL% NEQ 0 (
    echo [错误] 桌面应用构建失败
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
echo   - 运行开发模式: npm run dev
echo   - 构建 Windows: build.bat win
echo   - 构建全部:     build.bat all
echo.

endlocal
