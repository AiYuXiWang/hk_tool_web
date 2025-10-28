"""
pytest 配置文件
提供测试 fixtures 和配置
"""

import os
import sys
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app  # noqa: E402


@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, None, None]:
    """
    创建测试客户端
    使用 session scope 以在所有测试中复用
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture
def sample_station_ip() -> str:
    """返回示例站点 IP"""
    return "192.168.1.100"


@pytest.fixture
def sample_point_keys() -> list:
    """返回示例点位 keys"""
    return [
        "STATION.BUILDING.FLOOR.DEVICE.TEMP",
        "STATION.BUILDING.FLOOR.DEVICE.HUMIDITY",
        "STATION.BUILDING.FLOOR.DEVICE.POWER",
    ]


@pytest.fixture
def sample_kpi_data() -> dict:
    """返回示例 KPI 数据"""
    return {
        "total_kwh_today": 1250.5,
        "current_kw": 85.3,
        "peak_kw": 120.7,
        "station_count": 3,
        "efficiency": 0.87,
    }


@pytest.fixture
def sample_export_request() -> dict:
    """返回示例导出请求数据"""
    return {
        "line": "M3",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "export_type": "electricity",
        "file_format": "excel",
    }


@pytest.fixture
def sample_control_request() -> dict:
    """返回示例控制请求数据"""
    return {
        "point_key": "STATION.BUILDING.FLOOR.DEVICE.SETPOINT",
        "value": 25.5,
        "data_source": "192.168.1.100",
        "operator": "test_user",
    }


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """
    自动设置测试环境变量
    """
    monkeypatch.setenv("TESTING", "1")
    monkeypatch.setenv("HK_PLATFORM_TOKEN", "test_token")
    monkeypatch.setenv("HK_PLATFORM_BASE_URL", "http://test-api.example.com")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


@pytest.fixture
def mock_db_connection(monkeypatch):
    """
    Mock 数据库连接
    用于隔离数据库依赖的测试
    """
    from unittest.mock import MagicMock

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Mock 查询结果
    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = None

    return mock_conn


@pytest.fixture
def mock_http_session():
    """
    Mock HTTP 会话
    用于隔离外部 API 调用
    """
    from unittest.mock import AsyncMock, MagicMock

    mock_session = MagicMock()
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(
        return_value={"code": 200, "data": {"value": 25.5}, "message": "success"}
    )
    mock_response.status = 200

    mock_session.get = AsyncMock(return_value=mock_response)
    mock_session.post = AsyncMock(return_value=mock_response)

    return mock_session


def pytest_configure(config):
    """
    pytest 配置钩子
    """
    # 添加自定义标记
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "api: API endpoint tests")
    config.addinivalue_line("markers", "service: Service layer tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")


def pytest_collection_modifyitems(config, items):
    """
    修改测试收集
    自动为测试添加标记
    """
    for item in items:
        # 根据文件路径自动添加标记
        if "test_energy_api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        elif "service" in str(item.fspath):
            item.add_marker(pytest.mark.service)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)
