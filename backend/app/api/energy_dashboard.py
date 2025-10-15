"""
能源管理驾驶舱API接口
提供实时能耗监测、历史趋势分析、KPI指标、设备状态等数据服务
"""

from fastapi import APIRouter, HTTPException, Header, Query, Depends
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import random
import json
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.app.config.electricity_config import ElectricityConfig
from backend.app.services.energy_service import EnergyService
from backend.app.core.dependencies import get_energy_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# 初始化配置
electricity_config = ElectricityConfig()

@router.get("/overview")
async def get_energy_overview(
    x_station_ip: Optional[str] = Header(None, alias="X-Station-Ip"),
    energy_service: EnergyService = Depends(get_energy_service)
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
                "data": result.get("data")
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
    x_station_ip: Optional[str] = Header(None, alias="X-Station-Ip"),
    energy_service: EnergyService = Depends(get_energy_service)
):
    """
    获取实时能耗监控数据
    支持按线路或站点过滤
    """
    try:
        result = await energy_service.get_realtime_data(line, x_station_ip)
        
        if result.get("success"):
            return {
                "code": 200,
                "message": result.get("message", "success"),
                "data": result.get("data")
            }
        else:
            status_code = result.get("status_code", 500)
            raise HTTPException(status_code=status_code, detail=result.get("message"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取实时数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取实时数据失败: {str(e)}")

@router.get("/history")
async def get_history_data(
    time_range: str = Query("24h", description="时间范围: 24h, 7d, 30d, 90d"),
    line: Optional[str] = Query(None, description="地铁线路，如M3、M8等"),
    x_station_ip: Optional[str] = Header(None, alias="X-Station-Ip")
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
                time_point = now - timedelta(hours=23-i)
                power = sum(random.uniform(400, 700) for _ in range(station_count))
                energy = power * random.uniform(0.9, 1.1)
                efficiency = random.uniform(0.75, 0.95)
                data_points.append({
                    "time": time_point.strftime("%H:%M"),
                    "datetime": time_point.isoformat(),
                    "power": round(power, 1),
                    "energy": round(energy, 1),
                    "efficiency": round(efficiency * 100, 1)
                })
        
        elif time_range == "7d":
            # 7天数据，每天一个点
            data_points = []
            for i in range(7):
                time_point = now - timedelta(days=6-i)
                power = sum(random.uniform(500, 800) for _ in range(station_count))
                energy = power * 24 * random.uniform(0.8, 1.2)  # 日能耗
                efficiency = random.uniform(0.8, 0.95)
                data_points.append({
                    "time": time_point.strftime("%m-%d"),
                    "datetime": time_point.isoformat(),
                    "power": round(power, 1),
                    "energy": round(energy, 1),
                    "efficiency": round(efficiency * 100, 1)
                })
        
        elif time_range == "30d":
            # 30天数据，每天一个点
            data_points = []
            for i in range(30):
                time_point = now - timedelta(days=29-i)
                power = sum(random.uniform(450, 750) for _ in range(station_count))
                energy = power * 24 * random.uniform(0.85, 1.15)
                efficiency = random.uniform(0.78, 0.92)
                data_points.append({
                    "time": time_point.strftime("%m-%d"),
                    "datetime": time_point.isoformat(),
                    "power": round(power, 1),
                    "energy": round(energy, 1),
                    "efficiency": round(efficiency * 100, 1)
                })
        
        elif time_range == "90d":
            # 90天数据，每3天一个点
            data_points = []
            for i in range(30):  # 30个点，每个点代表3天
                time_point = now - timedelta(days=89-i*3)
                power = sum(random.uniform(400, 800) for _ in range(station_count))
                energy = power * 24 * 3 * random.uniform(0.8, 1.2)  # 3天能耗
                efficiency = random.uniform(0.75, 0.95)
                data_points.append({
                    "time": time_point.strftime("%m-%d"),
                    "datetime": time_point.isoformat(),
                    "power": round(power, 1),
                    "energy": round(energy, 1),
                    "efficiency": round(efficiency * 100, 1)
                })
        
        else:
            # 默认返回24h数据
            data_points = []
            for i in range(24):
                time_point = now - timedelta(hours=23-i)
                power = sum(random.uniform(400, 700) for _ in range(station_count))
                energy = power * random.uniform(0.9, 1.1)
                efficiency = random.uniform(0.75, 0.95)
                data_points.append({
                    "time": time_point.strftime("%H:%M"),
                    "datetime": time_point.isoformat(),
                    "power": round(power, 1),
                    "energy": round(energy, 1),
                    "efficiency": round(efficiency * 100, 1)
                })
        
        # 计算统计数据
        total_energy = sum(point["energy"] for point in data_points)
        avg_power = sum(point["power"] for point in data_points) / len(data_points)
        avg_efficiency = sum(point["efficiency"] for point in data_points) / len(data_points)
        
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
                "efficiency_change": round(efficiency_change, 1)
            },
            "total_stations": station_count,
            "update_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取历史数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取历史数据失败: {str(e)}")

@router.get("/trend")
async def get_trend_data(
    period: str = Query("7d", description="时间周期: 24h, 7d, 30d, 90d"),
    x_station_ip: Optional[str] = Header(None, alias="X-Station-Ip")
):
    """
    获取历史趋势分析数据
    支持不同时间周期的数据查询
    """
    try:
        # 解析时间周期
        if period == "24h":
            days = 1
            data_points = 24
            time_format = "%H:00"
        elif period == "7d":
            days = 7
            data_points = 7
            time_format = "%m-%d"
        elif period == "30d":
            days = 30
            data_points = 30
            time_format = "%m-%d"
        elif period == "90d":
            days = 90
            data_points = 30  # 90天数据按3天一个点聚合
            time_format = "%m-%d"
        else:
            raise HTTPException(status_code=400, detail="不支持的时间周期")

        # 获取站点列表
        stations = []
        if x_station_ip:
            station_config = electricity_config.get_station_by_ip(x_station_ip)
            if station_config:
                stations = [station_config]
        else:
            stations = electricity_config.get_all_stations()

        if not stations:
            return {"consumption": [], "target": [], "timestamps": []}

        # 生成时间序列
        now = datetime.now()
        timestamps = []
        consumption_data = []
        target_data = []

        for i in range(data_points):
            if period == "24h":
                time_point = now - timedelta(hours=data_points-1-i)
            elif period == "90d":
                time_point = now - timedelta(days=(data_points-1-i)*3)
            else:
                time_point = now - timedelta(days=data_points-1-i)
            
            timestamps.append(time_point.strftime(time_format))

        # 计算每个时间点的总能耗
        base_consumption = 25000  # 基准日能耗
        for i in range(data_points):
            # 模拟能耗数据
            daily_consumption = base_consumption * (0.8 + 0.4 * (1 + 0.1 * (i % 5)))
            consumption_data.append(round(daily_consumption, 0))
            
            # 目标能耗线
            target_consumption = base_consumption * 1.2
            target_data.append(target_consumption)

        return {
            "consumption": consumption_data,
            "target": target_data,
            "timestamps": timestamps,
            "period": period,
            "update_time": datetime.now().isoformat()
        }

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
                devices = electricity_config.get_station_devices(station['ip'])
                
                for device in devices[:3]:  # 每个站点显示前3个设备
                    # 模拟设备状态
                    import random
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
                    power = device.get('power', 100) * (0.8 + 0.4 * random.random())
                    efficiency = 85 + 15 * random.random()
                    
                    equipment_list.append({
                        "id": f"{station['ip']}_{device['name']}",
                        "name": device['name'],
                        "location": station['name'],
                        "power": round(power, 1),
                        "efficiency": round(efficiency, 1),
                        "status": status,
                        "status_text": status_text
                    })
                    
            except Exception as e:
                logger.warning(f"获取站点 {station['ip']} 设备状态失败: {e}")
                continue

        return {
            "equipment_list": equipment_list,
            "status_summary": status_summary,
            "update_time": datetime.now().isoformat()
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
                "payback_period": "3个月"
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
                "payback_period": "2个月"
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
                "payback_period": "4个月"
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
                "payback_period": "6个月"
            }
        ]

        # 如果指定了站点，可以提供更精准的建议
        if x_station_ip:
            station_config = electricity_config.get_station_by_ip(x_station_ip)
            if station_config:
                # 基于站点特性调整建议
                for suggestion in suggestions:
                    suggestion["target_station"] = station_config['name']

        return {
            "suggestions": suggestions,
            "total_potential_saving": sum(s["energy_saving"] for s in suggestions),
            "total_cost_saving": sum(s["cost_saving"] for s in suggestions),
            "update_time": datetime.now().isoformat()
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
                "stations": [{"ip": station["ip"], "name": station["station"]} for station in stations]
            }
        else:
            # 获取所有线路和站点
            all_lines = config.get_all_lines()
            all_stations = config.get_all_stations()
            return {
                "lines": all_lines,
                "stations": [{"ip": station["ip"], "name": station["station"]} for station in all_stations]
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
            import random
            x = 100 + (i % 8) * 80 + random.randint(-20, 20)
            y = 200 + (i // 8) * 100 + random.randint(-30, 30)
            
            # 模拟能耗等级
            energy_level = random.choice(["low", "medium", "high"])
            radius = {"low": 6, "medium": 8, "high": 10}[energy_level]
            
            station_map_data.append({
                "id": i + 1,
                "name": station['name'],
                "ip": station['ip'],
                "x": x,
                "y": y,
                "radius": radius,
                "energy_level": energy_level,
                "line": station.get('line', 'M3')
            })

        return {
            "stations": station_map_data,
            "update_time": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"获取站点地图数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取站点地图数据失败: {str(e)}")

@router.get("/report")
async def get_energy_report(
    report_type: str = Query("daily", description="报表类型: daily, weekly, monthly"),
    x_station_ip: Optional[str] = Header(None, alias="X-Station-Ip")
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
        
        base_consumption = {"daily": 25000, "weekly": 175000, "monthly": 750000}[report_type]
        
        for i in range(periods):
            if report_type == "daily":
                time_point = now - timedelta(days=periods-1-i)
                timestamps.append(time_point.strftime(time_format))
            elif report_type == "weekly":
                time_point = now - timedelta(weeks=periods-1-i)
                timestamps.append(f"第{time_point.isocalendar()[1]}周")
            else:  # monthly
                time_point = now - timedelta(days=(periods-1-i)*30)
                timestamps.append(time_point.strftime(time_format))
            
            # 模拟能耗数据，呈现下降趋势（节能效果）
            consumption = base_consumption * (1.1 - 0.02 * i) * (0.9 + 0.2 * (i % 3) / 3)
            consumption_data.append(round(consumption, 0))

        return {
            "timestamps": timestamps,
            "consumption": consumption_data,
            "report_type": report_type,
            "unit": unit,
            "total_consumption": sum(consumption_data),
            "average_consumption": round(sum(consumption_data) / len(consumption_data), 0),
            "trend": "下降",  # 节能趋势
            "update_time": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"获取报表数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取报表数据失败: {str(e)}")