"""
MySQL数据库配置

包含MySQL连接池、会话管理等配置。
"""

from typing import Dict, Any, Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from backend.app.core.config import get_config

config = get_config()


class DatabaseConfig:
    """数据库配置类"""
    
    def __init__(self):
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        self._db_config = config.get_database_config()
    
    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        db_config = self._db_config
        return (
            f"mysql+pymysql://{db_config['user']}:{db_config['password']}"
            f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
            f"?charset={db_config.get('charset', 'utf8mb4')}"
        )
    
    def get_engine_config(self) -> Dict[str, Any]:
        """获取数据库引擎配置"""
        db_config = self._db_config
        
        engine_config = {
            "poolclass": QueuePool,
            "pool_size": db_config.get("pool_size", 10),
            "max_overflow": db_config.get("max_overflow", 20),
            "pool_timeout": db_config.get("pool_timeout", 30),
            "pool_recycle": db_config.get("pool_recycle", 3600),
            "pool_pre_ping": True,
            "echo": config.is_development(),
        }
        
        return engine_config
    
    def create_engine(self) -> Engine:
        """创建数据库引擎"""
        if self._engine is None:
            database_url = self.get_database_url()
            engine_config = self.get_engine_config()
            self._engine = create_engine(database_url, **engine_config)
        
        return self._engine
    
    def create_session_factory(self) -> sessionmaker:
        """创建会话工厂"""
        if self._session_factory is None:
            engine = self.create_engine()
            self._session_factory = sessionmaker(
                bind=engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            )
        
        return self._session_factory
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        session_factory = self.create_session_factory()
        return session_factory()
    
    def close_engine(self) -> None:
        """关闭数据库引擎"""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None


# 全局数据库配置实例
db_config = DatabaseConfig()


def get_database_config() -> DatabaseConfig:
    """获取数据库配置实例"""
    return db_config


def get_db_session() -> Session:
    """获取数据库会话（依赖注入用）"""
    session = db_config.get_session()
    try:
        yield session
    finally:
        session.close()


def init_database() -> None:
    """初始化数据库连接"""
    try:
        engine = db_config.create_engine()
        # 测试连接
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print(f"✅ 数据库连接成功: {config.get('database.host')}:{config.get('database.port')}")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        raise


def close_database() -> None:
    """关闭数据库连接"""
    db_config.close_engine()
    print("✅ 数据库连接已关闭")