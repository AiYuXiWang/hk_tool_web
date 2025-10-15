"""
API日志记录中间件

提供详细的请求/响应日志记录、性能监控、审计跟踪等功能。
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict, Any, Optional, List
import logging
import time
import json
import uuid
from datetime import datetime
import asyncio
from urllib.parse import unquote
import sys
import traceback

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/api.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)
access_logger = logging.getLogger('access')
performance_logger = logging.getLogger('performance')
audit_logger = logging.getLogger('audit')

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志记录中间件
    
    记录所有API请求和响应的详细信息
    """
    
    def __init__(
        self,
        app,
        log_request_body: bool = True,
        log_response_body: bool = True,
        max_body_size: int = 10000,
        sensitive_headers: Optional[List[str]] = None,
        sensitive_fields: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None,
        log_level: str = "INFO"
    ):
        """
        初始化日志记录中间件
        
        Args:
            app: FastAPI应用实例
            log_request_body: 是否记录请求体
            log_response_body: 是否记录响应体
            max_body_size: 最大记录的请求/响应体大小
            sensitive_headers: 敏感请求头列表
            sensitive_fields: 敏感字段列表
            exclude_paths: 排除的路径列表
            log_level: 日志级别
        """
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.max_body_size = max_body_size
        self.sensitive_headers = sensitive_headers or [
            'authorization', 'cookie', 'x-api-key', 'x-auth-token'
        ]
        self.sensitive_fields = sensitive_fields or [
            'password', 'token', 'secret', 'key', 'auth', 'credential'
        ]
        self.exclude_paths = exclude_paths or [
            '/health', '/metrics', '/favicon.ico'
        ]
        
        # 设置日志级别
        log_level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR
        }
        logger.setLevel(log_level_map.get(log_level.upper(), logging.INFO))
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求并记录日志
        
        Args:
            request: 请求对象
            call_next: 下一个中间件或路由处理器
            
        Returns:
            Response: 响应对象
        """
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 检查是否需要排除此路径
        if self._should_exclude_path(request.url.path):
            return await call_next(request)
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 记录请求信息
        await self._log_request(request, request_id)
        
        # 处理请求
        response = None
        error = None
        try:
            response = await call_next(request)
        except Exception as e:
            error = e
            # 创建错误响应
            from fastapi.responses import JSONResponse
            response = JSONResponse(
                content={
                    "code": 500,
                    "message": "Internal Server Error",
                    "data": {"detail": str(e)},
                    "timestamp": datetime.now().isoformat(),
                    "request_id": request_id
                },
                status_code=500
            )
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录响应信息
        await self._log_response(request, response, request_id, process_time, error)
        
        # 记录性能指标
        await self._log_performance(request, response, process_time, request_id)
        
        # 记录审计信息
        await self._log_audit(request, response, request_id, error)
        
        # 添加响应头
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        
        return response
    
    def _should_exclude_path(self, path: str) -> bool:
        """
        检查是否应该排除此路径
        
        Args:
            path: 请求路径
            
        Returns:
            bool: 是否排除
        """
        return any(excluded in path for excluded in self.exclude_paths)
    
    async def _log_request(self, request: Request, request_id: str) -> None:
        """
        记录请求信息
        
        Args:
            request: 请求对象
            request_id: 请求ID
        """
        try:
            # 基本请求信息
            request_info = {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent", ""),
                "content_type": request.headers.get("content-type", ""),
                "content_length": request.headers.get("content-length", "0")
            }
            
            # 记录请求头（过滤敏感信息）
            headers = {}
            for name, value in request.headers.items():
                if name.lower() in self.sensitive_headers:
                    headers[name] = "***MASKED***"
                else:
                    headers[name] = value
            request_info["headers"] = headers
            
            # 记录请求体
            if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
                body = await self._get_request_body(request)
                if body:
                    request_info["body"] = self._mask_sensitive_data(body)
            
            # 记录日志
            access_logger.info(f"REQUEST - {json.dumps(request_info, ensure_ascii=False)}")
            
        except Exception as e:
            logger.error(f"Error logging request: {str(e)}")
    
    async def _log_response(
        self, 
        request: Request, 
        response: Response, 
        request_id: str, 
        process_time: float,
        error: Optional[Exception] = None
    ) -> None:
        """
        记录响应信息
        
        Args:
            request: 请求对象
            response: 响应对象
            request_id: 请求ID
            process_time: 处理时间
            error: 异常信息
        """
        try:
            # 基本响应信息
            response_info = {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "status_code": response.status_code,
                "process_time": f"{process_time:.4f}s",
                "content_type": response.headers.get("content-type", ""),
                "content_length": response.headers.get("content-length", "0")
            }
            
            # 记录响应头
            headers = {}
            for name, value in response.headers.items():
                headers[name] = value
            response_info["headers"] = headers
            
            # 记录响应体
            if self.log_response_body:
                body = await self._get_response_body(response)
                if body:
                    response_info["body"] = self._mask_sensitive_data(body)
            
            # 记录错误信息
            if error:
                response_info["error"] = {
                    "type": type(error).__name__,
                    "message": str(error),
                    "traceback": traceback.format_exc()
                }
            
            # 根据状态码选择日志级别
            if response.status_code >= 500:
                access_logger.error(f"RESPONSE - {json.dumps(response_info, ensure_ascii=False)}")
            elif response.status_code >= 400:
                access_logger.warning(f"RESPONSE - {json.dumps(response_info, ensure_ascii=False)}")
            else:
                access_logger.info(f"RESPONSE - {json.dumps(response_info, ensure_ascii=False)}")
                
        except Exception as e:
            logger.error(f"Error logging response: {str(e)}")
    
    async def _log_performance(
        self, 
        request: Request, 
        response: Response, 
        process_time: float, 
        request_id: str
    ) -> None:
        """
        记录性能指标
        
        Args:
            request: 请求对象
            response: 响应对象
            process_time: 处理时间
            request_id: 请求ID
        """
        try:
            performance_info = {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": process_time,
                "client_ip": self._get_client_ip(request)
            }
            
            # 性能警告阈值
            if process_time > 5.0:  # 超过5秒
                performance_logger.error(f"SLOW_REQUEST - {json.dumps(performance_info, ensure_ascii=False)}")
            elif process_time > 2.0:  # 超过2秒
                performance_logger.warning(f"SLOW_REQUEST - {json.dumps(performance_info, ensure_ascii=False)}")
            else:
                performance_logger.info(f"PERFORMANCE - {json.dumps(performance_info, ensure_ascii=False)}")
                
        except Exception as e:
            logger.error(f"Error logging performance: {str(e)}")
    
    async def _log_audit(
        self, 
        request: Request, 
        response: Response, 
        request_id: str,
        error: Optional[Exception] = None
    ) -> None:
        """
        记录审计信息
        
        Args:
            request: 请求对象
            response: 响应对象
            request_id: 请求ID
            error: 异常信息
        """
        try:
            # 只记录需要审计的操作
            audit_methods = ["POST", "PUT", "PATCH", "DELETE"]
            if request.method not in audit_methods:
                return
            
            audit_info = {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "action": f"{request.method} {request.url.path}",
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent", ""),
                "status_code": response.status_code,
                "success": response.status_code < 400 and error is None
            }
            
            # 添加用户信息（如果有）
            user_id = getattr(request.state, 'user_id', None)
            if user_id:
                audit_info["user_id"] = user_id
            
            # 添加错误信息
            if error:
                audit_info["error"] = {
                    "type": type(error).__name__,
                    "message": str(error)
                }
            
            audit_logger.info(f"AUDIT - {json.dumps(audit_info, ensure_ascii=False)}")
            
        except Exception as e:
            logger.error(f"Error logging audit: {str(e)}")
    
    def _get_client_ip(self, request: Request) -> str:
        """
        获取客户端IP地址
        
        Args:
            request: 请求对象
            
        Returns:
            str: 客户端IP地址
        """
        # 检查代理头
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # 返回直接连接的IP
        return request.client.host if request.client else "unknown"
    
    async def _get_request_body(self, request: Request) -> Optional[str]:
        """
        获取请求体内容
        
        Args:
            request: 请求对象
            
        Returns:
            Optional[str]: 请求体内容
        """
        try:
            body = await request.body()
            if not body:
                return None
            
            # 限制记录的大小
            if len(body) > self.max_body_size:
                return f"<Body too large: {len(body)} bytes>"
            
            # 尝试解码为文本
            try:
                return body.decode('utf-8')
            except UnicodeDecodeError:
                return f"<Binary content: {len(body)} bytes>"
                
        except Exception as e:
            logger.error(f"Error reading request body: {str(e)}")
            return None
    
    async def _get_response_body(self, response: Response) -> Optional[str]:
        """
        获取响应体内容
        
        Args:
            response: 响应对象
            
        Returns:
            Optional[str]: 响应体内容
        """
        try:
            # 只记录JSON响应
            content_type = response.headers.get("content-type", "")
            if "application/json" not in content_type:
                return None
            
            # 获取响应体
            if hasattr(response, 'body'):
                body = response.body
                if isinstance(body, bytes):
                    if len(body) > self.max_body_size:
                        return f"<Body too large: {len(body)} bytes>"
                    try:
                        return body.decode('utf-8')
                    except UnicodeDecodeError:
                        return f"<Binary content: {len(body)} bytes>"
            
            return None
            
        except Exception as e:
            logger.error(f"Error reading response body: {str(e)}")
            return None
    
    def _mask_sensitive_data(self, data: str) -> str:
        """
        屏蔽敏感数据
        
        Args:
            data: 原始数据
            
        Returns:
            str: 屏蔽后的数据
        """
        try:
            # 尝试解析为JSON
            try:
                json_data = json.loads(data)
                masked_data = self._mask_json_data(json_data)
                return json.dumps(masked_data, ensure_ascii=False)
            except json.JSONDecodeError:
                # 不是JSON，直接返回
                return data
                
        except Exception as e:
            logger.error(f"Error masking sensitive data: {str(e)}")
            return data
    
    def _mask_json_data(self, data: Any) -> Any:
        """
        递归屏蔽JSON中的敏感数据
        
        Args:
            data: JSON数据
            
        Returns:
            Any: 屏蔽后的数据
        """
        if isinstance(data, dict):
            masked = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in self.sensitive_fields):
                    masked[key] = "***MASKED***"
                else:
                    masked[key] = self._mask_json_data(value)
            return masked
        elif isinstance(data, list):
            return [self._mask_json_data(item) for item in data]
        else:
            return data

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """
    结构化日志中间件
    
    提供结构化的日志输出，便于日志分析和监控
    """
    
    def __init__(self, app, service_name: str = "api-service"):
        """
        初始化结构化日志中间件
        
        Args:
            app: FastAPI应用实例
            service_name: 服务名称
        """
        super().__init__(app)
        self.service_name = service_name
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求并记录结构化日志
        
        Args:
            request: 请求对象
            call_next: 下一个中间件或路由处理器
            
        Returns:
            Response: 响应对象
        """
        request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
        start_time = time.time()
        
        # 记录请求开始
        logger.info("Request started", extra={
            "service": self.service_name,
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
            "timestamp": datetime.now().isoformat()
        })
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录请求完成
        logger.info("Request completed", extra={
            "service": self.service_name,
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": process_time,
            "timestamp": datetime.now().isoformat()
        })
        
        return response