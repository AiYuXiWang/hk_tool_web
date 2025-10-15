"""
生产环境配置

包含生产环境特定的配置项，注重性能和安全性。
"""

import os
from typing import Dict, Any

# 应用配置
APP_CONFIG: Dict[str, Any] = {
    "debug": False,
    "host": "0.0.0.0",
    "port": int(os.getenv("PORT", "8000")),
    "reload": False,
    "log_level": "INFO",
    "cors_origins": [
        os.getenv("FRONTEND_URL", "https://hk-tool.example.com"),
    ],
}

# 数据库配置
DATABASE_CONFIG: Dict[str, Any] = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "hk_tool"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "hk_tool_platform"),
    "charset": "utf8mb4",
    "autocommit": True,
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 60,
    "pool_recycle": 7200,
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
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "WARNING",
            "formatter": "json",
            "filename": "/var/log/hk-tool/app.log",
            "maxBytes": 52428800,  # 50MB
            "backupCount": 10,
        },
    },
    "loggers": {
        "": {
            "level": "INFO",
            "handlers": ["console", "file"],
        },
        "uvicorn": {
            "level": "WARNING",
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
    "docs_url": None,  # 生产环境关闭文档
    "redoc_url": None,
    "openapi_url": None,
}

# 安全配置
SECURITY_CONFIG: Dict[str, Any] = {
    "secret_key": os.getenv("SECRET_KEY", ""),
    "algorithm": "HS256",
    "access_token_expire_minutes": 15,
    "refresh_token_expire_days": 1,
}

# 缓存配置
CACHE_CONFIG: Dict[str, Any] = {
    "backend": "redis",
    "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    "default_timeout": 3600,
    "key_prefix": "hk_tool:",
}