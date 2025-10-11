"""
设备控制服务模块

提供点位实时查询、写值控制、设备树管理等核心功能
支持小系统传感器数据模式（fSmallFan%, fRoomTemp%, fSmallHigh%, 等）
"""

import asyncio
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import requests
import logging
from threading import RLock

from db_config import execute_query, insert_operation_log
from models import (
    PointMetadata, DeviceTreeNode, RealtimeResponse, WriteCommand, 
    WriteResult, BatchWriteResponse, DeviceTreeResponse, PointListResponse
)
from logger_config import app_logger

logger = app_logger

class PlatformAPIService:
    """环控平台API服务类"""
    
    def __init__(self):
        self.base_url = "http://192.168.100.3"
        self.select_url = "http://192.168.100.3:9801/api/objectPointInfo/selectObjectPointValueByDataCode"
        self.write_url = f"{self.base_url}/api/objectPointInfo/writePointValue"
        self.login_url = "http://192.168.100.3:9801/api/user/login"
        
        # Token缓存机制
        self._token_cache = {"value": None, "exp": 0.0}
        self._token_lock = RLock()
        self._token_ttl = 1200  # 20分钟
        
        # 固定Token兜底
        self.fallback_token = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhaXRlc3QiLCJhdWRpZW5jZSI6IndlYiIsImNyZWF0ZWQiOjE3NTUyMjIzOTM0ODUsIm5pY2tOYW1lIjoi57O757uf566h55CG5ZGYIiwiYXV0aFRva2VuIjpudWxsLCJjb21wYW55IjoyNTEsImV4cCI6MTAzOTUyMjIzOTMsInVzZXJJZCI6NDA1fQ.ulpIECFHg11RMmGhkYSqwwgNaVJ1ZyzG8vwuziVL9MIADQ07Sr1H6TQ7-5-qtnl3raTRQ_qSmjF4CZeWgoosoQ"
    
    def get_runtime_token(self) -> str:
        """获取运行时token：优先使用缓存；过期则登录刷新"""
        now = time.time()
        with self._token_lock:
            if self._token_cache.get("value") and self._token_cache.get("exp", 0.0) > now:
                return self._token_cache["value"]
            
            try:
                token = self._login_platform()
                self._token_cache["value"] = token
                self._token_cache["exp"] = now + self._token_ttl
                return token
            except Exception as e:
                logger.warning(f"Token刷新失败，使用兜底token: {e}")
                return self.fallback_token
    
    def _login_platform(self) -> str:
        """调用平台登录接口获取token"""
        import os
        import hashlib
        
        user = os.environ.get("HK_LOGIN_USER", "aitest")
        pwd = os.environ.get("HK_LOGIN_PWD", "")
        
        try:
            sha = hashlib.sha256(pwd.encode("utf-8")).hexdigest()
            md5 = hashlib.md5(pwd.encode("utf-8")).hexdigest()
            hashed_pwd = f"{sha}{md5}"
            
            resp = requests.post(
                self.login_url,
                data={"user_name": user, "pwd": hashed_pwd},
                timeout=6.0,
            )
            
            if resp.status_code != 200:
                raise Exception(f"登录接口HTTP错误 code={resp.status_code}")
            
            data = resp.json() if resp.text else {}
            if isinstance(data, dict) and data.get("code") == 1 and data.get("data") and data["data"].get("token"):
                token = data["data"]["token"]
                logger.info(f"平台登录成功, token_len={len(token)}, user={user}")
                return token
            
            msg = data.get("message") if isinstance(data, dict) else "invalid_response"
            raise Exception(f"平台登录失败: {msg}")
            
        except Exception as e:
            logger.error(f"平台登录异常: {e}")
            raise e
    
    async def query_realtime_value(self, object_code: str, data_code: str) -> Dict[str, Any]:
        """查询点位实时值"""
        token = self.get_runtime_token()
        logger.info(f"实时查询 object_code={object_code} data_code={data_code} token_len={len(token)}")
        
        loop = asyncio.get_event_loop()
        
        def _do_request():
            try:
                resp = requests.post(
                    self.select_url,
                    data={
                        "object_code": object_code,
                        "data_code": data_code,
                        "token": token
                    },
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                        "authorization": token,
                        "token": token,
                        "x-locale": "zh_cn"
                    },
                    timeout=6.0,
                )
                
                if resp.status_code == 200 and resp.text:
                    return resp.json()
                else:
                    return {"code": resp.status_code, "message": "request_failed", "error": resp.text[:200]}
                    
            except Exception as e:
                return {"code": 502, "message": "exception", "error": str(e)}
        
        raw_result = await loop.run_in_executor(None, _do_request)
        return raw_result
    
    async def write_point_value(self, command: WriteCommand, token: str) -> Dict[str, Any]:
        """写入点位值"""
        payload = [  # 平台接口接受数组体
            {
                "point_key": command.point_key,
                "data_source": command.data_source,
                "control_value": command.control_value,
            }
        ]
        
        loop = asyncio.get_event_loop()
        
        def _do_request():
            try:
                resp = requests.post(
                    self.write_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "authorization": token,
                        "token": token
                    },
                    timeout=8.0
                )
                
                if resp.status_code == 200:
                    return {"success": True, "data": resp.json() if resp.text else {}}
                else:
                    return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
                    
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return await loop.run_in_executor(None, _do_request)


class DeviceControlService:
    """设备控制核心服务类"""
    
    def __init__(self):
        self.platform_api = PlatformAPIService()
    
    async def get_device_tree(self, operator_id: str = "system", station_ip: str | None = None) -> DeviceTreeResponse:
        """
        从MySQL数据库获取设备树结构
        构建层级：项目 -> 子项目/设备 -> 点位
        支持小系统传感器数据模式
        """
        try:
            # 查询项目根节点（parent_id = 0）
            root_sql = """
                SELECT object_id, object_code, object_name, object_type
                FROM bus_object_info 
                WHERE status = 1 AND parent_id = 0
                ORDER BY object_code
            """
            # 按车站IP切换数据源
            from db_config import execute_query_with_host
            root_nodes = execute_query_with_host(root_sql, None, station_ip) or []
            
            # 构建设备树
            tree_nodes = []
            
            for root in root_nodes:
                object_id, object_code, object_name, object_type = root
                
                # 查询子设备
                children_sql = """
                    SELECT 
                        o.object_id, 
                        o.object_code, 
                        o.object_name, 
                        o.object_type,
                        COUNT(p.data_id) as point_count
                    FROM bus_object_info o
                    LEFT JOIN bus_object_point_data p ON o.object_id = p.object_id
                    WHERE o.status = 1 AND o.parent_id = %s
                    GROUP BY o.object_id, o.object_code, o.object_name, o.object_type
                    ORDER BY o.object_code
                """
                children = execute_query_with_host(children_sql, (object_id,), station_ip) or []
                
                child_nodes = []
                total_points = 0
                
                for child in children:
                    child_id, child_code, child_name, child_type, point_count = child
                    total_points += point_count or 0
                    
                    # 查询该子设备的所有点位信息
                    points_sql = """
                        SELECT 
                            p.data_code,
                            p.data_name,
                            p.unit,
                            p.is_set,
                            p.lower_control,
                            p.point_key,
                            p.border_min,
                            p.border_max,
                            p.warn_min,
                            p.warn_max,
                            p.error_min,
                            p.error_max,
                            p.data_type,
                            p.data_source
                        FROM bus_object_point_data p
                        WHERE p.object_id = %s
                        ORDER BY p.data_code
                        LIMIT 100
                    """
                    points = execute_query_with_host(points_sql, (child_id,), station_ip) or []
                    
                    point_nodes = []
                    for point in points:
                        (
                            data_code, data_name, unit, is_set, lower_control, point_key,
                            border_min, border_max, warn_min, warn_max, error_min, error_max, data_type, data_source
                        ) = point
                        
                        # 判断是否可写
                        is_writable = (is_set == 1) or (lower_control == 1)
                        
                        point_nodes.append(DeviceTreeNode(
                            id=f"{child_code}:{data_code}",
                            label=f"{'✔ ' if is_writable else ''}{data_code} ({data_name})",
                            children=None,
                            meta={
                                "object_code": child_code,
                                "data_code": data_code,
                                "data_name": data_name,
                                "unit": unit or "",
                                "is_writable": is_writable,
                                "point_key": point_key,
                                "data_type": data_type,
                                "data_source": data_source,
                                "border_min": border_min,
                                "border_max": border_max,
                                "warn_min": warn_min,
                                "warn_max": warn_max,
                                "error_min": error_min,
                                "error_max": error_max
                            }
                        ))
                    
                    child_nodes.append(DeviceTreeNode(
                        id=child_code,
                        label=f"{child_name} ({child_code}) [{point_count or 0}点]",
                        children=point_nodes,
                        meta={
                            "object_code": child_code,
                            "object_name": child_name,
                            "object_type": child_type,
                            "point_count": point_count or 0
                        }
                    ))
                
                tree_nodes.append(DeviceTreeNode(
                    id=object_code,
                    label=f"{object_name} ({object_code}) [{total_points}点]",
                    children=child_nodes,
                    meta={
                        "object_code": object_code,
                        "object_name": object_name,
                        "object_type": object_type,
                        "total_points": total_points
                    }
                ))
            
            # 记录审计
            try:
                insert_operation_log(
                    operator_id=operator_id,
                    point_key=":device-tree:load",
                    object_code=None,
                    data_code=None,
                    before_value=None,
                    after_value=str(len(tree_nodes)),
                    result="query",
                    message=f"load_device_tree station_ip={station_ip or ''}",
                    duration_ms=None,
                )
            except Exception as e:
                logger.debug(f"设备树查询审计写入失败: {e}")
            
            return DeviceTreeResponse(tree=tree_nodes, count=len(tree_nodes))
            
        except Exception as e:
            logger.error(f"获取设备树失败: {e}")
            # 连接失败或查询异常时，回退到测试数据
            test_tree = [
                DeviceTreeNode(
                    id="test_project",
                    label="测试项目 (test_project) [2点]",
                    children=[
                        DeviceTreeNode(
                            id="test_device",
                            label="测试设备 (test_device) [2点]",
                            children=[
                                DeviceTreeNode(
                                    id="test_device:point1",
                                    label="✔ point1 (温度点位)",
                                    meta={
                                        "object_code": "test_device",
                                        "data_code": "point1",
                                        "data_name": "温度点位",
                                        "unit": "℃",
                                        "is_writable": True,
                                        "point_key": "test:point1",
                                        "data_type": "0",
                                        "station_ip": station_ip or ""
                                    }
                                ),
                                DeviceTreeNode(
                                    id="test_device:point2",
                                    label="point2 (湿度点位)",
                                    meta={
                                        "object_code": "test_device",
                                        "data_code": "point2",
                                        "data_name": "湿度点位",
                                        "unit": "%",
                                        "is_writable": False,
                                        "point_key": "test:point2",
                                        "data_type": "0",
                                        "station_ip": station_ip or ""
                                    }
                                )
                            ],
                            meta={
                                "object_code": "test_device",
                                "object_name": "测试设备",
                                "object_type": "device"
                            }
                        )
                    ],
                    meta={
                        "object_code": "test_project",
                        "object_name": "测试项目",
                        "object_type": "project"
                    }
                )
            ]
            return DeviceTreeResponse(tree=test_tree, count=len(test_tree))
    
    async def query_realtime_point(self, object_code: str, data_code: str, operator_id: str = "system") -> RealtimeResponse:
        """查询点位实时值"""
        try:
            raw_result = await self.platform_api.query_realtime_value(object_code, data_code)
            
            # 规范化返回
            now_iso = datetime.utcnow().isoformat() + "Z"
            
            # 从平台API响应中提取值
            value = None
            unit = None
            if isinstance(raw_result, dict):
                # 先尝试直接获取value字段
                value = raw_result.get("value")
                unit = raw_result.get("unit")
                
                # 如果没有直接的value字段，尝试从data数组中提取
                if value is None and "data" in raw_result and isinstance(raw_result["data"], list) and len(raw_result["data"]) > 0:
                    data_item = raw_result["data"][0]
                    if isinstance(data_item, dict):
                        # 优先使用property_num_value，如果不存在则使用property_value
                        if "property_num_value" in data_item:
                            value = data_item["property_num_value"]
                        elif "property_value" in data_item:
                            property_value = data_item["property_value"]
                            # 尝试转换为数字
                            try:
                                value = float(property_value) if property_value is not None else None
                            except (ValueError, TypeError):
                                value = property_value
            
            result = RealtimeResponse(
                object_code=object_code,
                data_code=data_code,
                value=value,
                unit=unit,
                ts=now_iso,
                token_len=len(self.platform_api.get_runtime_token()),
                raw=raw_result if isinstance(raw_result, dict) else {"data": raw_result}
            )
            
            # 审计记录
            try:
                insert_operation_log(
                    operator_id=operator_id,
                    point_key=f"{object_code}:{data_code}",
                    object_code=object_code,
                    data_code=data_code,
                    before_value=None,
                    after_value=str(value) if value is not None else None,
                    result="query",
                    message=None,
                    duration_ms=None,
                )
            except Exception as e:
                logger.debug(f"查询审计写入失败: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"实时查询失败: {e}")
            raise e
    
    def _get_point_data_source(self, point_key: str, station_ip: str = None) -> Optional[int]:
        """根据point_key查询数据库获取data_source，支持模糊匹配"""
        try:
            # 首先尝试精确匹配
            sql_exact = """
                SELECT p.data_source
                FROM bus_object_point_data p
                WHERE p.point_key = %s
                LIMIT 1
            """
            
            if station_ip:
                result = execute_query_with_host(sql_exact, (point_key,), station_ip)
            else:
                result = execute_query(sql_exact, (point_key,))
            
            if result and len(result) > 0:
                return result[0][0]  # 返回data_source值
            
            # 如果精确匹配失败，尝试模糊匹配（处理缺少设备前缀的情况）
            # 例如：shuanfa:BigFanFreSetMax 匹配 C251:shuanfa:BigFanFreSetMax
            if ':' in point_key:
                sql_fuzzy = """
                    SELECT p.data_source, p.point_key
                    FROM bus_object_point_data p
                    WHERE p.point_key LIKE %s
                    LIMIT 1
                """
                fuzzy_pattern = f"%{point_key}"
                
                if station_ip:
                    result = execute_query_with_host(sql_fuzzy, (fuzzy_pattern,), station_ip)
                else:
                    result = execute_query(sql_fuzzy, (fuzzy_pattern,))
                
                if result and len(result) > 0:
                    actual_point_key = result[0][1]
                    data_source = result[0][0]
                    logger.info(f"模糊匹配成功: {point_key} -> {actual_point_key}, data_source={data_source}")
                    return data_source
            
            logger.warning(f"未找到点位 {point_key} 的data_source信息")
            return None
            
        except Exception as e:
            logger.error(f"查询点位data_source失败: {e}")
            return None

    async def _validate_and_normalize_command(self, cmd: WriteCommand, station_ip: str = None) -> Optional[str]:
        """验证并规范化写值命令"""
        if not cmd.point_key or not isinstance(cmd.point_key, str):
            return "point_key 必须为非空字符串"
        
        # 动态获取正确的data_source
        correct_data_source = self._get_point_data_source(cmd.point_key, station_ip)
        if correct_data_source is not None:
            if cmd.data_source != correct_data_source:
                logger.info(f"点位 {cmd.point_key} data_source 从 {cmd.data_source} 修正为 {correct_data_source}")
                cmd.data_source = correct_data_source
        else:
            logger.warning(f"无法获取点位 {cmd.point_key} 的data_source，使用原值 {cmd.data_source}")
        
        if cmd.data_source not in (1, 2, 3):
            return "data_source 仅支持 1/2/3"
        
        # 控制值类型允许 string/number/bool，若是数字字符串，尝试转为浮点数以便平台接受
        if isinstance(cmd.control_value, str):
            try:
                if "." in cmd.control_value:
                    cmd.control_value = float(cmd.control_value)
                else:
                    cmd.control_value = int(cmd.control_value)
            except Exception:
                # 保留为字符串
                pass
        
        return None
    
    async def _get_before_value(self, command: WriteCommand, token: str) -> Optional[Any]:
        """获取写值前的当前值"""
        if not command.object_code or not command.data_code:
            return None
        
        try:
            raw_result = await self.platform_api.query_realtime_value(
                command.object_code, command.data_code
            )
            if isinstance(raw_result, dict):
                # 先尝试直接获取value字段
                value = raw_result.get("value")
                
                # 如果没有直接的value字段，尝试从data数组中提取
                if value is None and "data" in raw_result and isinstance(raw_result["data"], list) and len(raw_result["data"]) > 0:
                    data_item = raw_result["data"][0]
                    if isinstance(data_item, dict):
                        # 优先使用property_num_value，如果不存在则使用property_value
                        if "property_num_value" in data_item:
                            value = data_item["property_num_value"]
                        elif "property_value" in data_item:
                            property_value = data_item["property_value"]
                            # 尝试转换为数字
                            try:
                                value = float(property_value) if property_value is not None else None
                            except (ValueError, TypeError):
                                value = property_value
                
                return value
        except Exception as e:
            logger.debug(f"获取before_value失败: {e}")
        
        return None
    
    async def _write_single_point(self, command: WriteCommand, token: str, operator_id: str) -> WriteResult:
        """单条写值并带重试"""
        # 验证命令（动态获取data_source）
        error = await self._validate_and_normalize_command(command)
        if error:
            return WriteResult(
                point_key=command.point_key,
                status="failed",
                message=error,
                duration_ms=0,
                before=None,
                after=None,
                retries=0
            )
        
        # 获取修改前值
        before_value = await self._get_before_value(command, token)
        
        # 执行写值（带重试）
        max_retries = 3
        retries = 0
        start_time = datetime.utcnow()
        
        while retries < max_retries:
            try:
                result = await self.platform_api.write_point_value(command, token)
                
                if result.get("success"):
                    # 写值成功
                    duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                    
                    write_result = WriteResult(
                        point_key=command.point_key,
                        status="ok",
                        message=None,
                        duration_ms=duration,
                        before=before_value,
                        after=command.control_value,
                        retries=retries
                    )
                    
                    # 记录成功审计
                    try:
                        insert_operation_log(
                            operator_id=operator_id,
                            point_key=command.point_key,
                            object_code=command.object_code,
                            data_code=command.data_code,
                            before_value=str(before_value) if before_value is not None else None,
                            after_value=str(command.control_value),
                            result="ok",
                            message=None,
                            duration_ms=duration,
                        )
                    except Exception as e:
                        logger.debug(f"写值成功但审计写入失败: {e}")
                    
                    return write_result
                else:
                    # 写值失败，准备重试
                    error_msg = result.get("error", "写值失败")
                    raise Exception(error_msg)
                    
            except Exception as e:
                retries += 1
                if retries >= max_retries:
                    # 达到重试上限
                    duration = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                    
                    write_result = WriteResult(
                        point_key=command.point_key,
                        status="failed",
                        message=str(e),
                        duration_ms=duration,
                        before=before_value,
                        after=None,
                        retries=retries - 1
                    )
                    
                    # 记录失败审计
                    try:
                        insert_operation_log(
                            operator_id=operator_id,
                            point_key=command.point_key,
                            object_code=command.object_code,
                            data_code=command.data_code,
                            before_value=str(before_value) if before_value is not None else None,
                            after_value=None,
                            result="failed",
                            message=str(e),
                            duration_ms=duration,
                        )
                    except Exception as audit_e:
                        logger.debug(f"写值失败且审计写入失败: {audit_e}")
                    
                    return write_result
                
                # 指数退避
                backoff = 0.2 * (2 ** (retries - 1))
                await asyncio.sleep(backoff)
        
        # 不应该到达这里，但作为保险
        return WriteResult(
            point_key=command.point_key,
            status="failed",
            message="未知错误",
            duration_ms=0,
            before=None,
            after=None,
            retries=max_retries
        )
    
    async def batch_write_points(self, commands: List[WriteCommand], operator_id: str = "system") -> BatchWriteResponse:
        """批量写值控制：并发执行，部分失败不中断"""
        if not commands:
            return BatchWriteResponse(total=0, success=0, failed=0, items=[])
        
        token = self.platform_api.get_runtime_token()
        
        # 并发执行所有写值任务
        tasks = [
            asyncio.create_task(self._write_single_point(cmd, token, operator_id))
            for cmd in commands
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        # 统计结果
        total = len(results)
        success = sum(1 for r in results if r.status == "ok")
        failed = total - success
        
        return BatchWriteResponse(
            total=total,
            success=success,
            failed=failed,
            items=results
        )
    
    async def get_point_list(self, object_codes: str, operator_id: str = "system") -> PointListResponse:
        """
        获取指定设备的点位列表及元信息
        支持多个设备编码（逗号分隔）
        """
        codes = [c.strip() for c in (object_codes or "").split(",") if c.strip()]
        if not codes:
            raise ValueError("参数 object_codes 不能为空")
        
        # 动态占位符
        placeholders = ",".join(["%s"] * len(codes))
        sql = f"""
            SELECT 
                o.object_code,
                p.data_code,
                p.data_name,
                p.point_key,
                p.data_type,
                p.unit,
                p.is_set,
                p.lower_control,
                p.border_min,
                p.border_max,
                p.warn_min,
                p.warn_max,
                p.error_min,
                p.error_max,
                p.data_source
            FROM bus_object_point_data p
            JOIN bus_object_info o ON p.object_id = o.object_id
            WHERE o.object_code IN ({placeholders})
            ORDER BY o.object_code, p.data_code
            LIMIT 1000
        """
        
        try:
            rows = execute_query(sql, tuple(codes)) or []
        except Exception as e:
            logger.error(f"点位列表查询失败: {e}")
            raise e
        
        items = []
        for row in rows:
            (
                object_code, data_code, data_name, point_key, data_type, unit,
                is_set, lower_control, border_min, border_max, warn_min, warn_max,
                error_min, error_max, data_source
            ) = row
            
            # 可写性：is_set==1 或 lower_control==1
            is_writable = (is_set == 1) or (lower_control == 1)
            
            items.append(PointMetadata(
                object_code=object_code,
                data_code=data_code,
                data_name=data_name,
                unit=unit,
                is_writable=is_writable,
                point_key=point_key,
                data_type=data_type,
                data_source=data_source,
                border_min=border_min,
                border_max=border_max,
                warn_min=warn_min,
                warn_max=warn_max,
                error_min=error_min,
                error_max=error_max
            ))
        
        # 记录查询审计
        try:
            insert_operation_log(
                operator_id=operator_id,
                point_key=":point-list:query",
                object_code=",".join(codes),
                data_code=None,
                before_value=None,
                after_value=str(len(items)),
                result="query",
                message=None,
                duration_ms=None,
            )
        except Exception as e:
            logger.debug(f"点位列表查询审计写入失败: {e}")
        
        return PointListResponse(items=items, count=len(items))


# 全局服务实例
device_control_service = DeviceControlService()