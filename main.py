from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import logging
from datetime import datetime
import os
import time
from threading import RLock
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=True)
import requests
import hashlib
import config_electricity
from export_service import ElectricityExportService, SensorDataExportService
from models import (
    ExportRequest, SensorExportRequest, WriteCommand, 
    RealtimeQuery, BatchWriteRequest
)
from logger_config import app_logger
from db_config import ensure_operation_log_table, insert_operation_log, execute_query
from control_service import device_control_service
from audit_service import audit_service


# 使用配置好的logger
logger = app_logger

app = FastAPI(title="环控平台维护工具Web版", description="将桌面端环控平台维护工具迁移为Web应用")

@app.on_event("startup")
async def _startup_check():
    # 启动时输出 token 加载状态，便于问题定位（不打印明文）
    try:
        env_tok = os.environ.get("HK_PLATFORM_TOKEN")
        env_len = len(env_tok) if env_tok else 0
        logger.info(f"[startup] env HK_PLATFORM_TOKEN len={env_len}")
        if not env_tok:
            # 触发 .env 回退
            try:
                tok = _get_token()
                logger.info(f"[startup] .env fallback HK_PLATFORM_TOKEN len={len(tok)}")
            except Exception as _e:
                logger.warning(f"[startup] .env fallback failed: {_e}")
    except Exception as _e:
        logger.warning(f"[startup] token check error: {_e}")

# 确保审计表存在
try:
    ensure_operation_log_table()
except Exception as _e:
    logger.warning(f"初始化审计表遇到问题: {_e}")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
electricity_service = ElectricityExportService()
sensor_service = SensorDataExportService()

@app.get("/")
async def root():
    return {"message": "环控平台维护工具Web版 API"}



@app.get("/api/lines")
async def get_lines():
    """获取所有线路配置"""
    try:
        lines = list(config_electricity.line_configs.keys())
        return {"lines": lines}
    except Exception as e:
        logger.error(f"获取线路配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/line-config/{line_name}")
async def get_line_config(line_name: str):
    """获取指定线路的配置详情"""
    try:
        if line_name not in config_electricity.line_configs:
            raise HTTPException(status_code=404, detail=f"线路 {line_name} 不存在")
        
        config = config_electricity.line_configs[line_name]
        # 只返回基本信息，不返回完整的data_list以减少数据量
        simplified_config = {}
        for station_name, station_config in config.items():
            simplified_config[station_name] = {
                "ip": station_config["ip"],
                "station": station_config["station"]
            }
        return {"config": simplified_config}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取线路配置详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config/line_configs")
async def get_line_configs():
    """获取所有线路-车站配置"""
    try:
        # 转换为前端需要的格式：{线路名: [{station_name, station_ip}]}
        result = {}
        for line_name, line_config in config_electricity.line_configs.items():
            stations = []
            for station_name, station_config in line_config.items():
                stations.append({
                    "station_name": station_config.get("station", station_name),
                    "station_ip": station_config["ip"]
                })
            result[line_name] = stations
        return result
    except Exception as e:
        logger.error(f"获取线路配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/electricity")
async def export_electricity_data(request: ExportRequest):
    """导出电耗数据"""
    try:
        logger.info(f"开始导出电耗数据: 线路={request.line}, 时间范围={request.start_time} 到 {request.end_time}")
        
        # 异步执行导出任务
        result = await electricity_service.export_data_async(
            request.line, 
            request.start_time, 
            request.end_time
        )
        
        return result
    except Exception as e:
        logger.error(f"导出电耗数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/sensor")
async def export_sensor_data(request: SensorExportRequest):
    """导出传感器数据"""
    try:
        logger.info(f"开始导出传感器数据: 线路={request.line}, 时间范围={request.start_time} 到 {request.end_time}")
        
        # 异步执行导出任务
        result = await sensor_service.export_data_async(
            request.line, 
            request.start_time, 
            request.end_time
        )
        
        return result
    except Exception as e:
        logger.error(f"导出传感器数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """下载导出的文件"""
    try:
        # 检查文件是否存在
        if not os.path.exists(filename):
            raise HTTPException(status_code=404, detail=f"文件 {filename} 不存在")
        
        # 返回文件响应
        return FileResponse(
            path=filename,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载文件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===================== 设备控制模块：使用新的服务架构 =====================

@app.get("/control/device-tree")
async def get_device_tree_endpoint(request: Request, station_ip: Optional[str] = None):
    """获取设备树结构（支持按 station_ip 切换数据源）"""
    operator_id = request.headers.get("x-operator-id", "system")
    try:
        result = await device_control_service.get_device_tree(operator_id, station_ip)
        return result.dict()
    except Exception as e:
        logger.error(f"获取设备树失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/control/points/real-time")
async def get_point_realtime_endpoint(object_code: str, data_code: str, request: Request):
    """点位实时值查询"""
    operator_id = request.headers.get("x-operator-id", "system")
    try:
        result = await device_control_service.query_realtime_point(object_code, data_code, operator_id)
        return result.dict()
    except Exception as e:
        logger.error(f"实时查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/control/points/write")
async def write_points_endpoint(commands: List[WriteCommand], request: Request):
    """批量写值控制"""
    operator_id = request.headers.get("x-operator-id", "system")
    # INFO 入口日志：记录操作者、数量与示例摘要，便于审计与排查
    try:
        sample = []
        for cmd in commands[:5]:
            try:
                pk = getattr(cmd, "point_key", None) or f"{getattr(cmd, 'object_code', '')}:{getattr(cmd, 'data_code', '')}"
                cv = getattr(cmd, "control_value", None)
                sample.append(f"{pk}={cv}")
            except Exception:
                sample.append("<parse_error>")
        logger.info(f"批量写值请求: operator_id={operator_id}, count={len(commands)}, sample=[{'; '.join(sample)}]")
    except Exception as _e:
        logger.debug(f"记录批量写值入口日志失败: {_e}")
    try:
        result = await device_control_service.batch_write_points(commands, operator_id)
        return result.dict()
    except Exception as e:
        logger.error(f"批量写值失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/control/points/default")
async def get_default_points_endpoint(object_codes: str, request: Request):
    """获取指定设备的点位列表及元信息"""
    operator_id = request.headers.get("x-operator-id", "system")
    try:
        result = await device_control_service.get_point_list(object_codes, operator_id)
        return result.dict()
    except Exception as e:
        logger.error(f"获取点位列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===================== 审计日志接口 =====================

@app.get("/audit/logs")
async def get_audit_logs(
    operator_id: Optional[str] = None,
    point_key: Optional[str] = None,
    object_code: Optional[str] = None,
    result: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """查询操作审计日志"""
    try:
        logs, total = audit_service.query_operation_logs(
            operator_id=operator_id,
            point_key=point_key,
            object_code=object_code,
            result=result,
            limit=limit,
            offset=offset
        )
        return {
            "logs": [log.dict() for log in logs],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"查询审计日志失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

PLATFORM_BASE = "http://192.168.100.3"
# 实时查询使用 9801 端口的新接口；写值仍走默认端口
SELECT_URL = "http://192.168.100.3:9801/api/objectPointInfo/selectObjectPointValueByDataCode"
WRITE_URL = f"{PLATFORM_BASE}/api/objectPointInfo/writePointValue"
LOGIN_URL = "http://192.168.100.3:9801/api/user/login"
# 固定Token兜底（仅用于联通性验证；后续回滚至.env加载）
HK_TOKEN_FALLBACK = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhaXRlc3QiLCJhdWRpZW5jZSI6IndlYiIsImNyZWF0ZWQiOjE3NTUyMjIzOTM0ODUsIm5pY2tOYW1lIjoi57O757uf566h55CG5ZGYIiwiYXV0aFRva2VuIjpudWxsLCJjb21wYW55IjoyNTEsImV4cCI6MTAzOTUyMjIzOTMsInVzZXJJZCI6NDA1fQ.ulpIECFHg11RMmGhkYSqwwgNaVJ1ZyzG8vwuziVL9MIADQ07Sr1H6TQ7-5-qtnl3raTRQ_qSmjF4CZeWgoosoQ"

def _get_token_effective() -> str:
    try:
        t = _get_token()
        if isinstance(t, str) and t.strip():
            return t.strip()
    except Exception:
        pass
    return HK_TOKEN_FALLBACK

def _get_token() -> str:
    # 优先读环境变量；若为空则回退解析 .env
    token = os.environ.get("HK_PLATFORM_TOKEN")
    if token and isinstance(token, str) and token.strip():
        return token.strip()
    # 回退：直接读取 .env 解析 HK_PLATFORM_TOKEN
    try:
        env_path = Path(__file__).resolve().parent / ".env"
        if env_path.exists():
            content = env_path.read_text(encoding="utf-8")
            # 解析格式：HK_PLATFORM_TOKEN = "xxx" 或 HK_PLATFORM_TOKEN=xxx
            import re
            m = re.search(r"^\\s*HK_PLATFORM_TOKEN\\s*=\\s*[\"']?([^\"'\
\
]+)[\"']?\\s*$", content, re.MULTILINE)
            if m:
                token = m.group(1).strip()
                if token:
                    # 写回进程环境，后续调用可直接获取
                    os.environ["HK_PLATFORM_TOKEN"] = token
                    logger.info(f"已从 .env 加载 HK_PLATFORM_TOKEN，len={len(token)}")
                    return token
    except Exception as _e:
        logger.debug(f".env 回退解析失败: {_e}")
    logger.error("缺少 HK_PLATFORM_TOKEN（环境变量与 .env 均未获取到）")
    raise HTTPException(status_code=500, detail="服务端缺少平台访问凭证，请配置 HK_PLATFORM_TOKEN")

# ============ 动态登录获取 Token（缓存） ============
_TOKEN_TTL_SEC = 1200  # 20 分钟
_token_cache = {"value": None, "exp": 0.0}
_token_lock = RLock()

def _login_platform() -> str:
    """调用平台登录接口获取实时 token，不记录明文。"""
    user = os.environ.get("HK_LOGIN_USER") or "aitest"
    pwd = os.environ.get("HK_LOGIN_PWD") or ""
    try:
        sha = hashlib.sha256(pwd.encode("utf-8")).hexdigest()
        md5 = hashlib.md5(pwd.encode("utf-8")).hexdigest()
        hashed_pwd = f"{sha}{md5}"
        resp = requests.post(
            LOGIN_URL,
            data={"user_name": user, "pwd": hashed_pwd},
            timeout=6.0,
        )
        if resp.status_code != 200:
            logger.error(f"登录接口HTTP错误 code={resp.status_code}, body_head={(resp.text[:200] if resp.text else '')}")
            raise HTTPException(status_code=502, detail="平台登录失败(HTTP)")
        data = resp.json() if resp.text else {}
        if isinstance(data, dict) and data.get("code") == 1 and data.get("data") and data["data"].get("token"):
            tok = data["data"]["token"]
            logger.info(f"login ok, token_len={len(tok)} user={user}")
            return tok
        msg = data.get("message") if isinstance(data, dict) else "invalid_response"
        logger.error(f"登录返回异常: {msg}")
        raise HTTPException(status_code=502, detail=f"平台登录失败: {msg}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登录异常: {e}")
        raise HTTPException(status_code=502, detail="平台登录异常")

def _get_runtime_token() -> str:
    """获取运行时token：优先使用缓存；过期则登录刷新。"""
    now = time.time()
    with _token_lock:
        if _token_cache.get("value") and _token_cache.get("exp", 0.0) > now:
            return _token_cache["value"]
        tok = _login_platform()
        _token_cache["value"] = tok
        _token_cache["exp"] = now + _TOKEN_TTL_SEC
        return tok

def _requests_get(url: str, params: Dict[str, Any], headers: Optional[Dict[str, Any]] = None, timeout: float = 5.0) -> Dict[str, Any]:
    try:
        # 记录下游请求形态（脱敏 token）
        safe_headers = dict(headers or {})
        if "Authorization" in safe_headers:
            safe_headers["Authorization"] = "Bearer ***"
        if "token" in safe_headers:
            safe_headers["token"] = "***"
        if "Token" in safe_headers:
            safe_headers["Token"] = "***"
        logger.info(f"REQ GET url={url} params={params} headers={safe_headers}")
        resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        logger.info(f"RESP GET status={resp.status_code} text_head={resp.text[:120] if resp.text else ''}")
        if resp.status_code != 200:
            logger.error(f"下游查询失败 code={resp.status_code}, body={resp.text[:500]}")
            raise HTTPException(status_code=502, detail="下游平台查询失败")
        return resp.json()
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"下游查询异常: {e}")
        raise HTTPException(status_code=502, detail="下游平台查询异常")

def _requests_post_json(url: str, json_body: Any, headers: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None, cookies: Optional[Dict[str, str]] = None, timeout: float = 8.0) -> Dict[str, Any]:
    try:
        use_headers = dict(headers or {})
        if "Content-Type" not in {k.title(): v for k, v in use_headers.items()}:
            use_headers["Content-Type"] = "application/json"
        resp = requests.post(url, params=params, json=json_body, headers=use_headers, cookies=cookies, timeout=timeout)
        if resp.status_code != 200:
            logger.error(f"下游写值失败 code={resp.status_code}, body={resp.text[:500]}")
            raise HTTPException(status_code=502, detail="下游平台写值失败")
        return resp.json() if resp.text else {}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"下游写值异常: {e}")
        raise HTTPException(status_code=502, detail="下游平台写值异常")

def _call_select_with_variants(url: str, object_code: str, data_code: str, token: str) -> Dict[str, Any]:
    # 0) 统一候选集
    header_candidates = [
        {"token": token},
        {"Token": token},
        {"TOKEN": token},
        {"X-Auth-Token": token},
        {"Authorization": f"Bearer {token}"},
        {"Authorization": token},  # 裸值
    ]
    query_token_keys = ["token", "access_token", "auth_token", "Authorization"]
    json_token_keys = ["token", "access_token", "auth_token"]
    data_keys = ["object_code", "data_code"]
    alt_data_keys = [("object_code","data_code"), ("objectCode","dataCode"), ("point_object","point_code"), ("object","code")]
    # 1) 首次三轨（params+json+headers+cookie）
    base_json = {"object_code": object_code, "data_code": data_code, "token": token}
    base_params = {"object_code": object_code, "data_code": data_code, "token": token}
    base_headers = {"token": token, "Token": token, "Authorization": f"Bearer {token}"}
    try:
        return _requests_post_json(url, base_json, base_headers, base_params, {"token": token}, timeout=6.0)
    except Exception:
        pass
    # 2) headers only × 多头部
    for h in header_candidates:
        try:
            r = requests.post(url, json={"object_code": object_code, "data_code": data_code}, headers=h, timeout=4.0)
            if r.status_code == 200:
                return r.json() if r.text else {}
        except Exception:
            pass
    # 3) query×多token键
    for tk in query_token_keys:
        try:
            r = requests.post(url, params={tk: token, "object_code": object_code, "data_code": data_code}, timeout=4.0)
            if r.status_code == 200:
                return r.json() if r.text else {}
        except Exception:
            pass
    # 4) json×多token键
    for tk in json_token_keys:
        try:
            j = {"object_code": object_code, "data_code": data_code, tk: token}
            r = requests.post(url, json=j, timeout=4.0)
            if r.status_code == 200:
                return r.json() if r.text else {}
        except Exception:
            pass
    # 5) cookie
    try:
        r = requests.post(url, json={"object_code": object_code, "data_code": data_code}, cookies={"token": token}, timeout=4.0)
        if r.status_code == 200:
            return r.json() if r.text else {}
    except Exception:
        pass
    # 6) form-urlencoded（含token）
    for tk in ["token", "access_token", "auth_token"]:
        try:
            form = {"object_code": object_code, "data_code": data_code, tk: token}
            r = requests.post(url, data=form, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=4.0)
            if r.status_code == 200:
                return r.json() if r.text else {}
        except Exception:
            pass
    # 7) multipart/form-data（含token）
    try:
        mp = {"object_code": (None, object_code), "data_code": (None, data_code), "token": (None, token)}
        r = requests.post(url, files=mp, timeout=4.0)
        if r.status_code == 200:
            return r.json() if r.text else {}
    except Exception:
        pass
    # 8) 键名变体（只传 data_code 变体 + 头部 token）
    for k in ["data_code", "dataCode", "point_code", "code"]:
        for h in header_candidates:
            try:
                r = requests.post(url, json={k: data_code}, headers=h, timeout=4.0)
                if r.status_code == 200:
                    return r.json() if r.text else {}
            except Exception:
                pass
    raise HTTPException(status_code=502, detail="下游平台查询失败（鉴权矩阵均未命中）")

@app.get("/control/points/real-time")
async def get_point_realtime(object_code: str, data_code: str, request: Request):
    """点位实时值查询：封装平台POST接口（已改为POST），带固定Token兜底 + 鉴权矩阵回退"""
    token = _get_runtime_token()
    logger.info(f"RT CALL object_code={object_code} data_code={data_code} token_len={len(token)}")
    loop = asyncio.get_event_loop()
    try:
        raw = await loop.run_in_executor(
            None,
            lambda: (
                (lambda resp: (resp.json() if resp.status_code == 200 and resp.text else {}))(
                    requests.post(
                        SELECT_URL,
                        data={"object_code": object_code, "data_code": data_code, "token": token},
                        headers={
                            "Content-Type": "application/x-www-form-urlencoded",
                            "authorization": token,
                            "token": token,
                            "x-locale": "zh_cn"
                        },
                        timeout=6.0,
                    )
                )
            ),
        )
    except Exception as _e:
        logger.error(f"实时查询失败: {_e}")
        raw = {"code": 502, "message": "select_failed", "error": str(_e)}
    # 规范化返回
    now_iso = datetime.utcnow().isoformat() + "Z"
    
    # 从平台API响应中提取值
    value = None
    unit = None
    if isinstance(raw, dict):
        # 先尝试直接获取value字段
        value = raw.get("value")
        unit = raw.get("unit")
        
        # 如果没有直接的value字段，尝试从data数组中提取
        if value is None and "data" in raw and isinstance(raw["data"], list) and len(raw["data"]) > 0:
            data_item = raw["data"][0]
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
    result_obj = {
        "object_code": object_code,
        "data_code": data_code,
        "value": value,
        "unit": unit,
        "ts": now_iso,
        "token_len": len(token) if isinstance(token, str) else 0,
        "raw": raw if isinstance(raw, dict) else {"data": raw},
    }
    # 审计只记录查询操作概要（不写before/after）
    operator_id = request.headers.get("x-operator-id", "system")
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
    except Exception as _e:
        logger.debug(f"查询审计写入失败: {_e}")
    return result_obj

def _validate_and_normalize(cmd: Dict[str, Any]) -> Optional[str]:
    # 返回错误信息字符串；通过则返回 None
    if "point_key" not in cmd or "data_source" not in cmd or "control_value" not in cmd:
        return "缺少必填字段 point_key/data_source/control_value"
    if not isinstance(cmd["point_key"], str) or not cmd["point_key"]:
        return "point_key 必须为非空字符串"
    if cmd["data_source"] not in (1, 2, 3):
        return "data_source 仅支持 1/2/3"
    # 控制值类型允许 string/number/bool，若是数字字符串，尝试转为浮点数以便平台接受
    v = cmd["control_value"]
    if isinstance(v, str):
        try:
            if "." in v:
                cmd["control_value"] = float(v)
            else:
                cmd["control_value"] = int(v)
        except Exception:
            # 保留为字符串
            pass
    # 可在此添加范围规则：示例温度[-50, 100]
    return None

async def _write_one(cmd: Dict[str, Any], token: str, operator_id: str) -> Dict[str, Any]:
    # 单条下发并带重试；返回逐项结果
    err = _validate_and_normalize(cmd)
    if err:
        return {"point_key": cmd.get("point_key"), "status": "failed", "message": err, "retries": 0}
    # before_value：若提供 object_code + data_code，调用实时查询接口
    before_val = None
    try:
        if isinstance(cmd, dict) and cmd.get("object_code") and cmd.get("data_code"):
            loop = asyncio.get_event_loop()
            def _pre_read():
                r = requests.post(
                    SELECT_URL,
                    data={"object_code": cmd["object_code"], "data_code": cmd["data_code"], "token": token},
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                        "authorization": token,
                        "token": token,
                        "x-locale": "zh_cn"
                    },
                    timeout=6.0,
                )
                return r.json() if r.status_code == 200 and r.text else {}
            before_raw = await loop.run_in_executor(None, _pre_read)
            if isinstance(before_raw, dict):
                # 从平台API响应中提取值
                before_val = before_raw.get("value")
                
                # 如果没有直接的value字段，尝试从data数组中提取
                if before_val is None and "data" in before_raw and isinstance(before_raw["data"], list) and len(before_raw["data"]) > 0:
                    data_item = before_raw["data"][0]
                    if isinstance(data_item, dict):
                        # 优先使用property_num_value，如果不存在则使用property_value
                        if "property_num_value" in data_item:
                            before_val = data_item["property_num_value"]
                        elif "property_value" in data_item:
                            property_value = data_item["property_value"]
                            # 尝试转换为数字
                            try:
                                before_val = float(property_value) if property_value is not None else None
                            except (ValueError, TypeError):
                                before_val = property_value
    except Exception as _e:
        logger.debug(f"获取before_value失败: {_e}")
    payload = [  # 平台接口接受数组体
        {
            "point_key": cmd["point_key"],
            "data_source": cmd["data_source"],
            "control_value": cmd["control_value"],
        }
    ]
    params = None  # 写值接口为 POST JSON，不需 query
    tries, max_tries = 0, 3
    start = datetime.utcnow()
    loop = asyncio.get_event_loop()
    while True:
        tries += 1
        try:
            # 将 token 放在 header: token（若平台必须在 body，可改为 payload 注入）
            result = await loop.run_in_executor(
                None,
                lambda: requests.post(
                    WRITE_URL,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "authorization": token,
                        "token": token
                    },
                    timeout=8.0
                ),
            )
            if result.status_code == 200:
                duration = (datetime.utcnow() - start).total_seconds() * 1000
                # 响应结构不固定，尽量兼容
                res = {
                    "point_key": cmd["point_key"],
                    "status": "ok",
                    "message": None,
                    "duration_ms": int(duration),
                    "before": before_val,
                    "after": cmd.get("control_value"),
                    "retries": tries - 1,
                }
                try:
                    insert_operation_log(
                        operator_id=operator_id,
                        point_key=cmd["point_key"],
                        object_code=cmd.get("object_code"),
                        data_code=cmd.get("data_code"),
                        before_value=str(before_val) if before_val is not None else None,
                        after_value=str(cmd.get("control_value")),
                        result="ok",
                        message=f"data_source={cmd.get('data_source')}",
                        duration_ms=int(duration),
                    )
                except Exception as _e:
                    logger.debug(f"写值成功但审计写入失败: {_e}")
                return res
            else:
                msg = f"HTTP {result.status_code}: {result.text[:200]}"
                raise RuntimeError(msg)
        except Exception as e:
            if tries >= max_tries:
                duration = (datetime.utcnow() - start).total_seconds() * 1000
                logger.warning(f"写值失败且达到重试上限 point_key={cmd.get('point_key')}, err={e}")
                res = {
                    "point_key": cmd.get("point_key"),
                    "status": "failed",
                    "message": str(e),
                    "duration_ms": int(duration),
                    "before": before_val,
                    "after": None,
                    "retries": tries - 1,
                }
                try:
                    insert_operation_log(
                        operator_id=operator_id,
                        point_key=cmd.get("point_key") or "",
                        object_code=cmd.get("object_code"),
                        data_code=cmd.get("data_code"),
                        before_value=str(before_val) if before_val is not None else None,
                        after_value=None,
                        result="failed",
                        message=str(e),
                        duration_ms=int(duration),
                    )
                except Exception as _e:
                    logger.debug(f"写值失败且审计写入失败: {_e}")
                return res
            backoff = 0.2 * (2 ** (tries - 1))
            await asyncio.sleep(backoff)

# 旧实现的 /control/points/write 已移除，统一由 write_points_endpoint 提供实现

@app.get("/control/points/default")
async def get_default_points(object_codes: str, request: Request):
    """
    默认联调数据源：按 object_codes 过滤点位清单并返回必要元信息。
    返回字段：
      - object_code, data_code, point_key, data_type, unit, is_writable
      - border_min, border_max, warn_min, warn_max, error_min, error_max
    """
    codes = [c.strip() for c in (object_codes or "").split(",") if c.strip()]
    if not codes:
        raise HTTPException(status_code=400, detail="参数 object_codes 不能为空")
    # 动态占位符
    placeholders = ",".join(["%s"] * len(codes))
    sql = """
        SELECT 
            o.object_code,
            p.data_code,
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
            p.error_max
        FROM bus_object_point_data p
        JOIN bus_object_info o ON p.object_id = o.object_id
        WHERE o.object_code IN (""" + placeholders + """)
        LIMIT 1000
    """
    try:
        rows = execute_query(sql, tuple(codes)) or []
    except Exception as e:
        logger.error(f"默认数据源查询失败: {e}")
        raise HTTPException(status_code=500, detail="查询点位清单失败")
    result = []
    for row in rows:
        # execute_query 默认返回 tuple，按选取顺序映射
        (object_code, data_code, point_key, data_type, unit,
         is_set, lower_control, border_min, border_max, warn_min, warn_max, error_min, error_max) = row
        # 可写性：is_set==1 或 lower_control==1
        is_writable = (is_set == 1) or (lower_control == 1)
        result.append({
            "object_code": object_code,
            "data_code": data_code,
            "point_key": point_key,
            "data_type": data_type,
            "unit": unit,
            "is_writable": bool(is_writable),
            "border_min": border_min,
            "border_max": border_max,
            "warn_min": warn_min,
            "warn_max": warn_max,
            "error_min": error_min,
            "error_max": error_max,
        })
    # 记录一次只读审计
    operator_id = request.headers.get("x-operator-id", "system")
    try:
        insert_operation_log(
            operator_id=operator_id,
            point_key=":default:list",
            object_code=",".join(codes),
            data_code=None,
            before_value=None,
            after_value=str(len(result)),
            result="query",
            message=None,
            duration_ms=None,
        )
    except Exception as _e:
        logger.debug(f"默认数据源审计写入失败: {_e}")
    return {"items": result, "count": len(result)}

@app.get("/control/debug-token")
async def debug_token():
    # 尝试通过 _get_token 触发回退加载，以便确认来源
    src = "env"
    t = os.environ.get("HK_PLATFORM_TOKEN")
    if not t:
        src = "env+.env_fallback"
        try:
            t = _get_token()
        except Exception:
            t = None
    return {"has": bool(t), "len": (len(t) if t else 0), "source": src}

from fastapi.responses import PlainTextResponse

@app.get("/control/debug-token-raw", response_class=PlainTextResponse)
async def debug_token_raw():
    # 以纯文本返回，避免客户端解析差异
    src = "env"
    t = os.environ.get("HK_PLATFORM_TOKEN")
    if not t:
        src = "env+.env_fallback"
        try:
            t = _get_token()
        except Exception:
            t = None
    has_str = "true" if t else "false"
    ln = str(len(t)) if t else "0"
    return f"has={has_str}; len={ln}; source={src}"

@app.get("/control/debug-env")
async def debug_env():
    # 返回以 HK_ 开头的环境变量快照（不含明文 token）
    try:
        items = {k: (len(v) if isinstance(v, str) else None) for k, v in os.environ.items() if k.startswith("HK_")}
        return {"keys": list(items.keys()), "lens": items}
    except Exception as _e:
        return {"error": str(_e)}

@app.get("/control/debug-runtime-token")
async def debug_runtime_token():
    try:
        tok = _get_runtime_token()
        ln = len(tok) if tok else 0
        head = tok[:6] if tok and ln >= 6 else tok or ""
        tail = tok[-6:] if tok and ln >= 6 else ""
        return {"len": ln, "head": head, "tail": tail}
    except Exception as _e:
        return {"error": str(_e)}

@app.get("/control/device-tree-test")
async def get_device_tree_test(request: Request):
    """
    测试版本：返回带有点位的设备树结构
    """
    return {
        "tree": [
            {
                "id": "test_project",
                "label": "测试项目 (test_project) [2点]",
                "children": [
                    {
                        "id": "test_device",
                        "label": "测试设备 (test_device) [2点]",
                        "children": [
                            {
                                "id": "test_device:point1",
                                "label": "✔ point1 (温度点位)",
                                "meta": {
                                    "object_code": "test_device",
                                    "data_code": "point1",
                                    "data_name": "温度点位",
                                    "unit": "℃",
                                    "is_writable": True,
                                    "point_key": "test:point1",
                                    "data_type": "0"
                                }
                            },
                            {
                                "id": "test_device:point2",
                                "label": "point2 (湿度点位)",
                                "meta": {
                                    "object_code": "test_device",
                                    "data_code": "point2",
                                    "data_name": "湿度点位",
                                    "unit": "%",
                                    "is_writable": False,
                                    "point_key": "test:point2",
                                    "data_type": "0"
                                }
                            }
                        ],
                        "meta": {
                            "object_code": "test_device",
                            "object_name": "测试设备",
                            "object_type": "device",
                            "point_count": 2
                        }
                    }
                ],
                "meta": {
                    "object_code": "test_project",
                    "object_name": "测试项目",
                    "object_type": "project",
                    "total_points": 2
                }
            }
        ],
        "count": 1
    }

@app.get("/control/device-tree-legacy")
async def get_device_tree(request: Request):
    """
    从MySQL数据库获取设备树结构
    构建层级：项目 -> 子项目/设备 -> 点位
    支持小系统传感器数据模式（fSmallFan%, fRoomTemp%, fSmallHigh%, iSmallHigh%, fSmallLow%, iSmallLow%, fSmallChil%等）
    """
    operator_id = request.headers.get("x-operator-id", "system")
    
    try:
        # 查询项目根节点（parent_id = 0）
        root_sql = """
            SELECT object_id, object_code, object_name, object_type
            FROM bus_object_info 
            WHERE status = 1 AND parent_id = 0
            ORDER BY object_code
        """
        root_nodes = execute_query(root_sql) or []
        
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
            children = execute_query(children_sql, (object_id,)) or []
            
            child_nodes = []
            total_points = 0
            
            for child in children:
                child_id, child_code, child_name, child_type, point_count = child
                total_points += point_count or 0
                
                # 查询该子设备的点位信息（特别支持小系统传感器）
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
                        p.data_type
                    FROM bus_object_point_data p
                    WHERE p.object_id = %s
                    ORDER BY p.data_code
                    LIMIT 20
                """
                # 直接为 WSD_CGQ 添加一些点位作为测试
                if child_code == "WSD_CGQ":
                    point_nodes = [
                        {
                            "id": f"{child_code}:H-A01_1",
                            "label": "✔ H-A01_1 (温度传感器H-A01_温度值)",
                            "meta": {
                                "object_code": child_code,
                                "data_code": "H-A01_1",
                                "data_name": "温度传感器H-A01_温度值",
                                "unit": "℃",
                                "is_writable": True,
                                "point_key": f"C251:{child_code}:H-A01_1",
                                "data_type": "0"
                            }
                        },
                        {
                            "id": f"{child_code}:H-A01_2",
                            "label": "H-A01_2 (温度传感器H-A01_湿度值)",
                            "meta": {
                                "object_code": child_code,
                                "data_code": "H-A01_2",
                                "data_name": "温度传感器H-A01_湿度值",
                                "unit": "%",
                                "is_writable": False,
                                "point_key": f"C251:{child_code}:H-A01_2",
                                "data_type": "0"
                            }
                        },
                        {
                            "id": f"{child_code}:H-A02_1",
                            "label": "✔ H-A02_1 (温度传感器H-A02_温度值)",
                            "meta": {
                                "object_code": child_code,
                                "data_code": "H-A02_1",
                                "data_name": "温度传感器H-A02_温度值",
                                "unit": "℃",
                                "is_writable": True,
                                "point_key": f"C251:{child_code}:H-A02_1",
                                "data_type": "0"
                            }
                        }
                    ]
                else:
                    # 其他设备不显示点位，避免大量数据
                    point_nodes = []
                
                child_nodes.append({
                    "id": child_code,
                    "label": f"{child_name} ({child_code}) [{point_count or 0}点]",
                    "children": point_nodes,
                    "meta": {
                        "object_code": child_code,
                        "object_name": child_name,
                        "object_type": child_type,
                        "point_count": point_count or 0
                    }
                })
            
            tree_nodes.append({
                "id": object_code,
                "label": f"{object_name} ({object_code}) [{total_points}点]",
                "children": child_nodes,
                "meta": {
                    "object_code": object_code,
                    "object_name": object_name,
                    "object_type": object_type,
                    "total_points": total_points
                }
            })
        
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
                message="load_device_tree",
                duration_ms=None,
            )
        except Exception as _e:
            logger.debug(f"设备树查询审计写入失败: {_e}")
        
        return {"tree": tree_nodes, "count": len(tree_nodes)}
        
    except Exception as e:
        logger.error(f"获取设备树失败: {e}")
        raise HTTPException(status_code=500, detail="获取设备树失败")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)