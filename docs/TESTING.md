# 测试文档

## 概述

本项目采用全面的测试策略，包括单元测试、集成测试和端到端测试，确保代码质量和系统稳定性。

## 目录

- [测试结构](#测试结构)
- [测试工具](#测试工具)
- [运行测试](#运行测试)
- [测试覆盖率](#测试覆盖率)
- [编写测试](#编写测试)
- [测试最佳实践](#测试最佳实践)
- [CI/CD 集成](#cicd-集成)

## 测试结构

```
tests/
├── __init__.py                                 # 测试包初始化
├── conftest.py                                 # pytest 配置和 fixtures
├── test_energy_api.py                          # 能源 API 测试
├── test_energy_edge_cases.py                   # 边界情况测试
├── test_frontend_backend_integration.py        # 前后端集成测试
├── test_control_service.py                     # 控制服务测试
├── test_export_service.py                      # 导出服务测试
├── test_audit_service.py                       # 审计服务测试
├── test_main_api.py                            # 主 API 测试
└── test_db_config.py                           # 数据库配置测试

backend/tests/
├── __init__.py
├── test_energy_service.py                      # 能源服务测试
├── test_data_service.py                        # 数据服务测试
├── test_middleware.py                          # 中间件测试
└── test_models.py                              # 模型测试

frontend/tests/
├── unit/                                       # 单元测试
│   ├── components/                            # 组件测试
│   ├── stores/                                # 状态管理测试
│   └── utils/                                 # 工具函数测试
└── e2e/                                       # 端到端测试
    └── specs/                                 # E2E 测试用例
```

## 测试工具

### 后端测试工具

#### pytest
Python 测试框架，提供强大的测试功能。

```bash
# 安装
pip install pytest pytest-cov pytest-asyncio

# 运行
pytest
```

#### pytest-cov
测试覆盖率工具。

```bash
# 运行并生成覆盖率报告
pytest --cov=backend --cov-report=html
```

#### pytest-asyncio
异步测试支持。

```bash
# 测试异步函数
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

#### FastAPI TestClient
FastAPI 提供的测试客户端。

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
response = client.get("/api/endpoint")
```

### 前端测试工具

#### Vitest
Vue 3 推荐的测试框架。

```bash
# 运行测试
npm run test

# 运行覆盖率测试
npm run test:coverage
```

#### Vue Test Utils
Vue 组件测试工具。

```javascript
import { mount } from '@vue/test-utils'
import MyComponent from '@/components/MyComponent.vue'

test('renders properly', () => {
  const wrapper = mount(MyComponent, { props: { msg: 'Hello' } })
  expect(wrapper.text()).toContain('Hello')
})
```

#### Cypress
端到端测试框架。

```bash
# 运行 E2E 测试
npm run test:e2e
```

## 运行测试

### 后端测试

#### 运行所有测试
```bash
pytest
```

#### 运行特定测试文件
```bash
pytest tests/test_energy_api.py
```

#### 运行特定测试类
```bash
pytest tests/test_energy_api.py::TestEnergyKpiAPI
```

#### 运行特定测试函数
```bash
pytest tests/test_energy_api.py::TestEnergyKpiAPI::test_get_kpi_data_success
```

#### 运行标记的测试
```bash
# 只运行单元测试
pytest -m unit

# 只运行集成测试
pytest -m integration

# 跳过慢速测试
pytest -m "not slow"
```

#### 运行并生成覆盖率报告
```bash
# 生成终端报告
pytest --cov=backend --cov-report=term-missing

# 生成 HTML 报告
pytest --cov=backend --cov-report=html

# 查看 HTML 报告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

#### 详细输出
```bash
# 显示详细输出
pytest -v

# 显示测试输出（print 语句）
pytest -s

# 组合使用
pytest -vs
```

### 前端测试

#### 运行单元测试
```bash
cd frontend
npm run test
```

#### 运行测试并监听变化
```bash
npm run test:watch
```

#### 运行测试覆盖率
```bash
npm run test:coverage
```

#### 运行 E2E 测试
```bash
# 开发模式
npm run test:e2e:dev

# CI 模式
npm run test:e2e
```

### 使用 Make 命令

项目提供了 Makefile 简化测试命令：

```bash
# 运行所有测试
make test

# 运行后端测试
make test-backend

# 运行前端测试
make test-frontend

# 运行测试覆盖率
make coverage

# 运行代码检查
make lint

# 格式化代码
make format
```

### 使用重启脚本

快速重启服务并运行测试：

```bash
# Python 脚本（跨平台）
python scripts/restart_and_test.py

# Linux/macOS
./scripts/restart_and_test.sh

# Windows
scripts\restart_and_test.bat
```

## 测试覆盖率

### 覆盖率目标

- **总体覆盖率**: ≥ 80%
- **核心服务**: ≥ 90%
- **API 层**: ≥ 85%
- **工具函数**: ≥ 95%

### 查看覆盖率报告

#### 后端覆盖率
```bash
pytest --cov=backend --cov-report=html
open htmlcov/index.html
```

#### 前端覆盖率
```bash
cd frontend
npm run test:coverage
open coverage/index.html
```

### 覆盖率配置

在 `pyproject.toml` 中配置：

```toml
[tool.coverage.run]
source = ["backend"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__init__.py",
    "*/migrations/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

## 编写测试

### 后端测试示例

#### API 测试
```python
"""测试能源 API"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_kpi_data():
    """测试获取 KPI 数据"""
    response = client.get("/api/energy/kpi")
    assert response.status_code == 200
    
    data = response.json()
    assert "code" in data
    assert data["code"] == 200
    assert "data" in data
    
    kpi = data["data"]
    assert "total_kwh_today" in kpi
    assert isinstance(kpi["total_kwh_today"], (int, float))
```

#### 服务层测试
```python
"""测试能源服务"""
import pytest
from backend.app.services.energy_service import EnergyService

@pytest.fixture
def energy_service():
    """创建能源服务实例"""
    return EnergyService()

@pytest.mark.asyncio
async def test_get_kpi_data(energy_service):
    """测试获取 KPI 数据"""
    result = await energy_service.get_kpi_data()
    
    assert result is not None
    assert "total_kwh_today" in result
    assert result["total_kwh_today"] >= 0
```

#### Mock 外部依赖
```python
"""测试控制服务（使用 Mock）"""
from unittest.mock import Mock, patch
import pytest
from control_service import ControlService

@pytest.fixture
def mock_http_client():
    """Mock HTTP 客户端"""
    with patch('aiohttp.ClientSession') as mock:
        yield mock

@pytest.mark.asyncio
async def test_query_points(mock_http_client):
    """测试查询点位"""
    # 设置 mock 返回值
    mock_http_client.return_value.get.return_value.json.return_value = {
        "code": 200,
        "data": {"value": 25.5}
    }
    
    service = ControlService()
    result = await service.query_point("test_point_key")
    
    assert result["value"] == 25.5
```

### 前端测试示例

#### 组件测试
```javascript
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import BaseButton from '@/components/common/BaseButton.vue'

describe('BaseButton', () => {
  it('renders properly', () => {
    const wrapper = mount(BaseButton, {
      props: { text: 'Click me' }
    })
    expect(wrapper.text()).toContain('Click me')
  })

  it('emits click event', async () => {
    const wrapper = mount(BaseButton)
    await wrapper.trigger('click')
    expect(wrapper.emitted()).toHaveProperty('click')
  })
})
```

#### Store 测试
```javascript
import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach } from 'vitest'
import { useEnergyStore } from '@/stores/energy'

describe('Energy Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('fetches KPI data', async () => {
    const store = useEnergyStore()
    await store.fetchKpiData()
    
    expect(store.kpiData).toBeDefined()
    expect(store.kpiData.total_kwh_today).toBeGreaterThanOrEqual(0)
  })
})
```

## 测试最佳实践

### 1. 测试命名
使用描述性的测试名称：

```python
# 好的命名
def test_get_kpi_data_returns_correct_structure():
    """测试 KPI 接口返回正确的数据结构"""
    pass

# 不好的命名
def test_1():
    pass
```

### 2. AAA 模式
遵循 Arrange-Act-Assert 模式：

```python
def test_calculate_total():
    # Arrange（准备）
    items = [1, 2, 3, 4, 5]
    
    # Act（执行）
    result = calculate_total(items)
    
    # Assert（断言）
    assert result == 15
```

### 3. 测试独立性
每个测试应该独立运行，不依赖其他测试：

```python
# 使用 fixture 确保独立性
@pytest.fixture
def clean_database():
    """每次测试前清理数据库"""
    db.clear()
    yield
    db.clear()

def test_create_record(clean_database):
    record = create_record({"name": "test"})
    assert record.id is not None
```

### 4. 使用 Mock
对外部依赖使用 Mock：

```python
from unittest.mock import patch

@patch('requests.get')
def test_fetch_data(mock_get):
    mock_get.return_value.json.return_value = {"data": "test"}
    result = fetch_data("http://api.example.com")
    assert result["data"] == "test"
```

### 5. 测试边界条件
测试边界和异常情况：

```python
def test_divide_by_zero():
    """测试除以零的情况"""
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_empty_list():
    """测试空列表的情况"""
    assert calculate_average([]) == 0

def test_negative_numbers():
    """测试负数的情况"""
    assert abs_value(-5) == 5
```

### 6. 使用参数化测试
减少重复代码：

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (4, 8),
])
def test_double(input, expected):
    assert double(input) == expected
```

### 7. 测试文档
添加清晰的文档字符串：

```python
def test_user_registration():
    """
    测试用户注册流程
    
    测试场景:
    1. 提供有效的用户信息
    2. 用户应该成功创建
    3. 返回用户 ID
    
    预期结果:
    - 用户记录被创建
    - 返回的 ID 不为空
    - 密码被正确加密
    """
    pass
```

## CI/CD 集成

### GitHub Actions

在 `.github/workflows/test.yml` 中配置：

```yaml
name: Tests

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
          pip install -r requirements/testing.txt
      
      - name: Run tests
        run: |
          pytest --cov=backend --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          file: ./coverage.xml
```

### Pre-commit Hooks

在 `.pre-commit-config.yaml` 中配置：

```yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

## 故障排除

### 常见问题

#### 1. 数据库连接失败
```python
# 使用 SQLite 内存数据库进行测试
@pytest.fixture
def test_db():
    db = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(db)
    return db
```

#### 2. 异步测试失败
```python
# 确保安装 pytest-asyncio
pip install pytest-asyncio

# 标记异步测试
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

#### 3. Mock 不生效
```python
# 确保 patch 路径正确
# 错误：patch('requests.get')
# 正确：patch('your_module.requests.get')
```

#### 4. 测试超时
```python
# 设置测试超时
@pytest.mark.timeout(10)
def test_long_running():
    pass
```

## 性能测试

### 使用 pytest-benchmark

```python
def test_performance(benchmark):
    """测试函数性能"""
    result = benchmark(expensive_function, arg1, arg2)
    assert result is not None
```

### 负载测试

使用 Locust 进行负载测试：

```python
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def get_kpi_data(self):
        self.client.get("/api/energy/kpi")
    
    @task
    def get_realtime_data(self):
        self.client.get("/api/energy/realtime")
```

## 测试报告

### 生成 HTML 报告

```bash
pytest --html=report.html --self-contained-html
```

### 生成 JUnit XML 报告

```bash
pytest --junit-xml=report.xml
```

### 集成到 CI

报告会自动上传到 CI 平台（GitHub Actions, GitLab CI 等）。

## 相关资源

- [pytest 文档](https://docs.pytest.org/)
- [FastAPI 测试文档](https://fastapi.tiangolo.com/tutorial/testing/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Vitest 文档](https://vitest.dev/)
- [Cypress 文档](https://www.cypress.io/)

## 下一步

- 阅读 [贡献指南](CONTRIBUTING.md)
- 查看 [项目结构](PROJECT_STRUCTURE.md)
- 运行 `make test` 开始测试
