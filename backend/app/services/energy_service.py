"""
能源管理服务

提供能源数据的业务逻辑处理，包括实时监控、历史分析、KPI计算等。
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from backend.app.config.electricity_config import ElectricityConfig
from backend.app.services.base import CacheableService, service_method
from backend.app.services.realtime_energy_service import RealtimeEnergyService


class EnergyService(CacheableService):
    """能源管理服务"""

    def __init__(self):
        super().__init__()
        self.electricity_config = ElectricityConfig()
        self.realtime_service = RealtimeEnergyService()

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
        station_name = station.get("name", "未知站点")

        try:
            # 获取设备列表
            devices = self.electricity_config.get_station_devices(station["ip"])
            device_count = len(devices)

            self.logger.info("📊 [%s] 开始获取总览数据 - 设备数量: %d", station_name, device_count)

            # 从平台API获取实时功率（取消模拟数据fallback）
            current_power = await self.realtime_service.get_station_realtime_power(
                station
            )

            data_source = "real"
            error_detail: Optional[str] = None

            # 如果获取失败，记录详细错误并返回0
            if current_power is None:
                error_detail = (
                    "实时功率获取失败。请检查: " "1) 站点节能数据配置是否正确 " "2) 站点API是否可访问 " "3) 时间范围内是否有数据"
                )
                self.logger.error("❌ [%s] %s", station_name, error_detail)
                current_power = 0.0
                data_source = "unavailable"

            # 计算日能耗：使用与export_service相同的逻辑
            # 获取当天的实际能耗（从当天00:00到现在的电表读数差值）
            now = datetime.now()
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

            daily_consumption = (
                await self.realtime_service.get_station_energy_consumption(
                    station, start_of_day, now
                )
            )

            # 如果无法获取真实能耗，使用功率估算（向后兼容）
            if daily_consumption is None:
                daily_consumption = current_power * 20  # 假设平均运行20小时/天
                if data_source == "real":
                    data_source = "partial"  # 有功率但无能耗数据
                    self.logger.warning(
                        "⚠️ [%s] 能耗数据获取失败，使用功率估算: %.2f kWh",
                        station_name,
                        daily_consumption,
                    )
            else:
                self.logger.info(
                    "✅ [%s] 成功获取真实日能耗: %.2f kWh (使用电表读数计算)",
                    station_name,
                    daily_consumption,
                )

            if data_source == "real":
                self.logger.info(
                    "✅ [%s] 总览数据获取成功 - 当前功率: %.2f kW, 日能耗: %.2f kWh",
                    station_name,
                    current_power,
                    daily_consumption,
                )
            else:
                self.logger.warning(
                    "⚠️ [%s] 返回部分/默认总览数据 - 当前功率: %.2f kW, 日能耗: %.2f kWh",
                    station_name,
                    current_power,
                    daily_consumption,
                )

            return {
                "station_ip": station["ip"],
                "station_name": station["name"],
                "current_power": current_power,
                "daily_consumption": daily_consumption,
                "device_count": device_count,
                "data_source": data_source,
                "error": error_detail,
            }

        except Exception as e:
            self.logger.error(
                "❌ [%s] 获取总览数据失败: %s (类型: %s)", station_name, str(e), type(e).__name__
            )
            raise

    async def _get_station_realtime_data(
        self, station: Dict[str, Any]
    ) -> Dict[str, Any]:
        """获取单个站点的实时数据"""
        station_name = station.get("name", "未知站点")

        try:
            devices = self.electricity_config.get_station_devices(station["ip"])
            device_count = len(devices)

            self.logger.info("📈 [%s] 开始获取实时数据 - 设备数量: %d", station_name, device_count)

            # 从平台API获取实时功率（取消模拟数据fallback）
            current_power = await self.realtime_service.get_station_realtime_power(
                station
            )

            data_source = "real"
            error_detail: Optional[str] = None

            if current_power is None:
                error_detail = "实时功率获取失败。请检查: " "1) 节能数据配置 2) 站点API可达性 3) 是否存在实时数据"
                self.logger.error("❌ [%s] %s", station_name, error_detail)
                current_power = 0.0
                data_source = "unavailable"

            # 生成24小时功率曲线（基于当前功率估算历史曲线）
            hourly_data: List[float] = []
            now = datetime.now()

            if data_source == "real":
                base_power = current_power
                for i in range(24):
                    hour = (now - timedelta(hours=23 - i)).hour
                    if 6 <= hour <= 22:  # 白天功率较高
                        power = base_power * (0.8 + 0.4 * (1 + 0.1 * (i % 3)))
                    else:  # 夜间功率较低
                        power = base_power * (0.5 + 0.3 * (1 + 0.1 * (i % 2)))
                    hourly_data.append(round(max(0, power), 1))
            else:
                hourly_data = [0.0 for _ in range(24)]

            if data_source == "real":
                self.logger.info(
                    "✅ [%s] 实时数据获取成功 - 当前功率: %.2f kW", station_name, current_power
                )
            else:
                self.logger.warning("⚠️ [%s] 返回默认实时数据 - 当前功率: 0 kW", station_name)

            return {
                "station_name": station["name"],
                "station_ip": station["ip"],
                "current_power": round(current_power, 1),
                "device_count": device_count,
                "hourly_data": hourly_data,
                "data_source": data_source,
                "error": error_detail,
            }

        except Exception as e:
            self.logger.error(
                "❌ [%s] 获取实时数据失败: %s (类型: %s)", station_name, str(e), type(e).__name__
            )
            raise

    async def _calculate_overview_metrics(
        self, station_data_list: List[Dict[str, Any]], total_stations: int
    ) -> Dict[str, Any]:
        """计算总览指标"""
        total_consumption = sum(data["daily_consumption"] for data in station_data_list)
        current_power = sum(data["current_power"] for data in station_data_list)

        real_station_count = sum(
            1 for data in station_data_list if data.get("data_source") == "real"
        )
        unavailable_stations = [
            data
            for data in station_data_list
            if data.get("data_source") == "unavailable"
        ]

        if real_station_count == 0:
            data_source = "unavailable"
        elif unavailable_stations:
            data_source = "partial"
        else:
            data_source = "real"

        # 计算趋势数据（估算）
        yesterday_consumption = total_consumption * 0.95
        last_hour_power = current_power * 1.02

        # 计算能效比
        efficiency_ratio = round(3.5 + (total_consumption / 10000) * 0.1, 1)

        # 计算节能收益
        baseline_consumption = total_consumption * 1.15
        energy_saved = baseline_consumption - total_consumption
        cost_saving = energy_saved * 1.5  # 按1.5元/kWh计算

        self.logger.info(
            "📊 总览指标计算完成 - 总能耗: %.1f kWh, 当前功率: %.1f kW, 可用站点: %d/%d",
            total_consumption,
            current_power,
            real_station_count,
            total_stations,
        )

        if unavailable_stations:
            self.logger.warning(
                "⚠️ 以下站点总览数据不可用: %s",
                ", ".join(item["station_name"] for item in unavailable_stations),
            )

        # 计算趋势百分比，避免除以零
        consumption_percentage = 0.0
        if yesterday_consumption > 0:
            consumption_percentage = round(
                abs(
                    (total_consumption - yesterday_consumption)
                    / yesterday_consumption
                    * 100
                ),
                1,
            )

        power_percentage = 0.0
        if last_hour_power > 0:
            power_percentage = round(
                abs((current_power - last_hour_power) / last_hour_power * 100),
                1,
            )

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
                    "percentage": consumption_percentage,
                },
                "power_trend": {
                    "direction": "negative"
                    if current_power < last_hour_power
                    else "positive",
                    "percentage": power_percentage,
                },
                "efficiency_trend": {"direction": "positive", "percentage": 3.5},
            },
            "station_count": total_stations,
            "available_station_count": real_station_count,
            "update_time": datetime.now().isoformat(),
            "data_source": data_source,
            "unavailable_stations": [
                {
                    "station_name": item["station_name"],
                    "station_ip": item["station_ip"],
                    "reason": item.get("error"),
                }
                for item in unavailable_stations
            ],
        }

    async def _generate_realtime_response(
        self, station_data_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """生成实时监控响应数据"""
        if not station_data_list:
            self.logger.error("❌ 实时数据汇总失败: 所有站点实时功率获取失败，请检查配置或网络状态")
            return {
                "data": [],
                "timestamps": [],
                "total_power": 0,
                "chart_data": [],
                "station_comparison": [],
                "data_source": "unavailable",
            }

        real_station_count = sum(
            1 for item in station_data_list if item.get("data_source") == "real"
        )
        unavailable_stations = [
            item
            for item in station_data_list
            if item.get("data_source") == "unavailable"
        ]

        if real_station_count == 0:
            data_source = "unavailable"
        elif unavailable_stations:
            data_source = "partial"
        else:
            data_source = "real"

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
                    "data_source": item.get("data_source", "unknown"),
                }
            )

        self.logger.info(
            "📈 实时数据汇总完成 - 总功率: %.1f kW, 可用站点: %d/%d",
            total_current_power,
            real_station_count,
            len(station_data_list),
        )

        if unavailable_stations:
            self.logger.warning(
                "⚠️ 以下站点实时数据不可用: %s",
                ", ".join(item["station_name"] for item in unavailable_stations),
            )

        return {
            "data": station_data_list,
            "timestamps": timestamps,
            "total_power": round(total_current_power, 1),
            "chart_data": chart_data,
            "station_comparison": station_comparison,
            "data_source": data_source,
            "available_station_count": real_station_count,
            "unavailable_stations": [
                {
                    "station_name": item["station_name"],
                    "station_ip": item["station_ip"],
                    "reason": item.get("error"),
                }
                for item in unavailable_stations
            ],
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

    async def get_comparison_data(
        self,
        start_time: datetime,
        end_time: datetime,
        station_ip: Optional[str] = None,
        line: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        获取同比环比对比数据

        Args:
            start_time: 当前周期开始时间
            end_time: 当前周期结束时间
            station_ip: 可选的站点IP过滤

        Returns:
            包含同比(yoy)、环比(mom)百分比和当前能耗的字典
        """
        try:
            stations = await self._get_stations(station_ip, line)
            if not stations:
                raise ValueError("未找到站点配置")

            # 计算时间跨度
            time_diff = end_time - start_time

            # 并行获取当前周期、去年同期、上一周期的能耗数据
            current_tasks = [
                self.realtime_service.get_station_energy_consumption(
                    station, start_time, end_time
                )
                for station in stations
            ]

            # 去年同期（同比）
            year_delta = timedelta(days=365)
            yoy_start = start_time - year_delta
            yoy_end = end_time - year_delta
            yoy_tasks = [
                self.realtime_service.get_station_energy_consumption(
                    station, yoy_start, yoy_end
                )
                for station in stations
            ]

            # 上一周期（环比）- 向前推同样的时间跨度
            mom_end = start_time
            mom_start = start_time - time_diff
            mom_tasks = [
                self.realtime_service.get_station_energy_consumption(
                    station, mom_start, mom_end
                )
                for station in stations
            ]

            # 执行所有任务
            current_results = await asyncio.gather(
                *current_tasks, return_exceptions=True
            )
            yoy_results = await asyncio.gather(*yoy_tasks, return_exceptions=True)
            mom_results = await asyncio.gather(*mom_tasks, return_exceptions=True)

            # 过滤有效结果
            current_consumptions = [
                r
                for r in current_results
                if not isinstance(r, Exception) and r is not None
            ]
            yoy_consumptions = [
                r for r in yoy_results if not isinstance(r, Exception) and r is not None
            ]
            mom_consumptions = [
                r for r in mom_results if not isinstance(r, Exception) and r is not None
            ]

            # 计算总能耗
            current_kwh = sum(current_consumptions) if current_consumptions else 0
            yoy_kwh = sum(yoy_consumptions) if yoy_consumptions else 0
            mom_kwh = sum(mom_consumptions) if mom_consumptions else 0

            # 计算百分比变化
            yoy_percent = 0.0
            if yoy_kwh > 0:
                yoy_percent = ((current_kwh - yoy_kwh) / yoy_kwh) * 100

            mom_percent = 0.0
            if mom_kwh > 0:
                mom_percent = ((current_kwh - mom_kwh) / mom_kwh) * 100

            self.logger.info(
                "同比环比数据计算完成 - 当前能耗: %.1f kWh, 同比: %.1f%%, 环比: %.1f%%",
                current_kwh,
                yoy_percent,
                mom_percent,
            )

            return self.format_response(
                {
                    "current_kwh": round(current_kwh, 1),
                    "yoy_percent": round(yoy_percent, 1),
                    "mom_percent": round(mom_percent, 1),
                    "yoy_kwh": round(yoy_kwh, 1),
                    "mom_kwh": round(mom_kwh, 1),
                    "station_count": len(stations),
                    "valid_data_count": len(current_consumptions),
                },
                "同比环比数据获取成功",
            )

        except Exception as e:
            self.log_error("get_comparison_data", e, station_ip=station_ip)
            return self.format_error_response(f"获取同比环比数据失败: {str(e)}")

    async def get_trend_series(
        self,
        start_time: datetime,
        end_time: datetime,
        station_ip: Optional[str] = None,
        line: Optional[str] = None,
    ) -> Dict[str, Any]:
        """获取指定时间范围内的能耗趋势数据"""
        try:
            if start_time >= end_time:
                raise ValueError("开始时间必须早于结束时间")

            stations = await self._get_stations(station_ip, line)
            if not stations:
                raise ValueError("未找到站点配置")

            total_seconds = (end_time - start_time).total_seconds()
            if total_seconds <= 0:
                raise ValueError("时间范围无效")

            if total_seconds <= 48 * 3600:
                step = timedelta(hours=1)
                time_format = "%m-%d %H:%M"
                granularity = "hourly"
            else:
                step = timedelta(days=1)
                time_format = "%Y-%m-%d"
                granularity = "daily"

            timestamps: List[str] = []
            values: List[float] = []
            valid_points = 0

            current_start = start_time
            while current_start < end_time:
                current_end = min(current_start + step, end_time)
                tasks = [
                    self.realtime_service.get_station_energy_consumption(
                        station, current_start, current_end
                    )
                    for station in stations
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                consumptions = [
                    r for r in results if not isinstance(r, Exception) and r is not None
                ]
                total_consumption = sum(consumptions) if consumptions else 0.0
                if consumptions:
                    valid_points += 1

                timestamps.append(current_start.strftime(time_format))
                values.append(round(total_consumption, 1))

                current_start = current_end

            return self.format_response(
                {
                    "timestamps": timestamps,
                    "values": values,
                    "granularity": granularity,
                    "station_count": len(stations),
                    "valid_points": valid_points,
                },
                "趋势数据获取成功",
            )
        except Exception as e:
            self.log_error("get_trend_series", e, station_ip=station_ip, line=line)
            return self.format_error_response(f"获取趋势数据失败: {str(e)}")

    async def get_classification_data(  # noqa: C901
        self,
        start_time: datetime,
        end_time: datetime,
        station_ip: Optional[str] = None,
        line: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        获取按设备分类的能耗数据
        从config_electricity.py中读取设备信息，根据设备名称分类为：冷水机组、冷却塔、水泵、风机
        """
        try:
            if start_time >= end_time:
                raise ValueError("开始时间必须早于结束时间")

            # 获取站点列表
            stations = await self._get_stations(station_ip, line)
            if not stations:
                raise ValueError("未找到站点配置")

            # 分类统计容器
            categories = {
                "冷水机组": 0.0,
                "冷却塔": 0.0,
                "水泵": 0.0,
                "风机": 0.0,
            }

            total_consumption = 0.0
            device_count_by_category = {cat: 0 for cat in categories.keys()}

            # 统计所有站点的设备分类
            for station in stations:
                station_devices = (
                    self.electricity_config.get_station_devices(station["ip"]) or []
                )
                if not station_devices:
                    self.logger.warning(f"站点 {station.get('name')} 没有配置设备")
                    continue

                for device in station_devices:
                    device_type = device.get("type", "其他")
                    mapped_category = self._map_device_category(device_type)
                    if not mapped_category:
                        continue

                    device_count_by_category[mapped_category] += 1

            self.logger.info(
                f"设备分类统计: {device_count_by_category}, 共 {sum(device_count_by_category.values())} 台设备"
            )

            # 获取站点总能耗
            station_tasks = [
                self.realtime_service.get_station_energy_consumption(
                    station, start_time, end_time
                )
                for station in stations
            ]

            results = await asyncio.gather(*station_tasks, return_exceptions=True)

            valid_results = [
                r for r in results if not isinstance(r, Exception) and r is not None
            ]

            if valid_results:
                total_consumption = sum(valid_results)

                # 按设备类型分配能耗（基于设备数量占比）
                total_devices = sum(device_count_by_category.values())
                if total_devices > 0:
                    for category, device_count in device_count_by_category.items():
                        ratio = device_count / total_devices
                        categories[category] = total_consumption * ratio

            # 生成分类项
            items = []
            for category, kwh in categories.items():
                if total_consumption > 0:
                    percentage = round(kwh / total_consumption * 100, 1)
                else:
                    percentage = 0.0
                items.append(
                    {
                        "name": category,
                        "kwh": round(kwh, 1),
                        "percentage": percentage,
                        "device_count": device_count_by_category[category],
                    }
                )

            self.logger.info(
                f"分类能耗统计完成 - 总能耗: {total_consumption:.1f} kWh, 分类数: {len(items)}"
            )

            return self.format_response(
                {
                    "items": items,
                    "total_kwh": round(total_consumption, 1),
                    "station_count": len(stations),
                    "valid_station_count": len(valid_results),
                    "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                },
                "分类能耗数据获取成功",
            )

        except Exception as e:
            self.log_error(
                "get_classification_data",
                e,
                station_ip=station_ip,
                line=line,
            )
            return self.format_error_response(f"获取分类能耗数据失败: {str(e)}")

    def _map_device_category(self, device_type: str) -> Optional[str]:
        """将设备类型映射到分类"""
        mapping = {
            "冷机": "冷水机组",
            "冷却塔": "冷却塔",
            "水泵": "水泵",
            "风机": "风机",
        }
        return mapping.get(device_type)

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
