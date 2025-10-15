"""
API错误处理中间件

统一处理API异常，提供友好的错误响应和详细的错误日志。
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Callable, Dict, Any, Optional
import logging
import traceback
import sys
from datetime import datetime
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    错误处理中间件
    
    捕获和处理所有类型的异常，返回统一格式的错误响应
    """
    
    def __init__(self, app, debug: bool = False):
        """
        初始化错误处理中间件
        
        Args:
            app: FastAPI应用实例
            debug: 是否启用调试模式
        """
        super().__init__(app)
        self.debug = debug
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """
        处理请求并捕获异常
        
        Args:
            request: 请求对象
            call_next: 下一个中间件或路由处理器
            
        Returns:
            JSONResponse: 响应或错误响应
        """
        try:
            response = await call_next(request)
            return response
            
        except HTTPException as e:
            return await self._handle_http_exception(request, e)
            
        except StarletteHTTPException as e:
            return await self._handle_starlette_http_exception(request, e)
            
        except RequestValidationError as e:
            return await self._handle_validation_error(request, e)
            
        except ValidationError as e:
            return await self._handle_pydantic_validation_error(request, e)
            
        except ValueError as e:
            return await self._handle_value_error(request, e)
            
        except PermissionError as e:
            return await self._handle_permission_error(request, e)
            
        except FileNotFoundError as e:
            return await self._handle_file_not_found_error(request, e)
            
        except ConnectionError as e:
            return await self._handle_connection_error(request, e)
            
        except TimeoutError as e:
            return await self._handle_timeout_error(request, e)
            
        except Exception as e:
            return await self._handle_generic_exception(request, e)
    
    async def _handle_http_exception(
        self, 
        request: Request, 
        exc: HTTPException
    ) -> JSONResponse:
        """
        处理FastAPI HTTP异常
        
        Args:
            request: 请求对象
            exc: HTTP异常
            
        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        logger.warning(
            f"HTTP Exception - Request ID: {request_id}, "
            f"Status: {exc.status_code}, Detail: {exc.detail}"
        )
        
        return self._create_error_response(
            request=request,
            code=exc.status_code,
            message=self._get_error_message(exc.status_code),
            detail=exc.detail,
            error_type="HTTPException"
        )
    
    async def _handle_starlette_http_exception(
        self, 
        request: Request, 
        exc: StarletteHTTPException
    ) -> JSONResponse:
        """
        处理Starlette HTTP异常
        
        Args:
            request: 请求对象
            exc: Starlette HTTP异常
            
        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        logger.warning(
            f"Starlette HTTP Exception - Request ID: {request_id}, "
            f"Status: {exc.status_code}, Detail: {exc.detail}"
        )
        
        return self._create_error_response(
            request=request,
            code=exc.status_code,
            message=self._get_error_message(exc.status_code),
            detail=exc.detail,
            error_type="StarletteHTTPException"
        )
    
    async def _handle_validation_error(
        self, 
        request: Request, 
        exc: RequestValidationError
    ) -> JSONResponse:
        """
        处理请求验证错误
        
        Args:
            request: 请求对象
            exc: 验证错误
            
        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # 格式化验证错误
        errors = []
        for error in exc.errors():
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field_path,
                "message": error["msg"],
                "type": error["type"],
                "input": error.get("input")
            })
        
        logger.warning(
            f"Validation Error - Request ID: {request_id}, "
            f"Errors: {len(errors)}, Details: {errors}"
        )
        
        return self._create_error_response(
            request=request,
            code=422,
            message="Validation Error",
            detail="请求参数验证失败",
            error_type="ValidationError",
            validation_errors=errors
        )
    
    async def _handle_pydantic_validation_error(
        self, 
        request: Request, 
        exc: ValidationError
    ) -> JSONResponse:
        """
        处理Pydantic验证错误
        
        Args:
            request: 请求对象
            exc: Pydantic验证错误
            
        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # 格式化验证错误
        errors = []
        for error in exc.errors():
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field_path,
                "message": error["msg"],
                "type": error["type"]
            })
        
        logger.warning(
            f"Pydantic Validation Error - Request ID: {request_id}, "
            f"Errors: {len(errors)}, Details: {errors}"
        )
        
        return self._create_error_response(
            request=request,
            code=422,
            message="Data Validation Error",
            detail="数据验证失败",
            error_type="PydanticValidationError",
            validation_errors=errors
        )
    
    async def _handle_value_error(
        self, 
        request: Request, 
        exc: ValueError
    ) -> JSONResponse:
        """
        处理值错误
        
        Args:
            request: 请求对象
            exc: 值错误
            
        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        logger.warning(
            f"Value Error - Request ID: {request_id}, "
            f"Error: {str(exc)}"
        )
        
        return self._create_error_response(
            request=request,
            code=400,
            message="Bad Request",
            detail=str(exc),
            error_type="ValueError"
        )
    
    async def _handle_permission_error(
        self, 
        request: Request, 
        exc: PermissionError
    ) -> JSONResponse:
        """
        处理权限错误
        
        Args:
            request: 请求对象
            exc: 权限错误
            
        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        logger.warning(
            f"Permission Error - Request ID: {request_id}, "
            f"Error: {str(exc)}"
        )
        
        return self._create_error_response(
            request=request,
            code=403,
            message="Forbidden",
            detail="权限不足",
            error_type="PermissionError"
        )
    
    async def _handle_file_not_found_error(
        self, 
        request: Request, 
        exc: FileNotFoundError
    ) -> JSONResponse:
        """
        处理文件未找到错误
        
        Args:
            request: 请求对象
            exc: 文件未找到错误
            
        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        logger.warning(
            f"File Not Found Error - Request ID: {request_id}, "
            f"Error: {str(exc)}"
        )
        
        return self._create_error_response(
            request=request,
            code=404,
            message="Not Found",
            detail="请求的资源不存在",
            error_type="FileNotFoundError"
        )
    
    async def _handle_connection_error(
        self, 
        request: Request, 
        exc: ConnectionError
    ) -> JSONResponse:
        """
        处理连接错误
        
        Args:
            request: 请求对象
            exc: 连接错误
            
        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        logger.error(
            f"Connection Error - Request ID: {request_id}, "
            f"Error: {str(exc)}"
        )
        
        return self._create_error_response(
            request=request,
            code=503,
            message="Service Unavailable",
            detail="服务暂时不可用，请稍后重试",
            error_type="ConnectionError"
        )
    
    async def _handle_timeout_error(
        self, 
        request: Request, 
        exc: TimeoutError
    ) -> JSONResponse:
        """
        处理超时错误
        
        Args:
            request: 请求对象
            exc: 超时错误
            
        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        logger.error(
            f"Timeout Error - Request ID: {request_id}, "
            f"Error: {str(exc)}"
        )
        
        return self._create_error_response(
            request=request,
            code=504,
            message="Gateway Timeout",
            detail="请求超时，请稍后重试",
            error_type="TimeoutError"
        )
    
    async def _handle_generic_exception(
        self, 
        request: Request, 
        exc: Exception
    ) -> JSONResponse:
        """
        处理通用异常
        
        Args:
            request: 请求对象
            exc: 异常
            
        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # 记录详细错误信息
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        tb_text = ''.join(tb_lines)
        
        logger.error(
            f"Unhandled Exception - Request ID: {request_id}, "
            f"Type: {type(exc).__name__}, "
            f"Error: {str(exc)}, "
            f"Traceback: {tb_text}"
        )
        
        # 在调试模式下返回详细错误信息
        detail = str(exc) if self.debug else "服务器内部错误"
        extra_data = {"traceback": tb_text} if self.debug else None
        
        return self._create_error_response(
            request=request,
            code=500,
            message="Internal Server Error",
            detail=detail,
            error_type=type(exc).__name__,
            extra_data=extra_data
        )
    
    def _create_error_response(
        self,
        request: Request,
        code: int,
        message: str,
        detail: str,
        error_type: str,
        validation_errors: Optional[list] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """
        创建标准错误响应
        
        Args:
            request: 请求对象
            code: 错误码
            message: 错误消息
            detail: 错误详情
            error_type: 错误类型
            validation_errors: 验证错误列表
            extra_data: 额外数据
            
        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        error_data = {
            "detail": detail,
            "error_type": error_type,
            "path": str(request.url.path),
            "method": request.method
        }
        
        if validation_errors:
            error_data["validation_errors"] = validation_errors
        
        if extra_data:
            error_data.update(extra_data)
        
        content = {
            "code": code,
            "message": message,
            "data": error_data,
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id
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

class CustomExceptionHandler:
    """
    自定义异常处理器
    
    为特定异常类型提供专门的处理逻辑
    """
    
    @staticmethod
    def database_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        数据库错误处理器
        
        Args:
            request: 请求对象
            exc: 数据库异常
            
        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        logger.error(
            f"Database Error - Request ID: {request_id}, "
            f"Error: {str(exc)}"
        )
        
        return JSONResponse(
            content={
                "code": 503,
                "message": "Database Error",
                "data": {
                    "detail": "数据库连接异常，请稍后重试",
                    "error_type": "DatabaseError"
                },
                "timestamp": datetime.now().isoformat(),
                "request_id": request_id
            },
            status_code=200
        )
    
    @staticmethod
    def business_logic_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        业务逻辑错误处理器
        
        Args:
            request: 请求对象
            exc: 业务逻辑异常
            
        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        logger.warning(
            f"Business Logic Error - Request ID: {request_id}, "
            f"Error: {str(exc)}"
        )
        
        return JSONResponse(
            content={
                "code": 400,
                "message": "Business Logic Error",
                "data": {
                    "detail": str(exc),
                    "error_type": "BusinessLogicError"
                },
                "timestamp": datetime.now().isoformat(),
                "request_id": request_id
            },
            status_code=200
        )