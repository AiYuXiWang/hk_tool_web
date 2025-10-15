"""
依赖注入模块

提供FastAPI依赖注入的服务实例管理。
"""

from functools import lru_cache
from typing import Generator
from sqlalchemy.orm import Session

from backend.app.services.energy_service import EnergyService
from backend.app.services.data_service import DataService
from backend.app.services.base import ServiceRegistry
from config.database.mysql import get_db_session


# 服务注册表实例
service_registry = ServiceRegistry()


@lru_cache()
def get_energy_service() -> EnergyService:
    """
    获取能源服务实例
    
    Returns:
        EnergyService: 能源服务实例
    """
    service_name = "energy_service"
    
    # 尝试从注册表获取
    service = service_registry.get(service_name)
    if service is None:
        # 创建新实例并注册
        service = EnergyService()
        service_registry.register(service_name, service)
    
    return service


@lru_cache()
def get_data_service() -> DataService:
    """
    获取数据服务实例
    
    Returns:
        DataService: 数据服务实例
    """
    service_name = "data_service"
    
    # 尝试从注册表获取
    service = service_registry.get(service_name)
    if service is None:
        # 创建新实例并注册
        service = DataService()
        service_registry.register(service_name, service)
    
    return service


def get_database() -> Generator[Session, None, None]:
    """
    获取数据库会话
    
    Yields:
        Session: 数据库会话
    """
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()


def get_current_user():
    """
    获取当前用户（占位符）
    
    TODO: 实现用户认证逻辑
    """
    # 这里应该实现JWT token验证等逻辑
    return {"user_id": "anonymous", "username": "anonymous"}


def get_admin_user():
    """
    获取管理员用户（占位符）
    
    TODO: 实现管理员权限验证
    """
    # 这里应该实现管理员权限验证逻辑
    current_user = get_current_user()
    if current_user.get("role") != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user


# 清理函数
def cleanup_services():
    """清理所有注册的服务"""
    global service_registry
    
    # 获取所有服务并清理
    services = service_registry.list_services()
    for service_name in services:
        service = service_registry.get(service_name)
        if hasattr(service, 'cleanup'):
            try:
                service.cleanup()
            except Exception as e:
                print(f"清理服务 {service_name} 时出错: {e}")
        
        service_registry.unregister(service_name)


# 应用启动时的初始化函数
def initialize_services():
    """初始化所有服务"""
    try:
        # 预加载核心服务
        get_energy_service()
        get_data_service()
        
        print("服务初始化完成")
        
    except Exception as e:
        print(f"服务初始化失败: {e}")
        raise


# 应用关闭时的清理函数
def shutdown_services():
    """关闭所有服务"""
    try:
        cleanup_services()
        print("服务清理完成")
        
    except Exception as e:
        print(f"服务清理失败: {e}")