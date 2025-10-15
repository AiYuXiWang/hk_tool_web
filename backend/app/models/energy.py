"""
能源数据模型

定义能源管理相关的数据模型。
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import Field, validator
import uuid
from .base import BaseEntity

class EnergyOverview(BaseEntity):
    """能源总览数据模型"""
    
    total_consumption: float = Field(..., description="总能耗(kWh)")
    current_power: float = Field(..., description="当前功率(kW)")
    efficiency_ratio: float = Field(..., description="能效比")
    energy_saving: float = Field(..., description="节能收益(元)")
    site_ip: Optional[str] = Field(None, description="站点IP")
    
    def generate_id(self) -> str:
        """生成ID"""
        return f"energy_overview_{uuid.uuid4().hex[:8]}"
    
    @validator('efficiency_ratio')
    def validate_efficiency_ratio(cls, v):
        """验证能效比"""
        if v < 0:
            raise ValueError('能效比不能为负数')
        return v
    
    @validator('total_consumption', 'current_power', 'energy_saving')
    def validate_positive_values(cls, v):
        """验证正数值"""
        if v < 0:
            raise ValueError('数值不能为负数')
        return v

class RealtimeData(BaseEntity):
    """实时监控数据模型"""
    
    site_ip: str = Field(..., description="站点IP")
    site_name: str = Field(..., description="站点名称")
    current_power: float = Field(..., description="当前功率(kW)")
    device_count: int = Field(..., description="设备数量")
    power_curve: List[Dict[str, Any]] = Field(default_factory=list, description="24小时功率曲线")
    
    def generate_id(self) -> str:
        """生成ID"""
        return f"realtime_{self.site_ip}_{uuid.uuid4().hex[:8]}"
    
    @validator('device_count')
    def validate_device_count(cls, v):
        """验证设备数量"""
        if v < 0:
            raise ValueError('设备数量不能为负数')
        return v
    
    @validator('current_power')
    def validate_current_power(cls, v):
        """验证当前功率"""
        if v < 0:
            raise ValueError('功率不能为负数')
        return v

class HistoricalData(BaseEntity):
    """历史数据模型"""
    
    site_ip: Optional[str] = Field(None, description="站点IP")
    date_range: str = Field(..., description="日期范围")
    consumption_trend: List[Dict[str, Any]] = Field(default_factory=list, description="能耗趋势")
    power_trend: List[Dict[str, Any]] = Field(default_factory=list, description="功率趋势")
    efficiency_trend: List[Dict[str, Any]] = Field(default_factory=list, description="能效趋势")
    
    def generate_id(self) -> str:
        """生成ID"""
        return f"historical_{self.date_range}_{uuid.uuid4().hex[:8]}"

class KPIData(BaseEntity):
    """KPI指标数据模型"""
    
    site_ip: Optional[str] = Field(None, description="站点IP")
    period: str = Field(..., description="统计周期")
    total_consumption: float = Field(..., description="总能耗(kWh)")
    average_power: float = Field(..., description="平均功率(kW)")
    peak_power: float = Field(..., description="峰值功率(kW)")
    efficiency_score: float = Field(..., description="能效评分")
    cost_saving: float = Field(..., description="成本节约(元)")
    carbon_reduction: float = Field(..., description="碳减排(kg)")
    
    def generate_id(self) -> str:
        """生成ID"""
        return f"kpi_{self.period}_{uuid.uuid4().hex[:8]}"
    
    @validator('efficiency_score')
    def validate_efficiency_score(cls, v):
        """验证能效评分"""
        if not 0 <= v <= 100:
            raise ValueError('能效评分必须在0-100之间')
        return v
    
    @validator('total_consumption', 'average_power', 'peak_power', 'cost_saving', 'carbon_reduction')
    def validate_positive_values(cls, v):
        """验证正数值"""
        if v < 0:
            raise ValueError('数值不能为负数')
        return v

class EnergyDevice(BaseEntity):
    """能源设备模型"""
    
    device_id: str = Field(..., description="设备ID")
    device_name: str = Field(..., description="设备名称")
    device_type: str = Field(..., description="设备类型")
    site_ip: str = Field(..., description="所属站点IP")
    power_rating: float = Field(..., description="额定功率(kW)")
    current_power: float = Field(..., description="当前功率(kW)")
    status: str = Field(..., description="设备状态")
    efficiency: float = Field(..., description="设备能效")
    
    def generate_id(self) -> str:
        """生成ID"""
        return f"device_{self.device_id}"
    
    @validator('status')
    def validate_status(cls, v):
        """验证设备状态"""
        valid_statuses = ['online', 'offline', 'maintenance', 'error']
        if v not in valid_statuses:
            raise ValueError(f'设备状态必须是: {", ".join(valid_statuses)}')
        return v
    
    @validator('power_rating', 'current_power')
    def validate_power_values(cls, v):
        """验证功率值"""
        if v < 0:
            raise ValueError('功率值不能为负数')
        return v
    
    @validator('efficiency')
    def validate_efficiency(cls, v):
        """验证设备能效"""
        if not 0 <= v <= 1:
            raise ValueError('设备能效必须在0-1之间')
        return v

class EnergySite(BaseEntity):
    """能源站点模型"""
    
    site_ip: str = Field(..., description="站点IP")
    site_name: str = Field(..., description="站点名称")
    location: str = Field(..., description="站点位置")
    total_devices: int = Field(..., description="设备总数")
    online_devices: int = Field(..., description="在线设备数")
    total_power: float = Field(..., description="总功率(kW)")
    total_consumption: float = Field(..., description="总能耗(kWh)")
    efficiency_rating: str = Field(..., description="能效等级")
    
    def generate_id(self) -> str:
        """生成ID"""
        return f"site_{self.site_ip}"
    
    @validator('efficiency_rating')
    def validate_efficiency_rating(cls, v):
        """验证能效等级"""
        valid_ratings = ['A', 'B', 'C', 'D', 'E']
        if v not in valid_ratings:
            raise ValueError(f'能效等级必须是: {", ".join(valid_ratings)}')
        return v
    
    @validator('total_devices', 'online_devices')
    def validate_device_counts(cls, v):
        """验证设备数量"""
        if v < 0:
            raise ValueError('设备数量不能为负数')
        return v
    
    @validator('total_power', 'total_consumption')
    def validate_energy_values(cls, v):
        """验证能源值"""
        if v < 0:
            raise ValueError('能源值不能为负数')
        return v

class EnergyAlert(BaseEntity):
    """能源告警模型"""
    
    alert_type: str = Field(..., description="告警类型")
    severity: str = Field(..., description="严重程度")
    site_ip: str = Field(..., description="站点IP")
    device_id: Optional[str] = Field(None, description="设备ID")
    message: str = Field(..., description="告警消息")
    threshold: Optional[float] = Field(None, description="阈值")
    current_value: Optional[float] = Field(None, description="当前值")
    status: str = Field("active", description="告警状态")
    resolved_at: Optional[datetime] = Field(None, description="解决时间")
    
    def generate_id(self) -> str:
        """生成ID"""
        return f"alert_{uuid.uuid4().hex[:8]}"
    
    @validator('severity')
    def validate_severity(cls, v):
        """验证严重程度"""
        valid_severities = ['low', 'medium', 'high', 'critical']
        if v not in valid_severities:
            raise ValueError(f'严重程度必须是: {", ".join(valid_severities)}')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        """验证告警状态"""
        valid_statuses = ['active', 'resolved', 'ignored']
        if v not in valid_statuses:
            raise ValueError(f'告警状态必须是: {", ".join(valid_statuses)}')
        return v