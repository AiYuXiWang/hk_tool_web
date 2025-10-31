"""
测试能源驾驶舱数据与导出数据一致性修复

验证修复后能源驾驶舱使用与导出功能相同的配置
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.services.realtime_energy_service import RealtimeEnergyService


def test_miaoling_station_config():
    """测试苗岭路站配置读取"""
    service = RealtimeEnergyService()
    
    # 测试苗岭路配置（11号线）
    config = service._get_jieneng_config('M11', '苗岭路')
    
    # 验证配置不为空
    assert config is not None, "配置应该存在"
    
    # 验证包含所需字段
    assert "data_codes" in config, "配置应包含data_codes"
    assert "object_codes" in config, "配置应包含object_codes"
    
    # 验证数据量（苗岭路站应该有17个数据代码）
    assert len(config["data_codes"]) == 17, f"苗岭路站应有17个data_codes，实际: {len(config['data_codes'])}"
    assert len(config["object_codes"]) == 13, f"苗岭路站应有13个object_codes，实际: {len(config['object_codes'])}"
    
    # 验证具体配置内容
    expected_data_codes = [
        "LSA1_28", "LSA2_28", "LT/A1_7", "LT/A2_7",
        "LDA1_8", "LDA2_8", "LQA1_8", "LQA2_4",
        "XK-B1_3", "XK-B2_13", "XK-B3_13",
        "XHPF-B1_3", "XHPF-B2_13", "XHPF-B3_13",
        "XK-B1_7", "XK-B2_17", "HPF-B_34"
    ]
    
    assert config["data_codes"] == expected_data_codes, (
        f"data_codes不匹配\n期望: {expected_data_codes}\n实际: {config['data_codes']}"
    )
    
    print("✓ 苗岭路站配置测试通过")
    print(f"  - data_codes数量: {len(config['data_codes'])}")
    print(f"  - object_codes数量: {len(config['object_codes'])}")
    print(f"  - data_codes前3个: {config['data_codes'][:3]}")
    print(f"  - object_codes前3个: {config['object_codes'][:3]}")


def test_other_stations_config():
    """测试其他站点配置读取"""
    service = RealtimeEnergyService()
    
    test_stations = [
        ("M3", "振华路"),
        ("M3", "五四广场"),
        ("M11", "青岛二中"),
    ]
    
    for line, station_name in test_stations:
        config = service._get_jieneng_config(line, station_name)
        
        assert config is not None, f"{station_name}配置应该存在"
        assert "data_codes" in config, f"{station_name}配置应包含data_codes"
        assert "object_codes" in config, f"{station_name}配置应包含object_codes"
        assert len(config["data_codes"]) > 0, f"{station_name}应有data_codes"
        assert len(config["object_codes"]) > 0, f"{station_name}应有object_codes"
        
        print(f"✓ {station_name}配置测试通过 (data_codes: {len(config['data_codes'])}, object_codes: {len(config['object_codes'])})")


def test_config_consistency_with_export():
    """测试配置与导出功能的一致性"""
    from backend.app.services.realtime_energy_service import RealtimeEnergyService
    from config_electricity import line_configs
    
    service = RealtimeEnergyService()
    
    # 测试苗岭路站
    line_code = "M11"
    station_name = "苗岭路"
    
    # 从能源服务获取配置
    energy_config = service._get_jieneng_config(line_code, station_name)
    
    # 从原始配置获取（导出功能使用的方式）
    export_config = line_configs.get(line_code, {}).get(station_name, {})
    
    assert energy_config is not None, "能源服务配置应该存在"
    assert export_config, "导出服务配置应该存在"
    
    # 验证两者使用相同的data_codes和object_codes
    assert energy_config["data_codes"] == export_config.get("data_codes", []), (
        "能源服务和导出服务应使用相同的data_codes"
    )
    assert energy_config["object_codes"] == export_config.get("object_codes", []), (
        "能源服务和导出服务应使用相同的object_codes"
    )
    
    print("✓ 配置一致性测试通过")
    print(f"  - 能源服务与导出服务使用相同的配置")
    print(f"  - data_codes数量: {len(energy_config['data_codes'])}")
    print(f"  - object_codes数量: {len(energy_config['object_codes'])}")


def test_jienengfeijieneng_not_used():
    """确认不再使用jienengfeijieneng节点"""
    from backend.app.services.realtime_energy_service import RealtimeEnergyService
    from config_electricity import line_configs
    
    service = RealtimeEnergyService()
    
    # 测试苗岭路站
    line_code = "M11"
    station_name = "苗岭路"
    
    # 获取配置
    energy_config = service._get_jieneng_config(line_code, station_name)
    
    # 从原始配置获取jienengfeijieneng节点
    station_config = line_configs.get(line_code, {}).get(station_name, {})
    jieneng_node = station_config.get("jienengfeijieneng", {})
    
    # 验证：
    # 1. jienengfeijieneng节点只有1个data_code（节能状态）
    # 2. 能源服务使用的配置有17个data_codes（所有设备）
    assert len(jieneng_node.get("data_codes", [])) == 1, (
        "jienengfeijieneng节点应只有1个data_code（节能状态）"
    )
    assert len(energy_config["data_codes"]) == 17, (
        "能源服务应使用所有17个data_codes（所有设备功率）"
    )
    
    print("✓ 不再使用jienengfeijieneng节点测试通过")
    print(f"  - jienengfeijieneng节点data_codes: {len(jieneng_node.get('data_codes', []))} (仅节能状态)")
    print(f"  - 能源服务data_codes: {len(energy_config['data_codes'])} (所有设备)")


if __name__ == "__main__":
    print("=" * 60)
    print("能源驾驶舱数据一致性修复测试")
    print("=" * 60)
    print()
    
    try:
        test_miaoling_station_config()
        print()
        test_other_stations_config()
        print()
        test_config_consistency_with_export()
        print()
        test_jienengfeijieneng_not_used()
        print()
        print("=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"❌ 测试失败: {e}")
        print("=" * 60)
        raise
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ 测试异常: {e}")
        print("=" * 60)
        raise
