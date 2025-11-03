#!/usr/bin/env python3
"""验证能源驾驶舱配置修复"""

from typing import Any, Dict, List, Tuple

from backend.app.config.electricity_config import ElectricityConfig
from config_electricity import line_configs

line_configs_typed: Dict[str, Dict[str, Any]] = line_configs


def build_line_stats(stations: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    stats: Dict[str, List[str]] = {}
    for station in stations:
        line = station.get("line")
        name = station.get("name")
        if not isinstance(line, str) or not isinstance(name, str):
            continue
        stats.setdefault(line, []).append(name)
    return stats


def find_missing_jieneng(stations: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
    missing: List[Tuple[str, str]] = []
    for station in stations:
        line = station.get("line")
        name = station.get("name")

        if not isinstance(line, str) or not isinstance(name, str):
            continue

        line_config = line_configs_typed.get(line)
        if not isinstance(line_config, dict):
            missing.append((line, name))
            continue

        station_config = line_config.get(name)
        if not isinstance(station_config, dict):
            missing.append((line, name))
            continue

        jieneng_config = station_config.get("jienengfeijieneng")
        if not isinstance(jieneng_config, dict):
            missing.append((line, name))
            continue

        if not jieneng_config.get("data_codes") or not jieneng_config.get(
            "object_codes"
        ):
            missing.append((line, name))

    return missing


def main() -> bool:
    config = ElectricityConfig()
    all_stations = config.get_all_stations()

    print(f"✅ 成功加载 {len(all_stations)} 个站点")
    print("\n线路分布:")

    for line, stations in sorted(build_line_stats(all_stations).items()):
        print(f"  {line}: {len(stations)} 个站点")

    print("\n配置完整性检查:")

    missing_jieneng = find_missing_jieneng(all_stations)
    if missing_jieneng:
        print(f"❌ 有 {len(missing_jieneng)} 个站点缺少jienengfeijieneng配置:")
        for line, name in missing_jieneng:
            print(f"  - {name} ({line})")
        return False

    print(f"✅ 所有 {len(all_stations)} 个站点都具有完整的jienengfeijieneng配置")
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
