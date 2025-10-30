"""
真实能源数据服务
从平台API获取实时能源数据
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from backend.app.config.electricity_config import ElectricityConfig

logger = logging.getLogger(__name__)

try:  # noqa: SIM105
    from control_service import PlatformAPIService  # type: ignore
except Exception as exc:  # pragma: no cover - 环境缺失requests等依赖时的兼容处理
    PlatformAPIService = None  # type: ignore
    logging.getLogger(__name__).warning("PlatformAPIService 无法导入，能源数据将回退至估算模式: %s", exc)


class RealtimeEnergyService:
    """真实能源数据服务"""

    def __init__(self):
        self.platform_api = PlatformAPIService() if PlatformAPIService else None
        self.electricity_config = ElectricityConfig()

    def _get_station_query_pairs(self, station: Dict[str, Any]) -> List[tuple]:
        """从站点配置提取(object_code, data_code)对"""
        line_code = station.get("line")
        station_name = station.get("name")
        jieneng_config = self._get_jieneng_config(line_code, station_name)
        if not jieneng_config:
            logger.warning("站点 %s 没有节能数据配置", station_name)
            return []
        object_codes = jieneng_config.get("object_codes", [])
        data_codes = jieneng_config.get("data_codes", [])
        if not object_codes or not data_codes:
            return []
        if len(data_codes) == 1 and len(object_codes) == 1:
            return [(object_codes[0], data_codes[0])]
        return [(object_codes[0], data_codes[0])] if object_codes and data_codes else []

    async def get_station_realtime_power(
        self, station: Dict[str, Any]
    ) -> Optional[float]:
        """获取单个站点的实时总功率"""
        if not self.platform_api:
            logger.debug("PlatformAPIService 不可用，跳过实时数据查询")
            return None

        station_ip = station.get("ip")
        if not station_ip:
            logger.warning("站点 %s 没有IP配置", station.get("name"))
            return None

        query_pairs = self._get_station_query_pairs(station)
        if not query_pairs:
            return None

        try:
            results = await asyncio.gather(
                *(
                    self._query_power_value(obj, data, station_ip)
                    for obj, data in query_pairs
                ),
                return_exceptions=True,
            )
        except Exception as exc:  # pragma: no cover - gather内部异常
            logger.error("获取站点 %s 实时功率失败: %s", station.get("name"), exc)
            return None

        numeric_values = [value for value in results if isinstance(value, (int, float))]
        if not numeric_values:
            return None

        return float(sum(numeric_values))

    async def _query_power_value(
        self, object_code: str, data_code: str, station_ip: str
    ) -> Optional[float]:
        """查询单个点位的功率值"""
        if not self.platform_api:
            return None

        try:
            result = await self.platform_api.query_realtime_value(
                object_code, data_code, station_ip
            )
        except Exception as exc:  # pragma: no cover - 网络异常
            logger.error("查询功率值失败 %s:%s: %s", object_code, data_code, exc)
            return None

        if not isinstance(result, dict):
            return None

        return self._extract_numeric_value(result)

    def _extract_numeric_value(self, payload: Dict[str, Any]) -> Optional[float]:
        """从API返回中提取数值"""
        raw_value: Any = payload.get("value")
        if raw_value is None:
            data = payload.get("data")
            if isinstance(data, list) and data:
                item = data[0]
                if isinstance(item, dict):
                    raw_value = item.get(
                        "property_num_value", item.get("property_value")
                    )
        return self._safe_float(raw_value)

    def _safe_float(self, value: Any) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):  # pragma: no cover - 非数字字符串
            logger.warning("无法转换功率值: %s", value)
            return None

    def _get_jieneng_config(self, line_code: str, station_name: str) -> Optional[Dict]:
        """从config_electricity.py获取站点的节能配置"""
        try:
            from config_electricity import line_configs

            # 获取线路配置
            line_config = line_configs.get(line_code)
            if not line_config:
                return None

            # 获取站点配置
            station_config = line_config.get(station_name)
            if not station_config:
                return None

            # 返回节能配置
            return station_config.get("jienengfeijieneng")

        except Exception as e:
            logger.error(f"获取节能配置失败: {e}")
            return None

    async def get_multiple_stations_power(
        self, stations: List[Dict[str, Any]]
    ) -> Dict[str, Optional[float]]:
        """
        批量获取多个站点的实时功率
        返回: {station_name: power_value}
        """
        tasks = []
        station_names = []

        for station in stations:
            tasks.append(self.get_station_realtime_power(station))
            station_names.append(station.get("name"))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        power_map = {}
        for station_name, result in zip(station_names, results):
            if isinstance(result, (int, float)):
                power_map[station_name] = result
            else:
                power_map[station_name] = None

        return power_map

    async def get_station_device_powers(
        self, station: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        获取站点所有设备的实时功率
        从data_codes列表中逐个查询
        """
        try:
            station_ip = station.get("ip")
            line_code = station.get("line")
            station_name = station.get("name")

            if not station_ip:
                return []

            # 从config_electricity获取原始配置
            from config_electricity import line_configs

            line_config = line_configs.get(line_code)
            if not line_config:
                return []

            station_config = line_config.get(station_name)
            if not station_config:
                return []

            # 获取对象代码和数据代码列表
            object_codes = station_config.get("object_codes", [])
            data_codes = station_config.get("data_codes", [])
            data_list = station_config.get("data_list", [])

            if not object_codes or not data_codes:
                return []

            # 为每个数据代码创建查询任务
            device_powers = []

            # 限制查询数量，避免过多请求
            max_queries = min(len(data_codes), 20)

            for i, data_code in enumerate(data_codes[:max_queries]):
                # 选择合适的对象代码（通常第一个是主对象）
                object_code = object_codes[0] if object_codes else None

                if not object_code:
                    continue

                # 获取对应的设备信息
                device_name = f"设备{i+1}"
                if i < len(data_list):
                    device_info = data_list[i]
                    device_name = device_info.get("p3", device_name)

                # 查询功率值
                power = await self._query_power_value(
                    object_code, data_code, station_ip
                )

                device_powers.append(
                    {
                        "device_name": device_name,
                        "data_code": data_code,
                        "object_code": object_code,
                        "power": power if power is not None else 0.0,
                        "status": "online" if power is not None else "offline",
                    }
                )

            return device_powers

        except Exception as e:
            logger.error(f"获取站点设备功率失败: {e}")
            return []
