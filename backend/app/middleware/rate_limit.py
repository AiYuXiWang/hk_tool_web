"""
API限流中间件

提供基于IP、用户、API端点的限流功能，防止API滥用。
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict, Any, Optional, List, Tuple
import logging
import time
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict, deque
import hashlib
import json

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    限流中间件
    
    支持多种限流策略：固定窗口、滑动窗口、令牌桶等
    """
    
    def __init__(
        self,
        app,
        default_rate_limit: str = "100/minute",
        rate_limit_rules: Optional[Dict[str, str]] = None,
        storage_backend: str = "memory",
        redis_url: Optional[str] = None,
        enable_user_rate_limit: bool = True,
        enable_ip_rate_limit: bool = True,
        enable_endpoint_rate_limit: bool = True,
        whitelist_ips: Optional[List[str]] = None,
        blacklist_ips: Optional[List[str]] = None
    ):
        """
        初始化限流中间件
        
        Args:
            app: FastAPI应用实例
            default_rate_limit: 默认限流规则 (格式: "数量/时间单位")
            rate_limit_rules: 特定路径的限流规则
            storage_backend: 存储后端 ("memory" 或 "redis")
            redis_url: Redis连接URL
            enable_user_rate_limit: 是否启用用户级限流
            enable_ip_rate_limit: 是否启用IP级限流
            enable_endpoint_rate_limit: 是否启用端点级限流
            whitelist_ips: IP白名单
            blacklist_ips: IP黑名单
        """
        super().__init__(app)
        self.default_rate_limit = self._parse_rate_limit(default_rate_limit)
        self.rate_limit_rules = {}
        
        # 解析限流规则
        if rate_limit_rules:
            for path, rule in rate_limit_rules.items():
                self.rate_limit_rules[path] = self._parse_rate_limit(rule)
        
        self.storage_backend = storage_backend
        self.redis_url = redis_url
        self.enable_user_rate_limit = enable_user_rate_limit
        self.enable_ip_rate_limit = enable_ip_rate_limit
        self.enable_endpoint_rate_limit = enable_endpoint_rate_limit
        self.whitelist_ips = set(whitelist_ips or [])
        self.blacklist_ips = set(blacklist_ips or [])
        
        # 内存存储
        self.memory_storage = defaultdict(lambda: defaultdict(deque))
        self.cleanup_interval = 300  # 5分钟清理一次过期数据
        self.last_cleanup = time.time()
        
        # Redis存储（如果启用）
        self.redis_client = None
        if storage_backend == "redis" and redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(redis_url)
            except ImportError:
                logger.warning("Redis not available, falling back to memory storage")
                self.storage_backend = "memory"
    
    def _parse_rate_limit(self, rate_limit: str) -> Tuple[int, int]:
        """
        解析限流规则
        
        Args:
            rate_limit: 限流规则字符串 (如 "100/minute")
            
        Returns:
            Tuple[int, int]: (请求数量, 时间窗口秒数)
        """
        try:
            count, period = rate_limit.split('/')
            count = int(count)
            
            period_map = {
                'second': 1,
                'minute': 60,
                'hour': 3600,
                'day': 86400
            }
            
            period_seconds = period_map.get(period.lower(), 60)
            return count, period_seconds
            
        except (ValueError, KeyError):
            logger.error(f"Invalid rate limit format: {rate_limit}")
            return 100, 60  # 默认值
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """
        处理请求并应用限流
        
        Args:
            request: 请求对象
            call_next: 下一个中间件或路由处理器
            
        Returns:
            JSONResponse: 响应或限流错误响应
        """
        client_ip = self._get_client_ip(request)
        
        # 检查IP黑名单
        if client_ip in self.blacklist_ips:
            return await self._create_rate_limit_response(
                request, "IP已被禁止访问", "BLACKLISTED"
            )
        
        # 检查IP白名单
        if client_ip in self.whitelist_ips:
            return await call_next(request)
        
        # 清理过期数据
        await self._cleanup_expired_data()
        
        # 应用限流检查
        rate_limit_result = await self._check_rate_limits(request)
        if rate_limit_result:
            return rate_limit_result
        
        # 记录请求
        await self._record_request(request)
        
        # 继续处理请求
        response = await call_next(request)
        
        # 添加限流相关响应头
        await self._add_rate_limit_headers(request, response)
        
        return response
    
    async def _check_rate_limits(self, request: Request) -> Optional[JSONResponse]:
        """
        检查各种限流规则
        
        Args:
            request: 请求对象
            
        Returns:
            Optional[JSONResponse]: 如果触发限流则返回错误响应
        """
        client_ip = self._get_client_ip(request)
        user_id = getattr(request.state, 'user_id', None)
        path = request.url.path
        method = request.method
        
        # IP级限流
        if self.enable_ip_rate_limit:
            if await self._is_rate_limited(f"ip:{client_ip}", request):
                return await self._create_rate_limit_response(
                    request, "IP访问频率过高", "IP_RATE_LIMIT"
                )
        
        # 用户级限流
        if self.enable_user_rate_limit and user_id:
            if await self._is_rate_limited(f"user:{user_id}", request):
                return await self._create_rate_limit_response(
                    request, "用户访问频率过高", "USER_RATE_LIMIT"
                )
        
        # 端点级限流
        if self.enable_endpoint_rate_limit:
            endpoint_key = f"endpoint:{method}:{path}"
            if await self._is_rate_limited(endpoint_key, request):
                return await self._create_rate_limit_response(
                    request, "API端点访问频率过高", "ENDPOINT_RATE_LIMIT"
                )
        
        # 组合限流（IP + 端点）
        combined_key = f"combined:{client_ip}:{method}:{path}"
        if await self._is_rate_limited(combined_key, request):
            return await self._create_rate_limit_response(
                request, "访问频率过高", "COMBINED_RATE_LIMIT"
            )
        
        return None
    
    async def _is_rate_limited(self, key: str, request: Request) -> bool:
        """
        检查是否触发限流
        
        Args:
            key: 限流键
            request: 请求对象
            
        Returns:
            bool: 是否触发限流
        """
        # 获取适用的限流规则
        rate_limit = self._get_rate_limit_for_path(request.url.path)
        max_requests, window_seconds = rate_limit
        
        current_time = time.time()
        window_start = current_time - window_seconds
        
        if self.storage_backend == "redis" and self.redis_client:
            return await self._is_rate_limited_redis(key, max_requests, window_seconds, current_time)
        else:
            return await self._is_rate_limited_memory(key, max_requests, window_start, current_time)
    
    async def _is_rate_limited_memory(
        self, 
        key: str, 
        max_requests: int, 
        window_start: float, 
        current_time: float
    ) -> bool:
        """
        基于内存的限流检查
        
        Args:
            key: 限流键
            max_requests: 最大请求数
            window_start: 窗口开始时间
            current_time: 当前时间
            
        Returns:
            bool: 是否触发限流
        """
        requests = self.memory_storage[key]['requests']
        
        # 移除过期的请求记录
        while requests and requests[0] < window_start:
            requests.popleft()
        
        # 检查是否超过限制
        return len(requests) >= max_requests
    
    async def _is_rate_limited_redis(
        self, 
        key: str, 
        max_requests: int, 
        window_seconds: int, 
        current_time: float
    ) -> bool:
        """
        基于Redis的限流检查
        
        Args:
            key: 限流键
            max_requests: 最大请求数
            window_seconds: 窗口时间（秒）
            current_time: 当前时间
            
        Returns:
            bool: 是否触发限流
        """
        try:
            pipe = self.redis_client.pipeline()
            
            # 使用滑动窗口算法
            window_start = current_time - window_seconds
            
            # 移除过期记录
            pipe.zremrangebyscore(key, 0, window_start)
            
            # 获取当前窗口内的请求数
            pipe.zcard(key)
            
            results = pipe.execute()
            current_requests = results[1]
            
            return current_requests >= max_requests
            
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {str(e)}")
            # Redis失败时回退到内存存储
            return await self._is_rate_limited_memory(key, max_requests, current_time - window_seconds, current_time)
    
    async def _record_request(self, request: Request) -> None:
        """
        记录请求
        
        Args:
            request: 请求对象
        """
        client_ip = self._get_client_ip(request)
        user_id = getattr(request.state, 'user_id', None)
        path = request.url.path
        method = request.method
        current_time = time.time()
        
        keys = []
        
        # 构建所有需要记录的键
        if self.enable_ip_rate_limit:
            keys.append(f"ip:{client_ip}")
        
        if self.enable_user_rate_limit and user_id:
            keys.append(f"user:{user_id}")
        
        if self.enable_endpoint_rate_limit:
            keys.append(f"endpoint:{method}:{path}")
        
        keys.append(f"combined:{client_ip}:{method}:{path}")
        
        # 记录请求
        for key in keys:
            if self.storage_backend == "redis" and self.redis_client:
                await self._record_request_redis(key, current_time)
            else:
                await self._record_request_memory(key, current_time)
    
    async def _record_request_memory(self, key: str, current_time: float) -> None:
        """
        在内存中记录请求
        
        Args:
            key: 限流键
            current_time: 当前时间
        """
        self.memory_storage[key]['requests'].append(current_time)
    
    async def _record_request_redis(self, key: str, current_time: float) -> None:
        """
        在Redis中记录请求
        
        Args:
            key: 限流键
            current_time: 当前时间
        """
        try:
            pipe = self.redis_client.pipeline()
            
            # 添加当前请求时间戳
            pipe.zadd(key, {str(current_time): current_time})
            
            # 设置过期时间
            rate_limit = self._get_rate_limit_for_path("")
            _, window_seconds = rate_limit
            pipe.expire(key, window_seconds * 2)  # 设置为窗口时间的2倍
            
            pipe.execute()
            
        except Exception as e:
            logger.error(f"Redis record request failed: {str(e)}")
            # Redis失败时回退到内存存储
            await self._record_request_memory(key, current_time)
    
    def _get_rate_limit_for_path(self, path: str) -> Tuple[int, int]:
        """
        获取路径对应的限流规则
        
        Args:
            path: 请求路径
            
        Returns:
            Tuple[int, int]: (请求数量, 时间窗口秒数)
        """
        # 检查精确匹配
        if path in self.rate_limit_rules:
            return self.rate_limit_rules[path]
        
        # 检查前缀匹配
        for rule_path, rate_limit in self.rate_limit_rules.items():
            if path.startswith(rule_path):
                return rate_limit
        
        # 返回默认限流规则
        return self.default_rate_limit
    
    async def _add_rate_limit_headers(self, request: Request, response) -> None:
        """
        添加限流相关的响应头
        
        Args:
            request: 请求对象
            response: 响应对象
        """
        try:
            client_ip = self._get_client_ip(request)
            key = f"ip:{client_ip}"
            
            rate_limit = self._get_rate_limit_for_path(request.url.path)
            max_requests, window_seconds = rate_limit
            
            # 获取当前窗口内的请求数
            current_requests = await self._get_current_requests(key, window_seconds)
            remaining = max(0, max_requests - current_requests)
            
            # 计算重置时间
            reset_time = int(time.time()) + window_seconds
            
            # 添加响应头
            response.headers["X-RateLimit-Limit"] = str(max_requests)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset_time)
            response.headers["X-RateLimit-Window"] = str(window_seconds)
            
        except Exception as e:
            logger.error(f"Error adding rate limit headers: {str(e)}")
    
    async def _get_current_requests(self, key: str, window_seconds: int) -> int:
        """
        获取当前窗口内的请求数
        
        Args:
            key: 限流键
            window_seconds: 窗口时间（秒）
            
        Returns:
            int: 当前请求数
        """
        current_time = time.time()
        window_start = current_time - window_seconds
        
        if self.storage_backend == "redis" and self.redis_client:
            try:
                return self.redis_client.zcount(key, window_start, current_time)
            except Exception:
                pass
        
        # 内存存储
        requests = self.memory_storage[key]['requests']
        return sum(1 for req_time in requests if req_time >= window_start)
    
    async def _cleanup_expired_data(self) -> None:
        """
        清理过期数据
        """
        current_time = time.time()
        
        # 每5分钟清理一次
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        self.last_cleanup = current_time
        
        # 清理内存存储中的过期数据
        for key_type in list(self.memory_storage.keys()):
            requests = self.memory_storage[key_type]['requests']
            
            # 保留最近1小时的数据
            cutoff_time = current_time - 3600
            while requests and requests[0] < cutoff_time:
                requests.popleft()
            
            # 如果队列为空，删除整个键
            if not requests:
                del self.memory_storage[key_type]
    
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
    
    async def _create_rate_limit_response(
        self, 
        request: Request, 
        message: str, 
        limit_type: str
    ) -> JSONResponse:
        """
        创建限流错误响应
        
        Args:
            request: 请求对象
            message: 错误消息
            limit_type: 限流类型
            
        Returns:
            JSONResponse: 限流错误响应
        """
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # 记录限流事件
        logger.warning(
            f"Rate limit exceeded - Request ID: {request_id}, "
            f"IP: {self._get_client_ip(request)}, "
            f"Path: {request.url.path}, "
            f"Type: {limit_type}"
        )
        
        # 获取重试时间
        rate_limit = self._get_rate_limit_for_path(request.url.path)
        _, window_seconds = rate_limit
        retry_after = window_seconds
        
        content = {
            "code": 429,
            "message": "Too Many Requests",
            "data": {
                "detail": message,
                "error_type": "RateLimitError",
                "limit_type": limit_type,
                "retry_after": retry_after
            },
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id
        }
        
        return JSONResponse(
            content=content,
            status_code=200,  # 统一返回200，错误信息在code字段
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit-Type": limit_type
            }
        )

class AdaptiveRateLimitMiddleware(RateLimitMiddleware):
    """
    自适应限流中间件
    
    根据系统负载和历史数据动态调整限流阈值
    """
    
    def __init__(self, app, **kwargs):
        """
        初始化自适应限流中间件
        
        Args:
            app: FastAPI应用实例
            **kwargs: 其他参数
        """
        super().__init__(app, **kwargs)
        self.load_history = deque(maxlen=100)  # 保留最近100个负载数据点
        self.adjustment_factor = 1.0  # 动态调整因子
        self.last_adjustment = time.time()
        self.adjustment_interval = 60  # 每分钟调整一次
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """
        处理请求并应用自适应限流
        
        Args:
            request: 请求对象
            call_next: 下一个中间件或路由处理器
            
        Returns:
            JSONResponse: 响应或限流错误响应
        """
        # 更新系统负载
        await self._update_system_load()
        
        # 调整限流阈值
        await self._adjust_rate_limits()
        
        # 应用限流
        return await super().dispatch(request, call_next)
    
    async def _update_system_load(self) -> None:
        """
        更新系统负载指标
        """
        try:
            import psutil
            
            # 获取CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # 获取内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 计算综合负载
            load_score = (cpu_percent + memory_percent) / 2
            
            self.load_history.append({
                'timestamp': time.time(),
                'cpu': cpu_percent,
                'memory': memory_percent,
                'load': load_score
            })
            
        except ImportError:
            # 如果没有psutil，使用简单的负载估算
            current_connections = len(self.memory_storage)
            load_score = min(100, current_connections * 2)  # 简单估算
            
            self.load_history.append({
                'timestamp': time.time(),
                'load': load_score
            })
    
    async def _adjust_rate_limits(self) -> None:
        """
        根据系统负载调整限流阈值
        """
        current_time = time.time()
        
        # 每分钟调整一次
        if current_time - self.last_adjustment < self.adjustment_interval:
            return
        
        self.last_adjustment = current_time
        
        if not self.load_history:
            return
        
        # 计算平均负载
        recent_loads = [item['load'] for item in self.load_history if current_time - item['timestamp'] < 300]
        if not recent_loads:
            return
        
        avg_load = sum(recent_loads) / len(recent_loads)
        
        # 根据负载调整限流因子
        if avg_load > 80:  # 高负载
            self.adjustment_factor = 0.5  # 减少50%的限流阈值
        elif avg_load > 60:  # 中等负载
            self.adjustment_factor = 0.7  # 减少30%的限流阈值
        elif avg_load < 30:  # 低负载
            self.adjustment_factor = 1.5  # 增加50%的限流阈值
        else:  # 正常负载
            self.adjustment_factor = 1.0  # 保持原有阈值
        
        logger.info(f"Adjusted rate limit factor to {self.adjustment_factor} based on load {avg_load:.1f}%")
    
    def _get_rate_limit_for_path(self, path: str) -> Tuple[int, int]:
        """
        获取路径对应的自适应限流规则
        
        Args:
            path: 请求路径
            
        Returns:
            Tuple[int, int]: (调整后的请求数量, 时间窗口秒数)
        """
        max_requests, window_seconds = super()._get_rate_limit_for_path(path)
        
        # 应用调整因子
        adjusted_max_requests = int(max_requests * self.adjustment_factor)
        adjusted_max_requests = max(1, adjusted_max_requests)  # 至少允许1个请求
        
        return adjusted_max_requests, window_seconds