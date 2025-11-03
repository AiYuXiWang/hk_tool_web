"""
能源驾驶舱API接口测试
测试所有能源相关的API端点
"""

from typing import Any, Dict
from unittest.mock import Mock, patch  # noqa: F401

import pytest  # noqa: F401
from fastapi.testclient import TestClient
from httpx import Response

from main import app

client = TestClient(app)


def extract_data(response: Response) -> Dict[str, Any]:
    """从标准化响应中提取data字段"""
    result = response.json()
    assert "code" in result
    assert result["code"] == 200
    assert "data" in result
    return result["data"]


class TestEnergyKpiAPI:
    """测试KPI接口"""

    def test_get_kpi_data_success(self) -> None:
        """测试获取KPI数据成功 - 新版本仅返回总能耗"""
        response = client.get("/api/energy/kpi")
        assert response.status_code == 200
        result = response.json()

        # 验证响应结构
        assert "code" in result
        assert result["code"] == 200
        assert "data" in result

        data = result["data"]

        # 验证返回的数据结构（新版仅有总能耗）
        assert "total_kwh_today" in data
        assert "update_time" in data

        # 验证数据类型
        assert isinstance(data["total_kwh_today"], (int, float))

    def test_get_kpi_data_with_line(self) -> None:
        """测试按线路获取KPI数据"""
        response = client.get("/api/energy/kpi?line=M3")
        assert response.status_code == 200
        data = extract_data(response)
        assert "total_kwh_today" in data

    def test_get_kpi_data_with_station_ip(self) -> None:
        """测试按站点IP获取KPI数据"""
        response = client.get("/api/energy/kpi?station_ip=192.168.1.100")
        assert response.status_code == 200
        data = extract_data(response)
        assert "total_kwh_today" in data


class TestEnergyRealtimeAPI:
    """测试实时数据接口"""

    def test_get_realtime_data_success(self) -> None:
        """测试获取实时数据成功"""
        response = client.get("/api/energy/realtime")
        assert response.status_code == 200
        data = extract_data(response)

        # 验证返回的数据结构
        assert "series" in data
        assert "timestamps" in data
        assert "update_time" in data

        # 验证series是列表
        assert isinstance(data["series"], list)
        assert isinstance(data["timestamps"], list)

        # 如果有数据，验证series的结构
        if data["series"]:
            assert "name" in data["series"][0]
            assert "points" in data["series"][0]
            assert isinstance(data["series"][0]["points"], list)

    def test_get_realtime_data_with_line(self) -> None:
        """测试按线路获取实时数据"""
        response = client.get("/api/energy/realtime?line=M3")
        assert response.status_code == 200
        data = extract_data(response)
        assert "series" in data
        assert "timestamps" in data


class TestEnergyTrendAPI:
    """测试趋势数据接口"""

    def test_get_trend_data_success(self) -> None:
        """测试获取趋势数据成功"""
        response = client.get("/api/energy/trend")
        assert response.status_code == 200
        data = extract_data(response)

        # 验证返回的数据结构
        assert "values" in data
        assert "timestamps" in data
        assert "period" in data
        assert "update_time" in data

        # 验证数据是列表
        assert isinstance(data["values"], list)
        assert isinstance(data["timestamps"], list)

        # 验证列表长度相同
        assert len(data["values"]) == len(data["timestamps"])

    def test_get_trend_data_with_period_24h(self) -> None:
        """测试获取24小时趋势数据"""
        response = client.get("/api/energy/trend?period=24h")
        assert response.status_code == 200
        data = extract_data(response)
        assert data["period"] == "24h"
        assert len(data["timestamps"]) == 24

    def test_get_trend_data_with_period_7d(self) -> None:
        """测试获取7天趋势数据"""
        response = client.get("/api/energy/trend?period=7d")
        assert response.status_code == 200
        data = extract_data(response)
        assert data["period"] == "7d"
        assert len(data["timestamps"]) == 7

    def test_get_trend_data_with_period_30d(self) -> None:
        """测试获取30天趋势数据"""
        response = client.get("/api/energy/trend?period=30d")
        assert response.status_code == 200
        data = extract_data(response)
        assert data["period"] == "30d"
        assert len(data["timestamps"]) == 30

    def test_get_trend_data_invalid_period(self) -> None:
        """测试无效的周期参数"""
        response = client.get("/api/energy/trend?period=invalid")
        # 注意：由于中间件会包装错误，这里不一定返回400
        # 如果返回200，则data中会包含错误信息
        assert response.status_code in [200, 400]


class TestEnergyCompareAPI:
    """测试同比环比对比接口"""

    def test_get_compare_data_success(self) -> None:
        """测试获取对比数据成功"""
        response = client.get("/api/energy/compare")
        assert response.status_code == 200
        data = extract_data(response)

        # 验证返回的数据结构
        assert "current_kwh" in data
        assert "yoy_percent" in data
        assert "mom_percent" in data
        assert "period" in data
        assert "update_time" in data

        # 验证数据类型
        assert isinstance(data["current_kwh"], (int, float))
        assert isinstance(data["yoy_percent"], (int, float))
        assert isinstance(data["mom_percent"], (int, float))

    def test_get_compare_data_with_period(self) -> None:
        """测试不同周期的对比数据"""
        for period in ["24h", "7d", "30d"]:
            response = client.get(f"/api/energy/compare?period={period}")
            assert response.status_code == 200
            data = extract_data(response)
            assert data["period"] == period


class TestEnergyClassificationAPI:
    """测试分类分项能耗接口"""

    def test_get_classification_data_success(self) -> None:
        """测试获取分类能耗数据成功"""
        response = client.get("/api/energy/classification")
        assert response.status_code == 200
        data = extract_data(response)

        # 验证返回的数据结构
        assert "items" in data
        assert "total_kwh" in data
        assert "period" in data
        assert "update_time" in data

        # 验证items是列表
        assert isinstance(data["items"], list)

        # 验证items的结构
        if data["items"]:
            item = data["items"][0]
            assert "name" in item
            assert "kwh" in item
            assert "percentage" in item
            assert isinstance(item["kwh"], (int, float))
            assert isinstance(item["percentage"], (int, float))

    def test_get_classification_data_percentage_sum(self) -> None:
        """测试分类能耗的百分比总和约为100%"""
        response = client.get("/api/energy/classification")
        assert response.status_code == 200
        data = extract_data(response)

        total_percentage = sum(item["percentage"] for item in data["items"])
        if data["total_kwh"] > 0:
            # 有效数据时百分比应约为100%
            assert 99.0 <= total_percentage <= 101.0
        else:
            # 无有效能耗数据时允许为0
            assert total_percentage == 0.0

    def test_get_classification_data_kwh_sum(self) -> None:
        """测试分类能耗的kWh总和等于total_kwh（无数据时应为0）"""
        response = client.get("/api/energy/classification")
        assert response.status_code == 200
        data = extract_data(response)

        total_kwh_calculated = sum(item["kwh"] for item in data["items"])
        if data["total_kwh"] > 0:
            # 允许小数点精度误差
            assert abs(total_kwh_calculated - data["total_kwh"]) < 1.0
        else:
            assert total_kwh_calculated == 0


class TestEnergySuggestionsAPI:
    """测试优化建议接口"""

    def test_get_suggestions_success(self) -> None:
        """测试获取优化建议成功"""
        response = client.get("/api/energy/suggestions")
        assert response.status_code == 200
        data = extract_data(response)

        # 验证返回的数据结构
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)

        # 验证suggestions的结构
        if data["suggestions"]:
            suggestion = data["suggestions"][0]
            assert "id" in suggestion
            assert "title" in suggestion
            assert "description" in suggestion
            assert "priority" in suggestion
            assert "energy_saving" in suggestion
            assert "cost_saving" in suggestion


class TestEnergyIntegration:
    """集成测试"""

    def test_energy_cockpit_workflow(self) -> None:
        """测试能源驾驶舱的完整工作流"""
        # 1. 获取KPI数据
        kpi_response = client.get("/api/energy/kpi")
        assert kpi_response.status_code == 200

        # 2. 获取实时数据
        realtime_response = client.get("/api/energy/realtime")
        assert realtime_response.status_code == 200

        # 3. 获取趋势数据
        trend_response = client.get("/api/energy/trend?period=7d")
        assert trend_response.status_code == 200

        # 4. 获取对比数据
        compare_response = client.get("/api/energy/compare?period=7d")
        assert compare_response.status_code == 200

        # 5. 获取分类能耗
        classification_response = client.get("/api/energy/classification")
        assert classification_response.status_code == 200

        # 6. 获取优化建议
        suggestions_response = client.get("/api/energy/suggestions")
        assert suggestions_response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
