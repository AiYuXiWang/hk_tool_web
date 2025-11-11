@echo off
REM 环控平台维护工具 - 桌面版开发启动脚本 (Windows/PySide6 原生版)

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

REM 启动桌面应用
echo.
echo [启动] PySide6 桌面应用...
cd "%~dp0"

REM 检查 Python 虚拟环境
if not exist "venv" (
    echo   创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖（如果需要）
if not exist "venv\.installed" (
    echo   安装桌面版依赖...
    pip install -r requirements.txt
    echo installed > venv\.installed
)

echo.
echo ================================
echo [✓] 后端服务已就绪
echo ================================
echo.
echo 服务地址:
echo   - 后端 API:  http://localhost:8000
echo   - API 文档:  http://localhost:8000/docs
echo.
echo 桌面应用使用 PySide6 (Qt6) 原生界面
echo 关闭此窗口将退出桌面应用
echo （后端服务将继续运行）
echo.

REM 启动桌面应用（前台）
python main.py

echo.
echo 桌面应用已关闭
echo.
echo 如需停止后端服务，请手动关闭相应的窗口
echo 或使用任务管理器结束进程
echo.

endlocal
pause
