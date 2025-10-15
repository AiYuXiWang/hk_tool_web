"""
日志处理器配置

定义各种日志处理器和格式化器。
"""

import os
import logging
from typing import Dict, Any
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from backend.app.core.config import get_config

config = get_config()

# 日志目录
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    # 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m',       # 重置
    }
    
    def format(self, record):
        # 添加颜色
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}"
                f"{record.levelname}"
                f"{self.COLORS['RESET']}"
            )
        
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON格式化器"""
    
    def format(self, record):
        import json
        from datetime import datetime
        
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 添加异常信息
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # 添加额外字段
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        
        return json.dumps(log_entry, ensure_ascii=False)


def get_console_handler() -> logging.StreamHandler:
    """获取控制台处理器"""
    handler = logging.StreamHandler()
    
    if config.is_development():
        # 开发环境使用彩色格式
        formatter = ColoredFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    else:
        # 生产环境使用简单格式
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    handler.setFormatter(formatter)
    return handler


def get_file_handler(
    filename: str,
    level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> RotatingFileHandler:
    """获取文件处理器"""
    log_file = LOG_DIR / filename
    handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    
    if config.is_production():
        # 生产环境使用JSON格式
        formatter = JSONFormatter()
    else:
        # 开发环境使用普通格式
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler


def get_timed_file_handler(
    filename: str,
    level: int = logging.INFO,
    when: str = "midnight",
    interval: int = 1,
    backup_count: int = 30,
) -> TimedRotatingFileHandler:
    """获取按时间轮转的文件处理器"""
    log_file = LOG_DIR / filename
    handler = TimedRotatingFileHandler(
        log_file,
        when=when,
        interval=interval,
        backupCount=backup_count,
        encoding="utf-8",
    )
    
    if config.is_production():
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler


def get_error_handler() -> RotatingFileHandler:
    """获取错误日志处理器"""
    return get_file_handler("error.log", level=logging.ERROR)


def get_access_handler() -> TimedRotatingFileHandler:
    """获取访问日志处理器"""
    return get_timed_file_handler("access.log", level=logging.INFO)


def get_app_handler() -> RotatingFileHandler:
    """获取应用日志处理器"""
    return get_file_handler("app.log", level=logging.INFO)


def setup_loggers() -> None:
    """设置日志器"""
    # 根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 清除现有处理器
    root_logger.handlers.clear()
    
    # 添加控制台处理器
    root_logger.addHandler(get_console_handler())
    
    # 添加文件处理器
    if not config.is_testing():
        root_logger.addHandler(get_app_handler())
        root_logger.addHandler(get_error_handler())
    
    # 应用日志器
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)
    
    # API访问日志器
    access_logger = logging.getLogger("access")
    access_logger.setLevel(logging.INFO)
    if not config.is_testing():
        access_logger.addHandler(get_access_handler())
    
    # 数据库日志器
    db_logger = logging.getLogger("sqlalchemy")
    if config.is_development():
        db_logger.setLevel(logging.INFO)
    else:
        db_logger.setLevel(logging.WARNING)
    
    # 第三方库日志器
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    print(f"✅ 日志系统初始化完成，日志目录: {LOG_DIR}")


def get_logger(name: str) -> logging.Logger:
    """获取日志器"""
    return logging.getLogger(name)