"""
真实能源数据服务
从平台API获取实时能源数据
参考export_service中的能耗数据获取方式，使用 /data/selectHisData 接口
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from backend.app.config.electricity_config import ElectricityConfig

logger = logging.getLogger(__name__)

try:  # noqa: SIM105
    import requests  # type: ignore
except Exception as exc:  # pragma: no cover - 环境缺失requests依赖时的兼容处理
    requests = None  # type: ignore
    logging.getLogger(__name__).warning("requests模块无法导入，能源数据将回退至估算模式: %s", exc)


class RealtimeEnergyService:
    """真实能源数据服务"""

    def __init__(self) -> None:
        self.electricity_config = ElectricityConfig()
        self.requests_available = requests is not None

    def _get_station_api_url(self, station_ip: str) -> str:
        """构建站点API URL，参考export_service使用9898端口"""
        return f"http://{station_ip}:9898"

    async def get_station_realtime_power(
        self, station: Dict[str, Any]
    ) -> Optional[float]:
        """获取单个站点的实时总功率"""
        station_name = station.get("name", "未知站点")
        station_ip = station.get("ip")
        line_code = station.get("line", "未知线路")

        # 详细记录站点基础信息
        logger.info(
            "开始获取站点实时功率 - 站点: %s, IP: %s, 线路: %s", station_name, station_ip, line_code
        )

        if not self.requests_available:
            logger.error(
                "❌ [%s] requests模块不可用，无法查询实时数据。" "请确保已安装requests依赖包。", station_name
            )
            return None

        if not station_ip:
            logger.error(
                "❌ [%s] 站点配置缺少IP地址，无法查询实时数据。" "请检查站点配置中是否正确配置了'ip'字段。", station_name
            )
            return None

        # 获取节能配置
        jieneng_config = self._get_jieneng_config(line_code, station_name)
        if not jieneng_config:
            logger.error(
                "❌ [%s] 站点没有节能数据配置。"
                "请在config_electricity.py中为线路'%s'的站点'%s'配置'jienengfeijieneng'节点，"
                "包含object_codes和data_codes字段。",
                station_name,
                line_code,
                station_name,
            )
            return None

        object_codes = jieneng_config.get("object_codes", [])
        data_codes = jieneng_config.get("data_codes", [])

        logger.info(
            "📋 [%s] 节能配置解析成功 - object_codes数量: %d, data_codes数量: %d",
            station_name,
            len(object_codes),
            len(data_codes),
        )
        logger.debug(
            "📋 [%s] object_codes: %s, data_codes: %s",
            station_name,
            object_codes[:3] if len(object_codes) > 3 else object_codes,
            data_codes[:3] if len(data_codes) > 3 else data_codes,
        )

        if not object_codes or not data_codes:
            logger.error(
                "❌ [%s] 节能配置不完整 - object_codes: %s, data_codes: %s。"
                "请确保配置中同时包含有效的object_codes和data_codes数组。",
                station_name,
                "空" if not object_codes else f"{len(object_codes)}个",
                "空" if not data_codes else f"{len(data_codes)}个",
            )
            return None

        api_url = self._get_station_api_url(station_ip)
        logger.info("🔗 [%s] API地址: %s/data/selectHisData", station_name, api_url)

        try:
            power = await self._query_recent_power(api_url, object_codes, data_codes)
            if power is not None:
                logger.info("✅ [%s] 成功获取实时功率: %.2f kW (真实数据)", station_name, power)
            else:
                logger.warning(
                    "⚠️ [%s] API调用成功但未能获取有效功率数据。"
                    "可能原因: 1) API返回空数据 2) 数据格式无法解析 3) 时间范围内无数据",
                    station_name,
                )
            return power
        except Exception as exc:  # pragma: no cover - 网络异常
            logger.error(
                "❌ [%s] 获取实时功率异常: %s (类型: %s)",
                station_name,
                str(exc),
                type(exc).__name__,
            )
            return None

    async def get_station_energy_consumption(
        self, station: Dict[str, Any], start_time: datetime, end_time: datetime
    ) -> Optional[float]:
        """
        获取单个站点在指定时间段的能耗

        使用与export_service.py中process_data函数相同的逻辑：
        1. 获取时间段开始时的电表读数（起码）
        2. 获取时间段结束时的电表读数（止码）
        3. 计算差值作为耗电量

        Args:
            station: 站点配置信息
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            耗电量(kWh)，如果获取失败返回None
        """
        station_name = station.get("name", "未知站点")
        station_ip = station.get("ip")
        line_code = station.get("line", "未知线路")

        logger.info(
            "开始获取站点能耗 - 站点: %s, IP: %s, 线路: %s, 时间段: %s ~ %s",
            station_name,
            station_ip,
            line_code,
            start_time,
            end_time,
        )

        if not self.requests_available:
            logger.error("❌ [%s] requests模块不可用，无法查询能耗数据", station_name)
            return None

        if not station_ip:
            logger.error("❌ [%s] 站点配置缺少IP地址", station_name)
            return None

        # 获取配置
        jieneng_config = self._get_jieneng_config(line_code, station_name)
        if not jieneng_config:
            logger.error("❌ [%s] 站点没有节能数据配置", station_name)
            return None

        object_codes = jieneng_config.get("object_codes", [])
        data_codes = jieneng_config.get("data_codes", [])

        if not object_codes or not data_codes:
            logger.error("❌ [%s] 节能配置不完整", station_name)
            return None

        api_url = self._get_station_api_url(station_ip)

        try:
            # 按照export_service.py的process_data函数逻辑获取能耗
            consumption = await self._calculate_consumption_from_meter_readings(
                api_url, object_codes, data_codes, start_time, end_time, station_name
            )

            if consumption is not None:
                logger.info("✅ [%s] 成功获取能耗: %.2f kWh (真实数据)", station_name, consumption)
            else:
                logger.warning("⚠️ [%s] 未能获取有效能耗数据", station_name)

            return consumption

        except Exception as exc:
            logger.error(
                "❌ [%s] 获取能耗异常: %s (类型: %s)", station_name, str(exc), type(exc).__name__
            )
            return None

    async def _calculate_consumption_from_meter_readings(
        self,
        api_url: str,
        object_codes: List[str],
        data_codes: List[str],
        start_time: datetime,
        end_time: datetime,
        station_name: str = "未知站点",
    ) -> Optional[float]:
        """
        根据电表起码和止码计算能耗

        这个方法完全复制export_service.py中process_data函数的逻辑
        """
        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)

        # 获取结束时间的电表读数（止码）
        # 参考export_service.py第182-192行
        end_obj = {
            "dataCodes": data_codes,
            "endTime": end_timestamp,
            "fill": "0",
            "funcName": "mean",
            "funcTime": "",
            "measurement": "realData",
            "objectCodes": object_codes,
            "startTime": end_timestamp - 10 * 60000,  # 10分钟前
        }

        loop = asyncio.get_running_loop()
        end_data = await loop.run_in_executor(
            None, self._fetch_select_his_data, api_url, end_obj
        )

        if not end_data:
            logger.error("❌ [%s] 获取结束时间电表读数失败", station_name)
            return None

        # 获取开始时间的电表读数（起码）
        # 参考export_service.py第200-210行
        start_obj = {
            "dataCodes": data_codes,
            "endTime": start_timestamp + 3 * 60000,  # 3分钟后
            "fill": "0",
            "funcName": "mean",
            "funcTime": "",
            "measurement": "realData",
            "objectCodes": object_codes,
            "startTime": start_timestamp,
        }

        start_data = await loop.run_in_executor(
            None, self._fetch_select_his_data, api_url, start_obj
        )

        if not start_data:
            logger.error("❌ [%s] 获取开始时间电表读数失败", station_name)
            return None

        # 计算总能耗
        # 参考export_service.py第218-230行的逻辑
        total_consumption = 0.0
        valid_count = 0

        for data_code in data_codes:
            for object_code in object_codes:
                # 查找匹配的起始和结束读数
                start_entry = next(
                    (
                        item
                        for item in start_data
                        if item.get("tags", {}).get("dataCode") == data_code
                        and item.get("tags", {}).get("objectCode") == object_code
                    ),
                    None,
                )
                end_entry = next(
                    (
                        item
                        for item in end_data
                        if item.get("tags", {}).get("dataCode") == data_code
                        and item.get("tags", {}).get("objectCode") == object_code
                    ),
                    None,
                )

                if not start_entry or not end_entry:
                    continue

                start_values = start_entry.get("values", [])
                end_values = end_entry.get("values", [])
                if not start_values or not end_values:
                    continue

                start_reading = self._safe_float(start_values[0].get("value"))
                end_reading = self._safe_float(end_values[0].get("value"))
                if start_reading is None or end_reading is None:
                    logger.warning(
                        "⚠️ [%s] 设备 %s/%s 读数无法解析: start=%s, end=%s",
                        station_name,
                        data_code,
                        object_code,
                        start_values[0].get("value"),
                        end_values[0].get("value"),
                    )
                    continue

                # 计算能耗差值
                # 参考export_service.py第226-229行
                difference = end_reading - start_reading
                if difference >= -1:
                    consumption = round(difference, 2)
                    total_consumption += consumption
                    valid_count += 1
                    logger.debug(
                        "📊 [%s] 设备 %s/%s: 起码=%.2f, 止码=%.2f, 耗电=%.2f kWh",
                        station_name,
                        data_code,
                        object_code,
                        start_reading,
                        end_reading,
                        consumption,
                    )
                else:
                    logger.warning(
                        "⚠️ [%s] 设备 %s/%s 电表异常: 起码=%.2f > 止码=%.2f",
                        station_name,
                        data_code,
                        object_code,
                        start_reading,
                        end_reading,
                    )

                # 找到匹配的就跳出object_code循环
                break

        if valid_count > 0:
            logger.info(
                "📊 [%s] 能耗计算完成 - 有效设备数: %d/%d, 总能耗: %.2f kWh",
                station_name,
                valid_count,
                len(data_codes),
                total_consumption,
            )
            return round(total_consumption, 2)
        logger.warning("⚠️ [%s] 没有有效的能耗数据", station_name)
        return None

    def check_data_availability(self, station: Dict[str, Any]) -> bool:
        """
        检查站点是否能获取到真实数据
        返回True表示配置正确且可能获取到真实数据，False表示必定使用模拟数据
        """
        if not self.requests_available:
            return False

        station_ip = station.get("ip")
        if not station_ip:
            return False

        line_code = station.get("line")
        station_name = station.get("name")
        jieneng_config = self._get_jieneng_config(line_code, station_name)
        if not jieneng_config:
            return False

        object_codes = jieneng_config.get("object_codes", [])
        data_codes = jieneng_config.get("data_codes", [])
        return bool(object_codes and data_codes)

    async def _query_recent_power(
        self, api_url: str, object_codes: List[str], data_codes: List[str]
    ) -> Optional[float]:
        """查询最近10分钟的功率平均值"""
        loop = asyncio.get_running_loop()
        payload = self._build_select_payload(object_codes, data_codes)
        data = await loop.run_in_executor(
            None, self._fetch_select_his_data, api_url, payload
        )
        if not data:
            return None
        return self._aggregate_power_from_data(data)

    def _build_select_payload(
        self, object_codes: List[str], data_codes: List[str]
    ) -> Dict[str, Any]:
        """构建selectHisData请求体"""
        now = datetime.now()
        end_timestamp = int(now.timestamp() * 1000)
        start_timestamp = end_timestamp - 10 * 60_000  # 10分钟前

        return {
            "dataCodes": data_codes,
            "endTime": end_timestamp,
            "fill": "0",
            "funcName": "mean",
            "funcTime": "",
            "measurement": "realData",
            "objectCodes": object_codes,
            "startTime": start_timestamp,
        }

    def _fetch_select_his_data(
        self, api_url: str, payload: Dict[str, Any]
    ) -> Optional[List[Dict[str, Any]]]:
        """调用selectHisData接口并返回数据"""
        endpoint = f"{api_url}/data/selectHisData"

        logger.debug(
            "🌐 发起API请求 - URL: %s, payload: %s",
            endpoint,
            {
                "objectCodes数量": len(payload.get("objectCodes", [])),
                "dataCodes数量": len(payload.get("dataCodes", [])),
                "时间范围": f"{payload.get('startTime')} - {payload.get('endTime')}",
            },
        )

        try:
            response = requests.post(  # type: ignore[union-attr]
                endpoint,
                json=payload,
                timeout=5.0,
            )

            logger.debug(
                "📥 API响应 - URL: %s, 状态码: %d, 响应时间: %.2fs",
                endpoint,
                response.status_code,
                response.elapsed.total_seconds(),
            )

            if response.status_code != 200:
                logger.error(
                    "❌ API请求失败 - URL: %s, 状态码: %d, 响应内容: %s",
                    endpoint,
                    response.status_code,
                    response.text[:200],
                )
                return None

            result = response.json()
            data = result.get("data", [])

            if not data:
                logger.warning("⚠️ API返回空数据 - URL: %s, 完整响应: %s", endpoint, result)
                return None

            logger.info("✅ API请求成功 - URL: %s, 返回数据条数: %d", endpoint, len(data))
            return data

        except requests.Timeout:  # type: ignore[attr-defined]
            logger.error(
                "❌ API请求超时(>5s) - URL: %s, " "可能原因: 1) 网络延迟 2) 站点服务响应慢 3) 数据量过大",
                endpoint,
            )
            return None
        except requests.ConnectionError as exc:  # type: ignore[attr-defined]
            logger.error(
                "❌ API连接失败 - URL: %s, 错误: %s, " "可能原因: 1) 站点IP不可达 2) 端口9898未开放 3) 网络故障",
                endpoint,
                str(exc),
            )
            return None
        except requests.RequestException as exc:  # type: ignore[attr-defined]
            logger.error(
                "❌ API请求异常 - URL: %s, 错误类型: %s, 错误信息: %s",
                endpoint,
                type(exc).__name__,
                str(exc),
            )
            return None
        except Exception as exc:
            logger.error(
                "❌ 数据处理异常 - URL: %s, 错误类型: %s, 错误信息: %s",
                endpoint,
                type(exc).__name__,
                str(exc),
            )
            return None

    def _aggregate_power_from_data(self, data: List[Dict[str, Any]]) -> Optional[float]:
        """计算数据中的功率总和"""
        total_power = 0.0
        valid_count = 0

        for item in data:
            values = item.get("values", [])
            if not values:
                continue
            parsed = self._safe_float(values[-1].get("value"))
            if parsed is None:
                continue
            total_power += parsed
            valid_count += 1

        return total_power if valid_count > 0 else None

    def _safe_float(self, value: Any) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):  # pragma: no cover - 非数字字符串
            logger.warning("无法转换功率值: %s", value)
            return None

    def _get_jieneng_config(
        self, line_code: str, station_name: str
    ) -> Optional[Dict[str, Any]]:
        """从config_electricity.py获取站点的节能配置

        注意：这里应该使用data_codes和object_codes数组来获取所有设备的能耗数据，
        而不是jienengfeijieneng节点（该节点仅用于获取节能状态）
        """
        try:
            from config_electricity import line_configs

            line_config = line_configs.get(line_code)
            if not line_config:
                return None

            station_config = line_config.get(station_name)
            if not station_config:
                return None

            # 使用data_codes和object_codes数组，而不是jienengfeijieneng节点
            # 这样可以与导出功能保持一致，获取所有设备的实时功率
            data_codes = station_config.get("data_codes", [])
            object_codes = station_config.get("object_codes", [])

            if not data_codes or not object_codes:
                logger.warning(
                    "站点 %s (线路 %s) 缺少data_codes或object_codes配置", station_name, line_code
                )
                return None

            return {"data_codes": data_codes, "object_codes": object_codes}

        except Exception as exc:
            logger.error("获取节能配置失败: %s", exc)
            return None

    async def get_multiple_stations_power(
        self, stations: List[Dict[str, Any]]
    ) -> Dict[str, Optional[float]]:
        """批量获取多个站点的实时功率"""
        tasks = [self.get_station_realtime_power(station) for station in stations]
        station_names = [station.get("name") for station in stations]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        power_map: Dict[str, Optional[float]] = {}
        for station_name, result in zip(station_names, results):
            power_map[station_name] = (
                result if isinstance(result, (int, float)) else None
            )
        return power_map

    def _resolve_station_config(
        self, station: Dict[str, Any]
    ) -> Optional[Tuple[str, List[str], List[str], List[Dict[str, Any]]]]:
        """解析站点配置，返回 (api_url, object_codes, data_codes, data_list)"""
        station_ip = station.get("ip")
        line_code = station.get("line")
        station_name = station.get("name")

        if not station_ip:
            return None

        try:
            from config_electricity import line_configs
        except Exception as exc:  # pragma: no cover - 配置导入异常
            logger.error("导入配置失败: %s", exc)
            return None

        line_config = line_configs.get(line_code)
        if not line_config:
            return None

        station_config = line_config.get(station_name)
        if not station_config:
            return None

        object_codes = station_config.get("object_codes", [])
        data_codes = station_config.get("data_codes", [])
        data_list = station_config.get("data_list", [])
        if not object_codes or not data_codes:
            return None

        return (
            self._get_station_api_url(station_ip),
            object_codes,
            data_codes,
            data_list,
        )

    async def get_station_device_powers(
        self, station: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """获取站点所有设备的实时功率"""
        if not self.requests_available:
            return []

        resolved = self._resolve_station_config(station)
        if not resolved:
            return []

        api_url, object_codes, data_codes, data_list = resolved
        object_code = object_codes[0] if object_codes else None
        if not object_code:
            return []

        max_queries = min(len(data_codes), 20)
        device_powers: List[Dict[str, Any]] = []

        for index, data_code in enumerate(data_codes[:max_queries]):
            device_name = self._build_device_name(index, data_list)
            power = await self._query_recent_power(api_url, [object_code], [data_code])
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

    def _build_device_name(self, index: int, data_list: List[Dict[str, Any]]) -> str:
        default_name = f"设备{index + 1}"
        if index < len(data_list):
            device_info = data_list[index]
            return device_info.get("p3", default_name)
        return default_name
