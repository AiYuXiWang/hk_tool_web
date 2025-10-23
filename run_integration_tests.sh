#!/bin/bash

# 前后端集成测试运行脚本
# 用于运行所有能源模块的测试

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}前后端集成测试套件${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python环境检查通过${NC}"

# 检查pytest
if ! python -c "import pytest" &> /dev/null; then
    echo -e "${YELLOW}⚠ pytest未安装，正在安装...${NC}"
    pip install pytest pytest-cov pytest-asyncio
fi

echo -e "${GREEN}✓ pytest已准备就绪${NC}"
echo ""

# 运行测试
echo -e "${BLUE}开始运行测试...${NC}"
echo ""

# 1. 运行基础API测试
echo -e "${YELLOW}[1/3] 运行基础API测试${NC}"
python -m pytest tests/test_energy_api.py -v --tb=short --color=yes

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 基础API测试通过${NC}"
else
    echo -e "${RED}✗ 基础API测试失败${NC}"
    exit 1
fi
echo ""

# 2. 运行边界情况测试
echo -e "${YELLOW}[2/3] 运行边界情况测试${NC}"
python -m pytest tests/test_energy_edge_cases.py -v --tb=short --color=yes

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 边界情况测试通过${NC}"
else
    echo -e "${RED}✗ 边界情况测试失败${NC}"
    exit 1
fi
echo ""

# 3. 运行前后端集成测试
echo -e "${YELLOW}[3/3] 运行前后端集成测试${NC}"
python -m pytest tests/test_frontend_backend_integration.py -v --tb=short --color=yes

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 前后端集成测试通过${NC}"
else
    echo -e "${RED}✗ 前后端集成测试失败${NC}"
    exit 1
fi
echo ""

# 运行测试覆盖率报告（可选）
echo -e "${BLUE}生成测试覆盖率报告...${NC}"
python -m pytest tests/test_energy_*.py --cov=backend/app/api/energy_dashboard --cov=backend/app/services/energy_service --cov-report=term --cov-report=html -q

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 覆盖率报告已生成${NC}"
    echo -e "${BLUE}查看详细报告: htmlcov/index.html${NC}"
else
    echo -e "${YELLOW}⚠ 覆盖率报告生成失败（这不影响测试结果）${NC}"
fi
echo ""

# 测试总结
echo -e "${BLUE}=================================${NC}"
echo -e "${GREEN}🎉 所有测试通过！${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""
echo -e "测试结果摘要:"
echo -e "  ✓ 基础API测试"
echo -e "  ✓ 边界情况测试"
echo -e "  ✓ 前后端集成测试"
echo ""
echo -e "${GREEN}前后端集成顺畅，可以进行部署！${NC}"
