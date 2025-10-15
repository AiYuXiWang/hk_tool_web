"""
测试环境配置

包含测试环境特定的配置项，优化测试执行速度。
"""

from typing import Dict, Any

# 应用配置
APP_CONFIG: Dict[str, Any] = {
    "debug": True,
    "host": "127.0.0.1",
    "port": 8001,
    "reload": False,
    "log_level": "WARNING",
    "cors_origins": ["*"],
}

# 数据库配置 - 使用内存数据库或测试专用数据库
DATABASE_CONFIG: Dict[str, Any] = {
    "host": "localhost",
    "port": 3306,
    "user": "test_user",
    "password": "test_password",
    "database": "hk_tool_platform_test",
    "charset": "utf8mb4",
    "autocommit": True,
    "pool_size": 1,
    "max_overflow": 2,
    "pool_timeout": 10,
    "pool_recycle": 300,
}

# 日志配置 - 最小化日志输出
LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {
            "level": "WARNING",
            "handlers": ["console"],
        },
        "uvicorn": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

# API配置
API_CONFIG: Dict[str, Any] = {
    "title": "海康威视工具平台 API - 测试环境",
    "description": "测试环境API接口",
    "version": "1.0.0-test",
    "docs_url": "/docs",
    "redoc_url": "/redoc",
    "openapi_url": "/openapi.json",
}

# 安全配置
SECURITY_CONFIG: Dict[str, Any] = {
    "secret_key": "test-secret-key-not-for-production",
    "algorithm": "HS256",
    "access_token_expire_minutes": 5,
    "refresh_token_expire_days": 1,
}

# 缓存配置
CACHE_CONFIG: Dict[str, Any] = {
    "backend": "memory",
    "default_timeout": 60,
    "key_prefix": "test_hk_tool:",
}