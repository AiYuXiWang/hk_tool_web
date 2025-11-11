"""
API 客户端模块
负责与后端 API 通信
"""

import requests
from typing import Optional, Dict, Any, List
from datetime import datetime


class APIClient:
    """API 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def set_base_url(self, base_url: str):
        """设置 API 基础 URL"""
        self.base_url = base_url.rstrip('/')
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送 HTTP 请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API 请求失败: {str(e)}")
    
    # 设备控制相关 API
    
    def get_line_configs(self) -> Dict[str, Any]:
        """获取线路配置"""
        return self._request('GET', '/control/line-configs')
    
    def get_device_tree(self, station_ip: str, use_test_data: bool = False) -> Dict[str, Any]:
        """获取设备树"""
        params = {'station_ip': station_ip}
        if use_test_data:
            params['use_test_data'] = 'true'
        return self._request('GET', '/control/device-tree', params=params)
    
    def query_realtime_points(self, queries: List[Dict[str, str]], station_ip: Optional[str] = None) -> Dict[str, Any]:
        """查询点位实时数据"""
        headers = {}
        if station_ip:
            headers['X-Station-Ip'] = station_ip
        
        return self._request('POST', '/control/points/query', 
                           json={'queries': queries}, 
                           headers=headers)
    
    def write_points(self, commands: List[Dict[str, Any]], operator_id: str, station_ip: Optional[str] = None) -> Dict[str, Any]:
        """批量写值"""
        headers = {}
        if station_ip:
            headers['X-Station-Ip'] = station_ip
        
        data = {
            'commands': commands,
            'operator_id': operator_id
        }
        
        return self._request('POST', '/control/points/write', 
                           json=data, 
                           headers=headers)
    
    # 数据导出相关 API
    
    def export_electricity_data(self, line: str, start_time: str, end_time: str) -> Dict[str, Any]:
        """导出电耗数据"""
        data = {
            'line': line,
            'start_time': start_time,
            'end_time': end_time
        }
        return self._request('POST', '/export/electricity', json=data)
    
    def export_sensor_data(self, line: str, start_time: str, end_time: str) -> Dict[str, Any]:
        """导出传感器数据"""
        data = {
            'line': line,
            'start_time': start_time,
            'end_time': end_time
        }
        return self._request('POST', '/export/sensor', json=data)
    
    def get_export_status(self, task_id: str) -> Dict[str, Any]:
        """获取导出任务状态"""
        return self._request('GET', f'/export/status/{task_id}')
    
    def download_export_file(self, file_path: str) -> bytes:
        """下载导出文件"""
        url = f"{self.base_url}/export/download"
        params = {'file_path': file_path}
        
        try:
            response = self.session.get(url, params=params, stream=True)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            raise Exception(f"文件下载失败: {str(e)}")
    
    # 审计日志相关 API
    
    def get_audit_logs(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """获取审计日志"""
        params = {'limit': limit, 'offset': offset}
        return self._request('GET', '/audit/logs', params=params)
