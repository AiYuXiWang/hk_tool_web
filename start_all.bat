@echo off
title 环控平台维护工具Web版启动器

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
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 后端依赖安装失败，请手动运行 "pip install -r requirements.txt"
)

echo.
echo 启动后端服务...
start "后端服务 - 环控平台维护工具" cmd /k "python main.py"

REM 等待几秒让后端服务启动
timeout /t 5 /nobreak >nul

echo.
echo 安装前端依赖...
cd frontend
npm install >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 前端依赖安装失败，请进入frontend目录手动运行 "npm install"
)

echo.
echo 启动前端开发服务器...
start "前端开发服务器 - 环控平台维护工具" cmd /k "npm run dev"

echo.
echo ========================================
echo 启动完成!
echo.
echo 后端API服务: http://localhost:8000
echo 前端应用界面: http://localhost:3000
echo.
echo 注意: 请勿关闭此窗口，关闭后服务将停止
echo ========================================
echo.

REM 返回到项目根目录
cd ..

pause