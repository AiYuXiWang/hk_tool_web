"""
能源驾驶舱API接口
提供实时能耗监测、历史趋势分析、KPI指标、设备状态、同比环比对比、分类分项能耗等数据服务
"""

import logging
import os
import random
import sys
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.app.config.electricity_config import ElectricityConfig  # noqa: E402
from backend.app.core.dependencies import get_energy_service  # noqa: E402
from backend.app.services.energy_service import EnergyService  # noqa: E402

logger = logging.getLogger(__name__)
router = APIRouter()

# 初始化配置
electricity_config = ElectricityConfig()


@router.get("/overview")
async def get_energy_overview(
    x_station_ip: Optional[str] = Header(None, alias="X-Station-Ip"),
    energy_service: EnergyService = Depends(get_energy_service),
):
    """
    获取能源总览数据
    包含总能耗、当前功率、能效比、节能收益等KPI指标
    """
    try:
        result = await energy_service.get_energy_overview(x_station_ip)

        if result.get("success"):
            return {
                "code": 200,
                "message": result.get("message", "success"),
                "data": result.get("data"),
            }
        else:
            status_code = result.get("status_code", 500)
            raise HTTPException(status_code=status_code, detail=result.get("message"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取能源总览数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.get("/realtime")
async def get_realtime_data(
    line: Optional[str] = Query(None, description="地铁线路，如M3、M8等"),
    station_ip: Optional[str] = Query(None, description="站点IP"),
    hours: Optional[int] = Query(24, description="时间范围（小时数），默认24小时", ge=1, le=72),
    x_station_ip: Optional[str] = Header(None, alias="X-Station-Ip"),
    energy_service: EnergyService = Depends(get_energy_service),
):
    """
    获取实时能耗监控数据
    支持按线路或站点过滤，支持自定义时间范围（1-72小时）
    返回格式: { series: [{ name, points }], timestamps: [] }
    """
    try:
        # 确定站点IP
        target_station_ip = station_ip or x_station_ip

        # 使用 energy_service 获取实时数据
        result = await energy_service.get_realtime_data(line, target_station_ip)

        if not result.get("success"):
            return {
                "series": [],
                "timestamps": [],
                "update_time": datetime.now().isoformat(),
                "time_range_hours": hours,
            }

        data = result.get("data", {})

        # 转换数据格式以匹配前端期望的格式
        station_data_list = data.get("data", [])
        timestamps = data.get("timestamps", [])

        # 根据hours参数决定返回多少小时的数据
        data_points = min(hours, len(timestamps))
        if len(timestamps) > data_points:
            timestamps = timestamps[-data_points:]

        # 为每个站点生成一条曲线
        series = []
        for station_data in station_data_list[:5]:  # 最多显示5个站点的曲线
            hourly_data = station_data.get("hourly_data", [])

            # 根据hours参数截取相应长度的数据
            if len(hourly_data) > data_points:
                hourly_data = hourly_data[-data_points:]

            series.append(
                {
                    "name": station_data.get("station_name", "未知站点"),
                    "points": hourly_data,
                }
            )

        return {
            "series": series,
            "timestamps": timestamps[-data_points:],
            "update_time": datetime.now().isoformat(),
            "time_range_hours": hours,
        }

    except Exception as e:
        logger.error(f"获取实时数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取实时数据失败: {str(e)}")


@router.get("/history")
async def get_history_data(
    time_range: str = Query("24h", description="时间范围: 24h, 7d, 30d, 90d"),
    line: Optional[str] = Query(None, description="地铁线路，如M3、M8等"),
    x_station_ip: Optional[str] = Header(None, alias="X-Station-Ip"),
):
    """
    获取历史数据趋势分析
    """
    try:
        import random

        # 简化实现，直接生成模拟数据
        station_count = 3  # 默认站点数量

        now = datetime.now()

        # 根据时间范围生成数据
        if time_range == "24h":
            # 24小时数据，每小时一个点
            data_points = []
            for i in range(24):
                time_point = now - timedelta(hours=23 - i)
                power = sum(random.uniform(400, 700) for _ in range(station_count))
                energy = power * random.uniform(0.9, 1.1)
                efficiency = random.uniform(0.75, 0.95)
                data_points.append(
                    {
                        "time": time_point.strftime("%H:%M"),
                        "datetime": time_point.isoformat(),
                        "power": round(power, 1),
                        "energy": round(energy, 1),
                        "efficiency": round(efficiency * 100, 1),
                    }
                )

        elif time_range == "7d":
            # 7天数据，每天一个点
            data_points = []
            for i in range(7):
                time_point = now - timedelta(days=6 - i)
                power = sum(random.uniform(500, 800) for _ in range(station_count))
                energy = power * 24 * random.uniform(0.8, 1.2)  # 日能耗
                efficiency = random.uniform(0.8, 0.95)
                data_points.append(
                    {
                        "time": time_point.strftime("%m-%d"),
                        "datetime": time_point.isoformat(),
                        "power": round(power, 1),
                        "energy": round(energy, 1),
                        "efficiency": round(efficiency * 100, 1),
                    }
                )

        elif time_range == "30d":
            # 30天数据，每天一个点
            data_points = []
            for i in range(30):
                time_point = now - timedelta(days=29 - i)
                power = sum(random.uniform(450, 750) for _ in range(station_count))
                energy = power * 24 * random.uniform(0.85, 1.15)
                efficiency = random.uniform(0.78, 0.92)
                data_points.append(
                    {
                        "time": time_point.strftime("%m-%d"),
                        "datetime": time_point.isoformat(),
                        "power": round(power, 1),
                        "energy": round(energy, 1),
                        "efficiency": round(efficiency * 100, 1),
                    }
                )

        elif time_range == "90d":
            # 90天数据，每3天一个点
            data_points = []
            for i in range(30):  # 30个点，每个点代表3天
                time_point = now - timedelta(days=89 - i * 3)
                power = sum(random.uniform(400, 800) for _ in range(station_count))
                energy = power * 24 * 3 * random.uniform(0.8, 1.2)  # 3天能耗
                efficiency = random.uniform(0.75, 0.95)
                data_points.append(
                    {
                        "time": time_point.strftime("%m-%d"),
                        "datetime": time_point.isoformat(),
                        "power": round(power, 1),
                        "energy": round(energy, 1),
                        "efficiency": round(efficiency * 100, 1),
                    }
                )

        else:
            # 默认返回24h数据
            data_points = []
            for i in range(24):
                time_point = now - timedelta(hours=23 - i)
                power = sum(random.uniform(400, 700) for _ in range(station_count))
                energy = power * random.uniform(0.9, 1.1)
                efficiency = random.uniform(0.75, 0.95)
                data_points.append(
                    {
                        "time": time_point.strftime("%H:%M"),
                        "datetime": time_point.isoformat(),
                        "power": round(power, 1),
                        "energy": round(energy, 1),
                        "efficiency": round(efficiency * 100, 1),
                    }
                )

        # 计算统计数据
        total_energy = sum(point["energy"] for point in data_points)
        avg_power = sum(point["power"] for point in data_points) / len(data_points)
        avg_efficiency = sum(point["efficiency"] for point in data_points) / len(
            data_points
        )

        # 计算同比数据（模拟）
        energy_change = random.uniform(-15, 25)  # 同比变化百分比
        power_change = random.uniform(-10, 20)
        efficiency_change = random.uniform(-5, 15)

        return {
            "time_range": time_range,
            "data_points": data_points,
            "statistics": {
                "total_energy": round(total_energy, 1),
                "avg_power": round(avg_power, 1),
                "avg_efficiency": round(avg_efficiency, 1),
                "energy_change": round(energy_change, 1),
                "power_change": round(power_change, 1),
                "efficiency_change": round(efficiency_change, 1),
            },
            "total_stations": station_count,
            "update_time": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"获取历史数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取历史数据失败: {str(e)}")


@router.get("/trend")
async def get_trend_data(
    line: Optional[str] = Query(None, description="地铁线路，如M3、M8等"),
    station_ip: Optional[str] = Query(None, description="站点IP"),
    period: str = Query("7d", description="时间周期: 24h, 7d, 30d"),
    x_station_ip: Optional[str] = Header(None, alias="X-Station-Ip"),
):
    """
    获取历史趋势分析数据
    支持不同时间周期的数据查询
    返回格式: { values: [], timestamps: [] }
    """
    try:
        # 确定站点IP
        target_station_ip = station_ip or x_station_ip

        # 获取站点列表
        stations = []
        if target_station_ip:
            station_config = electricity_config.get_station_by_ip(target_station_ip)
            if station_config:
                stations = [station_config]
        elif line:
            stations = electricity_config.get_stations_by_line(line)
        else:
            stations = electricity_config.get_all_stations()

        station_count = len(stations) if stations else 1

        # 解析时间周期
        if period == "24h":
            data_points = 24
            time_format = "%H:00"
            base_value = station_count * 150  # 每站点每小时约150kWh
        elif period == "7d":
            data_points = 7
            time_format = "%m-%d"
            base_value = station_count * 3500  # 每站点每天约3500kWh
        elif period == "30d":
            data_points = 30
            time_format = "%m-%d"
            base_value = station_count * 3500
        else:
            raise HTTPException(status_code=400, detail="不支持的时间周期")

        # 生成时间序列和数据
        now = datetime.now()
        timestamps = []
        values = []

        for i in range(data_points):
            if period == "24h":
                time_point = now - timedelta(hours=data_points - 1 - i)
            else:
                time_point = now - timedelta(days=data_points - 1 - i)

            timestamps.append(time_point.strftime(time_format))

            # 模拟能耗数据，加入随机波动和趋势
            trend_factor = 1.0 - (i / data_points) * 0.1  # 轻微下降趋势（节能效果）
            random_factor = random.uniform(0.85, 1.15)
            value = base_value * trend_factor * random_factor
            values.append(round(value, 1))

        return {
            "values": values,
            "timestamps": timestamps,
            "period": period,
            "station_count": station_count,
            "update_time": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"获取趋势数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取趋势数据失败: {str(e)}")


@router.get("/equipment")
async def get_equipment_status(
    x_station_ip: Optional[str] = Header(None, alias="X-Station-Ip"),
    min_power: Optional[float] = Query(0, description="最小功率阈值(kW)", ge=0),
    max_power: Optional[float] = Query(None, description="最大功率阈值(kW)", ge=0),
):
    """
    获取设备运行状态数据
    支持按功率阈值筛选设备
    """
    try:
        # 导入realtime_energy_service
        from backend.app.services.realtime_energy_service import RealtimeEnergyService

        realtime_service = RealtimeEnergyService()

        # 获取站点列表
        stations = []
        if x_station_ip:
            station_config = electricity_config.get_station_by_ip(x_station_ip)
            if station_config:
                stations = [station_config]
        else:
            stations = electricity_config.get_all_stations()[:5]  # 限制显示前5个站点

        equipment_list = []
        status_summary = {"normal": 0, "warning": 0, "error": 0}

        for station in stations:
            try:
                # 获取站点设备功率数据
                device_powers = await realtime_service.get_station_device_powers(
                    station
                )

                # 如果没有获取到真实数据，使用配置中的设备列表
                if not device_powers:
                    devices = electricity_config.get_station_devices(station["ip"])
                    device_powers = [
                        {
                            "device_name": device.get("name", "未知设备"),
                            "power": device.get("power", 100)
                            * (0.8 + 0.4 * random.random()),
                            "status": "online",
                        }
                        for device in devices[:3]
                    ]

                # 根据功率阈值筛选设备
                filtered_device_powers = []
                for device_data in device_powers:
                    power_w = device_data.get("power", 0)
                    # 检查功率阈值
                    if min_power > 0 and power_w < min_power:
                        continue
                    if max_power and max_power > 0 and power_w > max_power:
                        continue
                    filtered_device_powers.append(device_data)

                if not filtered_device_powers:
                    continue

                for device_data in filtered_device_powers[:3]:  # 每个站点显示前3个设备
                    power = device_data.get("power", 0)
                    device_status = device_data.get("status", "online")

                    # 根据功率和状态判断设备状态
                    if device_status == "offline" or power == 0:
                        status = "error"
                        status_text = "设备离线"
                    elif power < 50:  # 功率过低可能表示效率问题
                        status = "warning"
                        status_text = "效率偏低"
                    else:
                        status = "normal"
                        status_text = "正常运行"

                    status_summary[status] += 1

                    # 计算效率（基于功率的估算）
                    efficiency = min(100, 75 + (power / 10))

                    equipment_list.append(
                        {
                            "id": f"{station['ip']}_{device_data['device_name']}",
                            "name": device_data["device_name"],
                            "location": station["name"],
                            "power": round(power, 1),
                            "efficiency": round(efficiency, 1),
                            "status": status,
                            "status_text": status_text,
                        }
                    )

            except Exception as e:
                logger.warning(f"获取站点 {station['ip']} 设备状态失败: {e}")
                continue

        return {
            "equipment_list": equipment_list,
            "status_summary": status_summary,
            "update_time": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"获取设备状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取设备状态失败: {str(e)}")


@router.get("/suggestions")
async def get_optimization_suggestions(
    x_station_ip: Optional[str] = Header(None, alias="X-Station-Ip")
):
    """
    获取节能优化建议
    基于AI分析提供智能建议
    """
    try:
        suggestions = [
            {
                "id": 1,
                "title": "冷机运行时间优化",
                "description": "建议在非高峰时段降低冷机运行功率，根据客流量动态调节",
                "priority": "high",
                "priority_text": "高优先级",
                "energy_saving": 2500,
                "cost_saving": 3750,
                "implementation_difficulty": "中等",
                "payback_period": "3个月",
            },
            {
                "id": 2,
                "title": "水泵变频调节优化",
                "description": "根据负荷需求实时调整水泵频率，提高系统整体效率",
                "priority": "medium",
                "priority_text": "中优先级",
                "energy_saving": 1200,
                "cost_saving": 1800,
                "implementation_difficulty": "简单",
                "payback_period": "2个月",
            },
            {
                "id": 3,
                "title": "照明系统智能控制",
                "description": "基于人流密度和自然光照度自动调节照明亮度",
                "priority": "medium",
                "priority_text": "中优先级",
                "energy_saving": 800,
                "cost_saving": 1200,
                "implementation_difficulty": "简单",
                "payback_period": "4个月",
            },
            {
                "id": 4,
                "title": "设备预防性维护",
                "description": "建立设备健康度监测，提前发现效率下降问题",
                "priority": "low",
                "priority_text": "低优先级",
                "energy_saving": 500,
                "cost_saving": 750,
                "implementation_difficulty": "复杂",
                "payback_period": "6个月",
            },
        ]

        # 如果指定了站点，可以提供更精准的建议
        if x_station_ip:
            station_config = electricity_config.get_station_by_ip(x_station_ip)
            if station_config:
                # 基于站点特性调整建议
                for suggestion in suggestions:
                    suggestion["target_station"] = station_config["name"]

        return {
            "suggestions": suggestions,
            "total_potential_saving": sum(s["energy_saving"] for s in suggestions),
            "total_cost_saving": sum(s["cost_saving"] for s in suggestions),
            "update_time": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"获取优化建议失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取优化建议失败: {str(e)}")


@router.get("/stations")
async def get_stations(line: Optional[str] = None):
    """获取站点列表"""
    try:
        config = ElectricityConfig()

        if line:
            # 获取指定线路的站点
            stations = config.get_stations_by_line(line)
            return {
                "lines": [line],
                "stations": [
                    {"ip": station["ip"], "name": station["station"]}
                    for station in stations
                ],
            }
        else:
            # 获取所有线路和站点
            all_lines = config.get_all_lines()
            all_stations = config.get_all_stations()
            return {
                "lines": all_lines,
                "stations": [
                    {"ip": station["ip"], "name": station["station"]}
                    for station in all_stations
                ],
            }
    except Exception as e:
        logger.error(f"获取站点列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/station-map")
async def get_station_map_data():
    """
    获取站点地图分布数据
    """
    try:
        stations = electricity_config.get_all_stations()

        station_map_data = []
        for i, station in enumerate(stations[:20]):  # 限制显示前20个站点
            # 模拟站点在地图上的位置
            x = 100 + (i % 8) * 80 + random.randint(-20, 20)
            y = 200 + (i // 8) * 100 + random.randint(-30, 30)

            # 模拟能耗等级
            energy_level = random.choice(["low", "medium", "high"])
            radius = {"low": 6, "medium": 8, "high": 10}[energy_level]

            station_map_data.append(
                {
                    "id": i + 1,
                    "name": station["name"],
                    "ip": station["ip"],
                    "x": x,
                    "y": y,
                    "radius": radius,
                    "energy_level": energy_level,
                    "line": station.get("line", "M3"),
                }
            )

        return {"stations": station_map_data, "update_time": datetime.now().isoformat()}

    except Exception as e:
        logger.error(f"获取站点地图数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取站点地图数据失败: {str(e)}")


@router.get("/report")
async def get_energy_report(
    report_type: str = Query("daily", description="报表类型: daily, weekly, monthly"),
    x_station_ip: Optional[str] = Header(None, alias="X-Station-Ip"),
):
    """
    获取能耗统计报表数据
    """
    try:
        # 根据报表类型生成数据
        if report_type == "daily":
            periods = 7
            time_format = "%m-%d"
            unit = "天"
        elif report_type == "weekly":
            periods = 12
            time_format = "第%W周"
            unit = "周"
        elif report_type == "monthly":
            periods = 12
            time_format = "%m月"
            unit = "月"
        else:
            raise HTTPException(status_code=400, detail="不支持的报表类型")

        # 生成时间序列和数据
        now = datetime.now()
        timestamps = []
        consumption_data = []

        base_consumption = {"daily": 25000, "weekly": 175000, "monthly": 750000}[
            report_type
        ]

        for i in range(periods):
            if report_type == "daily":
                time_point = now - timedelta(days=periods - 1 - i)
                timestamps.append(time_point.strftime(time_format))
            elif report_type == "weekly":
                time_point = now - timedelta(weeks=periods - 1 - i)
                timestamps.append(f"第{time_point.isocalendar()[1]}周")
            else:  # monthly
                time_point = now - timedelta(days=(periods - 1 - i) * 30)
                timestamps.append(time_point.strftime(time_format))

            # 模拟能耗数据，呈现下降趋势（节能效果）
            consumption = (
                base_consumption * (1.1 - 0.02 * i) * (0.9 + 0.2 * (i % 3) / 3)
            )
            consumption_data.append(round(consumption, 0))

        return {
            "timestamps": timestamps,
            "consumption": consumption_data,
            "report_type": report_type,
            "unit": unit,
            "total_consumption": sum(consumption_data),
            "average_consumption": round(
                sum(consumption_data) / len(consumption_data), 0
            ),
            "trend": "下降",  # 节能趋势
            "update_time": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"获取报表数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取报表数据失败: {str(e)}")


@router.get("/kpi")
async def get_kpi_data(
    line: Optional[str] = Query(None, description="地铁线路，如M3、M8等"),
    station_ip: Optional[str] = Query(None, description="站点IP"),
    x_station_ip: Optional[str] = Header(None, alias="X-Station-Ip"),
):
    """
    获取KPI指标数据
    包括：今日总能耗、当前功率、峰值功率、监控车站数
    """
    try:
        # 确定站点IP
        target_station_ip = station_ip or x_station_ip

        # 获取站点列表
        stations = []
        if target_station_ip:
            station_config = electricity_config.get_station_by_ip(target_station_ip)
            if station_config:
                stations = [station_config]
        elif line:
            stations = electricity_config.get_stations_by_line(line)
        else:
            stations = electricity_config.get_all_stations()

        station_count = len(stations)

        # 模拟KPI数据计算
        # 基于站点数量计算基础值
        base_power_per_station = 150  # 每站点基础功率(kW)

        # 当前功率：各站点当前功率之和，加入随机波动
        current_kw = sum(
            base_power_per_station * (0.8 + 0.4 * random.random())
            for _ in range(station_count)
        )
        current_kw = round(current_kw, 1)

        # 峰值功率：当前功率的1.2-1.5倍
        peak_kw = current_kw * random.uniform(1.2, 1.5)
        peak_kw = round(peak_kw, 1)

        # 今日总能耗：根据当前功率估算（假设当前已经运行了部分时间）
        hours_elapsed = datetime.now().hour + datetime.now().minute / 60
        total_kwh_today = current_kw * hours_elapsed * random.uniform(0.8, 1.2)
        total_kwh_today = round(total_kwh_today, 1)

        return {
            "total_kwh_today": total_kwh_today,
            "current_kw": current_kw,
            "peak_kw": peak_kw,
            "station_count": station_count,
            "update_time": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"获取KPI数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取KPI数据失败: {str(e)}")


@router.get("/compare")
async def get_compare_data(
    line: Optional[str] = Query(None, description="地铁线路，如M3、M8等"),
    station_ip: Optional[str] = Query(None, description="站点IP"),
    period: str = Query("24h", description="对比周期: 24h, 7d, 30d"),
    x_station_ip: Optional[str] = Header(None, alias="X-Station-Ip"),
):
    """
    获取同比环比对比数据
    返回同比百分比(yoy_percent)、环比百分比(mom_percent)、当前周期能耗(current_kwh)
    """
    try:
        # 确定站点IP
        target_station_ip = station_ip or x_station_ip

        # 获取站点列表
        stations = []
        if target_station_ip:
            station_config = electricity_config.get_station_by_ip(target_station_ip)
            if station_config:
                stations = [station_config]
        elif line:
            stations = electricity_config.get_stations_by_line(line)
        else:
            stations = electricity_config.get_all_stations()

        station_count = len(stations)

        # 根据周期计算基准能耗
        if period == "24h":
            base_kwh = station_count * 3500  # 每站点日均3500kWh
        elif period == "7d":
            base_kwh = station_count * 3500 * 7
        elif period == "30d":
            base_kwh = station_count * 3500 * 30
        else:
            base_kwh = station_count * 3500

        # 当前周期能耗（加入随机波动）
        current_kwh = base_kwh * random.uniform(0.9, 1.1)
        current_kwh = round(current_kwh, 1)

        # 同比变化（与去年同期对比）：模拟节能效果，一般为负值或小正值
        yoy_percent = random.uniform(-15, 5)
        yoy_percent = round(yoy_percent, 1)

        # 环比变化（与上一周期对比）：波动较小
        mom_percent = random.uniform(-10, 10)
        mom_percent = round(mom_percent, 1)

        return {
            "current_kwh": current_kwh,
            "yoy_percent": yoy_percent,
            "mom_percent": mom_percent,
            "period": period,
            "station_count": station_count,
            "update_time": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"获取对比数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取对比数据失败: {str(e)}")


@router.get("/classification")
async def get_classification_data(
    line: Optional[str] = Query(None, description="地铁线路，如M3、M8等"),
    station_ip: Optional[str] = Query(None, description="站点IP"),
    period: str = Query("24h", description="统计周期: 24h, 7d, 30d"),
    x_station_ip: Optional[str] = Header(None, alias="X-Station-Ip"),
):
    """
    获取分类分项能耗数据
    返回各类设备的能耗占比，用于饼图展示
    """
    try:
        # 确定站点IP
        target_station_ip = station_ip or x_station_ip

        # 获取站点列表
        stations = []
        if target_station_ip:
            station_config = electricity_config.get_station_by_ip(target_station_ip)
            if station_config:
                stations = [station_config]
        elif line:
            stations = electricity_config.get_stations_by_line(line)
        else:
            stations = electricity_config.get_all_stations()

        station_count = len(stations)

        # 定义设备分类及其占比范围
        categories = [
            {"name": "冷机系统", "ratio_range": (0.35, 0.45)},
            {"name": "水泵系统", "ratio_range": (0.15, 0.25)},
            {"name": "冷却塔", "ratio_range": (0.08, 0.15)},
            {"name": "通风系统", "ratio_range": (0.10, 0.18)},
            {"name": "照明系统", "ratio_range": (0.05, 0.12)},
            {"name": "其他设备", "ratio_range": (0.03, 0.08)},
        ]

        # 根据周期计算总能耗
        if period == "24h":
            total_kwh = station_count * 3500
        elif period == "7d":
            total_kwh = station_count * 3500 * 7
        elif period == "30d":
            total_kwh = station_count * 3500 * 30
        else:
            total_kwh = station_count * 3500

        # 生成各分类能耗数据
        items = []
        used_ratio_sum = 0.0
        kwh_values = []

        for i, category in enumerate(categories):
            if i == len(categories) - 1:
                # 最后一项使用剩余比例，确保总和为1.0
                ratio = 1.0 - used_ratio_sum
                # 确保ratio在合理范围内
                ratio = max(0.01, min(ratio, 0.20))
            else:
                # 根据占比范围随机生成
                ratio = random.uniform(
                    category["ratio_range"][0], category["ratio_range"][1]
                )
                used_ratio_sum += ratio

            kwh = total_kwh * ratio
            kwh_values.append(kwh)

        # 归一化确保总和等于total_kwh
        actual_total = sum(kwh_values)
        normalization_factor = total_kwh / actual_total

        for i, category in enumerate(categories):
            normalized_kwh = kwh_values[i] * normalization_factor
            percentage = (normalized_kwh / total_kwh) * 100

            # 确保百分比在0-100范围内
            percentage = max(0.0, min(percentage, 100.0))

            items.append(
                {
                    "name": category["name"],
                    "kwh": round(normalized_kwh, 1),
                    "percentage": round(percentage, 1),
                }
            )

        return {
            "items": items,
            "total_kwh": round(total_kwh, 1),
            "period": period,
            "station_count": station_count,
            "update_time": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"获取分类能耗数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取分类能耗数据失败: {str(e)}")
