"""
API响应标准化中间件

统一API响应格式，确保所有API返回一致的数据结构。
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse, FileResponse
from starlette.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Any, Dict
import json
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ResponseStandardizationMiddleware(BaseHTTPMiddleware):
    """
    响应标准化中间件
    
    将所有API响应统一为标准格式：
    {
        "code": 200,
        "message": "success",
        "data": {...},
        "timestamp": "2025-01-27T22:00:00",
        "request_id": "uuid",
        "duration": 0.123
    }
    """
    
    def __init__(self, app, exclude_paths: list = None):
        """
        初始化中间件
        
        Args:
            app: FastAPI应用实例
            exclude_paths: 排除的路径列表
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/docs", "/redoc", "/openapi.json", "/favicon.ico",
            "/health", "/metrics", 
            "/api/download"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求和响应
        
        Args:
            request: 请求对象
            call_next: 下一个中间件或路由处理器
            
        Returns:
            Response: 标准化后的响应
        """
        logger.debug(f"Processing request: {request.url.path}")
        
        # 记录开始时间
        start_time = time.time()
        
        # 生成请求ID
        request_id = getattr(request.state, 'request_id', None)
        if not request_id:
            import uuid
            request_id = str(uuid.uuid4())
            request.state.request_id = request_id
        
        # 检查是否需要排除
        if self._should_exclude(request.url.path):
            response = await call_next(request)
            return response
        
        try:
            # 执行请求
            response = await call_next(request)
            
            logger.debug(f"Response type: {type(response)}")
            
            # 计算处理时间
            duration = time.time() - start_time
            
            # 处理JSON响应（包括JSONResponse和StreamingResponse）
            if (isinstance(response, JSONResponse) or 
                (hasattr(response, 'headers') and 
                 response.headers.get('content-type', '').startswith('application/json'))):
                
                logger.debug("Processing JSON response")
                
                try:
                    # 获取响应内容
                    content = None
                    
                    # 对于JSONResponse，直接从content属性获取
                    if isinstance(response, JSONResponse) and hasattr(response, 'content'):
                        content = response.content
                        logger.debug(f"Got content from JSONResponse.content: {type(content)}")
                    
                    # 对于StreamingResponse，从body_iterator读取
                    else:
                        try:
                            body = b""
                            if hasattr(response, 'body_iterator'):
                                async for chunk in response.body_iterator:
                                    body += chunk
                            elif hasattr(response, 'body'):
                                body = response.body
                            
                            if body:
                                content = json.loads(body.decode())
                                logger.debug(f"Got content from body: {type(content)}")
                        except Exception as e:
                            logger.warning(f"Failed to read response body: {e}")
                    
                    if content is not None:
                        logger.debug(f"Processing content: {content}")
                        
                        # 检查是否已经是标准格式
                        if isinstance(content, dict) and self._is_standard_format(content):
                            logger.debug("Content is already in standard format")
                            # 更新元数据
                            content.update({
                                "request_id": request_id,
                                "duration": round(duration, 3)
                            })
                            # 创建新的响应头，移除可能冲突的头
                            new_headers = dict(response.headers)
                            # 移除Content-Length，让FastAPI自动计算
                            new_headers.pop('content-length', None)
                            new_headers.pop('Content-Length', None)
                            
                            return JSONResponse(
                                content=content,
                                status_code=response.status_code,
                                headers=new_headers
                            )
                        
                        # 包装为标准格式
                        logger.debug("Wrapping content to standard format")
                        standard_content = self._wrap_content(
                            content, response.status_code, request_id, duration
                        )
                        
                        # 创建新的响应头，移除可能冲突的头
                        new_headers = dict(response.headers)
                        # 移除Content-Length，让FastAPI自动计算
                        new_headers.pop('content-length', None)
                        new_headers.pop('Content-Length', None)
                        
                        return JSONResponse(
                            content=standard_content,
                            status_code=200,  # 统一返回200，错误信息在code字段
                            headers=new_headers
                        )
                    else:
                        logger.debug("No content found in response")
                        logger.warning("No content found in response")
                    
                except Exception as e:
                    logger.debug(f"Failed to process JSON response: {e}")
                    logger.warning(f"Failed to process JSON response: {e}")
                    # 如果处理失败，使用原来的方法
                    pass
            
            # 标准化响应（非JSON响应直接透传）
            standardized_response = await self._standardize_response(
                response, request_id, duration
            )
            return standardized_response
            
        except Exception as e:
            # 处理异常
            duration = time.time() - start_time
            logger.error(f"Request {request_id} failed: {str(e)}")
            
            return self._create_error_response(
                code=500,
                message="Internal Server Error",
                request_id=request_id,
                duration=duration,
                error_detail=str(e)
            )
    
    def _should_exclude(self, path: str) -> bool:
        """
        检查路径是否应该排除
        
        Args:
            path: 请求路径
            
        Returns:
            bool: 是否排除
        """
        return any(path.startswith(exclude_path) for exclude_path in self.exclude_paths)
    
    async def _standardize_response(
        self, 
        response: Response, 
        request_id: str, 
        duration: float
    ) -> JSONResponse:
        """
        标准化响应格式
        
        Args:
            response: 原始响应
            request_id: 请求ID
            duration: 处理时间
            
        Returns:
            JSONResponse: 标准化响应
        """
        # 如果已经是JSONResponse且包含标准格式，直接返回
        if isinstance(response, JSONResponse):
            try:
                # 读取响应体 - 修复读取方式
                body = b""
                logger.debug(f"Response type: {type(response)}")
                logger.debug(f"Response has body_iterator: {hasattr(response, 'body_iterator')}")
                logger.debug(f"Response has body: {hasattr(response, 'body')}")
                
                if hasattr(response, 'body_iterator'):
                    async for chunk in response.body_iterator:
                        body += chunk
                elif hasattr(response, 'body'):
                    # 对于FastAPI直接返回的字典，使用body属性
                    body = response.body
                
                logger.debug(f"Body length: {len(body)}")
                logger.debug(f"Body content: {body[:200] if body else 'None'}")
                
                if body:
                    content = json.loads(body.decode())
                    
                    # 检查是否已经是标准格式
                    if self._is_standard_format(content):
                        # 更新元数据
                        content.update({
                            "request_id": request_id,
                            "duration": round(duration, 3)
                        })
                        return JSONResponse(
                            content=content,
                            status_code=response.status_code,
                            headers=dict(response.headers)
                        )
                    
                    # 包装为标准格式
                    standard_content = self._wrap_content(
                        content, response.status_code, request_id, duration
                    )
                    
                    return JSONResponse(
                        content=standard_content,
                        status_code=200,  # 统一返回200，错误信息在code字段
                        headers=dict(response.headers)
                    )
                else:
                    # 如果没有响应体，但是JSONResponse，可能是空响应
                    standard_content = self._wrap_content(
                        None, response.status_code, request_id, duration
                    )
                    
                    return JSONResponse(
                        content=standard_content,
                        status_code=200,
                        headers=dict(response.headers)
                    )
                    
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                # 如果不是JSON，创建标准错误响应
                logger.warning(f"Failed to decode JSON response: {e}")
                pass
        
        # 非JSON响应（包括文件/流）直接透传，避免破坏下载等二进制内容
        try:
            if isinstance(response, (FileResponse, StreamingResponse)):
                return response
        except Exception:
            # 类型判断失败时也直接透传
            return response
        return response
    
    def _is_standard_format(self, content: Dict[str, Any]) -> bool:
        """
        检查是否已经是标准格式
        
        Args:
            content: 响应内容
            
        Returns:
            bool: 是否标准格式
        """
        required_fields = {"code", "message", "timestamp"}
        return all(field in content for field in required_fields)
    
    def _wrap_content(
        self, 
        content: Any, 
        status_code: int, 
        request_id: str, 
        duration: float
    ) -> Dict[str, Any]:
        """
        包装内容为标准格式
        
        Args:
            content: 原始内容
            status_code: HTTP状态码
            request_id: 请求ID
            duration: 处理时间
            
        Returns:
            Dict[str, Any]: 标准格式内容
        """
        # 确定响应码和消息
        if status_code >= 400:
            code = status_code
            message = self._get_error_message(status_code)
            data = content if isinstance(content, dict) else {"detail": content}
        else:
            code = 200
            message = "success"
            data = content
        
        return {
            "code": code,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "duration": round(duration, 3)
        }
    
    def _create_error_response(
        self,
        code: int,
        message: str,
        request_id: str,
        duration: float,
        error_detail: str = None
    ) -> JSONResponse:
        """
        创建错误响应
        
        Args:
            code: 错误码
            message: 错误消息
            request_id: 请求ID
            duration: 处理时间
            error_detail: 错误详情
            
        Returns:
            JSONResponse: 错误响应
        """
        content = {
            "code": code,
            "message": message,
            "data": {"detail": error_detail} if error_detail else None,
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "duration": round(duration, 3)
        }
        
        return JSONResponse(
            content=content,
            status_code=200  # 统一返回200，错误信息在code字段
        )
    
    def _get_error_message(self, status_code: int) -> str:
        """
        根据状态码获取错误消息
        
        Args:
            status_code: HTTP状态码
            
        Returns:
            str: 错误消息
        """
        error_messages = {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            422: "Validation Error",
            429: "Too Many Requests",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout"
        }
        
        return error_messages.get(status_code, f"HTTP {status_code}")

class ResponseCompressionMiddleware(BaseHTTPMiddleware):
    """
    响应压缩中间件
    
    对大型响应进行压缩以减少传输时间
    """
    
    def __init__(self, app, min_size: int = 1024):
        """
        初始化压缩中间件
        
        Args:
            app: FastAPI应用实例
            min_size: 最小压缩大小（字节）
        """
        super().__init__(app)
        self.min_size = min_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求和响应压缩
        
        Args:
            request: 请求对象
            call_next: 下一个中间件或路由处理器
            
        Returns:
            Response: 可能压缩的响应
        """
        response = await call_next(request)
        
        # 检查是否支持压缩
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding:
            return response
        
        # 检查响应类型
        if not isinstance(response, JSONResponse):
            return response
        
        # 检查响应大小
        try:
            # 获取响应体
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            if len(body) < self.min_size:
                # 重新创建响应（因为body_iterator已被消费）
                return JSONResponse(
                    content=json.loads(body.decode()),
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
            
            # 压缩响应
            import gzip
            compressed_body = gzip.compress(body)
            
            # 创建压缩响应
            headers = dict(response.headers)
            headers["content-encoding"] = "gzip"
            headers["content-length"] = str(len(compressed_body))
            
            return Response(
                content=compressed_body,
                status_code=response.status_code,
                headers=headers,
                media_type=response.media_type
            )
            
        except Exception as e:
            logger.warning(f"Response compression failed: {str(e)}")
            return response