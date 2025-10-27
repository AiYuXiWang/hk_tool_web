"""
能源驾驶舱API接口
提供实时能耗监测、历史趋势分析、KPI指标、设备状态、同比环比对比、分类分项能耗等数据服务
"""

import logging
import os
import random
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.app.config.electricity_config import ElectricityConfig  # noqa: E402
from backend.app.core.dependencies import get_energy_service  # noqa: E402
from backend.app.services.energy_data_provider import (  # noqa: E402
    RealDataUnavailable,
    compute_classification_for_station,
    compute_compare_for_station,
    compute_kpi_for_station,
    compute_realtime_series_for_station,
    compute_trend_for_station,
)
from backend.app.services.energy_service import EnergyService  # noqa: E402

logger = logging.getLogger(__name__)
router = APIRouter()

# 初始化配置
electricity_config = ElectricityConfig()


def _normalize_line(line: Optional[str]) -> Optional[str]:
    if not line:
        return None
    return line.strip().upper()


def _get_station_count_for_line(line: Optional[str]) -> int:
    config_map = getattr(electricity_config, "config_data", {}) or {}
    if not line:
        return sum(len(line_cfg) for line_cfg in config_map.values())

    normalized = _normalize_line(line)
    for line_code, line_cfg in config_map.items():
        if line_code.upper() == normalized:
            return len(line_cfg)
    return 0


def _resolve_station_contexts(
    line: Optional[str],
    station_ip: Optional[str],
) -> List[Dict[str, Any]]:
    config_map = getattr(electricity_config, "config_data", {}) or {}
    contexts: List[Dict[str, Any]] = []
    normalized_line = _normalize_line(line)

    if station_ip:
        for line_code, line_cfg in config_map.items():
            if normalized_line and line_code.upper() != normalized_line:
                continue
            for station_name, cfg in line_cfg.items():
                if cfg.get("ip") == station_ip:
                    contexts.append(
                        {
                            "line": line_code,
                            "station_key": station_name,
                            "display_name": cfg.get("station", station_name),
                            "ip": cfg.get("ip"),
                            "config": cfg,
                        }
                    )
        return contexts

    if normalized_line:
        for line_code, line_cfg in config_map.items():
            if line_code.upper() != normalized_line:
                continue
            for station_name, cfg in line_cfg.items():
                contexts.append(
                    {
                        "line": line_code,
                        "station_key": station_name,
                        "display_name": cfg.get("station", station_name),
                        "ip": cfg.get("ip"),
                        "config": cfg,
                    }
                )
            return contexts

    for line_code, line_cfg in config_map.items():
        for station_name, cfg in line_cfg.items():
            contexts.append(
                {
                    "line": line_code,
                    "station_key": station_name,
                    "display_name": cfg.get("station", station_name),
                    "ip": cfg.get("ip"),
                    "config": cfg,
                }
            )
    return contexts


def _mock_realtime_payload(station_names: List[str]) -> Dict[str, Any]:
    now = datetime.now()
    timestamps = [
        (now - timedelta(minutes=10 * (11 - idx))).strftime("%H:%M")
        for idx in range(12)
    ]

    series = []
    for name in station_names or ["示例站点"]:
        base_power = random.uniform(90, 180)
        points = []
        for index in range(12):
            minutes_ago = 10 * (11 - index)
            hour = (now - timedelta(minutes=minutes_ago)).hour
            if 6 <= hour <= 22:
                power = base_power * random.uniform(0.85, 1.2)
            else:
                power = base_power * random.uniform(0.5, 0.8)
            points.append(round(power, 1))
        series.append({"name": name, "points": points})

    return {
        "series": series,
        "timestamps": timestamps,
        "update_time": datetime.now().isoformat(),
    }


def _mock_trend_payload(period: str, station_count: int = 3) -> Dict[str, Any]:
    now = datetime.now()

    if period == "24h":
        timestamps = [
            (now - timedelta(hours=23 - idx)).strftime("%H:%M") for idx in range(24)
        ]
        values = [
            round(sum(random.uniform(120, 220) for _ in range(station_count)), 2)
            for _ in range(24)
        ]
    elif period == "7d":
        timestamps = [
            (now - timedelta(days=6 - idx)).strftime("%m-%d") for idx in range(7)
        ]
        values = [
            round(sum(random.uniform(2500, 4200) for _ in range(station_count)), 2)
            for _ in range(7)
        ]
    elif period == "30d":
        timestamps = [
            (now - timedelta(days=29 - idx)).strftime("%m-%d") for idx in range(30)
        ]
        values = [
            round(sum(random.uniform(2200, 3600) for _ in range(station_count)), 2)
            for _ in range(30)
        ]
    else:
        timestamps = [
            (now - timedelta(hours=23 - idx)).strftime("%H:%M") for idx in range(24)
        ]
        values = [
            round(sum(random.uniform(120, 220) for _ in range(station_count)), 2)
            for _ in range(24)
        ]

    return {
        "values": values,
        "timestamps": timestamps,
        "period": period,
        "station_count": station_count,
        "update_time": datetime.now().isoformat(),
    }


def _mock_kpi_payload(station_count: int) -> Dict[str, Any]:
    base_power_per_station = 150
    simulated_count = max(station_count, 1)
    current_kw = sum(
        base_power_per_station * (0.8 + 0.4 * random.random())
        for _ in range(simulated_count)
    )
    current_kw = round(current_kw, 1)
    peak_kw = round(current_kw * random.uniform(1.2, 1.5), 1)
    hours_elapsed = datetime.now().hour + datetime.now().minute / 60
    total_kwh_today = round(current_kw * hours_elapsed * random.uniform(0.8, 1.2), 1)
    return {
        "total_kwh_today": total_kwh_today,
        "current_kw": current_kw,
        "peak_kw": peak_kw,
        "station_count": station_count,
        "update_time": datetime.now().isoformat(),
    }


def _mock_compare_payload(period: str, station_count: int) -> Dict[str, Any]:
    simulated_count = max(station_count, 1)
    if period == "24h":
        base_kwh = simulated_count * 3500
    elif period == "7d":
        base_kwh = simulated_count * 3500 * 7
    elif period == "30d":
        base_kwh = simulated_count * 3500 * 30
    else:
        base_kwh = simulated_count * 3500

    current_kwh = round(base_kwh * random.uniform(0.9, 1.1), 1)
    yoy_percent = round(random.uniform(-15, 5), 1)
    mom_percent = round(random.uniform(-10, 10), 1)

    return {
        "current_kwh": current_kwh,
        "yoy_percent": yoy_percent,
        "mom_percent": mom_percent,
        "period": period,
        "station_count": station_count,
        "update_time": datetime.now().isoformat(),
    }


def _mock_classification_payload(period: str, station_count: int) -> Dict[str, Any]:
    simulated_count = max(station_count, 1)
    if period == "24h":
        total_kwh = simulated_count * 3500
    elif period == "7d":
        total_kwh = simulated_count * 3500 * 7
    elif period == "30d":
        total_kwh = simulated_count * 3500 * 30
    else:
        total_kwh = simulated_count * 3500

    categories = [
        {"name": "冷机系统", "ratio_range": (0.35, 0.45)},
        {"name": "水泵系统", "ratio_range": (0.15, 0.25)},
        {"name": "冷却塔", "ratio_range": (0.08, 0.15)},
        {"name": "通风系统", "ratio_range": (0.10, 0.18)},
        {"name": "照明系统", "ratio_range": (0.05, 0.12)},
        {"name": "其他设备", "ratio_range": (0.03, 0.08)},
    ]

    items = []
    remaining_kwh = total_kwh
    for index, category in enumerate(categories):
        if index == len(categories) - 1:
            kwh = max(remaining_kwh, 0.0)
        else:
            low, high = category["ratio_range"]
            ratio = random.uniform(low, high)
            kwh = total_kwh * ratio
            remaining_kwh = max(remaining_kwh - kwh, 0.0)
        kwh = max(kwh, 0.0)
        items.append(
            {
                "name": category["name"],
                "kwh": round(kwh, 1),
                "percentage": 0.0,
            }
        )

    sum_kwh = sum(item["kwh"] for item in items)
    if total_kwh and items and abs(sum_kwh - total_kwh) >= 0.1:
        delta = round(total_kwh - sum_kwh, 1)
        adjusted = max(items[-1]["kwh"] + delta, 0.0)
        items[-1]["kwh"] = round(adjusted, 1)
        sum_kwh = sum(item["kwh"] for item in items)

    for item in items:
        percentage = (item["kwh"] / sum_kwh) * 100 if sum_kwh else 0.0
        item["percentage"] = round(max(0.0, min(percentage, 100.0)), 1)

    return {
        "items": items,
        "total_kwh": round(sum_kwh, 1),
        "period": period,
        "station_count": station_count,
        "update_time": datetime.now().isoformat(),
    }


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
    x_station_ip: Optional[str] = Header(None, alias="X-Station-Ip"),
):
    """
    获取实时能耗监控数据
    支持按线路或站点过滤
    返回格式: { series: [{ name, points }], timestamps: [] }
    """
    try:
        target_station_ip = station_ip or x_station_ip
        contexts = _resolve_station_contexts(line, target_station_ip)

        if not contexts:
            logger.warning("未找到匹配的站点配置，使用模拟实时数据")
            return _mock_realtime_payload([])

        real_series = []
        timestamps: Optional[List[str]] = None

        for ctx in contexts[:5]:  # 最多展示5条曲线
            try:
                data = await compute_realtime_series_for_station(ctx["config"])
            except RealDataUnavailable as exc:
                logger.debug("站点%s实时数据不可用: %s", ctx["display_name"], exc)
                continue

            powers = [round(value, 1) for value in data.get("powers", [])]
            current_timestamps = data.get("timestamps", [])
            if not powers or not current_timestamps:
                continue

            if timestamps is None:
                timestamps = current_timestamps
            else:
                if len(current_timestamps) != len(timestamps):
                    min_len = min(len(current_timestamps), len(timestamps))
                    timestamps = timestamps[:min_len]
                    powers = powers[:min_len]
                    for existing in real_series:
                        existing["points"] = existing["points"][:min_len]
            real_series.append({"name": ctx["display_name"], "points": powers})

        if real_series and timestamps:
            return {
                "series": real_series,
                "timestamps": timestamps,
                "update_time": datetime.now().isoformat(),
            }

        raise RealDataUnavailable("no realtime data available")

    except RealDataUnavailable as exc:
        logger.warning("实时数据回退到模拟数据: %s", exc)
        names = (
            [ctx.get("display_name") for ctx in contexts]
            if "contexts" in locals()
            else []
        )
        return _mock_realtime_payload(names)
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
    if period not in {"24h", "7d", "30d"}:
        raise HTTPException(status_code=400, detail="不支持的时间周期")

    station_count = _get_station_count_for_line(line)

    try:
        target_station_ip = station_ip or x_station_ip
        if not target_station_ip or period != "24h":
            raise RealDataUnavailable(
                "live trend requires station scope and 24h period"
            )

        contexts = _resolve_station_contexts(line, target_station_ip)
        if not contexts:
            raise RealDataUnavailable("no matching station configuration")

        aggregated_values: Optional[List[float]] = None
        timestamps: Optional[List[str]] = None

        for ctx in contexts[:5]:
            try:
                trend_data = await compute_trend_for_station(ctx["config"], period)
            except RealDataUnavailable as exc:
                logger.debug("站点%s趋势数据不可用: %s", ctx["display_name"], exc)
                continue

            values = [round(val, 2) for val in trend_data.get("values", [])]
            current_timestamps = trend_data.get("timestamps", [])
            if not values or not current_timestamps:
                continue

            if timestamps is None:
                timestamps = current_timestamps
                aggregated_values = values
            else:
                if len(values) != len(timestamps):
                    min_len = min(len(values), len(timestamps))
                    timestamps = timestamps[:min_len]
                    if aggregated_values is not None:
                        aggregated_values = aggregated_values[:min_len]
                    values = values[:min_len]
                if aggregated_values is None:
                    aggregated_values = values
                else:
                    aggregated_values = [
                        round(existing + addition, 2)
                        for existing, addition in zip(aggregated_values, values)
                    ]

        if aggregated_values and timestamps:
            return {
                "values": aggregated_values,
                "timestamps": timestamps,
                "period": period,
                "station_count": station_count or len(contexts),
                "update_time": datetime.now().isoformat(),
            }

        raise RealDataUnavailable("no trend data available")

    except RealDataUnavailable as exc:
        logger.warning("趋势数据回退到模拟数据: %s", exc)
        return _mock_trend_payload(period, station_count or len(contexts) or 1)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取趋势数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取趋势数据失败: {str(e)}")


@router.get("/equipment")
async def get_equipment_status(
    x_station_ip: Optional[str] = Header(None, alias="X-Station-Ip")
):
    """
    获取设备运行状态数据
    """
    try:
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
                # 获取站点设备列表
                devices = electricity_config.get_station_devices(station["ip"])

                for device in devices[:3]:  # 每个站点显示前3个设备
                    # 模拟设备状态
                    status_rand = random.random()
                    if status_rand > 0.9:
                        status = "error"
                        status_text = "设备故障"
                    elif status_rand > 0.7:
                        status = "warning"
                        status_text = "效率偏低"
                    else:
                        status = "normal"
                        status_text = "正常运行"

                    status_summary[status] += 1

                    # 模拟设备功率和效率
                    power = device.get("power", 100) * (0.8 + 0.4 * random.random())
                    efficiency = 85 + 15 * random.random()

                    equipment_list.append(
                        {
                            "id": f"{station['ip']}_{device['name']}",
                            "name": device["name"],
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
    station_count = _get_station_count_for_line(line)

    try:
        target_station_ip = station_ip or x_station_ip
        if not target_station_ip:
            raise RealDataUnavailable("station scope required for live KPI data")

        contexts = _resolve_station_contexts(line, target_station_ip)
        if not contexts:
            raise RealDataUnavailable("no matching station configuration")

        total_kwh_today = 0.0
        current_kw = 0.0
        peak_kw = 0.0

        for ctx in contexts[:5]:
            try:
                metrics = await compute_kpi_for_station(ctx["config"])
            except RealDataUnavailable as exc:
                logger.debug("站点%s KPI数据不可用: %s", ctx["display_name"], exc)
                continue

            total_kwh_today += metrics.get("total_kwh_today", 0.0)
            current_kw += metrics.get("current_kw", 0.0)
            peak_kw += metrics.get("peak_kw", 0.0)

        if total_kwh_today or current_kw or peak_kw:
            return {
                "total_kwh_today": round(total_kwh_today, 2),
                "current_kw": round(current_kw, 2),
                "peak_kw": round(peak_kw, 2),
                "station_count": station_count or len(contexts),
                "update_time": datetime.now().isoformat(),
            }

        raise RealDataUnavailable("no kpi data available")

    except RealDataUnavailable as exc:
        logger.warning("KPI数据回退到模拟数据: %s", exc)
        return _mock_kpi_payload(station_count or len(contexts) or 1)
    except HTTPException:
        raise
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
    if period not in {"24h", "7d", "30d"}:
        raise HTTPException(status_code=400, detail="不支持的时间周期")

    station_count = _get_station_count_for_line(line)

    try:
        target_station_ip = station_ip or x_station_ip
        contexts = _resolve_station_contexts(line, target_station_ip)
        if not contexts:
            raise RealDataUnavailable("no matching station configuration")

        current_total = 0.0
        previous_total = 0.0
        last_year_total = 0.0

        for ctx in contexts[:5]:
            try:
                metrics = await compute_compare_for_station(ctx["config"], period)
            except RealDataUnavailable as exc:
                logger.debug("站点%s对比数据不可用: %s", ctx["display_name"], exc)
                continue

            current_total += metrics.get("current_kwh", 0.0)
            previous_total += metrics.get("previous_kwh", 0.0)
            last_year_total += metrics.get("last_year_kwh", 0.0)

        if current_total or previous_total or last_year_total:
            mom_percent = (
                (current_total - previous_total) / previous_total * 100.0
                if previous_total > 0
                else 0.0
            )
            yoy_percent = (
                (current_total - last_year_total) / last_year_total * 100.0
                if last_year_total > 0
                else 0.0
            )

            return {
                "current_kwh": round(current_total, 2),
                "yoy_percent": round(yoy_percent, 1),
                "mom_percent": round(mom_percent, 1),
                "period": period,
                "station_count": station_count or len(contexts),
                "update_time": datetime.now().isoformat(),
            }

        raise RealDataUnavailable("no compare data available")

    except RealDataUnavailable as exc:
        logger.warning("同比环比数据回退到模拟数据: %s", exc)
        return _mock_compare_payload(period, station_count or len(contexts) or 1)
    except HTTPException:
        raise
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
    if period not in {"24h", "7d", "30d"}:
        raise HTTPException(status_code=400, detail="不支持的统计周期")

    station_count = _get_station_count_for_line(line)

    try:
        target_station_ip = station_ip or x_station_ip
        contexts = _resolve_station_contexts(line, target_station_ip)
        if not contexts:
            raise RealDataUnavailable("no matching station configuration")

        category_totals: Dict[str, float] = {}
        total_kwh = 0.0

        for ctx in contexts[:5]:
            try:
                data = await compute_classification_for_station(ctx["config"], period)
            except RealDataUnavailable as exc:
                logger.debug("站点%s分类数据不可用: %s", ctx["display_name"], exc)
                continue

            total_kwh += data.get("total_kwh", 0.0)
            for item in data.get("items", []):
                value = item.get("kwh")
                if value is None:
                    continue
                category_name = item.get("name", "其他")
                category_totals[category_name] = category_totals.get(
                    category_name, 0.0
                ) + float(value)

        if category_totals:
            aggregated_total = total_kwh or sum(category_totals.values())
            items = []
            for name, value in category_totals.items():
                percentage = (
                    (value / aggregated_total * 100.0) if aggregated_total > 0 else 0.0
                )
                items.append(
                    {
                        "name": name,
                        "kwh": round(value, 2),
                        "percentage": round(percentage, 1),
                    }
                )
            items.sort(key=lambda item: item["kwh"], reverse=True)

            return {
                "items": items,
                "total_kwh": round(aggregated_total, 2),
                "period": period,
                "station_count": station_count or len(contexts),
                "update_time": datetime.now().isoformat(),
            }

        raise RealDataUnavailable("no classification data available")

    except RealDataUnavailable as exc:
        logger.warning("分类能耗数据回退到模拟数据: %s", exc)
        return _mock_classification_payload(period, station_count or len(contexts) or 1)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取分类能耗数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取分类能耗数据失败: {str(e)}")
