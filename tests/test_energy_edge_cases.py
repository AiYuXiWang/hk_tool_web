"""
能源驾驶舱API边界情况测试
测试各种边界条件、异常输入和极端场景
"""

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from main import app

client = TestClient(app)


class TestEnergyAPIBoundaryConditions:
    """测试API边界条件"""

    def test_invalid_line_parameter(self) -> None:
        """测试无效的线路参数"""
        response = client.get("/api/energy/kpi?line=INVALID_LINE")
        assert response.status_code == 200
        # 应该返回空数据或默认数据，而不是报错
        data = response.json()
        assert "data" in data

    def test_invalid_station_ip_format(self) -> None:
        """测试无效的站点IP格式"""
        invalid_ips = [
            "invalid_ip",
            "999.999.999.999",
            "192.168.1",
            "192.168.1.1.1",
            "",
        ]
        for ip in invalid_ips:
            response = client.get(f"/api/energy/kpi?station_ip={ip}")
            # 系统应该优雅处理，返回空数据或错误信息
            assert response.status_code in [200, 400, 422]

    def test_extremely_large_period_value(self) -> None:
        """测试极大的周期值"""
        response = client.get("/api/energy/trend?period=999999d")
        # 应该返回错误或使用默认值
        assert response.status_code in [200, 400]

    def test_negative_values_handling(self) -> None:
        """测试是否正确处理负值（功率不应为负）"""
        response = client.get("/api/energy/realtime")
        assert response.status_code == 200
        result = response.json()

        if result["code"] == 200 and result["data"]["series"]:
            for series in result["data"]["series"]:
                for point in series["points"]:
                    # 功率值不应为负
                    assert point >= 0, f"功率值不应为负: {point}"


class TestEnergyAPIEmptyData:
    """测试空数据场景"""

    def test_no_stations_configured(self) -> None:
        """测试没有配置站点时的响应"""
        # 使用一个不存在的线路，应该返回空数据
        response = client.get("/api/energy/realtime?line=NONEXISTENT")
        assert response.status_code == 200
        result = response.json()

        # 验证空数据的结构
        if result["code"] == 200:
            data = result["data"]
            # 应该返回空列表或数组，而不是null
            if "series" in data:
                assert isinstance(data["series"], list)
            if "timestamps" in data:
                assert isinstance(data["timestamps"], list)

    def test_empty_classification_data(self) -> None:
        """测试分类数据为空时的处理"""
        response = client.get("/api/energy/classification?line=NONEXISTENT&period=24h")
        assert response.status_code == 200
        result = response.json()

        if result["code"] == 200:
            data = result["data"]
            assert "items" in data
            assert isinstance(data["items"], list)


class TestEnergyAPIDataConsistency:
    """测试数据一致性"""

    def test_trend_data_timestamp_count_matches_values(self) -> None:
        """测试趋势数据的时间戳数量与数值数量匹配"""
        for period in ["24h", "7d", "30d"]:
            response = client.get(f"/api/energy/trend?period={period}")
            assert response.status_code == 200
            result = response.json()

            if result["code"] == 200:
                data = result["data"]
                assert len(data["values"]) == len(
                    data["timestamps"]
                ), f"Period {period}: 数值数量与时间戳数量不匹配"

    def test_classification_percentages_sum_to_100(self) -> None:
        """测试分类能耗百分比总和为100%（无数据时为0）"""
        response = client.get("/api/energy/classification")
        assert response.status_code == 200
        result = response.json()

        if result["code"] == 200:
            data = result["data"]
            if data["items"] and data["total_kwh"] > 0:
                total_percentage = sum(item["percentage"] for item in data["items"])
                # 允许1%的舍入误差
                assert (
                    99.0 <= total_percentage <= 101.0
                ), f"百分比总和应为100%，实际为 {total_percentage}%"
            else:
                # 无有效数据时允许为0
                total_percentage = sum(item["percentage"] for item in data["items"])
                assert total_percentage == 0.0, "无数据时百分比应为0"

    def test_classification_kwh_sum_matches_total(self) -> None:
        """测试分类能耗kWh总和与总能耗匹配"""
        response = client.get("/api/energy/classification")
        assert response.status_code == 200
        result = response.json()

        if result["code"] == 200:
            data = result["data"]
            if data["total_kwh"] > 0 and data["items"]:
                calculated_total = sum(item["kwh"] for item in data["items"])
                # 允许小数点精度误差
                assert (
                    abs(calculated_total - data["total_kwh"]) < 1.0
                ), f"分类能耗总和 ({calculated_total}) 与 total_kwh ({data['total_kwh']}) 不匹配"
            else:
                calculated_total = sum(item["kwh"] for item in data["items"])
                assert calculated_total == 0, "无数据时分类能耗总和应为0"

    def test_compare_data_logical_consistency(self) -> None:
        """测试对比数据的逻辑一致性"""
        response = client.get("/api/energy/compare?period=7d")
        assert response.status_code == 200
        result = response.json()

        if result["code"] == 200:
            data = result["data"]
            # 同比和环比百分比应该在合理范围内
            assert (
                -100 <= data["yoy_percent"] <= 1000
            ), f"同比百分比超出合理范围: {data['yoy_percent']}"
            assert (
                -100 <= data["mom_percent"] <= 1000
            ), f"环比百分比超出合理范围: {data['mom_percent']}"

            # 当前能耗应为正数
            assert data["current_kwh"] >= 0, "当前能耗不应为负数"


class TestEnergyAPIDataTypes:
    """测试数据类型正确性"""

    def test_kpi_data_types(self) -> None:
        """测试KPI数据的类型正确性"""
        response = client.get("/api/energy/kpi")
        assert response.status_code == 200
        result = response.json()

        if result["code"] == 200:
            data = result["data"]

            # 验证数值字段的类型（新版本仅有总能耗）
            assert isinstance(
                data["total_kwh_today"], (int, float)
            ), "total_kwh_today应为数值类型"

            # 验证字符串字段的类型
            assert isinstance(data["update_time"], str), "update_time应为字符串类型"

    def test_realtime_data_types(self) -> None:
        """测试实时数据的类型正确性"""
        response = client.get("/api/energy/realtime")
        assert response.status_code == 200
        result = response.json()

        if result["code"] == 200:
            data = result["data"]

            assert isinstance(data["series"], list), "series应为列表类型"
            assert isinstance(data["timestamps"], list), "timestamps应为列表类型"

            if data["series"]:
                series = data["series"][0]
                assert isinstance(series["name"], str), "series.name应为字符串类型"
                assert isinstance(series["points"], list), "series.points应为列表类型"

                if series["points"]:
                    assert isinstance(
                        series["points"][0], (int, float)
                    ), "points元素应为数值类型"

    def test_trend_data_types(self) -> None:
        """测试趋势数据的类型正确性"""
        response = client.get("/api/energy/trend?period=7d")
        assert response.status_code == 200
        result = response.json()

        if result["code"] == 200:
            data = result["data"]

            assert isinstance(data["values"], list), "values应为列表类型"
            assert isinstance(data["timestamps"], list), "timestamps应为列表类型"
            assert isinstance(data["period"], str), "period应为字符串类型"

            if data["values"]:
                assert isinstance(data["values"][0], (int, float)), "values元素应为数值类型"

            if data["timestamps"]:
                assert isinstance(data["timestamps"][0], str), "timestamps元素应为字符串类型"


class TestEnergyAPIRangeValidation:
    """测试数值范围验证"""

    def test_power_values_in_reasonable_range(self) -> None:
        """测试功率值在合理范围内"""
        response = client.get("/api/energy/realtime")
        assert response.status_code == 200
        result = response.json()

        if result["code"] == 200 and result["data"]["series"]:
            for series in result["data"]["series"]:
                for point in series["points"]:
                    # 功率值应在0-10000 kW之间（单站点）
                    assert 0 <= point <= 10000, f"功率值超出合理范围: {point} kW"

    def test_efficiency_values_in_valid_range(self) -> None:
        """测试能效比在有效范围内"""
        response = client.get("/api/energy/kpi")
        assert response.status_code == 200
        result = response.json()

        if result["code"] == 200:
            data = result["data"]
            # 能效比通常在1.0-10.0之间
            if "efficiency_ratio" in data:
                assert (
                    1.0 <= data["efficiency_ratio"] <= 10.0
                ), f"能效比超出合理范围: {data['efficiency_ratio']}"

    def test_percentage_values_in_valid_range(self) -> None:
        """测试百分比值在0-100范围内"""
        response = client.get("/api/energy/classification")
        assert response.status_code == 200
        result = response.json()

        if result["code"] == 200 and result["data"]["items"]:
            for item in result["data"]["items"]:
                assert (
                    0 <= item["percentage"] <= 100
                ), f"百分比超出有效范围: {item['percentage']}"


class TestEnergyAPIConcurrency:
    """测试并发请求"""

    def test_concurrent_requests_same_endpoint(self) -> None:
        """测试对同一端点的并发请求"""
        import concurrent.futures

        def make_request():
            return client.get("/api/energy/kpi")

        # 同时发起10个请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [f.result() for f in futures]

        # 所有请求都应该成功
        for response in responses:
            assert response.status_code == 200

    def test_concurrent_requests_different_endpoints(self) -> None:
        """测试对不同端点的并发请求"""
        import concurrent.futures

        endpoints = [
            "/api/energy/kpi",
            "/api/energy/realtime",
            "/api/energy/trend?period=7d",
            "/api/energy/compare",
            "/api/energy/classification",
        ]

        def make_request(endpoint):
            return client.get(endpoint)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, ep) for ep in endpoints]
            responses = [f.result() for f in futures]

        # 所有请求都应该成功
        for response in responses:
            assert response.status_code == 200


class TestEnergyAPIPerformance:
    """测试性能相关"""

    def test_response_time_acceptable(self) -> None:
        """测试响应时间在可接受范围内"""
        import time

        start_time = time.time()
        response = client.get("/api/energy/kpi")
        end_time = time.time()

        assert response.status_code == 200

        # 响应时间应在1秒内
        response_time = end_time - start_time
        assert response_time < 1.0, f"响应时间过长: {response_time:.2f}秒"

    def test_large_period_response_time(self) -> None:
        """测试大周期数据的响应时间"""
        import time

        start_time = time.time()
        response = client.get("/api/energy/trend?period=30d")
        end_time = time.time()

        assert response.status_code == 200

        # 即使是30天的数据，响应时间也应在2秒内
        response_time = end_time - start_time
        assert response_time < 2.0, f"大周期数据响应时间过长: {response_time:.2f}秒"


class TestEnergyAPISpecialCharacters:
    """测试特殊字符处理"""

    def test_special_characters_in_line(self) -> None:
        """测试线路参数中的特殊字符"""
        special_chars = ["M3%20", "M3&station=test", "M3<script>", "M3'; DROP TABLE"]

        for char_str in special_chars:
            response = client.get(f"/api/energy/kpi?line={char_str}")
            # 应该安全处理，不应该报500错误
            assert response.status_code in [200, 400, 422]

    def test_sql_injection_attempts(self) -> None:
        """测试SQL注入防护"""
        injection_attempts = [
            "' OR '1'='1",
            "1; DROP TABLE users",
            "' UNION SELECT * FROM stations",
        ]

        for attempt in injection_attempts:
            response = client.get(f"/api/energy/kpi?station_ip={attempt}")
            # 应该安全处理
            assert response.status_code in [200, 400, 422]
            # 不应该执行任何数据库操作


class TestEnergyAPIHeaderHandling:
    """测试HTTP头处理"""

    def test_x_station_ip_header(self) -> None:
        """测试X-Station-Ip头的处理"""
        headers = {"X-Station-Ip": "192.168.1.100"}
        response = client.get("/api/energy/kpi", headers=headers)
        assert response.status_code == 200

    def test_invalid_x_station_ip_header(self) -> None:
        """测试无效的X-Station-Ip头"""
        headers = {"X-Station-Ip": "invalid_ip"}
        response = client.get("/api/energy/kpi", headers=headers)
        # 应该优雅处理
        assert response.status_code in [200, 400]

    def test_missing_headers(self) -> None:
        """测试缺少可选头的情况"""
        response = client.get("/api/energy/kpi")
        # 可选头缺失时应该正常工作
        assert response.status_code == 200


class TestEnergyAPIRateLimit:
    """测试速率限制（如果实现）"""

    def test_rapid_requests_handling(self) -> None:
        """测试快速连续请求的处理"""
        # 快速发送多个请求
        responses = []
        for _ in range(20):
            response = client.get("/api/energy/kpi")
            responses.append(response)

        # 至少前几个请求应该成功
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count >= 15, "大多数请求应该成功"


class TestEnergyAPICache:
    """测试缓存行为（如果实现）"""

    def test_repeated_requests_consistency(self) -> None:
        """测试重复请求的一致性"""
        # 发送两次相同的请求
        response1 = client.get("/api/energy/kpi")
        response2 = client.get("/api/energy/kpi")

        assert response1.status_code == 200
        assert response2.status_code == 200

        # 短时间内的结果应该相似（考虑缓存）
        data1 = response1.json()["data"]
        data2 = response2.json()["data"]

        # station_count应该相同
        if "station_count" in data1 and "station_count" in data2:
            assert data1["station_count"] == data2["station_count"]


class TestEnergyAPIErrorMessages:
    """测试错误消息"""

    def test_error_messages_are_informative(self) -> None:
        """测试错误消息是否提供有用信息"""
        # 测试无效的周期参数
        response = client.get("/api/energy/trend?period=invalid")

        if response.status_code in [400, 422]:
            result = response.json()
            # 错误消息应该存在且非空
            assert "detail" in result or "message" in result


class TestEnergyAPIDataFreshness:
    """测试数据时效性"""

    def test_update_time_is_recent(self) -> None:
        """测试更新时间是否为最近时间"""
        from datetime import datetime, timedelta

        response = client.get("/api/energy/kpi")
        assert response.status_code == 200
        result = response.json()

        if result["code"] == 200:
            data = result["data"]
            update_time_str = data["update_time"]

            # 尝试解析时间
            try:
                update_time = datetime.fromisoformat(
                    update_time_str.replace("Z", "+00:00")
                )
                now = datetime.now(update_time.tzinfo)

                # 更新时间应该在最近1分钟内
                time_diff = abs((now - update_time).total_seconds())
                assert time_diff < 60, f"更新时间不够新鲜，时间差: {time_diff}秒"
            except ValueError:
                # 如果解析失败，至少验证格式
                assert isinstance(update_time_str, str) and len(update_time_str) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-x"])
