@echo off
REM 环控平台维护工具 - 桌面版开发启动脚本 (Windows)

setlocal enabledelayedexpansion

echo ================================
echo 环控平台维护工具 - 开发模式
echo ================================

REM 进入 desktop 目录
cd /d "%~dp0"

REM 检查后端是否运行
curl -s http://localhost:8000/docs >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [✓] 后端服务已在运行
    set BACKEND_RUNNING=1
) else (
    set BACKEND_RUNNING=0
)

REM 启动后端（如果未运行）
if !BACKEND_RUNNING! EQU 0 (
    echo.
    echo [启动] 后端服务...
    cd ..
    
    REM 检查虚拟环境
    if exist ".venv\Scripts\activate.bat" (
        call .venv\Scripts\activate.bat
    )
    
    REM 后台启动后端
    start "HK Tool Backend" /MIN python main.py
    
    echo [✓] 后端服务已启动
    echo   访问地址: http://localhost:8000
    echo   API 文档: http://localhost:8000/docs
    
    REM 等待后端启动
    echo   等待后端就绪...
    timeout /t 5 /nobreak >nul
)

REM 检查前端是否运行
curl -s http://localhost:5173 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [✓] 前端服务已在运行
    set FRONTEND_RUNNING=1
) else (
    set FRONTEND_RUNNING=0
)

REM 启动前端（如果未运行）
if !FRONTEND_RUNNING! EQU 0 (
    echo.
    echo [启动] 前端开发服务器...
    cd "%~dp0\..\frontend"
    
    if not exist "node_modules" (
        echo   安装前端依赖...
        call npm install
    )
    
    REM 后台启动前端
    start "HK Tool Frontend" /MIN npm run dev
    
    echo [✓] 前端服务已启动
    echo   访问地址: http://localhost:5173
    
    REM 等待前端启动
    echo   等待前端就绪...
    timeout /t 5 /nobreak >nul
)

REM 启动 Electron
echo.
echo [启动] Electron 桌面应用...
cd "%~dp0"

if not exist "node_modules" (
    echo   安装桌面版依赖...
    call npm install
)

echo.
echo ================================
echo [✓] 所有服务已启动
echo ================================
echo.
echo 服务地址:
echo   - 后端 API:  http://localhost:8000
echo   - API 文档:  http://localhost:8000/docs
echo   - 前端界面: http://localhost:5173
echo.
echo 关闭此窗口将退出桌面应用
echo （后端和前端服务将继续运行）
echo.

REM 启动 Electron（前台）
call npm run dev

echo.
echo 桌面应用已关闭
echo.
echo 如需停止后端和前端服务，请手动关闭相应的窗口
echo 或使用任务管理器结束进程
echo.

endlocal
pause
