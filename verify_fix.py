#!/usr/bin/env python3
"""验证能源驾驶舱配置修复"""

from backend.app.config.electricity_config import ElectricityConfig
from config_electricity import line_configs

def main():
    config = ElectricityConfig()
    all_stations = config.get_all_stations()
    
    print(f"✅ 成功加载 {len(all_stations)} 个站点")
    print(f"\n线路分布:")
    
    line_stats = {}
    for station in all_stations:
        line = station['line']
        if line not in line_stats:
            line_stats[line] = []
        line_stats[line].append(station['name'])
    
    for line, stations in sorted(line_stats.items()):
        print(f"  {line}: {len(stations)} 个站点")
    
    # 检查配置完整性
    print(f"\n配置完整性检查:")
    missing_jieneng = []
    for station in all_stations:
        line = station['line']
        name = station['name']
        line_config = line_configs.get(line, {})
        station_config = line_config.get(name, {})
        jieneng_config = station_config.get('jienengfeijieneng')
        
        if not jieneng_config:
            missing_jieneng.append((line, name))
            continue
            
        if not jieneng_config.get('data_codes') or not jieneng_config.get('object_codes'):
            missing_jieneng.append((line, name))
    
    if missing_jieneng:
        print(f"❌ 有 {len(missing_jieneng)} 个站点缺少jienengfeijieneng配置:")
        for line, name in missing_jieneng:
            print(f"  - {name} ({line})")
        return False
    else:
        print(f"✅ 所有 {len(all_stations)} 个站点都具有完整的jienengfeijieneng配置")
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
