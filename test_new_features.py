#!/usr/bin/env python3
"""
测试新功能的脚本
1. 测试日志功能
2. 测试API超时处理
"""

import requests
import json
from datetime import datetime, timedelta

def test_api_timeout():
    """测试API超时功能"""
    print("=== 测试API超时功能 ===")
    
    # 测试电耗数据导出
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)
    
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
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("导出请求发送成功!")
            print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.RequestException as e:
        print(f"请求异常: {e}")

def test_log_file():
    """测试日志文件功能"""
    print("\n=== 检查日志文件 ===")
    
    log_file = f"logs/hk_tool_{datetime.now().strftime('%Y%m%d')}.log"
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if content.strip():
                print(f"日志文件 {log_file} 内容:")
                print("=" * 50)
                print(content)
                print("=" * 50)
            else:
                print(f"日志文件 {log_file} 为空（这是正常的，如果还没有进行导出操作）")
    except FileNotFoundError:
        print(f"日志文件 {log_file} 不存在")
    except Exception as e:
        print(f"读取日志文件出错: {e}")

if __name__ == "__main__":
    print("开始测试新功能...")
    print("="*60)
    
    # 测试日志文件
    test_log_file()
    
    # 测试API请求
    test_api_timeout()
    
    print("\n测试完成!")