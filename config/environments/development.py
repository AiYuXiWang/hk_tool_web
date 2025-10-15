"""
开发环境配置

包含开发环境特定的配置项，如调试模式、日志级别等。
"""

from typing import Dict, Any

# 应用配置
APP_CONFIG: Dict[str, Any] = {
    "debug": True,
    "host": "0.0.0.0",
    "port": 8000,
    "reload": True,
    "log_level": "DEBUG",
    "cors_origins": [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
}

# 数据库配置
DATABASE_CONFIG: Dict[str, Any] = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "hk_tool_platform",
    "charset": "utf8mb4",
    "autocommit": True,
    "pool_size": 5,
    "max_overflow": 10,
    "pool_timeout": 30,
    "pool_recycle": 3600,
}

# 日志配置
LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

# API配置
API_CONFIG: Dict[str, Any] = {
    "title": "海康威视工具平台 API",
    "description": "海康威视工具平台后端API接口文档",
    "version": "1.0.0",
    "docs_url": "/docs",
    "redoc_url": "/redoc",
    "openapi_url": "/openapi.json",
}

# 安全配置
SECURITY_CONFIG: Dict[str, Any] = {
    "secret_key": "dev-secret-key-change-in-production",
    "algorithm": "HS256",
    "access_token_expire_minutes": 30,
    "refresh_token_expire_days": 7,
}

# 缓存配置
CACHE_CONFIG: Dict[str, Any] = {
    "backend": "memory",
    "default_timeout": 300,
    "key_prefix": "hk_tool:",
}