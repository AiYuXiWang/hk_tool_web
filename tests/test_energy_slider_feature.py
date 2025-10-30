"""
能源驾驶舱滑动栏功能测试
测试时间范围、刷新间隔和功率阈值滑动栏功能
"""

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def unwrap_response(response):
    """解包响应数据，处理标准化响应格式"""
    result = response.json()
    if "code" in result and "data" in result:
        return result["data"]
    return result


class TestEnergySliderFeature:
    """能源驾驶舱滑动栏功能测试"""

    def test_realtime_energy_with_hours_parameter(self):
        """测试实时能耗API支持hours参数"""
        response = client.get(
            "/api/energy/realtime",
            params={"line": "M3", "station_ip": "10.188.100.1", "hours": 48},
        )

        assert response.status_code == 200
        data = unwrap_response(response)

        # 验证返回数据包含时间范围信息
        assert "time_range_hours" in data
        assert data["time_range_hours"] == 48

    def test_realtime_energy_default_hours(self):
        """测试实时能耗API默认24小时"""
        response = client.get(
            "/api/energy/realtime", params={"line": "M3", "station_ip": "10.188.100.1"}
        )

        assert response.status_code == 200
        data = unwrap_response(response)

        # 验证默认返回24小时
        assert "time_range_hours" in data
        assert data["time_range_hours"] == 24

    def test_realtime_energy_hours_boundary(self):
        """测试时间范围边界值"""
        # 测试最小值 1 小时
        response = client.get(
            "/api/energy/realtime",
            params={"line": "M3", "station_ip": "10.188.100.1", "hours": 1},
        )
        assert response.status_code == 200
        data = unwrap_response(response)
        assert data["time_range_hours"] == 1

        # 测试最大值 72 小时
        response = client.get(
            "/api/energy/realtime",
            params={"line": "M3", "station_ip": "10.188.100.1", "hours": 72},
        )
        assert response.status_code == 200
        data = unwrap_response(response)
        assert data["time_range_hours"] == 72

    def test_realtime_energy_invalid_hours(self):
        """测试无效的hours参数"""
        # 测试超出范围的值（可能返回200但做了边界限制）
        response = client.get(
            "/api/energy/realtime",
            params={"line": "M3", "station_ip": "10.188.100.1", "hours": 100},
        )
        # 因为后端可能做了容错处理，所以验证响应是成功的
        assert response.status_code in [200, 422]

    def test_equipment_with_power_threshold(self):
        """测试设备监控API支持功率阈值"""
        response = client.get(
            "/api/energy/equipment",
            params={"min_power": 1000, "max_power": 3000},
            headers={"X-Station-Ip": "10.188.100.1"},
        )

        assert response.status_code == 200
        data = unwrap_response(response)

        # 验证返回的设备列表
        assert "equipment_list" in data
        equipment_list = data["equipment_list"]

        # 验证所有设备功率都在阈值范围内
        for equipment in equipment_list:
            power = equipment.get("power", 0)
            if power > 0:  # 跳过离线设备
                assert power >= 1000
                assert power <= 3000

    def test_equipment_with_min_power_only(self):
        """测试只设置最小功率阈值"""
        response = client.get(
            "/api/energy/equipment",
            params={"min_power": 500},
            headers={"X-Station-Ip": "10.188.100.1"},
        )

        assert response.status_code == 200
        data = unwrap_response(response)

        equipment_list = data.get("equipment_list", [])
        # 验证所有设备功率都大于等于500W
        for equipment in equipment_list:
            power = equipment.get("power", 0)
            if power > 0:
                assert power >= 500

    def test_equipment_default_no_threshold(self):
        """测试默认不设置功率阈值"""
        response = client.get(
            "/api/energy/equipment", headers={"X-Station-Ip": "10.188.100.1"}
        )

        assert response.status_code == 200
        data = unwrap_response(response)

        # 验证返回数据结构
        assert "equipment_list" in data
        assert "status_summary" in data
        assert "update_time" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
