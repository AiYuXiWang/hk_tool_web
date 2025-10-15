"""
异步任务管理器
支持后台导出任务和进度查询
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import json
from logger_config import app_logger

logger = app_logger

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 等待中
    RUNNING = "running"      # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 已取消

@dataclass
class TaskProgress:
    """任务进度信息"""
    current: int = 0         # 当前进度
    total: int = 0           # 总数
    percentage: float = 0.0  # 百分比
    message: str = ""        # 当前状态消息
    details: Dict[str, Any] = None  # 详细信息
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.total > 0:
            self.percentage = round((self.current / self.total) * 100, 2)

@dataclass
class ExportTask:
    """导出任务信息"""
    task_id: str
    task_type: str           # 'electricity' 或 'sensor'
    line: str               # 线路名称
    start_time: datetime
    end_time: datetime
    status: TaskStatus
    progress: TaskProgress
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    download_urls: Optional[Dict[str, str]] = None  # 下载链接
    
    def to_dict(self):
        """转换为字典格式"""
        data = asdict(self)
        # 转换枚举和日期时间
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        if self.started_at:
            data['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        return data

class TaskManager:
    """异步任务管理器"""
    
    def __init__(self):
        self.tasks: Dict[str, ExportTask] = {}
        self._lock = threading.Lock()
        self._cleanup_interval = 3600  # 1小时清理一次过期任务
        self._task_ttl = 24 * 3600     # 任务保留24小时
        
        # 启动清理任务
        self._start_cleanup_task()
    
    def create_task(self, task_type: str, line: str, start_time: datetime, end_time: datetime) -> str:
        """创建新的导出任务"""
        task_id = str(uuid.uuid4())
        
        task = ExportTask(
            task_id=task_id,
            task_type=task_type,
            line=line,
            start_time=start_time,
            end_time=end_time,
            status=TaskStatus.PENDING,
            progress=TaskProgress(message="任务已创建，等待执行"),
            created_at=datetime.now()
        )
        
        with self._lock:
            self.tasks[task_id] = task
        
        logger.info(f"创建导出任务: {task_id}, 类型={task_type}, 线路={line}")
        return task_id
    
    def get_task(self, task_id: str) -> Optional[ExportTask]:
        """获取任务信息"""
        with self._lock:
            return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: str, status: TaskStatus, error_message: str = None):
        """更新任务状态"""
        with self._lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = status
                
                if status == TaskStatus.RUNNING and not task.started_at:
                    task.started_at = datetime.now()
                elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    task.completed_at = datetime.now()
                
                if error_message:
                    task.error_message = error_message
                
                logger.info(f"任务状态更新: {task_id} -> {status.value}")
    
    def update_task_progress(self, task_id: str, current: int, total: int, message: str = "", details: Dict[str, Any] = None):
        """更新任务进度"""
        with self._lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.progress = TaskProgress(
                    current=current,
                    total=total,
                    message=message,
                    details=details or {}
                )
                logger.debug(f"任务进度更新: {task_id} -> {current}/{total} ({task.progress.percentage}%)")
    
    def set_task_result(self, task_id: str, result_data: Dict[str, Any], download_urls: Dict[str, str] = None):
        """设置任务结果"""
        with self._lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.result_data = result_data
                task.download_urls = download_urls or {}
                logger.info(f"任务结果设置: {task_id}")
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        with self._lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                    task.status = TaskStatus.CANCELLED
                    task.completed_at = datetime.now()
                    logger.info(f"任务已取消: {task_id}")
                    return True
        return False
    
    def list_tasks(self, limit: int = 50) -> list:
        """列出最近的任务"""
        with self._lock:
            tasks = list(self.tasks.values())
            # 按创建时间倒序排列
            tasks.sort(key=lambda x: x.created_at, reverse=True)
            return [task.to_dict() for task in tasks[:limit]]
    
    def _start_cleanup_task(self):
        """启动清理任务"""
        def cleanup_expired_tasks():
            while True:
                try:
                    current_time = datetime.now()
                    expired_task_ids = []
                    
                    with self._lock:
                        for task_id, task in self.tasks.items():
                            # 清理超过TTL的已完成任务
                            if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] and
                                current_time - task.created_at > timedelta(seconds=self._task_ttl)):
                                expired_task_ids.append(task_id)
                    
                    # 删除过期任务
                    if expired_task_ids:
                        with self._lock:
                            for task_id in expired_task_ids:
                                del self.tasks[task_id]
                        logger.info(f"清理过期任务: {len(expired_task_ids)} 个")
                    
                except Exception as e:
                    logger.error(f"清理任务时出错: {e}")
                
                # 等待下次清理
                threading.Event().wait(self._cleanup_interval)
        
        # 在后台线程中运行清理任务
        cleanup_thread = threading.Thread(target=cleanup_expired_tasks, daemon=True)
        cleanup_thread.start()

# 全局任务管理器实例
task_manager = TaskManager()