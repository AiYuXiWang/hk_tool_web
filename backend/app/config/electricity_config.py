"""
电力配置管理服务
解析和管理config_electricity.py中的站点和设备配置
"""

import logging
import os
import sys
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ElectricityConfig:
    """电力配置管理类"""

    def __init__(self):
        self.config_data = None
        self._load_config()

    def _load_config(self):
        """加载电力配置文件"""
        try:
            # 添加项目根目录到Python路径
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            )
            if project_root not in sys.path:
                sys.path.insert(0, project_root)

            # 导入配置文件
            import config_electricity

            self.config_data = config_electricity.line_configs
            logger.info(f"成功加载电力配置，包含 {len(self.config_data)} 条线路")

        except Exception as e:
            logger.error(f"加载电力配置失败: {e}")
            # 使用默认配置
            self.config_data = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "3号线电耗数据配置": {
                "振华路": {
                    "ip": "192.168.100.4",
                    "站点名称": "振华路",
                    "节能对象代码": "1001",
                    "非节能对象代码": "1002",
                    "节能数据代码": "2001",
                    "非节能数据代码": "2002",
                    "data_list": [
                        {
                            "name": "冷机LS01",
                            "location": "设备房A",
                            "power": 150,
                            "ct_ratio": 100,
                        }
                    ],
                }
            }
        }

    def get_all_stations(self) -> List[Dict[str, Any]]:
        """获取所有站点配置"""
        stations = []

        for line_name, line_config in self.config_data.items():
            line_code = self._extract_line_code(line_name)

            for station_name, station_config in line_config.items():
                station_info = {
                    "name": station_name,
                    "ip": station_config.get("ip", ""),
                    "line": line_code,
                    "line_name": line_name,
                    "station_code": station_config.get("站点名称", station_name),
                    "energy_object_code": station_config.get("节能对象代码", ""),
                    "non_energy_object_code": station_config.get("非节能对象代码", ""),
                    "energy_data_code": station_config.get("节能数据代码", ""),
                    "non_energy_data_code": station_config.get("非节能数据代码", ""),
                    "device_count": len(station_config.get("data_list", [])),
                    "jienengfeijieneng": station_config.get("jienengfeijieneng", {}),
                }
                stations.append(station_info)

        return stations

    def get_station_by_ip(self, ip: str) -> Optional[Dict[str, Any]]:
        """根据IP获取站点配置"""
        for line_name, line_config in self.config_data.items():
            for station_name, station_config in line_config.items():
                if station_config.get("ip") == ip:
                    return {
                        "name": station_name,
                        "ip": ip,
                        "line": self._extract_line_code(line_name),
                        "line_name": line_name,
                        "station_code": station_config.get("站点名称", station_name),
                        "energy_object_code": station_config.get("节能对象代码", ""),
                        "non_energy_object_code": station_config.get("非节能对象代码", ""),
                        "energy_data_code": station_config.get("节能数据代码", ""),
                        "non_energy_data_code": station_config.get("非节能数据代码", ""),
                        "device_count": len(station_config.get("data_list", [])),
                        "jienengfeijieneng": station_config.get(
                            "jienengfeijieneng", {}
                        ),
                    }
        return None

    def get_stations_by_line(self, line_code: str) -> List[Dict[str, Any]]:
        """根据线路代码获取站点列表"""
        stations = []

        for line_name, line_config in self.config_data.items():
            if self._extract_line_code(line_name) == line_code:
                for station_name, station_config in line_config.items():
                    station_info = {
                        "name": station_name,
                        "ip": station_config.get("ip", ""),
                        "line": line_code,
                        "line_name": line_name,
                        "station_code": station_config.get("站点名称", station_name),
                        "energy_object_code": station_config.get("节能对象代码", ""),
                        "non_energy_object_code": station_config.get("非节能对象代码", ""),
                        "energy_data_code": station_config.get("节能数据代码", ""),
                        "non_energy_data_code": station_config.get("非节能数据代码", ""),
                        "device_count": len(station_config.get("data_list", [])),
                        "jienengfeijieneng": station_config.get(
                            "jienengfeijieneng", {}
                        ),
                    }
                    stations.append(station_info)

        return stations

    def get_station_devices(self, station_ip: str) -> List[Dict[str, Any]]:
        """获取指定站点的设备列表"""
        for line_name, line_config in self.config_data.items():
            for station_name, station_config in line_config.items():
                if station_config.get("ip") == station_ip:
                    devices = station_config.get("data_list", [])
                    # 标准化设备信息，同时保留原始配置
                    standardized_devices = []
                    for device in devices:
                        standardized_device = {
                            # 保留原始配置
                            **device,
                            # 添加标准化字段
                            "name": device.get("p3", device.get("name", "未知设备")),
                            "location": device.get(
                                "p6", device.get("location", "未知位置")
                            ),
                            "power": device.get("p5", device.get("power", "0")),
                            "ct_ratio": device.get("p7", device.get("ct_ratio", "1/1")),
                            "type": self._classify_device_type(
                                device.get("p3", device.get("name", ""))
                            ),
                            "station_name": station_name,
                            "station_ip": station_ip,
                        }
                        standardized_devices.append(standardized_device)
                    return standardized_devices
        return []

    def get_line_summary(self) -> List[Dict[str, Any]]:
        """获取线路汇总信息"""
        line_summary = []

        for line_name, line_config in self.config_data.items():
            line_code = self._extract_line_code(line_name)
            station_count = len(line_config)
            total_devices = sum(
                len(station.get("data_list", [])) for station in line_config.values()
            )

            line_info = {
                "line_code": line_code,
                "line_name": line_name,
                "station_count": station_count,
                "device_count": total_devices,
                "stations": list(line_config.keys()),
            }
            line_summary.append(line_info)

        return line_summary

    def _extract_line_code(self, line_name: str) -> str:
        """从线路名称中提取线路代码"""
        if "3号线" in line_name:
            return "M3"
        elif "8号线" in line_name:
            return "M8"
        elif "11号线" in line_name:
            return "M11"
        elif "1号线" in line_name:
            return "M1"
        elif "2号线" in line_name:
            return "M2"
        else:
            # 尝试从名称中提取数字
            import re

            match = re.search(r"(\d+)号线", line_name)
            if match:
                return f"M{match.group(1)}"
            return "M0"  # 默认值

    def _classify_device_type(self, device_name: str) -> str:
        """根据设备名称分类设备类型"""
        device_name_lower = device_name.lower()

        if any(keyword in device_name_lower for keyword in ["冷机", "制冷", "chiller"]):
            return "冷机"
        elif any(keyword in device_name_lower for keyword in ["水泵", "pump"]):
            return "水泵"
        elif any(keyword in device_name_lower for keyword in ["冷却塔", "cooling_tower"]):
            return "冷却塔"
        elif any(keyword in device_name_lower for keyword in ["风机", "fan"]):
            return "风机"
        elif any(keyword in device_name_lower for keyword in ["照明", "light"]):
            return "照明"
        elif any(keyword in device_name_lower for keyword in ["电梯", "elevator"]):
            return "电梯"
        else:
            return "其他"

    def get_device_by_name(
        self, station_ip: str, device_name: str
    ) -> Optional[Dict[str, Any]]:
        """根据站点IP和设备名称获取设备信息"""
        devices = self.get_station_devices(station_ip)
        for device in devices:
            if device["name"] == device_name:
                return device
        return None

    def validate_station_ip(self, ip: str) -> bool:
        """验证站点IP是否存在于配置中"""
        return self.get_station_by_ip(ip) is not None

    def get_config_stats(self) -> Dict[str, Any]:
        """获取配置统计信息"""
        all_stations = self.get_all_stations()
        line_summary = self.get_line_summary()

        total_devices = sum(station["device_count"] for station in all_stations)

        return {
            "total_lines": len(line_summary),
            "total_stations": len(all_stations),
            "total_devices": total_devices,
            "lines": [line["line_code"] for line in line_summary],
            "config_loaded": self.config_data is not None,
        }
