"""
数据文件模型

定义文件上传、解析、验证相关的数据模型。
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import Field, validator
import uuid
from .base import BaseEntity

class DataFile(BaseEntity):
    """数据文件模型"""
    
    filename: str = Field(..., description="文件名")
    original_filename: str = Field(..., description="原始文件名")
    file_size: int = Field(..., description="文件大小(字节)")
    content_type: str = Field(..., description="文件类型")
    file_path: str = Field(..., description="文件路径")
    file_hash: str = Field(..., description="文件哈希值")
    upload_status: str = Field("uploaded", description="上传状态")
    parse_status: str = Field("pending", description="解析状态")
    validation_status: str = Field("pending", description="验证状态")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="文件元数据")
    
    def generate_id(self) -> str:
        """生成ID"""
        return f"file_{uuid.uuid4().hex}"
    
    @validator('upload_status')
    def validate_upload_status(cls, v):
        """验证上传状态"""
        valid_statuses = ['uploading', 'uploaded', 'failed']
        if v not in valid_statuses:
            raise ValueError(f'上传状态必须是: {", ".join(valid_statuses)}')
        return v
    
    @validator('parse_status')
    def validate_parse_status(cls, v):
        """验证解析状态"""
        valid_statuses = ['pending', 'parsing', 'parsed', 'failed']
        if v not in valid_statuses:
            raise ValueError(f'解析状态必须是: {", ".join(valid_statuses)}')
        return v
    
    @validator('validation_status')
    def validate_validation_status(cls, v):
        """验证验证状态"""
        valid_statuses = ['pending', 'validating', 'valid', 'invalid']
        if v not in valid_statuses:
            raise ValueError(f'验证状态必须是: {", ".join(valid_statuses)}')
        return v
    
    @validator('file_size')
    def validate_file_size(cls, v):
        """验证文件大小"""
        if v < 0:
            raise ValueError('文件大小不能为负数')
        # 限制文件大小为100MB
        max_size = 100 * 1024 * 1024
        if v > max_size:
            raise ValueError(f'文件大小不能超过{max_size}字节')
        return v

class ParsedData(BaseEntity):
    """解析后的数据模型"""
    
    file_id: str = Field(..., description="文件ID")
    sheet_name: Optional[str] = Field(None, description="工作表名称")
    headers: List[str] = Field(default_factory=list, description="数据头")
    data: List[Dict[str, Any]] = Field(default_factory=list, description="数据内容")
    row_count: int = Field(0, description="数据行数")
    column_count: int = Field(0, description="数据列数")
    parse_options: Dict[str, Any] = Field(default_factory=dict, description="解析选项")
    parse_errors: List[str] = Field(default_factory=list, description="解析错误")
    
    def generate_id(self) -> str:
        """生成ID"""
        return f"parsed_{self.file_id}_{uuid.uuid4().hex[:8]}"
    
    @validator('row_count', 'column_count')
    def validate_counts(cls, v):
        """验证计数"""
        if v < 0:
            raise ValueError('计数不能为负数')
        return v

class ValidationRule(BaseEntity):
    """验证规则模型"""
    
    rule_name: str = Field(..., description="规则名称")
    rule_type: str = Field(..., description="规则类型")
    column_name: str = Field(..., description="列名")
    rule_config: Dict[str, Any] = Field(default_factory=dict, description="规则配置")
    error_message: str = Field(..., description="错误消息")
    is_required: bool = Field(True, description="是否必需")
    
    def generate_id(self) -> str:
        """生成ID"""
        return f"rule_{uuid.uuid4().hex[:8]}"
    
    @validator('rule_type')
    def validate_rule_type(cls, v):
        """验证规则类型"""
        valid_types = [
            'required', 'data_type', 'range', 'length', 
            'pattern', 'unique', 'custom'
        ]
        if v not in valid_types:
            raise ValueError(f'规则类型必须是: {", ".join(valid_types)}')
        return v

class ValidationResult(BaseEntity):
    """验证结果模型"""
    
    file_id: str = Field(..., description="文件ID")
    parsed_data_id: str = Field(..., description="解析数据ID")
    validation_rules: List[str] = Field(default_factory=list, description="验证规则ID列表")
    is_valid: bool = Field(False, description="是否验证通过")
    error_count: int = Field(0, description="错误数量")
    warning_count: int = Field(0, description="警告数量")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="错误详情")
    warnings: List[Dict[str, Any]] = Field(default_factory=list, description="警告详情")
    summary: Dict[str, Any] = Field(default_factory=dict, description="验证摘要")
    
    def generate_id(self) -> str:
        """生成ID"""
        return f"validation_{self.file_id}_{uuid.uuid4().hex[:8]}"
    
    @validator('error_count', 'warning_count')
    def validate_counts(cls, v):
        """验证计数"""
        if v < 0:
            raise ValueError('计数不能为负数')
        return v

class ExportTask(BaseEntity):
    """导出任务模型"""
    
    task_name: str = Field(..., description="任务名称")
    export_format: str = Field(..., description="导出格式")
    data_source: str = Field(..., description="数据源")
    export_options: Dict[str, Any] = Field(default_factory=dict, description="导出选项")
    status: str = Field("pending", description="任务状态")
    progress: float = Field(0.0, description="进度百分比")
    file_path: Optional[str] = Field(None, description="导出文件路径")
    error_message: Optional[str] = Field(None, description="错误消息")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    
    def generate_id(self) -> str:
        """生成ID"""
        return f"export_{uuid.uuid4().hex}"
    
    @validator('export_format')
    def validate_export_format(cls, v):
        """验证导出格式"""
        valid_formats = ['xlsx', 'csv', 'json', 'pdf', 'xml']
        if v not in valid_formats:
            raise ValueError(f'导出格式必须是: {", ".join(valid_formats)}')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        """验证任务状态"""
        valid_statuses = ['pending', 'running', 'completed', 'failed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f'任务状态必须是: {", ".join(valid_statuses)}')
        return v
    
    @validator('progress')
    def validate_progress(cls, v):
        """验证进度"""
        if not 0 <= v <= 100:
            raise ValueError('进度必须在0-100之间')
        return v

class DataTemplate(BaseEntity):
    """数据模板模型"""
    
    template_name: str = Field(..., description="模板名称")
    template_type: str = Field(..., description="模板类型")
    description: str = Field(..., description="模板描述")
    columns: List[Dict[str, Any]] = Field(default_factory=list, description="列定义")
    validation_rules: List[str] = Field(default_factory=list, description="验证规则ID列表")
    sample_data: List[Dict[str, Any]] = Field(default_factory=list, description="示例数据")
    is_active: bool = Field(True, description="是否激活")
    version: str = Field("1.0", description="模板版本")
    
    def generate_id(self) -> str:
        """生成ID"""
        return f"template_{uuid.uuid4().hex[:8]}"
    
    @validator('template_type')
    def validate_template_type(cls, v):
        """验证模板类型"""
        valid_types = ['energy', 'device', 'sensor', 'report', 'custom']
        if v not in valid_types:
            raise ValueError(f'模板类型必须是: {", ".join(valid_types)}')
        return v

class DataImportLog(BaseEntity):
    """数据导入日志模型"""
    
    file_id: str = Field(..., description="文件ID")
    import_type: str = Field(..., description="导入类型")
    status: str = Field(..., description="导入状态")
    total_rows: int = Field(0, description="总行数")
    success_rows: int = Field(0, description="成功行数")
    failed_rows: int = Field(0, description="失败行数")
    error_details: List[Dict[str, Any]] = Field(default_factory=list, description="错误详情")
    import_options: Dict[str, Any] = Field(default_factory=dict, description="导入选项")
    duration: Optional[float] = Field(None, description="导入耗时(秒)")
    
    def generate_id(self) -> str:
        """生成ID"""
        return f"import_log_{self.file_id}_{uuid.uuid4().hex[:8]}"
    
    @validator('status')
    def validate_status(cls, v):
        """验证导入状态"""
        valid_statuses = ['pending', 'processing', 'completed', 'failed', 'partial']
        if v not in valid_statuses:
            raise ValueError(f'导入状态必须是: {", ".join(valid_statuses)}')
        return v
    
    @validator('total_rows', 'success_rows', 'failed_rows')
    def validate_row_counts(cls, v):
        """验证行数"""
        if v < 0:
            raise ValueError('行数不能为负数')
        return v
    
    @validator('duration')
    def validate_duration(cls, v):
        """验证耗时"""
        if v is not None and v < 0:
            raise ValueError('耗时不能为负数')
        return v