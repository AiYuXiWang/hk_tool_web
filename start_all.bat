@echo off
setlocal ENABLEEXTENSIONS
setlocal ENABLEDELAYEDEXPANSION
chcp 65001 >nul
cd /d "%~dp0"
title 环控平台维护工具Web版启动器

REM 在某些集成终端环境下无法打开新窗口，支持无新窗口模式
set "USE_START=1"
if /I "%NO_START_WINDOWS%"=="1" (
    set "USE_START=0"
    echo 检测到 NO_START_WINDOWS=1，将在当前终端后台启动服务。
)

echo ========================================
echo   环控平台维护工具Web版启动器
echo ========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python环境，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

REM 检查Node.js环境
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Node.js环境，请先安装Node.js
    pause
    exit /b 1
)

REM 安装后端依赖（如果尚未安装）
echo 检查并安装后端依赖...
python -m pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 后端依赖安装失败，请手动运行 "pip install -r requirements.txt"
)

echo.
echo 启动后端服务...
set "PYTHONIOENCODING=utf-8"
if "%USE_START%"=="1" (
    start "后端服务 - 环控平台维护工具" cmd /k "chcp 65001 >nul && python main.py"
) else (
    echo 在当前窗口后台启动后端服务...
    start /b "" cmd /c "chcp 65001 >nul && python main.py"
)

REM 等待后端服务启动并进行健康检查（支持重试并不中断前端启动）
timeout /t 10 /nobreak >nul
set "BACKEND_OK=0"
for /l %%i in (1,1,5) do (
    powershell -NoLogo -NoProfile -Command "try { (Invoke-WebRequest 'http://localhost:8000/docs' -UseBasicParsing -TimeoutSec 3) | Out-Null; exit 0 } catch { exit 1 }"
    if !errorlevel! equ 0 (
        set "BACKEND_OK=1"
        goto :HC_DONE
    )
    timeout /t 2 /nobreak >nul
)
:HC_DONE
if "!BACKEND_OK!"=="1" (
    echo 后端健康检查通过。
) else (
    echo 警告: 后端服务未通过健康检查，将继续启动前端。
)

echo.
echo 安装前端依赖...
cd frontend
npm install >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 前端依赖安装失败，请进入frontend目录手动运行 "npm install"
)

echo.
echo 启动前端开发服务器...
if "%USE_START%"=="1" (
    start "前端开发服务器 - 环控平台维护工具" cmd /k "chcp 65001 >nul && npm run dev"
) else (
    echo 在当前窗口后台启动前端开发服务器...
    start /b "" cmd /c "chcp 65001 >nul && npm run dev"
)

echo.
echo ========================================
echo 启动完成!
echo.
echo 后端API服务: http://localhost:8000
echo 前端应用界面: http://localhost:5173
echo.
echo 注意: 请勿关闭此窗口，关闭后服务将停止
echo ========================================
echo.

REM 返回到项目根目录
cd ..
if "%USE_START%"=="1" (
    pause
) else (
    echo 已在当前终端后台启动服务（不暂停当前窗口）。
)