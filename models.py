from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

# ===================== 原有导出相关模型 =====================

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

# ===================== 设备控制相关模型 =====================

class PointMetadata(BaseModel):
    """点位元数据模型"""
    object_code: str = Field(..., description="设备编码")
    data_code: str = Field(..., description="点位编码")
    data_name: Optional[str] = Field(None, description="点位名称")
    unit: Optional[str] = Field(None, description="单位")
    is_writable: bool = Field(False, description="是否可写")
    point_key: Optional[str] = Field(None, description="点位键")
    data_type: Optional[str] = Field(None, description="数据类型")
    data_source: Optional[int] = Field(None, description="数据源类型")
    border_min: Optional[float] = Field(None, description="边界最小值")
    border_max: Optional[float] = Field(None, description="边界最大值")
    warn_min: Optional[float] = Field(None, description="警告最小值")
    warn_max: Optional[float] = Field(None, description="警告最大值")
    error_min: Optional[float] = Field(None, description="错误最小值")
    error_max: Optional[float] = Field(None, description="错误最大值")

class DeviceTreeNode(BaseModel):
    """设备树节点模型"""
    id: str = Field(..., description="节点ID")
    label: str = Field(..., description="节点显示名称")
    children: Optional[List['DeviceTreeNode']] = Field(None, description="子节点")
    meta: Optional[Dict[str, Any]] = Field(None, description="节点元数据")

class RealtimeQuery(BaseModel):
    """实时查询请求模型"""
    object_code: str = Field(..., description="设备编码")
    data_code: str = Field(..., description="点位编码")

class RealtimeResponse(BaseModel):
    """实时查询响应模型"""
    object_code: str = Field(..., description="设备编码")
    data_code: str = Field(..., description="点位编码")
    value: Optional[Union[str, int, float, bool]] = Field(None, description="当前值")
    unit: Optional[str] = Field(None, description="单位")
    ts: str = Field(..., description="时间戳")
    token_len: int = Field(0, description="Token长度")
    raw: Dict[str, Any] = Field(..., description="原始响应数据")

class WriteCommand(BaseModel):
    """写值命令模型"""
    point_key: str = Field(..., description="点位键")
    data_source: int = Field(..., description="数据源类型", ge=1, le=3)
    control_value: Union[str, int, float, bool] = Field(..., description="控制值")
    object_code: Optional[str] = Field(None, description="设备编码")
    data_code: Optional[str] = Field(None, description="点位编码")
    
    @validator('data_source')
    def validate_data_source(cls, v):
        if v not in (1, 2, 3):
            raise ValueError('data_source必须为1、2或3')
        return v

class WriteResult(BaseModel):
    """写值结果模型"""
    point_key: str = Field(..., description="点位键")
    status: str = Field(..., description="执行状态")
    message: Optional[str] = Field(None, description="错误信息")
    duration_ms: int = Field(0, description="执行耗时(毫秒)")
    before: Optional[Union[str, int, float, bool]] = Field(None, description="修改前值")
    after: Optional[Union[str, int, float, bool]] = Field(None, description="修改后值")
    retries: int = Field(0, description="重试次数")

class BatchWriteRequest(BaseModel):
    """批量写值请求模型"""
    commands: List[WriteCommand] = Field(..., description="写值命令列表")
    operator_id: Optional[str] = Field("system", description="操作员ID")

class BatchWriteResponse(BaseModel):
    """批量写值响应模型"""
    total: int = Field(..., description="总命令数")
    success: int = Field(..., description="成功数量")
    failed: int = Field(..., description="失败数量")
    items: List[WriteResult] = Field(..., description="详细结果列表")

class DeviceTreeResponse(BaseModel):
    """设备树响应模型"""
    tree: List[DeviceTreeNode] = Field(..., description="设备树节点列表")
    count: int = Field(..., description="根节点数量")

class PointListResponse(BaseModel):
    """点位列表响应模型"""
    items: List[PointMetadata] = Field(..., description="点位元数据列表")
    count: int = Field(..., description="点位数量")

class OperationLog(BaseModel):
    """操作审计日志模型"""
    id: Optional[int] = Field(None, description="日志ID")
    operator_id: str = Field(..., description="操作员ID")
    point_key: str = Field(..., description="点位键")
    object_code: Optional[str] = Field(None, description="设备编码")
    data_code: Optional[str] = Field(None, description="点位编码")
    before_value: Optional[str] = Field(None, description="修改前值")
    after_value: Optional[str] = Field(None, description="修改后值")
    result: str = Field(..., description="操作结果")
    message: Optional[str] = Field(None, description="消息")
    duration_ms: Optional[int] = Field(None, description="执行耗时(毫秒)")
    created_at: Optional[datetime] = Field(None, description="创建时间")

# 更新DeviceTreeNode的前向引用
DeviceTreeNode.update_forward_refs()