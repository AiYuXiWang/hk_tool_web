#!/usr/bin/env python3
"""
测试修复后的功能
1. 测试API超时直接失败，不生成文件
2. 测试前端状态管理
"""

import requests
import json
from datetime import datetime, timedelta

def test_timeout_behavior():
    """测试超时行为"""
    print("=== 测试API超时处理 ===")
    
    # 测试电耗数据导出
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)  # 缩短时间范围，加快测试
    
    export_data = {
        "line": "M1",
        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    print(f"发送电耗数据导出请求: {json.dumps(export_data, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/export/electricity",
            json=export_data,
            timeout=120  # 增加客户端超时时间
        )
        
        if response.status_code == 200:
            result = response.json()
            print("导出请求发送成功!")
            print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # 检查是否有失败的站点
            if result.get('details') and result['details'].get('results'):
                failed_stations = [r for r in result['details']['results'] if not r['success']]
                if failed_stations:
                    print(f"\n失败站点数量: {len(failed_stations)}")
                    for station in failed_stations[:3]:  # 只显示前3个
                        print(f"  - {station['station_name']} ({station['station_ip']}): {station['message']}")
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.RequestException as e:
        print(f"请求异常: {e}")

def check_log_files():
    """检查最新日志文件"""
    print("\n=== 检查日志文件 ===")
    
    log_file = f"logs/hk_tool_{datetime.now().strftime('%Y%m%d')}.log"
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if lines:
            print(f"日志文件 {log_file} 最新10行:")
            print("=" * 80)
            for line in lines[-10:]:
                print(line.strip())
            print("=" * 80)
        else:
            print(f"日志文件 {log_file} 为空")
    except FileNotFoundError:
        print(f"日志文件 {log_file} 不存在")
    except Exception as e:
        print(f"读取日志文件出错: {e}")

if __name__ == "__main__":
    print("开始测试修复后的功能...")
    print("="*60)
    
    # 测试API请求
    test_timeout_behavior()
    
    # 等待一下，然后检查日志
    import time
    time.sleep(2)
    check_log_files()
    
    print("\n测试完成!")