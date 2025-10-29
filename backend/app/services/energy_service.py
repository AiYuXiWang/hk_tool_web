"""
能源管理服务

提供能源数据的业务逻辑处理，包括实时监控、历史分析、KPI计算等。
"""

import asyncio
import os
import random
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from backend.app.config.electricity_config import ElectricityConfig
from backend.app.services.base import CacheableService, service_method

# 添加项目根目录到路径以导入 control_service
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from control_service import PlatformAPIService

    PLATFORM_API_AVAILABLE = True
except ImportError:
    PLATFORM_API_AVAILABLE = False


class EnergyService(CacheableService):
    """能源管理服务"""

    def __init__(self):
        super().__init__()
        self.electricity_config = ElectricityConfig()
        # 集成平台API服务用于查询真实数据（可通过环境变量控制开关）
        enable_real_data = os.environ.get("ENABLE_REAL_ENERGY", "0") == "1"
        if PLATFORM_API_AVAILABLE and enable_real_data:
            try:
                self.platform_api = PlatformAPIService()
                self.logger.info("PlatformAPIService 已成功集成")
            except Exception as exc:
                self.logger.warning(f"PlatformAPIService 初始化失败: {exc}")
                self.platform_api = None
        else:
            self.platform_api = None
            reason = (
                "PlatformAPIService 不可用"
                if not PLATFORM_API_AVAILABLE
                else "未开启 ENABLE_REAL_ENERGY，使用模拟数据"
            )
            self.logger.warning(reason)

    @service_method(cache_timeout=60)
    async def get_energy_overview(
        self, station_ip: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取能源总览数据

        Args:
            station_ip: 可选的站点IP，如果提供则只返回该站点数据

        Returns:
            包含总能耗、当前功率、能效比、节能收益等KPI指标的字典
        """
        try:
            # 获取站点列表
            stations = await self._get_stations(station_ip)
            if not stations:
                raise ValueError("未找到站点配置")

            # 并行获取各站点数据
            tasks = [self._get_station_overview_data(station) for station in stations]
            station_data_list = await asyncio.gather(*tasks, return_exceptions=True)

            # 过滤异常结果并汇总数据
            valid_data = [
                data for data in station_data_list if not isinstance(data, Exception)
            ]

            if not valid_data:
                raise ValueError("无法获取任何站点数据")

            # 计算总览指标
            overview = await self._calculate_overview_metrics(valid_data, len(stations))

            return self.format_response(overview, "能源总览数据获取成功")

        except Exception as e:
            self.log_error("get_energy_overview", e, station_ip=station_ip)
            return self.format_error_response(f"获取能源总览数据失败: {str(e)}")

    @service_method(cache_timeout=30)
    async def get_realtime_data(
        self, line: Optional[str] = None, station_ip: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取实时能耗监控数据

        Args:
            line: 地铁线路过滤条件
            station_ip: 站点IP过滤条件

        Returns:
            实时监控数据，包括功率曲线、站点对比等
        """
        try:
            # 获取站点列表
            stations = await self._get_stations(station_ip, line)

            if not stations:
                return self.format_response(
                    {
                        "data": [],
                        "timestamps": [],
                        "total_power": 0,
                        "chart_data": [],
                        "station_comparison": [],
                    },
                    "未找到匹配的站点",
                )

            # 并行获取实时数据
            tasks = [self._get_station_realtime_data(station) for station in stations]
            station_data_list = await asyncio.gather(*tasks, return_exceptions=True)

            # 过滤异常结果
            valid_data = [
                data for data in station_data_list if not isinstance(data, Exception)
            ]

            # 生成实时监控数据
            realtime_data = await self._generate_realtime_response(valid_data)

            return self.format_response(realtime_data, "实时数据获取成功")

        except Exception as e:
            self.log_error("get_realtime_data", e, line=line, station_ip=station_ip)
            return self.format_error_response(f"获取实时数据失败: {str(e)}")

    @service_method(cache_timeout=300)
    async def get_historical_trends(
        self,
        start_date: str,
        end_date: str,
        station_ip: Optional[str] = None,
        granularity: str = "daily",
    ) -> Dict[str, Any]:
        """
        获取历史趋势数据

        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            station_ip: 可选的站点IP过滤
            granularity: 数据粒度 (hourly/daily/monthly)

        Returns:
            历史趋势数据
        """
        try:
            # 验证日期格式
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

            if start_dt > end_dt:
                raise ValueError("开始日期不能晚于结束日期")

            # 获取站点列表
            stations = await self._get_stations(station_ip)

            # 生成历史趋势数据
            trends_data = await self._generate_historical_trends(
                stations, start_dt, end_dt, granularity
            )

            return self.format_response(trends_data, "历史趋势数据获取成功")

        except ValueError as e:
            return self.format_error_response(str(e), 400)
        except Exception as e:
            self.log_error("get_historical_trends", e)
            return self.format_error_response(f"获取历史趋势数据失败: {str(e)}")

    @service_method(cache_timeout=120)
    async def get_kpi_metrics(self, station_ip: Optional[str] = None) -> Dict[str, Any]:
        """
        获取KPI指标数据

        Args:
            station_ip: 可选的站点IP过滤

        Returns:
            KPI指标数据
        """
        try:
            stations = await self._get_stations(station_ip)

            # 计算各类KPI指标
            kpi_data = await self._calculate_kpi_metrics(stations)

            return self.format_response(kpi_data, "KPI指标数据获取成功")

        except Exception as e:
            self.log_error("get_kpi_metrics", e, station_ip=station_ip)
            return self.format_error_response(f"获取KPI指标失败: {str(e)}")

    # 私有方法
    async def _get_stations(
        self, station_ip: Optional[str] = None, line: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取站点列表"""
        if station_ip:
            station_config = self.electricity_config.get_station_by_ip(station_ip)
            return [station_config] if station_config else []
        elif line:
            return self.electricity_config.get_stations_by_line(line)
        else:
            return self.electricity_config.get_all_stations()

    async def _get_station_overview_data(
        self, station: Dict[str, Any]
    ) -> Dict[str, Any]:
        """获取单个站点的总览数据"""
        try:
            # 模拟获取站点数据（实际应该调用外部API或数据库）
            devices = self.electricity_config.get_station_devices(station["ip"])
            device_count = len(devices)

            # 基于设备数量计算基础功率
            base_power = device_count * 25 + random.uniform(-10, 10)
            current_power = max(0, base_power + random.uniform(-15, 15))

            # 计算日能耗
            daily_consumption = current_power * 20 + random.uniform(-50, 50)

            return {
                "station_ip": station["ip"],
                "station_name": station["name"],
                "current_power": current_power,
                "daily_consumption": daily_consumption,
                "device_count": device_count,
            }

        except Exception as e:
            self.logger.warning(f"获取站点 {station['ip']} 总览数据失败: {e}")
            raise

    async def _get_station_realtime_data(
        self, station: Dict[str, Any]
    ) -> Dict[str, Any]:
        """获取单个站点的实时数据"""
        try:
            devices = self.electricity_config.get_station_devices(station["ip"])
            device_count = len(devices)
            base_power = device_count * 25 + random.uniform(-10, 10)
            current_power = max(0, base_power + random.uniform(-15, 15))

            # 生成24小时功率曲线
            hourly_data = []
            now = datetime.now()

            for i in range(24):
                hour = (now - timedelta(hours=23 - i)).hour
                if 6 <= hour <= 22:  # 白天功率较高
                    power = base_power * (0.8 + 0.4 * (1 + 0.1 * (i % 3)))
                else:  # 夜间功率较低
                    power = base_power * (0.5 + 0.3 * (1 + 0.1 * (i % 2)))
                hourly_data.append(round(max(0, power), 1))

            return {
                "station_name": station["name"],
                "station_ip": station["ip"],
                "current_power": round(current_power, 1),
                "device_count": device_count,
                "hourly_data": hourly_data,
            }

        except Exception as e:
            self.logger.warning(f"获取站点 {station['ip']} 实时数据失败: {e}")
            raise

    async def _calculate_overview_metrics(
        self, station_data_list: List[Dict[str, Any]], total_stations: int
    ) -> Dict[str, Any]:
        """计算总览指标"""
        total_consumption = sum(data["daily_consumption"] for data in station_data_list)
        current_power = sum(data["current_power"] for data in station_data_list)

        # 计算趋势数据（模拟）
        yesterday_consumption = total_consumption * 0.95
        last_hour_power = current_power * 1.02

        # 计算能效比
        efficiency_ratio = round(3.5 + (total_consumption / 10000) * 0.1, 1)

        # 计算节能收益
        baseline_consumption = total_consumption * 1.15
        energy_saved = baseline_consumption - total_consumption
        cost_saving = energy_saved * 1.5  # 按1.5元/kWh计算

        return {
            "total_consumption": round(total_consumption, 1),
            "current_power": round(current_power, 1),
            "efficiency_ratio": efficiency_ratio,
            "cost_saving": round(cost_saving, 0),
            "trends": {
                "consumption_trend": {
                    "direction": "positive"
                    if total_consumption > yesterday_consumption
                    else "negative",
                    "percentage": round(
                        abs(
                            (total_consumption - yesterday_consumption)
                            / yesterday_consumption
                            * 100
                        ),
                        1,
                    ),
                },
                "power_trend": {
                    "direction": "negative"
                    if current_power < last_hour_power
                    else "positive",
                    "percentage": round(
                        abs((current_power - last_hour_power) / last_hour_power * 100),
                        1,
                    ),
                },
                "efficiency_trend": {"direction": "positive", "percentage": 3.5},
            },
            "station_count": total_stations,
            "update_time": datetime.now().isoformat(),
        }

    async def _generate_realtime_response(
        self, station_data_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """生成实时监控响应数据"""
        if not station_data_list:
            return {
                "data": [],
                "timestamps": [],
                "total_power": 0,
                "chart_data": [],
                "station_comparison": [],
            }

        # 生成时间戳
        now = datetime.now()
        timestamps = []
        for i in range(24):
            time_point = now - timedelta(hours=23 - i)
            timestamps.append(time_point.strftime("%H:%M"))

        # 计算总功率
        total_current_power = sum(item["current_power"] for item in station_data_list)

        # 生成24小时图表数据
        chart_data = []
        for i in range(24):
            time_point = now - timedelta(hours=23 - i)
            power_sum = sum(
                item["hourly_data"][i]
                for item in station_data_list
                if len(item["hourly_data"]) > i
            )
            chart_data.append(
                {
                    "time": time_point.strftime("%H:%M"),
                    "power": round(power_sum, 1),
                    "energy": round(power_sum * 0.8, 1),
                }
            )

        # 生成站点对比数据
        station_comparison = []
        for item in station_data_list[:8]:  # 最多显示8个站点
            station_comparison.append(
                {
                    "station": item["station_name"],
                    "energy": round(
                        item["current_power"] * 0.8 + random.uniform(-5, 5), 1
                    ),
                    "device_count": item["device_count"],
                }
            )

        return {
            "data": station_data_list,
            "timestamps": timestamps,
            "total_power": round(total_current_power, 1),
            "chart_data": chart_data,
            "station_comparison": station_comparison,
        }

    async def _generate_historical_trends(
        self,
        stations: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime,
        granularity: str,
    ) -> Dict[str, Any]:
        """生成历史趋势数据"""
        # 根据粒度计算时间点
        time_points = []
        current_date = start_date

        if granularity == "hourly":
            while current_date <= end_date:
                time_points.append(current_date)
                current_date += timedelta(hours=1)
        elif granularity == "daily":
            while current_date <= end_date:
                time_points.append(current_date)
                current_date += timedelta(days=1)
        elif granularity == "monthly":
            while current_date <= end_date:
                time_points.append(current_date)
                # 简化处理，每月按30天计算
                current_date += timedelta(days=30)

        # 生成模拟数据
        trends_data = []
        base_consumption = len(stations) * 500  # 基础能耗

        for i, time_point in enumerate(time_points):
            # 模拟季节性变化
            seasonal_factor = 1 + 0.2 * (1 + 0.5 * (time_point.month % 12 / 12))

            # 模拟随机波动
            random_factor = 1 + random.uniform(-0.1, 0.1)

            consumption = base_consumption * seasonal_factor * random_factor

            trends_data.append(
                {
                    "time": time_point.strftime(
                        "%Y-%m-%d %H:%M" if granularity == "hourly" else "%Y-%m-%d"
                    ),
                    "consumption": round(consumption, 1),
                    "power": round(consumption / 20, 1),  # 假设平均功率
                    "efficiency": round(3.5 + random.uniform(-0.5, 0.5), 2),
                }
            )

        return {
            "trends": trends_data,
            "summary": {
                "total_consumption": sum(item["consumption"] for item in trends_data),
                "avg_power": sum(item["power"] for item in trends_data)
                / len(trends_data),
                "avg_efficiency": sum(item["efficiency"] for item in trends_data)
                / len(trends_data),
            },
            "granularity": granularity,
            "period": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
            },
        }

    async def _calculate_kpi_metrics(
        self, stations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """计算KPI指标"""
        station_count = len(stations)

        # 模拟KPI计算
        kpi_data = {
            "energy_efficiency": {
                "value": round(3.5 + random.uniform(-0.5, 0.5), 2),
                "unit": "kWh/m²",
                "trend": "positive",
                "target": 4.0,
            },
            "cost_saving": {
                "value": round(station_count * 1500 + random.uniform(-500, 500), 0),
                "unit": "元",
                "trend": "positive",
                "target": station_count * 2000,
            },
            "carbon_reduction": {
                "value": round(station_count * 2.5 + random.uniform(-0.5, 0.5), 1),
                "unit": "吨CO2",
                "trend": "positive",
                "target": station_count * 3.0,
            },
            "equipment_utilization": {
                "value": round(85 + random.uniform(-10, 10), 1),
                "unit": "%",
                "trend": "stable",
                "target": 90.0,
            },
        }

        return kpi_data

    # ==================== 真实数据查询辅助方法 ====================

    def _parse_ct_ratio(self, ct_str: str) -> float:
        """
        解析CT变比字符串

        Args:
            ct_str: CT变比字符串，如 "400/5" 或 "650/5"

        Returns:
            float: CT变比值，如 80.0 或 130.0
        """
        try:
            if "/" in ct_str:
                numerator, denominator = ct_str.split("/")
                return float(numerator) / float(denominator)
            return float(ct_str)
        except Exception as e:
            self.logger.warning(f"解析CT变比失败: {ct_str}, 错误: {e}")
            return 1.0

    def _parse_power(self, power_str: str) -> float:
        """
        解析功率字符串

        Args:
            power_str: 功率字符串，如 "137KW" 或 "18.5KW"

        Returns:
            float: 功率值（kW），如 137.0 或 18.5
        """
        try:
            # 移除单位和空格
            power_str = power_str.upper().replace("KW", "").replace("K", "").strip()
            return float(power_str)
        except Exception as e:
            self.logger.warning(f"解析功率失败: {power_str}, 错误: {e}")
            return 0.0

    def _classify_device(self, device_name: str) -> str:
        """
        根据设备名称自动分类

        Args:
            device_name: 设备名称，如 "冷机LS01电表" 或 "冷冻水泵LD01电表"

        Returns:
            str: 设备分类，如 "冷机系统" 或 "水泵系统"
        """
        name_lower = device_name.lower()

        if "冷机" in device_name or "ls" in name_lower:
            return "冷机系统"
        elif "水泵" in device_name or "ld" in name_lower or "lq" in name_lower:
            if "冷冻" in device_name or "ld" in name_lower:
                return "水泵系统"
            elif "冷却" in device_name or "lq" in name_lower:
                return "水泵系统"
            else:
                return "水泵系统"
        elif "冷却塔" in device_name or "lqt" in name_lower:
            return "冷却塔"
        elif "风机" in device_name or "zsf" in name_lower or "paf" in name_lower:
            return "通风系统"
        elif "照明" in device_name or "light" in name_lower:
            return "照明系统"
        else:
            return "其他设备"

    def _simulate_station_power(self, station: Dict[str, Any]) -> float:
        """根据设备数量生成模拟功率"""
        station_ip = station.get("ip", "")
        devices = self.electricity_config.get_station_devices(station_ip)
        device_count = len(devices) if devices else 5
        base_power = device_count * 25 + random.uniform(-10, 10)
        return max(0, base_power + random.uniform(-15, 15))

    def _aggregate_power_from_results(
        self,
        station: Dict[str, Any],
        station_ip: str,
        point_pairs: list,
        results: list,
    ) -> tuple:
        """从查询结果中聚合功率数据"""
        total_power = 0.0
        success_count = 0

        for (object_code, data_code), result in zip(point_pairs, results):
            if isinstance(result, Exception):
                self.logger.warning(
                    "站点 %s 请求点位 object=%s data=%s 失败: %s",
                    station.get("name", station_ip),
                    object_code,
                    data_code,
                    result,
                )
                continue

            if isinstance(result, dict):
                data = result.get("data", [])
                if data:
                    point_value = float(data[0].get("value", 0))
                    total_power += max(point_value, 0)
                    success_count += 1

        return total_power, success_count

    async def _query_station_realtime_power(self, station: Dict[str, Any]) -> float:
        """
        查询站点实时总功率（真实数据）

        Args:
            station: 站点配置信息

        Returns:
            float: 站点总功率（kW），查询失败返回模拟值
        """
        if not self.platform_api:
            # 平台API不可用，使用模拟数据
            return self._simulate_station_power(station)

        station_ip = station.get("ip", "")
        if not station_ip:
            self.logger.warning("站点缺少IP配置，使用模拟数据")
            return self._simulate_station_power(station)

        jnfjn_config = station.get("jienengfeijieneng", {})
        object_codes = jnfjn_config.get("object_codes", [])
        data_codes = jnfjn_config.get("data_codes", [])

        if not object_codes or not data_codes:
            self.logger.warning(
                "站点 %s 缺少节能/非节能点位配置，使用模拟数据",
                station.get("name", station_ip),
            )
            return self._simulate_station_power(station)

        point_pairs = [(oc, dc) for oc in object_codes for dc in data_codes]

        try:
            tasks = [
                self.platform_api.query_realtime_value(
                    object_code=object_code,
                    data_code=data_code,
                    station_ip=station_ip,
                )
                for object_code, data_code in point_pairs
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as exc:
            self.logger.error(
                "查询站点 %s 功率异常: %s",
                station.get("name", "unknown"),
                exc,
            )
            return self._simulate_station_power(station)

        total_power, success_count = self._aggregate_power_from_results(
            station, station_ip, point_pairs, results
        )

        if success_count > 0 and total_power > 0:
            self.logger.info(
                "成功查询站点 %s 实时功率: %.2fkW (成功 %s/%s 个点位)",
                station.get("name", station_ip),
                total_power,
                success_count,
                len(point_pairs),
            )
            return total_power

        self.logger.warning(
            "站点 %s 实时功率点位查询失败，使用模拟数据",
            station.get("name", station_ip),
        )
        return self._simulate_station_power(station)
