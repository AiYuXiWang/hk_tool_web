@echo off
REM 前后端集成测试运行脚本 (Windows版本)
REM 用于运行所有能源模块的测试

echo ================================
echo 前后端集成测试套件
echo ================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python未安装
    exit /b 1
)

echo [OK] Python环境检查通过
echo.

REM 检查pytest
python -c "import pytest" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] pytest未安装，正在安装...
    pip install pytest pytest-cov pytest-asyncio
)

echo [OK] pytest已准备就绪
echo.

REM 运行测试
echo 开始运行测试...
echo.

REM 1. 运行基础API测试
echo [1/3] 运行基础API测试
python -m pytest tests/test_energy_api.py -v --tb=short --color=yes
if errorlevel 1 (
    echo [FAIL] 基础API测试失败
    exit /b 1
)
echo [PASS] 基础API测试通过
echo.

REM 2. 运行边界情况测试
echo [2/3] 运行边界情况测试
python -m pytest tests/test_energy_edge_cases.py -v --tb=short --color=yes
if errorlevel 1 (
    echo [FAIL] 边界情况测试失败
    exit /b 1
)
echo [PASS] 边界情况测试通过
echo.

REM 3. 运行前后端集成测试
echo [3/3] 运行前后端集成测试
python -m pytest tests/test_frontend_backend_integration.py -v --tb=short --color=yes
if errorlevel 1 (
    echo [FAIL] 前后端集成测试失败
    exit /b 1
)
echo [PASS] 前后端集成测试通过
echo.

REM 运行测试覆盖率报告（可选）
echo 生成测试覆盖率报告...
python -m pytest tests/test_energy_*.py --cov=backend/app/api/energy_dashboard --cov=backend/app/services/energy_service --cov-report=term --cov-report=html -q
if errorlevel 1 (
    echo [WARNING] 覆盖率报告生成失败（这不影响测试结果）
) else (
    echo [OK] 覆盖率报告已生成
    echo 查看详细报告: htmlcov\index.html
)
echo.

REM 测试总结
echo ================================
echo 所有测试通过！
echo ================================
echo.
echo 测试结果摘要:
echo   [OK] 基础API测试
echo   [OK] 边界情况测试
echo   [OK] 前后端集成测试
echo.
echo 前后端集成顺畅，可以进行部署！

pause
