"""
操作审计模块

提供操作日志记录、查询、统计等功能
支持操作轨迹追溯和审计报表生成
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from db_config import execute_query, insert_operation_log
from models import OperationLog
from logger_config import app_logger

logger = app_logger

class AuditService:
    """操作审计服务类"""
    
    def __init__(self):
        pass
    
    def record_operation(
        self,
        operator_id: str,
        point_key: str,
        object_code: Optional[str] = None,
        data_code: Optional[str] = None,
        before_value: Optional[str] = None,
        after_value: Optional[str] = None,
        result: str = "ok",
        message: Optional[str] = None,
        duration_ms: Optional[int] = None
    ) -> bool:
        """记录操作审计日志"""
        try:
            return insert_operation_log(
                operator_id=operator_id,
                point_key=point_key,
                object_code=object_code,
                data_code=data_code,
                before_value=before_value,
                after_value=after_value,
                result=result,
                message=message,
                duration_ms=duration_ms
            )
        except Exception as e:
            logger.error(f"记录操作审计失败: {e}")
            return False
    
    def query_operation_logs(
        self,
        operator_id: Optional[str] = None,
        point_key: Optional[str] = None,
        object_code: Optional[str] = None,
        result: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[OperationLog], int]:
        """查询操作审计日志"""
        try:
            # 构建查询条件
            where_conditions = ["1=1"]
            params = []
            
            if operator_id:
                where_conditions.append("operator_id = %s")
                params.append(operator_id)
            
            if point_key:
                where_conditions.append("point_key LIKE %s")
                params.append(f"%{point_key}%")
            
            if object_code:
                where_conditions.append("object_code = %s")
                params.append(object_code)
            
            if result:
                where_conditions.append("result = %s")
                params.append(result)
            
            if start_time:
                where_conditions.append("created_at >= %s")
                params.append(start_time)
            
            if end_time:
                where_conditions.append("created_at <= %s")
                params.append(end_time)
            
            where_clause = " AND ".join(where_conditions)
            
            # 查询总数
            count_sql = f"""
                SELECT COUNT(*) 
                FROM operation_log 
                WHERE {where_clause}
            """
            count_result = execute_query(count_sql, tuple(params))
            total_count = count_result[0][0] if count_result else 0
            
            # 查询日志列表
            list_sql = f"""
                SELECT 
                    id, operator_id, point_key, object_code, data_code,
                    before_value, after_value, result, message, duration_ms, created_at
                FROM operation_log 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            list_params = list(params) + [limit, offset]
            rows = execute_query(list_sql, tuple(list_params)) or []
            
            # 转换为模型对象
            logs = []
            for row in rows:
                (
                    log_id, operator_id, point_key, object_code, data_code,
                    before_value, after_value, result, message, duration_ms, created_at
                ) = row
                
                logs.append(OperationLog(
                    id=log_id,
                    operator_id=operator_id,
                    point_key=point_key,
                    object_code=object_code,
                    data_code=data_code,
                    before_value=before_value,
                    after_value=after_value,
                    result=result,
                    message=message,
                    duration_ms=duration_ms,
                    created_at=created_at
                ))
            
            return logs, total_count
            
        except Exception as e:
            logger.error(f"查询操作审计日志失败: {e}")
            return [], 0

# 全局审计服务实例
audit_service = AuditService()