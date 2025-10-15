"""
配置管理模块

统一管理应用配置，支持多环境配置加载。
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._environment: str = ""
        self._load_environment()
        self._load_config()
    
    def _load_environment(self) -> None:
        """加载环境变量"""
        # 加载.env文件
        env_file = PROJECT_ROOT / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        
        # 确定运行环境
        self._environment = os.getenv("ENVIRONMENT", "development").lower()
        
        # 验证环境名称
        valid_environments = ["development", "production", "testing"]
        if self._environment not in valid_environments:
            raise ValueError(f"Invalid environment: {self._environment}. Must be one of {valid_environments}")
    
    def _load_config(self) -> None:
        """加载配置"""
        try:
            # 动态导入环境配置
            import sys
            sys.path.insert(0, str(PROJECT_ROOT))
            config_module_path = f"config.environments.{self._environment}"
            config_module = __import__(config_module_path, fromlist=[""])
            
            # 加载各类配置
            self._config = {
                "app": getattr(config_module, "APP_CONFIG", {}),
                "database": getattr(config_module, "DATABASE_CONFIG", {}),
                "logging": getattr(config_module, "LOGGING_CONFIG", {}),
                "api": getattr(config_module, "API_CONFIG", {}),
                "security": getattr(config_module, "SECURITY_CONFIG", {}),
                "cache": getattr(config_module, "CACHE_CONFIG", {}),
            }
            
            # 环境变量覆盖
            self._apply_env_overrides()
            
        except ImportError as e:
            raise ImportError(f"Failed to load config for environment '{self._environment}': {e}")
    
    def _apply_env_overrides(self) -> None:
        """应用环境变量覆盖"""
        # 数据库配置覆盖
        db_config = self._config["database"]
        db_config["host"] = os.getenv("DB_HOST", db_config.get("host"))
        db_config["port"] = int(os.getenv("DB_PORT", str(db_config.get("port", 3306))))
        db_config["user"] = os.getenv("DB_USER", db_config.get("user"))
        db_config["password"] = os.getenv("DB_PASSWORD", db_config.get("password"))
        db_config["database"] = os.getenv("DB_NAME", db_config.get("database"))
        
        # 应用配置覆盖
        app_config = self._config["app"]
        app_config["host"] = os.getenv("HOST", app_config.get("host"))
        app_config["port"] = int(os.getenv("PORT", str(app_config.get("port", 8000))))
        app_config["debug"] = os.getenv("DEBUG", "").lower() in ("true", "1", "yes")
        
        # 安全配置覆盖
        security_config = self._config["security"]
        if os.getenv("SECRET_KEY"):
            security_config["secret_key"] = os.getenv("SECRET_KEY")
    
    @property
    def environment(self) -> str:
        """获取当前环境"""
        return self._environment
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split(".")
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_app_config(self) -> Dict[str, Any]:
        """获取应用配置"""
        return self._config.get("app", {})
    
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return self._config.get("database", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self._config.get("logging", {})
    
    def get_api_config(self) -> Dict[str, Any]:
        """获取API配置"""
        return self._config.get("api", {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """获取安全配置"""
        return self._config.get("security", {})
    
    def get_cache_config(self) -> Dict[str, Any]:
        """获取缓存配置"""
        return self._config.get("cache", {})
    
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self._environment == "development"
    
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self._environment == "production"
    
    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self._environment == "testing"


# 全局配置实例
config = ConfigManager()


def get_config() -> ConfigManager:
    """获取配置管理器实例"""
    return config


def setup_logging() -> None:
    """设置日志配置"""
    logging_config = config.get_logging_config()
    if logging_config:
        # 确保日志目录存在
        log_dir = PROJECT_ROOT / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # 应用日志配置
        logging.config.dictConfig(logging_config)
    else:
        # 默认日志配置
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )