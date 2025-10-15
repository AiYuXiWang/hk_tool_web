"""
模型层基础类

提供数据模型的基础功能，包括验证、序列化、缓存等。
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from datetime import datetime
from pydantic import BaseModel, Field, validator
from abc import ABC, abstractmethod
import json
import hashlib

T = TypeVar('T', bound='BaseEntity')

class BaseEntity(BaseModel, ABC):
    """
    基础实体类
    
    提供所有数据模型的通用功能：
    - 自动时间戳
    - 数据验证
    - 序列化/反序列化
    - 缓存键生成
    """
    
    id: Optional[str] = Field(None, description="实体ID")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="创建时间")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, description="更新时间")
    
    class Config:
        """Pydantic配置"""
        # 允许使用字段别名
        allow_population_by_field_name = True
        # 验证赋值
        validate_assignment = True
        # 使用枚举值
        use_enum_values = True
        # JSON编码器
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    def __init__(self, **data):
        """初始化实体"""
        super().__init__(**data)
        if not self.id:
            self.id = self.generate_id()
    
    @abstractmethod
    def generate_id(self) -> str:
        """
        生成实体ID
        
        Returns:
            str: 实体ID
        """
        pass
    
    def update_timestamp(self) -> None:
        """更新时间戳"""
        self.updated_at = datetime.now()
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """
        转换为字典
        
        Args:
            exclude_none: 是否排除None值
            
        Returns:
            Dict[str, Any]: 字典表示
        """
        return self.dict(exclude_none=exclude_none)
    
    def to_json(self, exclude_none: bool = True) -> str:
        """
        转换为JSON字符串
        
        Args:
            exclude_none: 是否排除None值
            
        Returns:
            str: JSON字符串
        """
        return self.json(exclude_none=exclude_none)
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        从字典创建实体
        
        Args:
            data: 字典数据
            
        Returns:
            T: 实体实例
        """
        return cls(**data)
    
    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        """
        从JSON字符串创建实体
        
        Args:
            json_str: JSON字符串
            
        Returns:
            T: 实体实例
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def get_cache_key(self, prefix: str = "") -> str:
        """
        生成缓存键
        
        Args:
            prefix: 键前缀
            
        Returns:
            str: 缓存键
        """
        class_name = self.__class__.__name__.lower()
        if prefix:
            return f"{prefix}:{class_name}:{self.id}"
        return f"{class_name}:{self.id}"
    
    def get_hash(self) -> str:
        """
        生成数据哈希
        
        Returns:
            str: 数据哈希值
        """
        # 排除时间戳字段
        data = self.dict(exclude={'created_at', 'updated_at'})
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(json_str.encode()).hexdigest()

class BaseResponse(BaseModel):
    """
    基础响应模型
    
    统一API响应格式
    """
    
    code: int = Field(200, description="响应码")
    message: str = Field("success", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")
    
    class Config:
        """Pydantic配置"""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    @classmethod
    def success(cls, data: Any = None, message: str = "success") -> "BaseResponse":
        """
        创建成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            
        Returns:
            BaseResponse: 成功响应
        """
        return cls(code=200, message=message, data=data)
    
    @classmethod
    def error(cls, code: int = 500, message: str = "error", data: Any = None) -> "BaseResponse":
        """
        创建错误响应
        
        Args:
            code: 错误码
            message: 错误消息
            data: 错误数据
            
        Returns:
            BaseResponse: 错误响应
        """
        return cls(code=code, message=message, data=data)

class PaginatedResponse(BaseResponse):
    """
    分页响应模型
    """
    
    class PaginationInfo(BaseModel):
        """分页信息"""
        page: int = Field(1, description="当前页码")
        page_size: int = Field(20, description="每页数量")
        total: int = Field(0, description="总数量")
        total_pages: int = Field(0, description="总页数")
        has_next: bool = Field(False, description="是否有下一页")
        has_prev: bool = Field(False, description="是否有上一页")
    
    pagination: PaginationInfo = Field(default_factory=PaginationInfo, description="分页信息")
    
    @classmethod
    def create(
        cls,
        data: List[Any],
        page: int,
        page_size: int,
        total: int,
        message: str = "success"
    ) -> "PaginatedResponse":
        """
        创建分页响应
        
        Args:
            data: 数据列表
            page: 当前页码
            page_size: 每页数量
            total: 总数量
            message: 响应消息
            
        Returns:
            PaginatedResponse: 分页响应
        """
        total_pages = (total + page_size - 1) // page_size
        has_next = page < total_pages
        has_prev = page > 1
        
        pagination = cls.PaginationInfo(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
        return cls(
            code=200,
            message=message,
            data=data,
            pagination=pagination
        )

class BaseRepository(ABC, Generic[T]):
    """
    基础仓储类
    
    提供数据访问的通用接口
    """
    
    def __init__(self, entity_class: Type[T]):
        """
        初始化仓储
        
        Args:
            entity_class: 实体类
        """
        self.entity_class = entity_class
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """
        创建实体
        
        Args:
            entity: 实体实例
            
        Returns:
            T: 创建的实体
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """
        根据ID获取实体
        
        Args:
            entity_id: 实体ID
            
        Returns:
            Optional[T]: 实体实例或None
        """
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """
        更新实体
        
        Args:
            entity: 实体实例
            
        Returns:
            T: 更新的实体
        """
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """
        删除实体
        
        Args:
            entity_id: 实体ID
            
        Returns:
            bool: 是否删除成功
        """
        pass
    
    @abstractmethod
    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[T], int]:
        """
        获取实体列表
        
        Args:
            page: 页码
            page_size: 每页数量
            filters: 过滤条件
            
        Returns:
            tuple[List[T], int]: 实体列表和总数量
        """
        pass