from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import logging
from datetime import datetime
import os
import config_electricity
from export_service import ElectricityExportService, SensorDataExportService
from models import ExportRequest, SensorExportRequest
from logger_config import app_logger


# 使用配置好的logger
logger = app_logger

app = FastAPI(title="环控平台维护工具Web版", description="将桌面端环控平台维护工具迁移为Web应用")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)