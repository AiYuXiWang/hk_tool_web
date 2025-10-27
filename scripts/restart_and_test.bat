@echo off
setlocal ENABLEEXTENSIONS
setlocal ENABLEDELAYEDEXPANSION
chcp 65001 >nul
cd /d "%~dp0\.."

REM 重启前后端并运行测试脚本（Windows版本）
REM 功能：
REM 1. 停止现有的前后端服务
REM 2. 重新启动后端服务
REM 3. 重新启动前端服务
REM 4. 运行集成测试

title 重启前后端服务并运行测试

echo =========================================
echo   重启前后端服务并运行测试
echo =========================================
echo.

REM 项目根目录
set "PROJECT_ROOT=%CD%"
set "BACKEND_PORT=8000"
set "FRONTEND_PORT=5173"

REM 日志目录
if not exist "%PROJECT_ROOT%\logs" mkdir "%PROJECT_ROOT%\logs"
set "BACKEND_LOG=%PROJECT_ROOT%\logs\backend.log"
set "FRONTEND_LOG=%PROJECT_ROOT%\logs\frontend.log"

REM ===== 步骤 1: 环境检查 =====
echo [步骤 1/5] 环境检查
echo -----------------------------------------

REM 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python环境
    pause
    exit /b 1
)
echo [成功] Python环境检查通过

REM 检查Node.js环境
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Node.js环境
    pause
    exit /b 1
)
echo [成功] Node.js环境检查通过
echo.

REM ===== 步骤 2: 停止现有服务 =====
echo [步骤 2/5] 停止现有服务
echo -----------------------------------------

REM 停止后端服务
echo [信息] 检查端口 %BACKEND_PORT% (后端服务)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%BACKEND_PORT%" ^| findstr "LISTENING"') do (
    set "BACKEND_PID=%%a"
    echo [信息] 发现后端进程 PID: !BACKEND_PID!
    taskkill /F /PID !BACKEND_PID! >nul 2>&1
    if !errorlevel! equ 0 (
        echo [成功] 后端服务已停止
    ) else (
        echo [警告] 后端服务停止失败
    )
)

REM 停止前端服务
echo [信息] 检查端口 %FRONTEND_PORT% (前端服务)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%FRONTEND_PORT%" ^| findstr "LISTENING"') do (
    set "FRONTEND_PID=%%a"
    echo [信息] 发现前端进程 PID: !FRONTEND_PID!
    taskkill /F /PID !FRONTEND_PID! >nul 2>&1
    if !errorlevel! equ 0 (
        echo [成功] 前端服务已停止
    ) else (
        echo [警告] 前端服务停止失败
    )
)

REM 等待端口释放
timeout /t 2 /nobreak >nul
echo.

REM ===== 步骤 3: 启动后端服务 =====
echo [步骤 3/5] 启动后端服务
echo -----------------------------------------

REM 清空后端日志
type nul > "%BACKEND_LOG%"

echo [信息] 启动后端服务...
set "PYTHONIOENCODING=utf-8"
set "PYTHONUNBUFFERED=1"

REM 启动后端服务
start /B "" cmd /c "python main.py > "%BACKEND_LOG%" 2>&1"

REM 等待后端服务启动
echo [信息] 等待后端服务就绪...
set "BACKEND_READY=0"
for /l %%i in (1,1,30) do (
    timeout /t 1 /nobreak >nul
    netstat -an | findstr ":%BACKEND_PORT%" >nul 2>&1
    if !errorlevel! equ 0 (
        set "BACKEND_READY=1"
        goto :BACKEND_CHECK_DONE
    )
    echo [等待] 后端启动中... (%%i/30^)
)

:BACKEND_CHECK_DONE
if "!BACKEND_READY!"=="1" (
    echo [成功] 后端服务启动成功
    echo [信息] 后端API: http://localhost:%BACKEND_PORT%
    echo [信息] API文档: http://localhost:%BACKEND_PORT%/docs
    echo [信息] 后端日志: %BACKEND_LOG%
) else (
    echo [错误] 后端服务启动超时
    echo [信息] 请查看日志: %BACKEND_LOG%
    pause
    exit /b 1
)
echo.

REM ===== 步骤 4: 启动前端服务 =====
echo [步骤 4/5] 启动前端服务
echo -----------------------------------------

REM 清空前端日志
type nul > "%FRONTEND_LOG%"

echo [信息] 切换到前端目录...
cd /d "%PROJECT_ROOT%\frontend"

echo [信息] 启动前端服务...
start /B "" cmd /c "npm run dev > "%FRONTEND_LOG%" 2>&1"

REM 等待前端服务启动
echo [信息] 等待前端服务就绪...
set "FRONTEND_READY=0"
for /l %%i in (1,1,30) do (
    timeout /t 1 /nobreak >nul
    netstat -an | findstr ":%FRONTEND_PORT%" >nul 2>&1
    if !errorlevel! equ 0 (
        set "FRONTEND_READY=1"
        goto :FRONTEND_CHECK_DONE
    )
    echo [等待] 前端启动中... (%%i/30^)
)

:FRONTEND_CHECK_DONE
cd /d "%PROJECT_ROOT%"
if "!FRONTEND_READY!"=="1" (
    echo [成功] 前端服务启动成功
    echo [信息] 前端应用: http://localhost:%FRONTEND_PORT%
    echo [信息] 前端日志: %FRONTEND_LOG%
) else (
    echo [错误] 前端服务启动超时
    echo [信息] 请查看日志: %FRONTEND_LOG%
    pause
    exit /b 1
)
echo.

REM ===== 步骤 5: 运行测试 =====
echo [步骤 5/5] 运行测试
echo -----------------------------------------
echo.

REM 检查pytest
python -c "import pytest" >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] pytest未安装，正在安装...
    pip install pytest pytest-cov pytest-asyncio
)

set "TEST_FAILED=0"

REM 运行基础API测试
echo [测试 1/3] 运行基础API测试
echo -----------------------------------------
if exist "tests\test_energy_api.py" (
    python -m pytest tests\test_energy_api.py -v --tb=short --color=yes
    if !errorlevel! equ 0 (
        echo [成功] 基础API测试通过
    ) else (
        echo [失败] 基础API测试失败
        set "TEST_FAILED=1"
    )
) else (
    echo [警告] 未找到基础API测试文件
)
echo.

REM 运行边界情况测试
echo [测试 2/3] 运行边界情况测试
echo -----------------------------------------
if exist "tests\test_energy_edge_cases.py" (
    python -m pytest tests\test_energy_edge_cases.py -v --tb=short --color=yes
    if !errorlevel! equ 0 (
        echo [成功] 边界情况测试通过
    ) else (
        echo [失败] 边界情况测试失败
        set "TEST_FAILED=1"
    )
) else (
    echo [警告] 未找到边界情况测试文件
)
echo.

REM 运行前后端集成测试
echo [测试 3/3] 运行前后端集成测试
echo -----------------------------------------
if exist "tests\test_frontend_backend_integration.py" (
    python -m pytest tests\test_frontend_backend_integration.py -v --tb=short --color=yes
    if !errorlevel! equ 0 (
        echo [成功] 前后端集成测试通过
    ) else (
        echo [失败] 前后端集成测试失败
        set "TEST_FAILED=1"
    )
) else (
    echo [警告] 未找到前后端集成测试文件
)
echo.

REM 运行前端单元测试
echo [测试 4/4] 运行前端单元测试
echo -----------------------------------------
cd /d "%PROJECT_ROOT%\frontend"
call npm run test -- --run >nul 2>&1
if !errorlevel! equ 0 (
    echo [成功] 前端单元测试通过
) else (
    echo [警告] 前端单元测试失败或未配置
)
cd /d "%PROJECT_ROOT%"
echo.

REM ===== 测试结果 =====
echo =========================================
if "!TEST_FAILED!"=="0" (
    echo   [成功] 所有测试通过！
) else (
    echo   [失败] 部分测试失败
)
echo =========================================
echo.

REM ===== 服务信息 =====
echo 服务信息:
echo   - 后端API: http://localhost:%BACKEND_PORT%
echo   - 前端应用: http://localhost:%FRONTEND_PORT%
echo   - API文档: http://localhost:%BACKEND_PORT%/docs
echo.
echo 日志文件:
echo   - 后端日志: %BACKEND_LOG%
echo   - 前端日志: %FRONTEND_LOG%
echo.
echo 停止服务:
echo   - 运行此脚本会自动停止现有服务并重启
echo.

if "!TEST_FAILED!"=="0" (
    echo [完成] 前后端服务已重启并通过所有测试
    pause
    exit /b 0
) else (
    echo [警告] 服务已启动但部分测试失败
    pause
    exit /b 1
)
