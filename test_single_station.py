#!/usr/bin/env python3
"""
单站点快速测试脚本
用于快速验证单个站点的数据获取情况
"""

import asyncio
import sys
from datetime import datetime, timedelta

from backend.app.services.realtime_energy_service import RealtimeEnergyService
from config_electricity import line_configs


async def test_single_station(line_code: str, station_name: str):
    """测试单个站点的数据获取"""
    print("=" * 80)
    print("  单站点测试: {} (线路: {})".format(station_name, line_code))
    print("=" * 80)
    print()

    # 检查配置是否存在
    line_config = line_configs.get(line_code)
    if not line_config:
        print(f"❌ 错误: 未找到线路 '{line_code}' 的配置")
        return False

    station_config = line_config.get(station_name)
    if not station_config:
        print(f"❌ 错误: 未找到站点 '{station_name}' 的配置")
        print(f"可用站点: {', '.join(line_config.keys())}")
        return False

    # 显示配置信息
    station_ip = station_config.get("ip")
    data_codes = station_config.get("data_codes", [])
    object_codes = station_config.get("object_codes", [])

    print("📋 站点信息:")
    print(f"  - IP地址: {station_ip}")
    print(f"  - Data Codes数量: {len(data_codes)}")
    print(f"  - Object Codes数量: {len(object_codes)}")
    print()

    if not station_ip or not data_codes or not object_codes:
        print("❌ 错误: 站点配置不完整")
        return False

    # 构建站点对象
    station = {
        "name": station_name,
        "ip": station_ip,
        "line": line_code,
    }

    # 初始化服务
    service = RealtimeEnergyService()

    # 测试1: 获取实时功率
    print("🔍 测试1: 获取实时功率")
    print("-" * 80)
    try:
        power = await service.get_station_realtime_power(station)
        if power is not None:
            print(f"✅ 成功获取实时功率: {power:.2f} kW")
        else:
            print("❌ 获取实时功率失败")
            return False
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

    print()

    # 测试2: 获取能耗数据
    print("🔍 测试2: 获取今日能耗")
    print("-" * 80)
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    try:
        consumption = await service.get_station_energy_consumption(
            station, start_of_day, now
        )
        if consumption is not None:
            print(f"✅ 成功获取今日能耗: {consumption:.2f} kWh")
            print(
                f"   时间段: {start_of_day.strftime('%Y-%m-%d %H:%M')} 至 {now.strftime('%H:%M')}"
            )
        else:
            print("❌ 获取能耗数据失败")
            return False
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

    print()
    print("=" * 80)
    print("✅ 所有测试通过！站点数据获取正常。")
    print("=" * 80)
    return True


def print_usage():
    """打印使用说明"""
    print("使用方法:")
    print("  python test_single_station.py <线路代码> <站点名称>")
    print()
    print("示例:")
    print("  python test_single_station.py M3 振华路")
    print("  python test_single_station.py M3 五四广场")
    print()
    print("可用线路代码:")
    print("  - M3: 3号线")
    print("  - M8: 8号线")
    print("  - M11: 11号线")
    print()
    print("查看所有可用站点:")
    print(
        "  python -c \"from config_electricity import line_configs; print('\\n'.join(f'{line}: {list(stations.keys())}' for line, stations in line_configs.items()))\""
    )


async def main():
    """主函数"""
    if len(sys.argv) != 3:
        print_usage()
        sys.exit(1)

    line_code = sys.argv[1]
    station_name = sys.argv[2]

    success = await test_single_station(line_code, station_name)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
