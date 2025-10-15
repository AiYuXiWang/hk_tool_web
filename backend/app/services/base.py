"""
基础服务类

定义服务层的基础接口和通用功能。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from datetime import datetime
import logging
from backend.app.core.config import get_config

config = get_config()
logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseService(ABC, Generic[T]):
    """基础服务类"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
    
    def log_operation(self, operation: str, **kwargs) -> None:
        """记录操作日志"""
        self.logger.info(f"执行操作: {operation}", extra=kwargs)
    
    def log_error(self, operation: str, error: Exception, **kwargs) -> None:
        """记录错误日志"""
        self.logger.error(
            f"操作失败: {operation} - {str(error)}", 
            exc_info=True,
            extra=kwargs
        )
    
    def validate_input(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """验证输入数据"""
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            raise ValueError(f"缺少必需字段: {', '.join(missing_fields)}")
    
    def format_response(self, data: Any, message: str = "操作成功") -> Dict[str, Any]:
        """格式化响应数据"""
        return {
            "success": True,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    def format_error_response(self, error: str, code: int = 500) -> Dict[str, Any]:
        """格式化错误响应"""
        return {
            "success": False,
            "error": error,
            "code": code,
            "timestamp": datetime.now().isoformat()
        }


class CacheableService(BaseService[T]):
    """支持缓存的服务类"""
    
    def __init__(self):
        super().__init__()
        self.cache_enabled = config.get("cache.backend") != "dummy"
        self.cache_timeout = config.get("cache.default_timeout", 300)
    
    def get_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        import hashlib
        key_parts = [prefix] + [str(arg) for arg in args]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        
        key_string = ":".join(key_parts)
        return f"{config.get('cache.key_prefix', 'app:')}{hashlib.md5(key_string.encode()).hexdigest()}"
    
    async def get_from_cache(self, key: str) -> Optional[Any]:
        """从缓存获取数据"""
        if not self.cache_enabled:
            return None
        
        try:
            # 这里应该集成实际的缓存系统（Redis等）
            # 暂时返回None，表示缓存未命中
            return None
        except Exception as e:
            self.logger.warning(f"缓存读取失败: {e}")
            return None
    
    async def set_cache(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """设置缓存数据"""
        if not self.cache_enabled:
            return
        
        try:
            # 这里应该集成实际的缓存系统（Redis等）
            # 暂时跳过缓存设置
            pass
        except Exception as e:
            self.logger.warning(f"缓存设置失败: {e}")
    
    async def delete_cache(self, key: str) -> None:
        """删除缓存数据"""
        if not self.cache_enabled:
            return
        
        try:
            # 这里应该集成实际的缓存系统（Redis等）
            # 暂时跳过缓存删除
            pass
        except Exception as e:
            self.logger.warning(f"缓存删除失败: {e}")


class AsyncService(BaseService[T]):
    """异步服务基类"""
    
    async def execute_with_retry(
        self, 
        operation: callable, 
        max_retries: int = 3, 
        delay: float = 1.0,
        *args, 
        **kwargs
    ) -> Any:
        """带重试的异步操作执行"""
        import asyncio
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    self.logger.warning(
                        f"操作失败，第{attempt + 1}次重试: {str(e)}"
                    )
                    await asyncio.sleep(delay * (2 ** attempt))  # 指数退避
                else:
                    self.logger.error(f"操作最终失败: {str(e)}")
        
        raise last_exception
    
    async def execute_batch(
        self, 
        operations: List[callable], 
        max_concurrent: int = 10
    ) -> List[Any]:
        """批量执行异步操作"""
        import asyncio
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_with_semaphore(operation):
            async with semaphore:
                return await operation()
        
        tasks = [execute_with_semaphore(op) for op in operations]
        return await asyncio.gather(*tasks, return_exceptions=True)


class ServiceRegistry:
    """服务注册表"""
    
    _services: Dict[str, BaseService] = {}
    
    @classmethod
    def register(cls, name: str, service: BaseService) -> None:
        """注册服务"""
        cls._services[name] = service
        logger.info(f"服务已注册: {name}")
    
    @classmethod
    def get(cls, name: str) -> Optional[BaseService]:
        """获取服务"""
        return cls._services.get(name)
    
    @classmethod
    def list_services(cls) -> List[str]:
        """列出所有已注册的服务"""
        return list(cls._services.keys())
    
    @classmethod
    def unregister(cls, name: str) -> None:
        """注销服务"""
        if name in cls._services:
            del cls._services[name]
            logger.info(f"服务已注销: {name}")


def service_method(cache_timeout: Optional[int] = None):
    """服务方法装饰器"""
    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            operation_name = f"{self.__class__.__name__}.{func.__name__}"
            
            try:
                # 记录操作开始
                self.log_operation(operation_name, args=args, kwargs=kwargs)
                
                # 检查缓存（如果是CacheableService）
                if isinstance(self, CacheableService) and cache_timeout:
                    cache_key = self.get_cache_key(operation_name, *args, **kwargs)
                    cached_result = await self.get_from_cache(cache_key)
                    if cached_result is not None:
                        return cached_result
                
                # 执行实际操作
                result = await func(self, *args, **kwargs)
                
                # 设置缓存（如果是CacheableService）
                if isinstance(self, CacheableService) and cache_timeout:
                    await self.set_cache(cache_key, result, cache_timeout)
                
                return result
                
            except Exception as e:
                self.log_error(operation_name, e, args=args, kwargs=kwargs)
                raise
        
        return wrapper
    return decorator