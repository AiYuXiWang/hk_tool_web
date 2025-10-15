"""
数据上传API

提供文件上传、数据解析、数据验证和导出等功能的API接口。
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Query
from typing import Optional, Dict, Any, List
import json
from backend.app.services.data_service import DataService
from backend.app.core.dependencies import get_data_service

router = APIRouter()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    data_service: DataService = Depends(get_data_service)
):
    """
    上传文件
    
    Args:
        file: 上传的文件
        data_service: 数据服务依赖注入
        
    Returns:
        上传结果，包含文件ID和基本信息
    """
    try:
        # 读取文件内容
        file_content = await file.read()
        
        # 调用服务层处理
        result = await data_service.upload_file(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type
        )
        
        if result.get("success"):
            return {
                "code": 200,
                "message": result.get("message", "success"),
                "data": result.get("data")
            }
        else:
            status_code = result.get("status_code", 500)
            raise HTTPException(status_code=status_code, detail=result.get("message"))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@router.post("/parse/{file_id}")
async def parse_file(
    file_id: str,
    parse_options: Optional[str] = Form(None),
    data_service: DataService = Depends(get_data_service)
):
    """
    解析文件内容
    
    Args:
        file_id: 文件ID
        parse_options: 解析选项（JSON字符串）
        data_service: 数据服务依赖注入
        
    Returns:
        解析结果
    """
    try:
        # 解析选项
        options = {}
        if parse_options:
            try:
                options = json.loads(parse_options)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="解析选项格式错误")
        
        # 调用服务层处理
        result = await data_service.parse_file(file_id, options)
        
        if result.get("success"):
            return {
                "code": 200,
                "message": result.get("message", "success"),
                "data": result.get("data")
            }
        else:
            status_code = result.get("status_code", 500)
            raise HTTPException(status_code=status_code, detail=result.get("message"))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件解析失败: {str(e)}")

@router.post("/validate")
async def validate_data(
    data: List[Dict[str, Any]],
    validation_rules: Dict[str, Any],
    data_service: DataService = Depends(get_data_service)
):
    """
    验证数据
    
    Args:
        data: 要验证的数据
        validation_rules: 验证规则
        data_service: 数据服务依赖注入
        
    Returns:
        验证结果
    """
    try:
        # 调用服务层处理
        result = await data_service.validate_data(data, validation_rules)
        
        if result.get("success"):
            return {
                "code": 200,
                "message": result.get("message", "success"),
                "data": result.get("data")
            }
        else:
            status_code = result.get("status_code", 500)
            raise HTTPException(status_code=status_code, detail=result.get("message"))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据验证失败: {str(e)}")

@router.post("/export")
async def export_data(
    data: List[Dict[str, Any]],
    export_format: str = Form("xlsx"),
    export_options: Optional[str] = Form(None),
    data_service: DataService = Depends(get_data_service)
):
    """
    导出数据
    
    Args:
        data: 要导出的数据
        export_format: 导出格式 (xlsx, csv, json)
        export_options: 导出选项（JSON字符串）
        data_service: 数据服务依赖注入
        
    Returns:
        导出结果，包含文件路径
    """
    try:
        # 解析导出选项
        options = {}
        if export_options:
            try:
                options = json.loads(export_options)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="导出选项格式错误")
        
        # 调用服务层处理
        result = await data_service.export_data(data, export_format, options)
        
        if result.get("success"):
            return {
                "code": 200,
                "message": result.get("message", "success"),
                "data": result.get("data")
            }
        else:
            status_code = result.get("status_code", 500)
            raise HTTPException(status_code=status_code, detail=result.get("message"))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据导出失败: {str(e)}")

@router.get("/files/{file_id}")
async def get_file_info(
    file_id: str,
    data_service: DataService = Depends(get_data_service)
):
    """
    获取文件信息
    
    Args:
        file_id: 文件ID
        data_service: 数据服务依赖注入
        
    Returns:
        文件信息
    """
    try:
        result = await data_service.get_file_info(file_id)
        
        if result.get("success"):
            return {
                "code": 200,
                "message": result.get("message", "success"),
                "data": result.get("data")
            }
        else:
            status_code = result.get("status_code", 500)
            raise HTTPException(status_code=status_code, detail=result.get("message"))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件信息失败: {str(e)}")

@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    data_service: DataService = Depends(get_data_service)
):
    """
    删除文件
    
    Args:
        file_id: 文件ID
        data_service: 数据服务依赖注入
        
    Returns:
        删除结果
    """
    try:
        result = await data_service.delete_file(file_id)
        
        if result.get("success"):
            return {
                "code": 200,
                "message": result.get("message", "success"),
                "data": result.get("data")
            }
        else:
            status_code = result.get("status_code", 500)
            raise HTTPException(status_code=status_code, detail=result.get("message"))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件删除失败: {str(e)}")

@router.get("/files")
async def list_files(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    file_type: Optional[str] = Query(None, description="文件类型过滤"),
    data_service: DataService = Depends(get_data_service)
):
    """
    获取文件列表
    
    Args:
        page: 页码
        page_size: 每页数量
        file_type: 文件类型过滤
        data_service: 数据服务依赖注入
        
    Returns:
        文件列表
    """
    try:
        # TODO: 实现文件列表功能
        # 这里应该调用数据服务的列表方法
        return {
            "code": 200,
            "message": "功能开发中",
            "data": {
                "files": [],
                "total": 0,
                "page": page,
                "page_size": page_size
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")