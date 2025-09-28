from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Optional

class ExportRequest(BaseModel):
    """电耗数据导出请求模型"""
    line: str
    start_time: datetime
    end_time: datetime

class SensorExportRequest(BaseModel):
    """传感器数据导出请求模型"""
    line: str
    start_time: datetime
    end_time: datetime

class ExportResult(BaseModel):
    """导出结果模型"""
    success: bool
    message: str
    file_path: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class StationExportResult(BaseModel):
    """车站导出结果模型"""
    station_ip: str
    station_name: str
    success: bool
    message: str
    file_path: Optional[str] = None