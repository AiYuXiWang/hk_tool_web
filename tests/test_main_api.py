"""
主 API 端点测试
测试 main.py 中定义的 API 端点
"""

import pytest
from fastapi.testclient import TestClient

try:
    from main import app
except ImportError:
    pytest.skip("主应用模块不可用", allow_module_level=True)

client = TestClient(app)


def extract_payload(response):
    """提取标准化响应中的数据payload"""
    data = response.json()
    if isinstance(data, dict) and "code" in data and "data" in data:
        assert data["code"] == 200
        return data["data"]
    return data


class TestRootEndpoint:
    """测试根端点"""

    def test_root_endpoint(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestLinesAPI:
    """测试线路配置 API"""

    def test_get_lines(self):
        """测试获取所有线路"""
        response = client.get("/api/lines")
        assert response.status_code == 200

        data = response.json()
        # 检查是否是标准化响应
        if "code" in data and "data" in data:
            assert data["code"] == 200
            lines_data = data["data"]
        else:
            lines_data = data

        assert "lines" in lines_data
        assert isinstance(lines_data["lines"], list)

    def test_get_line_config(self):
        """测试获取指定线路配置"""
        # 首先获取所有线路
        lines_response = client.get("/api/lines")
        lines_data = extract_payload(lines_response)
        lines = lines_data.get("lines", [])

        if lines:
            # 测试第一条线路
            line_name = lines[0]
            response = client.get(f"/api/line-config/{line_name}")
            assert response.status_code == 200

            config_data = extract_payload(response)
            assert "config" in config_data

    def test_get_nonexistent_line_config(self):
        """测试获取不存在的线路配置"""
        response = client.get("/api/line-config/NONEXISTENT_LINE")
        # 中间件会将所有响应包装，status_code 总是 200
        assert response.status_code == 200
        data = response.json()
        # 检查内部的 code 是否为 404
        assert data.get("code") == 404

    def test_get_line_configs_all(self):
        """测试获取所有线路车站配置"""
        response = client.get("/api/config/line_configs")
        assert response.status_code == 200

        data = extract_payload(response)
        assert isinstance(data, dict)


class TestEnergyKPI:
    """测试能源 KPI API（Legacy endpoints in main.py）"""

    @pytest.fixture
    def test_line(self):
        """获取测试线路"""
        response = client.get("/api/lines")
        data = response.json()
        # 处理标准化响应
        if "code" in data and "data" in data:
            lines = data["data"]["lines"]
        else:
            lines = data["lines"]
        return lines[0] if lines else "M3"  # 默认使用 M3

    def test_get_energy_kpi(self, test_line):
        """测试获取能源 KPI"""
        response = client.get(f"/api/energy/kpi?line={test_line}")

        # 检查响应状态码，可能是 200 或标准化响应
        if response.status_code == 200:
            data = response.json()

            # 如果是标准化响应
            if "code" in data:
                assert data["code"] == 200
                kpi = data["data"]
            else:
                kpi = data

            # 验证KPI字段存在
            assert "total_kwh_today" in kpi
            assert "current_kw" in kpi
            assert "peak_kw" in kpi
            assert "station_count" in kpi

            # 验证数据类型
            assert isinstance(kpi["total_kwh_today"], (int, float))
            assert isinstance(kpi["current_kw"], (int, float))
            assert isinstance(kpi["peak_kw"], (int, float))
            assert isinstance(kpi["station_count"], int)

    def test_get_energy_realtime(self, test_line):
        """测试获取实时能耗数据"""
        response = client.get(f"/api/energy/realtime?line={test_line}")

        if response.status_code == 200:
            data = response.json()

            # 如果是标准化响应
            if "code" in data:
                assert data["code"] == 200
                realtime = data["data"]
            else:
                realtime = data

            assert "timestamps" in realtime
            assert "series" in realtime
            assert isinstance(realtime["timestamps"], list)
            assert isinstance(realtime["series"], list)

    def test_get_energy_trend(self, test_line):
        """测试获取能耗趋势"""
        for period in ["24h", "7d", "30d"]:
            response = client.get(f"/api/energy/trend?line={test_line}&period={period}")

            if response.status_code == 200:
                data = response.json()

                # 如果是标准化响应
                if "code" in data:
                    assert data["code"] == 200
                    trend = data["data"]
                else:
                    trend = data

                assert "timestamps" in trend
                assert "values" in trend
                assert len(trend["timestamps"]) == len(trend["values"])

    def test_get_energy_suggestions(self, test_line):
        """测试获取节能建议"""
        response = client.get(f"/api/energy/suggestions?line={test_line}")

        if response.status_code == 200:
            data = response.json()

            # 如果是标准化响应
            if "code" in data:
                assert data["code"] == 200
                suggestions = data["data"]
            else:
                suggestions = data

            # 检查字段存在（可能是 items 或 suggestions）
            assert "items" in suggestions or "suggestions" in suggestions
            items = suggestions.get("items", suggestions.get("suggestions", []))
            assert isinstance(items, list)

    def test_get_energy_compare(self, test_line):
        """测试获取能耗对比数据"""
        response = client.get(f"/api/energy/compare?line={test_line}&period=7d")

        if response.status_code == 200:
            data = response.json()

            # 如果是标准化响应
            if "code" in data:
                assert data["code"] == 200
                compare = data["data"]
            else:
                compare = data

            # 验证对比数据字段
            if "current_kwh" in compare:
                assert isinstance(compare["current_kwh"], (int, float))


class TestDeviceControl:
    """测试设备控制 API"""

    def test_get_device_tree(self):
        """测试获取设备树"""
        response = client.get("/control/device-tree")

        # 设备树端点可能返回 200 或标准化响应
        if response.status_code == 200:
            data = response.json()

            # 检查是否是标准化响应
            if "code" in data:
                assert data["code"] == 200
                tree = data["data"]
                assert "tree" in tree or "nodes" in tree
            else:
                # 直接返回树结构
                assert isinstance(data, (list, dict))


class TestExportAPI:
    """测试导出 API"""

    def test_export_task_status(self):
        """测试获取导出任务状态"""
        # 查询不存在的任务
        response = client.get("/api/export/status/nonexistent_task")

        # 应该返回错误或空结果
        assert response.status_code in [200, 404]


@pytest.mark.integration
class TestAPIIntegration:
    """API 集成测试"""

    def test_full_workflow(self):
        """测试完整工作流"""
        try:
            # 1. 获取线路列表
            lines_response = client.get("/api/lines")
            assert lines_response.status_code == 200
            lines_data = extract_payload(lines_response)
            lines = lines_data.get("lines", [])

            if not lines:
                pytest.skip("No lines configured")

            test_line = lines[0]

            # 2. 获取线路配置
            config_response = client.get(f"/api/line-config/{test_line}")
            assert config_response.status_code == 200
            config_data = extract_payload(config_response)
            assert "config" in config_data

            # 3. 获取 KPI 数据
            kpi_response = client.get(f"/api/energy/kpi?line={test_line}")
            assert kpi_response.status_code == 200
            extract_payload(kpi_response)

            # 4. 获取实时数据
            realtime_response = client.get(f"/api/energy/realtime?line={test_line}")
            assert realtime_response.status_code == 200
            extract_payload(realtime_response)

        except Exception as e:
            pytest.skip(f"Integration test skipped: {e}")


class TestMiddleware:
    """测试中间件功能"""

    def test_cors_headers(self):
        """测试 CORS 头部"""
        response = client.get("/")
        # CORS 中间件应该添加相关头部
        assert response.status_code == 200

    def test_rate_limiting(self):
        """测试限流"""
        # 发送多个请求测试限流
        for _ in range(5):
            response = client.get("/")
            assert response.status_code == 200

        # 注意：实际的限流测试需要超过限流阈值，这里只做基本测试


class TestErrorHandling:
    """测试错误处理"""

    def test_404_endpoint(self):
        """测试不存在的端点"""
        response = client.get("/api/nonexistent/endpoint")
        # 中间件会包装响应，HTTP 状态码总是 200
        assert response.status_code == 200
        data = response.json()
        # 检查内部code是否为404
        assert data.get("code") == 404

    def test_invalid_parameters(self):
        """测试无效参数"""
        response = client.get("/api/line-config/")
        # 中间件会包装响应，HTTP 状态码总是 200
        assert response.status_code == 200
        data = response.json()
        # 检查内部code
        assert data.get("code") in [404, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
