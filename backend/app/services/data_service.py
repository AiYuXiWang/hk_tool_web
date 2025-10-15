"""
数据访问服务

提供统一的数据访问接口，包括文件上传、数据解析、数据验证等功能。
"""

import os
import pandas as pd
from typing import Dict, List, Optional, Any, Union, BinaryIO
from datetime import datetime
import json
import hashlib
from pathlib import Path
from backend.app.services.base import BaseService, service_method
from backend.app.core.config import config


class DataService(BaseService):
    """数据访问服务"""
    
    def __init__(self):
        super().__init__()
        self.upload_dir = Path(config.get_app_config().get("upload_dir", "uploads"))
        self.upload_dir.mkdir(exist_ok=True)
        
        # 支持的文件类型
        self.supported_extensions = {
            '.xlsx', '.xls', '.csv', '.json', '.txt'
        }
        
        # 文件大小限制 (MB)
        self.max_file_size = config.get_app_config().get("max_file_size", 50) * 1024 * 1024
    
    @service_method()
    async def upload_file(
        self, 
        file_content: bytes, 
        filename: str,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        上传文件
        
        Args:
            file_content: 文件内容
            filename: 文件名
            content_type: 文件MIME类型
            
        Returns:
            上传结果，包含文件ID、路径等信息
        """
        try:
            # 验证文件
            validation_result = await self._validate_file(file_content, filename)
            if not validation_result["valid"]:
                return self.format_error_response(validation_result["error"], 400)
            
            # 生成文件ID和路径
            file_id = self._generate_file_id(filename, file_content)
            file_path = self.upload_dir / f"{file_id}_{filename}"
            
            # 保存文件
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # 记录文件信息
            file_info = {
                "file_id": file_id,
                "filename": filename,
                "file_path": str(file_path),
                "file_size": len(file_content),
                "content_type": content_type,
                "upload_time": datetime.now().isoformat(),
                "status": "uploaded"
            }
            
            # 保存文件元数据
            await self._save_file_metadata(file_id, file_info)
            
            return self.format_response(file_info, "文件上传成功")
            
        except Exception as e:
            self.log_error("upload_file", e, filename=filename)
            return self.format_error_response(f"文件上传失败: {str(e)}")
    
    @service_method()
    async def parse_file(self, file_id: str, parse_options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        解析文件内容
        
        Args:
            file_id: 文件ID
            parse_options: 解析选项
            
        Returns:
            解析结果
        """
        try:
            # 获取文件信息
            file_info = await self._get_file_metadata(file_id)
            if not file_info:
                return self.format_error_response("文件不存在", 404)
            
            file_path = Path(file_info["file_path"])
            if not file_path.exists():
                return self.format_error_response("文件已被删除", 404)
            
            # 根据文件类型解析
            file_extension = file_path.suffix.lower()
            
            if file_extension in ['.xlsx', '.xls']:
                parsed_data = await self._parse_excel(file_path, parse_options)
            elif file_extension == '.csv':
                parsed_data = await self._parse_csv(file_path, parse_options)
            elif file_extension == '.json':
                parsed_data = await self._parse_json(file_path, parse_options)
            elif file_extension == '.txt':
                parsed_data = await self._parse_text(file_path, parse_options)
            else:
                return self.format_error_response(f"不支持的文件类型: {file_extension}", 400)
            
            # 更新文件状态
            file_info["status"] = "parsed"
            file_info["parse_time"] = datetime.now().isoformat()
            file_info["data_summary"] = parsed_data.get("summary", {})
            await self._save_file_metadata(file_id, file_info)
            
            return self.format_response(parsed_data, "文件解析成功")
            
        except Exception as e:
            self.log_error("parse_file", e, file_id=file_id)
            return self.format_error_response(f"文件解析失败: {str(e)}")
    
    @service_method()
    async def validate_data(
        self, 
        data: Union[List[Dict], pd.DataFrame], 
        validation_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        验证数据
        
        Args:
            data: 要验证的数据
            validation_rules: 验证规则
            
        Returns:
            验证结果
        """
        try:
            # 转换为DataFrame便于处理
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = data.copy()
            
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "summary": {
                    "total_rows": len(df),
                    "total_columns": len(df.columns),
                    "valid_rows": 0,
                    "invalid_rows": 0
                }
            }
            
            # 执行各种验证规则
            if "required_columns" in validation_rules:
                await self._validate_required_columns(df, validation_rules["required_columns"], validation_result)
            
            if "data_types" in validation_rules:
                await self._validate_data_types(df, validation_rules["data_types"], validation_result)
            
            if "value_ranges" in validation_rules:
                await self._validate_value_ranges(df, validation_rules["value_ranges"], validation_result)
            
            if "custom_rules" in validation_rules:
                await self._validate_custom_rules(df, validation_rules["custom_rules"], validation_result)
            
            # 计算有效行数
            validation_result["summary"]["valid_rows"] = len(df) - validation_result["summary"]["invalid_rows"]
            
            # 如果有错误，标记为无效
            if validation_result["errors"]:
                validation_result["valid"] = False
            
            return self.format_response(validation_result, "数据验证完成")
            
        except Exception as e:
            self.log_error("validate_data", e)
            return self.format_error_response(f"数据验证失败: {str(e)}")
    
    @service_method()
    async def export_data(
        self, 
        data: Union[List[Dict], pd.DataFrame], 
        export_format: str = "xlsx",
        export_options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        导出数据
        
        Args:
            data: 要导出的数据
            export_format: 导出格式 (xlsx, csv, json)
            export_options: 导出选项
            
        Returns:
            导出结果，包含文件路径
        """
        try:
            # 转换为DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = data.copy()
            
            if df.empty:
                return self.format_error_response("没有数据可导出", 400)
            
            # 生成导出文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{timestamp}.{export_format}"
            export_path = self.upload_dir / filename
            
            # 根据格式导出
            if export_format == "xlsx":
                df.to_excel(export_path, index=False, **(export_options or {}))
            elif export_format == "csv":
                df.to_csv(export_path, index=False, encoding='utf-8-sig', **(export_options or {}))
            elif export_format == "json":
                df.to_json(export_path, orient='records', force_ascii=False, indent=2)
            else:
                return self.format_error_response(f"不支持的导出格式: {export_format}", 400)
            
            export_info = {
                "filename": filename,
                "file_path": str(export_path),
                "file_size": export_path.stat().st_size,
                "format": export_format,
                "rows_count": len(df),
                "columns_count": len(df.columns),
                "export_time": datetime.now().isoformat()
            }
            
            return self.format_response(export_info, "数据导出成功")
            
        except Exception as e:
            self.log_error("export_data", e, export_format=export_format)
            return self.format_error_response(f"数据导出失败: {str(e)}")
    
    @service_method()
    async def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """
        获取文件信息
        
        Args:
            file_id: 文件ID
            
        Returns:
            文件信息
        """
        try:
            file_info = await self._get_file_metadata(file_id)
            if not file_info:
                return self.format_error_response("文件不存在", 404)
            
            return self.format_response(file_info, "获取文件信息成功")
            
        except Exception as e:
            self.log_error("get_file_info", e, file_id=file_id)
            return self.format_error_response(f"获取文件信息失败: {str(e)}")
    
    @service_method()
    async def delete_file(self, file_id: str) -> Dict[str, Any]:
        """
        删除文件
        
        Args:
            file_id: 文件ID
            
        Returns:
            删除结果
        """
        try:
            file_info = await self._get_file_metadata(file_id)
            if not file_info:
                return self.format_error_response("文件不存在", 404)
            
            # 删除物理文件
            file_path = Path(file_info["file_path"])
            if file_path.exists():
                file_path.unlink()
            
            # 删除元数据
            await self._delete_file_metadata(file_id)
            
            return self.format_response({"file_id": file_id}, "文件删除成功")
            
        except Exception as e:
            self.log_error("delete_file", e, file_id=file_id)
            return self.format_error_response(f"文件删除失败: {str(e)}")
    
    # 私有方法
    async def _validate_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """验证文件"""
        # 检查文件大小
        if len(file_content) > self.max_file_size:
            return {
                "valid": False,
                "error": f"文件大小超过限制 ({self.max_file_size / 1024 / 1024:.1f}MB)"
            }
        
        # 检查文件扩展名
        file_extension = Path(filename).suffix.lower()
        if file_extension not in self.supported_extensions:
            return {
                "valid": False,
                "error": f"不支持的文件类型: {file_extension}"
            }
        
        # 检查文件内容（简单验证）
        if len(file_content) == 0:
            return {
                "valid": False,
                "error": "文件内容为空"
            }
        
        return {"valid": True}
    
    def _generate_file_id(self, filename: str, content: bytes) -> str:
        """生成文件ID"""
        content_hash = hashlib.md5(content).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{timestamp}_{content_hash}"
    
    async def _save_file_metadata(self, file_id: str, file_info: Dict[str, Any]):
        """保存文件元数据"""
        metadata_path = self.upload_dir / f"{file_id}.meta"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(file_info, f, ensure_ascii=False, indent=2)
    
    async def _get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """获取文件元数据"""
        metadata_path = self.upload_dir / f"{file_id}.meta"
        if not metadata_path.exists():
            return None
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    async def _delete_file_metadata(self, file_id: str):
        """删除文件元数据"""
        metadata_path = self.upload_dir / f"{file_id}.meta"
        if metadata_path.exists():
            metadata_path.unlink()
    
    async def _parse_excel(self, file_path: Path, options: Optional[Dict] = None) -> Dict[str, Any]:
        """解析Excel文件"""
        options = options or {}
        
        # 读取Excel文件
        df = pd.read_excel(
            file_path,
            sheet_name=options.get('sheet_name', 0),
            header=options.get('header', 0),
            nrows=options.get('max_rows')
        )
        
        return {
            "data": df.to_dict('records'),
            "columns": df.columns.tolist(),
            "summary": {
                "rows": len(df),
                "columns": len(df.columns),
                "data_types": df.dtypes.to_dict()
            }
        }
    
    async def _parse_csv(self, file_path: Path, options: Optional[Dict] = None) -> Dict[str, Any]:
        """解析CSV文件"""
        options = options or {}
        
        # 读取CSV文件
        df = pd.read_csv(
            file_path,
            encoding=options.get('encoding', 'utf-8'),
            sep=options.get('separator', ','),
            header=options.get('header', 0),
            nrows=options.get('max_rows')
        )
        
        return {
            "data": df.to_dict('records'),
            "columns": df.columns.tolist(),
            "summary": {
                "rows": len(df),
                "columns": len(df.columns),
                "data_types": df.dtypes.to_dict()
            }
        }
    
    async def _parse_json(self, file_path: Path, options: Optional[Dict] = None) -> Dict[str, Any]:
        """解析JSON文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 如果是列表，转换为DataFrame分析
        if isinstance(data, list) and data and isinstance(data[0], dict):
            df = pd.DataFrame(data)
            return {
                "data": data,
                "columns": df.columns.tolist(),
                "summary": {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "data_types": df.dtypes.to_dict()
                }
            }
        else:
            return {
                "data": data,
                "summary": {
                    "type": type(data).__name__,
                    "size": len(data) if hasattr(data, '__len__') else 1
                }
            }
    
    async def _parse_text(self, file_path: Path, options: Optional[Dict] = None) -> Dict[str, Any]:
        """解析文本文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        return {
            "data": {
                "content": content,
                "lines": lines
            },
            "summary": {
                "total_chars": len(content),
                "total_lines": len(lines),
                "encoding": "utf-8"
            }
        }
    
    async def _validate_required_columns(
        self, 
        df: pd.DataFrame, 
        required_columns: List[str], 
        result: Dict[str, Any]
    ):
        """验证必需列"""
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            result["errors"].append(f"缺少必需列: {', '.join(missing_columns)}")
    
    async def _validate_data_types(
        self, 
        df: pd.DataFrame, 
        data_types: Dict[str, str], 
        result: Dict[str, Any]
    ):
        """验证数据类型"""
        for column, expected_type in data_types.items():
            if column not in df.columns:
                continue
            
            try:
                if expected_type == "numeric":
                    pd.to_numeric(df[column], errors='raise')
                elif expected_type == "datetime":
                    pd.to_datetime(df[column], errors='raise')
                # 可以添加更多类型验证
            except Exception:
                result["errors"].append(f"列 '{column}' 数据类型不符合要求: {expected_type}")
    
    async def _validate_value_ranges(
        self, 
        df: pd.DataFrame, 
        value_ranges: Dict[str, Dict], 
        result: Dict[str, Any]
    ):
        """验证值范围"""
        for column, range_config in value_ranges.items():
            if column not in df.columns:
                continue
            
            if "min" in range_config:
                invalid_rows = df[df[column] < range_config["min"]]
                if not invalid_rows.empty:
                    result["warnings"].append(f"列 '{column}' 有 {len(invalid_rows)} 行小于最小值 {range_config['min']}")
            
            if "max" in range_config:
                invalid_rows = df[df[column] > range_config["max"]]
                if not invalid_rows.empty:
                    result["warnings"].append(f"列 '{column}' 有 {len(invalid_rows)} 行大于最大值 {range_config['max']}")
    
    async def _validate_custom_rules(
        self, 
        df: pd.DataFrame, 
        custom_rules: List[Dict], 
        result: Dict[str, Any]
    ):
        """验证自定义规则"""
        for rule in custom_rules:
            rule_name = rule.get("name", "未命名规则")
            try:
                # 这里可以实现自定义验证逻辑
                # 例如：eval(rule["expression"]) 等
                pass
            except Exception as e:
                result["errors"].append(f"自定义规则 '{rule_name}' 执行失败: {str(e)}")