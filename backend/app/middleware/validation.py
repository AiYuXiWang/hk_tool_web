"""
API请求验证中间件

提供请求参数验证、文件上传验证、安全检查等功能。
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict, Any, List, Optional, Set
import logging
import re
import json
from datetime import datetime
import mimetypes
from urllib.parse import unquote

logger = logging.getLogger(__name__)

class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    请求验证中间件
    
    验证请求参数、文件上传、安全检查等
    """
    
    def __init__(
        self, 
        app,
        max_content_length: int = 50 * 1024 * 1024,  # 50MB
        allowed_file_types: Optional[Set[str]] = None,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        enable_sql_injection_check: bool = True,
        enable_xss_check: bool = True,
        enable_path_traversal_check: bool = True,
        whitelist_paths: Optional[List[str]] = None
    ):
        """
        初始化请求验证中间件
        
        Args:
            app: FastAPI应用实例
            max_content_length: 最大请求内容长度
            allowed_file_types: 允许的文件类型
            max_file_size: 最大文件大小
            enable_sql_injection_check: 是否启用SQL注入检查
            enable_xss_check: 是否启用XSS检查
            enable_path_traversal_check: 是否启用路径遍历检查
            whitelist_paths: 跳过安全检查的路径白名单
        """
        super().__init__(app)
        self.max_content_length = max_content_length
        self.allowed_file_types = allowed_file_types or {
            '.xlsx', '.xls', '.csv', '.json', '.txt', '.pdf', '.doc', '.docx'
        }
        self.max_file_size = max_file_size
        self.enable_sql_injection_check = enable_sql_injection_check
        self.enable_xss_check = enable_xss_check
        self.enable_path_traversal_check = enable_path_traversal_check
        self.whitelist_paths = whitelist_paths or []
        
        # SQL注入检测模式
        self.sql_injection_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
            # 仅在行首或空白后出现的注释标记才匹配，避免误判像 1#2#LDB 这种业务编码
            r"((^|\s)--|(^|\s)#|/\*|\*/)",
            r"(\bUNION\s+SELECT\b)",
            r"(\bINTO\s+OUTFILE\b)",
            r"(\bLOAD_FILE\b)"
        ]
        
        # XSS检测模式
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            # 仅在HTML标签属性环境中匹配 on* 事件处理器，避免如 station_ip= 误判
            r"(<[^>]+\s)on[a-z]+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
            r"expression\s*\(",
            r"vbscript:",
            r"data:text/html"
        ]
        
        # 路径遍历检测模式
        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e%5c",
            r"..%2f",
            r"..%5c"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """
        处理请求验证
        
        Args:
            request: 请求对象
            call_next: 下一个中间件或路由处理器
            
        Returns:
            JSONResponse: 响应或错误响应
        """
        try:
            # 检查是否在白名单路径中，如果是则跳过安全检查
            request_path = str(request.url.path)
            # 规范化路径，确保尾部斜杠不影响匹配
            normalized_path = request_path.rstrip('/')
            normalized_whitelist = [p.rstrip('/') for p in self.whitelist_paths]
            if any(normalized_path == p or normalized_path.startswith(p + '/') for p in normalized_whitelist):
                logger.info(f"Request path {request_path} is in whitelist, skipping security checks")
                response = await call_next(request)
                return response

            # 针对实时点位查询GET请求的额外保护：强制跳过安全检查
            if request.method == "GET" and normalized_path == "/control/points/real-time":
                logger.info(f"Force-skip security checks for {request.method} {request_path}")
                response = await call_next(request)
                return response
            
            # 检查请求内容长度
            await self._check_content_length(request)
            
            # 检查请求路径
            await self._check_request_path(request)
            
            # 检查查询参数
            await self._check_query_params(request)
            
            # 检查请求头
            await self._check_headers(request)
            
            # 对于POST/PUT/PATCH请求，检查请求体
            if request.method in ["POST", "PUT", "PATCH"]:
                await self._check_request_body(request)
            
            # 继续处理请求
            response = await call_next(request)
            return response
            
        except HTTPException as e:
            return await self._create_validation_error_response(request, str(e.detail))
        except Exception as e:
            logger.error(f"Validation middleware error: {str(e)}")
            return await self._create_validation_error_response(request, "请求验证失败")
    
    async def _check_content_length(self, request: Request) -> None:
        """
        检查请求内容长度
        
        Args:
            request: 请求对象
            
        Raises:
            HTTPException: 如果内容长度超过限制
        """
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                if length > self.max_content_length:
                    raise HTTPException(
                        status_code=413,
                        detail=f"请求内容过大，最大允许 {self.max_content_length / 1024 / 1024:.1f}MB"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="无效的Content-Length头"
                )
    
    async def _check_request_path(self, request: Request) -> None:
        """
        检查请求路径
        
        Args:
            request: 请求对象
            
        Raises:
            HTTPException: 如果路径包含恶意内容
        """
        path = unquote(str(request.url.path))
        
        # 检查路径遍历
        if self.enable_path_traversal_check:
            for pattern in self.path_traversal_patterns:
                if re.search(pattern, path, re.IGNORECASE):
                    logger.warning(f"Path traversal attempt detected: {path}")
                    raise HTTPException(
                        status_code=400,
                        detail="请求路径包含非法字符"
                    )
        
        # 检查路径长度
        if len(path) > 2048:
            raise HTTPException(
                status_code=414,
                detail="请求路径过长"
            )
    
    async def _check_query_params(self, request: Request) -> None:
        """
        检查查询参数
        
        Args:
            request: 请求对象
            
        Raises:
            HTTPException: 如果参数包含恶意内容
        """
        # 对实时点位查询路径跳过参数安全检查，防止业务编码被误判
        request_path = str(request.url.path).rstrip('/')
        if request_path == "/control/points/real-time":
            return

        query_params = dict(request.query_params)
        
        for key, value in query_params.items():
            # 检查参数名和值的长度
            if len(key) > 100:
                raise HTTPException(
                    status_code=400,
                    detail=f"查询参数名过长: {key[:50]}..."
                )
            
            if len(value) > 1000:
                raise HTTPException(
                    status_code=400,
                    detail=f"查询参数值过长: {key}"
                )
            
            # 安全检查
            await self._check_security_threats(f"{key}={value}", "query parameter")
    
    async def _check_headers(self, request: Request) -> None:
        """
        检查请求头
        
        Args:
            request: 请求对象
            
        Raises:
            HTTPException: 如果请求头包含恶意内容
        """
        # 检查User-Agent
        user_agent = request.headers.get("user-agent", "")
        if len(user_agent) > 500:
            raise HTTPException(
                status_code=400,
                detail="User-Agent头过长"
            )
        
        # 检查Referer
        referer = request.headers.get("referer", "")
        if referer and len(referer) > 1000:
            raise HTTPException(
                status_code=400,
                detail="Referer头过长"
            )
        
        # 检查自定义头
        for name, value in request.headers.items():
            if name.lower().startswith("x-"):
                if len(value) > 1000:
                    raise HTTPException(
                        status_code=400,
                        detail=f"自定义头值过长: {name}"
                    )
                
                # 安全检查
                await self._check_security_threats(value, f"header {name}")
    
    async def _check_request_body(self, request: Request) -> None:
        """
        检查请求体
        
        Args:
            request: 请求对象
            
        Raises:
            HTTPException: 如果请求体包含恶意内容
        """
        content_type = request.headers.get("content-type", "")
        
        # 检查JSON请求体
        if "application/json" in content_type:
            await self._check_json_body(request)
        
        # 检查表单请求体
        elif "application/x-www-form-urlencoded" in content_type:
            await self._check_form_body(request)
        
        # 检查文件上传
        elif "multipart/form-data" in content_type:
            await self._check_multipart_body(request)
    
    async def _check_json_body(self, request: Request) -> None:
        """
        检查JSON请求体
        
        Args:
            request: 请求对象
            
        Raises:
            HTTPException: 如果JSON包含恶意内容
        """
        try:
            # 获取原始请求体
            body = await request.body()
            if not body:
                return
            
            # 检查JSON大小
            if len(body) > self.max_content_length:
                raise HTTPException(
                    status_code=413,
                    detail="JSON请求体过大"
                )
            
            # 解析JSON
            try:
                json_data = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="无效的JSON格式"
                )
            
            # 递归检查JSON内容
            await self._check_json_content(json_data)
            
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="请求体编码错误"
            )
    
    async def _check_json_content(self, data: Any, path: str = "") -> None:
        """
        递归检查JSON内容
        
        Args:
            data: JSON数据
            path: 当前路径
            
        Raises:
            HTTPException: 如果内容包含恶意数据
        """
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                # 检查键名
                if len(str(key)) > 100:
                    raise HTTPException(
                        status_code=400,
                        detail=f"JSON键名过长: {current_path}"
                    )
                
                await self._check_json_content(value, current_path)
        
        elif isinstance(data, list):
            if len(data) > 1000:
                raise HTTPException(
                    status_code=400,
                    detail=f"JSON数组过大: {path}"
                )
            
            for i, item in enumerate(data):
                await self._check_json_content(item, f"{path}[{i}]")
        
        elif isinstance(data, str):
            # 检查字符串长度
            if len(data) > 10000:
                raise HTTPException(
                    status_code=400,
                    detail=f"JSON字符串过长: {path}"
                )
            
            # 安全检查
            await self._check_security_threats(data, f"JSON field {path}")
    
    async def _check_form_body(self, request: Request) -> None:
        """
        检查表单请求体
        
        Args:
            request: 请求对象
            
        Raises:
            HTTPException: 如果表单包含恶意内容
        """
        try:
            form_data = await request.form()
            
            for key, value in form_data.items():
                # 检查字段名长度
                if len(key) > 100:
                    raise HTTPException(
                        status_code=400,
                        detail=f"表单字段名过长: {key[:50]}..."
                    )
                
                # 检查字段值
                if hasattr(value, 'read'):  # 文件对象
                    await self._check_uploaded_file(value, key)
                else:  # 普通字段
                    if len(str(value)) > 10000:
                        raise HTTPException(
                            status_code=400,
                            detail=f"表单字段值过长: {key}"
                        )
                    
                    await self._check_security_threats(str(value), f"form field {key}")
        
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=400,
                detail="表单数据解析失败"
            )
    
    async def _check_multipart_body(self, request: Request) -> None:
        """
        检查多部分请求体（文件上传）
        
        Args:
            request: 请求对象
            
        Raises:
            HTTPException: 如果上传内容包含恶意数据
        """
        try:
            form_data = await request.form()
            
            for key, value in form_data.items():
                if hasattr(value, 'read'):  # 文件对象
                    await self._check_uploaded_file(value, key)
                else:  # 普通字段
                    await self._check_security_threats(str(value), f"multipart field {key}")
        
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=400,
                detail="文件上传数据解析失败"
            )
    
    async def _check_uploaded_file(self, file, field_name: str) -> None:
        """
        检查上传的文件
        
        Args:
            file: 上传的文件对象
            field_name: 字段名
            
        Raises:
            HTTPException: 如果文件不符合要求
        """
        # 检查文件名
        filename = getattr(file, 'filename', '')
        if not filename:
            raise HTTPException(
                status_code=400,
                detail=f"文件名不能为空: {field_name}"
            )
        
        if len(filename) > 255:
            raise HTTPException(
                status_code=400,
                detail=f"文件名过长: {field_name}"
            )
        
        # 检查文件扩展名
        file_ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
        if file_ext not in self.allowed_file_types:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file_ext}，支持的类型: {', '.join(self.allowed_file_types)}"
            )
        
        # 检查文件大小
        file_size = getattr(file, 'size', 0)
        if file_size > self.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"文件过大: {filename}，最大允许 {self.max_file_size / 1024 / 1024:.1f}MB"
            )
        
        # 检查MIME类型
        content_type = getattr(file, 'content_type', '')
        if content_type:
            expected_type, _ = mimetypes.guess_type(filename)
            if expected_type and not content_type.startswith(expected_type.split('/')[0]):
                logger.warning(f"MIME type mismatch: {filename}, expected: {expected_type}, got: {content_type}")
    
    async def _check_security_threats(self, content: str, context: str) -> None:
        """
        检查安全威胁
        
        Args:
            content: 要检查的内容
            context: 内容上下文
            
        Raises:
            HTTPException: 如果发现安全威胁
        """
        # SQL注入检查
        if self.enable_sql_injection_check:
            for pattern in self.sql_injection_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    logger.warning(f"SQL injection attempt detected in {context}: {content[:100]}...")
                    raise HTTPException(
                        status_code=400,
                        detail="请求包含可疑的SQL语句"
                    )
        
        # XSS检查
        if self.enable_xss_check:
            for pattern in self.xss_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    logger.warning(f"XSS attempt detected in {context}: {content[:100]}...")
                    raise HTTPException(
                        status_code=400,
                        detail="请求包含可疑的脚本内容"
                    )
        
        # 路径遍历检查
        if self.enable_path_traversal_check:
            for pattern in self.path_traversal_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    logger.warning(f"Path traversal attempt detected in {context}: {content[:100]}...")
                    raise HTTPException(
                        status_code=400,
                        detail="请求包含可疑的路径字符"
                    )
    
    async def _create_validation_error_response(
        self, 
        request: Request, 
        detail: str
    ) -> JSONResponse:
        """
        创建验证错误响应
        
        Args:
            request: 请求对象
            detail: 错误详情
            
        Returns:
            JSONResponse: 错误响应
        """
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        content = {
            "code": 400,
            "message": "Validation Error",
            "data": {
                "detail": detail,
                "error_type": "ValidationError",
                "path": str(request.url.path),
                "method": request.method
            },
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id
        }
        
        return JSONResponse(
            content=content,
            status_code=200
        )