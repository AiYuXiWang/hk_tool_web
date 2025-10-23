# 能源驾驶舱测试套件

本目录包含能源驾驶舱模块的完整测试套件，包括基础API测试、边界情况测试和前后端集成测试。

## 测试文件

### 1. test_energy_api.py
基础API功能测试，验证所有能源相关API端点的基本功能。

**测试类**：
- `TestEnergyKpiAPI` - KPI接口测试（3个用例）
- `TestEnergyRealtimeAPI` - 实时数据接口测试（2个用例）
- `TestEnergyTrendAPI` - 趋势数据接口测试（5个用例）
- `TestEnergyCompareAPI` - 同比环比接口测试（2个用例）
- `TestEnergyClassificationAPI` - 分类能耗接口测试（3个用例）
- `TestEnergySuggestionsAPI` - 优化建议接口测试（1个用例）
- `TestEnergyIntegration` - 集成测试（1个用例）

**总计**: 22个测试用例

### 2. test_energy_edge_cases.py
边界情况和异常场景测试，确保系统在各种极端情况下的健壮性。

**测试类**：
- `TestEnergyAPIBoundaryConditions` - 边界条件测试
- `TestEnergyAPIEmptyData` - 空数据场景测试
- `TestEnergyAPIDataConsistency` - 数据一致性测试
- `TestEnergyAPIDataTypes` - 数据类型验证测试
- `TestEnergyAPIRangeValidation` - 数值范围验证测试
- `TestEnergyAPIConcurrency` - 并发请求测试
- `TestEnergyAPIPerformance` - 性能测试
- `TestEnergyAPISpecialCharacters` - 特殊字符处理测试
- `TestEnergyAPIHeaderHandling` - HTTP头处理测试
- `TestEnergyAPIRateLimit` - 速率限制测试
- `TestEnergyAPICache` - 缓存行为测试
- `TestEnergyAPIErrorMessages` - 错误消息测试
- `TestEnergyAPIDataFreshness` - 数据时效性测试

**总计**: 40+个测试用例

### 3. test_frontend_backend_integration.py
前后端集成测试，模拟前端组件调用后端API的完整流程。

**测试类**：
- `TestEnergyCockpitWorkflow` - 能源驾驶舱工作流测试
- `TestChartDataIntegration` - 图表数据集成测试
- `TestKpiCardIntegration` - KPI卡片集成测试
- `TestErrorHandlingIntegration` - 错误处理集成测试
- `TestDataConsistencyIntegration` - 数据一致性集成测试
- `TestUserInteractionSimulation` - 用户交互模拟测试

**总计**: 15个测试用例

## 快速开始

### 运行所有测试

**Linux/Mac**:
```bash
cd /home/engine/project
./run_integration_tests.sh
```

**Windows**:
```cmd
cd \home\engine\project
run_integration_tests.bat
```

### 运行特定测试文件

```bash
# 运行基础API测试
pytest tests/test_energy_api.py -v

# 运行边界情况测试
pytest tests/test_energy_edge_cases.py -v

# 运行集成测试
pytest tests/test_frontend_backend_integration.py -v
```

### 运行特定测试类

```bash
# 运行KPI API测试
pytest tests/test_energy_api.py::TestEnergyKpiAPI -v

# 运行边界条件测试
pytest tests/test_energy_edge_cases.py::TestEnergyAPIBoundaryConditions -v

# 运行工作流测试
pytest tests/test_frontend_backend_integration.py::TestEnergyCockpitWorkflow -v
```

### 运行特定测试用例

```bash
# 运行单个测试
pytest tests/test_energy_api.py::TestEnergyKpiAPI::test_get_kpi_data_success -v
```

## 测试选项

### 详细输出
```bash
pytest tests/test_energy_api.py -v
```

### 显示打印输出
```bash
pytest tests/test_energy_api.py -v -s
```

### 遇到失败立即停止
```bash
pytest tests/test_energy_api.py -v -x
```

### 只运行失败的测试
```bash
pytest tests/test_energy_api.py -v --lf
```

### 生成覆盖率报告
```bash
# 终端输出
pytest tests/test_energy_*.py --cov=backend/app/api/energy_dashboard --cov=backend/app/services/energy_service --cov-report=term

# HTML报告
pytest tests/test_energy_*.py --cov=backend/app --cov-report=html
# 查看报告: open htmlcov/index.html
```

### 并行运行测试（需要安装pytest-xdist）
```bash
pip install pytest-xdist
pytest tests/test_energy_*.py -n auto
```

## 测试覆盖范围

### API端点覆盖
- ✅ GET /api/energy/kpi
- ✅ GET /api/energy/realtime
- ✅ GET /api/energy/trend
- ✅ GET /api/energy/compare
- ✅ GET /api/energy/classification
- ✅ GET /api/energy/suggestions

### 场景覆盖
- ✅ 正常场景（所有参数组合）
- ✅ 异常场景（无效参数、空数据）
- ✅ 边界场景（极值、类型错误）
- ✅ 安全场景（SQL注入、XSS）
- ✅ 性能场景（响应时间、并发）

### 前端组件覆盖
- ✅ EnergyCockpit.vue 完整工作流
- ✅ EnergyKpiCard 数据结构
- ✅ EnergyChart 三种图表类型
- ✅ 错误处理和降级

## 持续集成

### GitHub Actions示例

```yaml
name: Energy API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/test_energy_*.py -v --cov=backend/app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
```

## 故障排除

### 导入错误
确保已安装所有依赖：
```bash
pip install -r requirements.txt
```

### 数据库连接错误
某些测试可能需要数据库连接。确保数据库配置正确或使用mock。

### 端口冲突
如果8000端口被占用，测试可能失败。停止其他服务或修改配置。

### 慢速测试
某些测试可能较慢（特别是并发和性能测试）。使用 `-k` 选项跳过：
```bash
pytest tests/test_energy_*.py -v -k "not Performance and not Concurrency"
```

## 添加新测试

### 测试命名约定
- 测试文件: `test_*.py`
- 测试类: `Test*`
- 测试方法: `test_*`

### 测试结构
```python
class TestNewFeature:
    """测试新功能"""
    
    def test_feature_success(self) -> None:
        """测试成功场景"""
        response = client.get("/api/new-endpoint")
        assert response.status_code == 200
        # 更多断言...
    
    def test_feature_failure(self) -> None:
        """测试失败场景"""
        response = client.get("/api/new-endpoint?invalid=param")
        assert response.status_code in [400, 422]
```

### 最佳实践
1. 每个测试应该独立（不依赖其他测试）
2. 使用描述性的测试名称
3. 添加文档字符串说明测试目的
4. 验证响应状态码、数据结构和数据类型
5. 使用断言消息帮助调试

## 测试数据

测试使用模拟数据，不依赖真实数据源。这确保了：
- 测试可重复性
- 测试速度快
- 不影响生产数据

## 相关文档

- [集成测试计划](../docs/INTEGRATION_TEST_PLAN.md)
- [真实数据校准方案](../docs/REAL_DATA_CALIBRATION_PLAN.md)
- [任务完成报告](../docs/TASK_COMPLETION_REPORT_INTEGRATION.md)

## 贡献

欢迎添加更多测试用例！请遵循现有的测试结构和命名约定。

## 许可证

与主项目相同。
