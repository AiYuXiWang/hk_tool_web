"""
前后端集成测试
模拟前端调用后端API的完整流程
"""

from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestEnergyCockpitWorkflow:
    """测试能源驾驶舱的完整工作流"""

    def test_complete_energy_cockpit_workflow(self) -> None:
        """
        测试能源驾驶舱页面加载的完整流程
        模拟前端EnergyCockpit.vue组件的数据加载
        """

        # 1. 页面加载 - 获取线路配置
        line_config_response = client.get("/api/control/line-configs")
        assert line_config_response.status_code == 200
        line_configs = line_config_response.json()

        # 验证线路配置结构
        assert isinstance(line_configs, dict) or isinstance(line_configs, list)

        # 2. 获取KPI数据
        kpi_response = client.get("/api/energy/kpi")
        assert kpi_response.status_code == 200
        kpi_data = self._extract_data(kpi_response)

        # 验证KPI数据完整性
        required_kpi_fields = [
            "total_kwh_today",
            "current_kw",
            "peak_kw",
            "station_count",
        ]
        for field in required_kpi_fields:
            assert field in kpi_data, f"KPI数据缺少字段: {field}"

        # 3. 获取实时能耗数据
        realtime_response = client.get("/api/energy/realtime")
        assert realtime_response.status_code == 200
        realtime_data = self._extract_data(realtime_response)

        # 验证实时数据结构
        assert "series" in realtime_data
        assert "timestamps" in realtime_data
        assert isinstance(realtime_data["series"], list)
        assert isinstance(realtime_data["timestamps"], list)

        # 4. 获取历史趋势数据（默认7天）
        trend_response = client.get("/api/energy/trend?period=7d")
        assert trend_response.status_code == 200
        trend_data = self._extract_data(trend_response)

        # 验证趋势数据
        assert "values" in trend_data
        assert "timestamps" in trend_data
        assert len(trend_data["values"]) == len(trend_data["timestamps"])

        # 5. 获取同比环比数据
        compare_response = client.get("/api/energy/compare?period=7d")
        assert compare_response.status_code == 200
        compare_data = self._extract_data(compare_response)

        # 验证对比数据
        assert "yoy_percent" in compare_data
        assert "mom_percent" in compare_data
        assert "current_kwh" in compare_data

        # 6. 获取分类分项能耗
        classification_response = client.get("/api/energy/classification?period=7d")
        assert classification_response.status_code == 200
        classification_data = self._extract_data(classification_response)

        # 验证分类数据
        assert "items" in classification_data
        assert "total_kwh" in classification_data

        # 7. 获取优化建议
        suggestions_response = client.get("/api/energy/suggestions")
        assert suggestions_response.status_code == 200
        suggestions_data = self._extract_data(suggestions_response)

        # 验证建议数据
        assert "suggestions" in suggestions_data
        assert isinstance(suggestions_data["suggestions"], list)

        print("\n✅ 能源驾驶舱完整工作流测试通过")
        print(f"   - 站点数量: {kpi_data['station_count']}")
        print(f"   - 实时功率: {kpi_data['current_kw']} kW")
        print(f"   - 实时数据点: {len(realtime_data['timestamps'])} 个")
        print(f"   - 趋势数据点: {len(trend_data['values'])} 个")
        print(f"   - 分类项数: {len(classification_data['items'])} 个")
        print(f"   - 优化建议数: {len(suggestions_data['suggestions'])} 条")

    def test_line_and_station_selection_workflow(self) -> None:
        """
        测试线路和站点选择的工作流
        模拟用户切换线路和站点的操作
        """

        # 1. 获取线路配置
        line_config_response = client.get("/api/control/line-configs")
        assert line_config_response.status_code == 200

        # 2. 选择特定线路获取数据
        kpi_m3_response = client.get("/api/energy/kpi?line=M3")
        assert kpi_m3_response.status_code == 200

        realtime_m3_response = client.get("/api/energy/realtime?line=M3")
        assert realtime_m3_response.status_code == 200

        # 3. 选择特定站点获取数据
        station_ip = "192.168.1.100"
        kpi_station_response = client.get(f"/api/energy/kpi?station_ip={station_ip}")
        assert kpi_station_response.status_code == 200

        print("\n✅ 线路和站点选择工作流测试通过")

    def test_time_period_switch_workflow(self) -> None:
        """
        测试时间周期切换的工作流
        模拟用户切换24h/7d/30d的操作
        """

        periods = ["24h", "7d", "30d"]

        for period in periods:
            # 获取趋势数据
            trend_response = client.get(f"/api/energy/trend?period={period}")
            assert trend_response.status_code == 200
            trend_data = self._extract_data(trend_response)

            # 获取对比数据
            compare_response = client.get(f"/api/energy/compare?period={period}")
            assert compare_response.status_code == 200

            # 获取分类数据
            classification_response = client.get(
                f"/api/energy/classification?period={period}"
            )
            assert classification_response.status_code == 200

            # 验证数据点数量符合预期
            if period == "24h":
                assert len(trend_data["values"]) == 24
            elif period == "7d":
                assert len(trend_data["values"]) == 7
            elif period == "30d":
                assert len(trend_data["values"]) == 30

        print(f"\n✅ 时间周期切换工作流测试通过 (测试了 {len(periods)} 个周期)")

    def test_refresh_data_workflow(self) -> None:
        """
        测试刷新数据的工作流
        模拟用户点击刷新按钮
        """

        # 第一次获取数据
        response1 = client.get("/api/energy/kpi")
        assert response1.status_code == 200
        data1 = self._extract_data(response1)

        # 模拟短时间后刷新
        response2 = client.get("/api/energy/kpi")
        assert response2.status_code == 200
        data2 = self._extract_data(response2)

        # 两次请求都应该成功
        assert data1 is not None
        assert data2 is not None

        # station_count应该保持一致（短时间内不会变化）
        assert data1["station_count"] == data2["station_count"]

        print("\n✅ 刷新数据工作流测试通过")

    def test_auto_refresh_simulation(self) -> None:
        """
        测试自动刷新机制
        模拟前端30秒自动刷新实时数据
        """

        # 模拟连续3次自动刷新
        responses = []
        for i in range(3):
            response = client.get("/api/energy/realtime")
            assert response.status_code == 200
            responses.append(response)

        # 所有请求都应该成功
        assert len(responses) == 3

        # 验证数据结构一致
        for response in responses:
            data = self._extract_data(response)
            assert "series" in data
            assert "timestamps" in data

        print("\n✅ 自动刷新模拟测试通过")

    def _extract_data(self, response) -> Dict[str, Any]:
        """从标准化响应中提取data字段"""
        result = response.json()
        if "code" in result and result["code"] == 200:
            return result["data"]
        elif "data" in result:
            return result["data"]
        else:
            return result


class TestChartDataIntegration:
    """测试图表数据集成"""

    def test_line_chart_data_format(self) -> None:
        """测试折线图数据格式（实时能耗监测）"""
        response = client.get("/api/energy/realtime")
        assert response.status_code == 200
        result = response.json()

        if result.get("code") == 200:
            data = result["data"]

            # ECharts折线图需要的数据格式
            assert "series" in data
            assert "timestamps" in data

            if data["series"]:
                # 验证系列数据格式
                series = data["series"][0]
                assert "name" in series
                assert "points" in series
                assert len(series["points"]) == len(data["timestamps"])

        print("\n✅ 折线图数据格式测试通过")

    def test_bar_chart_data_format(self) -> None:
        """测试柱状图数据格式（历史趋势）"""
        response = client.get("/api/energy/trend?period=7d")
        assert response.status_code == 200
        result = response.json()

        if result.get("code") == 200:
            data = result["data"]

            # ECharts柱状图需要的数据格式
            assert "values" in data
            assert "timestamps" in data
            assert len(data["values"]) == len(data["timestamps"])

        print("\n✅ 柱状图数据格式测试通过")

    def test_pie_chart_data_format(self) -> None:
        """测试饼图数据格式（分类分项能耗）"""
        response = client.get("/api/energy/classification")
        assert response.status_code == 200
        result = response.json()

        if result.get("code") == 200:
            data = result["data"]

            # ECharts饼图需要的数据格式
            assert "items" in data

            if data["items"]:
                item = data["items"][0]
                assert "name" in item
                assert "kwh" in item
                assert "percentage" in item

        print("\n✅ 饼图数据格式测试通过")


class TestKpiCardIntegration:
    """测试KPI卡片集成"""

    def test_kpi_card_data_structure(self) -> None:
        """测试KPI卡片所需的数据结构"""
        response = client.get("/api/energy/kpi")
        assert response.status_code == 200
        result = response.json()

        if result.get("code") == 200:
            data = result["data"]

            # EnergyKpiCard组件需要的数据
            kpi_fields = ["total_kwh_today", "current_kw", "peak_kw", "station_count"]

            for field in kpi_fields:
                assert field in data, f"缺少KPI字段: {field}"
                assert isinstance(data[field], (int, float)), f"{field}应为数值类型"

        print("\n✅ KPI卡片数据结构测试通过")

    def test_compare_card_data_structure(self) -> None:
        """测试同比环比卡片所需的数据结构"""
        response = client.get("/api/energy/compare?period=7d")
        assert response.status_code == 200
        result = response.json()

        if result.get("code") == 200:
            data = result["data"]

            # 同比环比卡片需要的数据
            compare_fields = ["yoy_percent", "mom_percent", "current_kwh"]

            for field in compare_fields:
                assert field in data, f"缺少对比字段: {field}"
                assert isinstance(data[field], (int, float)), f"{field}应为数值类型"

        print("\n✅ 同比环比卡片数据结构测试通过")


class TestErrorHandlingIntegration:
    """测试错误处理集成"""

    def test_frontend_error_handling(self) -> None:
        """测试前端错误处理场景"""

        # 场景1: 无效参数
        response = client.get("/api/energy/trend?period=invalid")
        # 应该返回错误或使用默认值
        assert response.status_code in [200, 400, 422]

        # 场景2: 不存在的线路
        response = client.get("/api/energy/kpi?line=NONEXISTENT")
        assert response.status_code == 200
        # 应该返回空数据或默认数据

        # 场景3: 无效的IP
        response = client.get("/api/energy/kpi?station_ip=invalid")
        assert response.status_code in [200, 400]

        print("\n✅ 前端错误处理测试通过")

    def test_network_timeout_simulation(self) -> None:
        """测试网络超时场景（简化版本）"""
        # 注意: 实际的超时测试需要更复杂的设置
        # 这里只验证API响应时间
        import time

        start = time.time()
        response = client.get("/api/energy/kpi")
        end = time.time()

        assert response.status_code == 200
        # 响应时间应该在合理范围内
        assert (end - start) < 5.0, "响应时间过长"

        print("\n✅ 网络超时模拟测试通过")


class TestDataConsistencyIntegration:
    """测试数据一致性集成"""

    def test_kpi_and_realtime_consistency(self) -> None:
        """测试KPI数据与实时数据的一致性"""

        # 获取KPI数据
        kpi_response = client.get("/api/energy/kpi")
        assert kpi_response.status_code == 200
        kpi_data = kpi_response.json()["data"]

        # 获取实时数据
        realtime_response = client.get("/api/energy/realtime")
        assert realtime_response.status_code == 200
        realtime_data = realtime_response.json()["data"]

        # 两者应该都有数据
        assert kpi_data is not None
        assert realtime_data is not None

        # 数据应该在合理范围内
        assert kpi_data["current_kw"] >= 0
        assert kpi_data["total_kwh_today"] >= 0

        print("\n✅ KPI与实时数据一致性测试通过")

    def test_trend_and_compare_consistency(self) -> None:
        """测试趋势数据与对比数据的一致性"""

        period = "7d"

        # 获取趋势数据
        trend_response = client.get(f"/api/energy/trend?period={period}")
        assert trend_response.status_code == 200
        trend_data = trend_response.json()["data"]

        # 获取对比数据
        compare_response = client.get(f"/api/energy/compare?period={period}")
        assert compare_response.status_code == 200
        compare_data = compare_response.json()["data"]

        # 验证周期一致
        assert trend_data["period"] == period
        assert compare_data["period"] == period

        # 当前能耗应该为正
        assert compare_data["current_kwh"] >= 0

        print("\n✅ 趋势与对比数据一致性测试通过")


class TestUserInteractionSimulation:
    """测试用户交互模拟"""

    def test_typical_user_session(self) -> None:
        """模拟典型用户会话"""

        # 1. 用户打开页面
        kpi_response = client.get("/api/energy/kpi")
        assert kpi_response.status_code == 200

        # 2. 查看实时监测
        realtime_response = client.get("/api/energy/realtime")
        assert realtime_response.status_code == 200

        # 3. 切换到7天趋势
        trend_7d_response = client.get("/api/energy/trend?period=7d")
        assert trend_7d_response.status_code == 200

        # 4. 切换到30天趋势
        trend_30d_response = client.get("/api/energy/trend?period=30d")
        assert trend_30d_response.status_code == 200

        # 5. 查看分类能耗
        classification_response = client.get("/api/energy/classification")
        assert classification_response.status_code == 200

        # 6. 查看优化建议
        suggestions_response = client.get("/api/energy/suggestions")
        assert suggestions_response.status_code == 200

        # 7. 选择特定线路
        kpi_line_response = client.get("/api/energy/kpi?line=M3")
        assert kpi_line_response.status_code == 200

        # 8. 刷新数据
        refresh_response = client.get("/api/energy/kpi")
        assert refresh_response.status_code == 200

        print("\n✅ 典型用户会话测试通过（8个操作）")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
