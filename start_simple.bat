@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 环控平台维护工具Web版启动器(简化版)

echo ========================================
echo   环控平台维护工具Web版启动器(简化版)
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

echo 启动后端服务...
start /b "" cmd /c "python main.py"

echo 等待后端启动...
timeout /t 5 /nobreak >nul

echo 启动前端服务...
cd frontend
start /b "" cmd /c "npm run dev"

echo.
echo ========================================
echo 启动完成!
echo.
echo 后端API服务: http://localhost:8000
echo 前端应用界面: http://localhost:5173
echo.
echo 注意: 服务已在后台启动
echo ========================================
echo.

cd ..
echo 按任意键退出...
pause >nul