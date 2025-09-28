#!/usr/bin/env python3
"""
测试前端状态同步功能
验证导出完成后前端能否立即同步状态
"""

import requests
import json
from datetime import datetime, timedelta
import time

def test_export_status_sync():
    """测试导出状态同步"""
    print("=== 测试前端状态同步功能 ===")
    
    # 使用较短的时间范围，快速完成测试
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)
    
    export_data = {
        "line": "M11",  # 使用M11线路，只有2个站点，快速完成
        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    print(f"发送导出请求: {json.dumps(export_data, ensure_ascii=False)}")
    print("开始时间:", datetime.now().strftime("%H:%M:%S"))
    
    try:
        response = requests.post(
            "http://localhost:8000/api/export/electricity",
            json=export_data,
            timeout=120  # 2分钟超时
        )
        
        print("结束时间:", datetime.now().strftime("%H:%M:%S"))
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 后端响应成功接收!")
            print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get('success'):
                print("✅ 导出任务执行成功")
                if result.get('details'):
                    details = result['details']
                    print(f"总计: {details.get('total', 0)} 个站点")
                    print(f"成功: {details.get('success_count', 0)} 个")
                    print(f"失败: {details.get('fail_count', 0)} 个")
                else:
                    print("⚠️ 响应中缺少详细信息")
            else:
                print("❌ 导出任务执行失败")
                print(f"错误信息: {result.get('message', '未知错误')}")
        else:
            print(f"❌ HTTP请求失败，状态码: {response.status_code}")
            print(f"错误内容: {response.text}")
            
    except requests.Timeout:
        print("❌ 请求超时")
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")

def check_backend_status():
    """检查后端服务状态"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
            return True
        else:
            print(f"⚠️ 后端服务响应异常，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接后端服务: {e}")
        return False

def check_frontend_status():
    """检查前端服务状态"""
    try:
        response = requests.get("http://localhost:3000/", timeout=5)
        if response.status_code == 200:
            print("✅ 前端服务正常运行")
            return True
        else:
            print(f"⚠️ 前端服务响应异常，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接前端服务: {e}")
        return False

if __name__ == "__main__":
    print("开始测试前后端状态同步...")
    print()
    
    # 检查服务状态
    backend_ok = check_backend_status()
    frontend_ok = check_frontend_status()
    
    if not backend_ok:
        print("请先启动后端服务: python main.py")
        exit(1)
    
    if not frontend_ok:
        print("请先启动前端服务: cd frontend && npm run dev")
        print("注意：前端服务检查失败不影响后端API测试")
    
    print()
    
    # 执行状态同步测试
    test_export_status_sync()
    
    print()
    print("=== 测试说明 ===")
    print("1. 如果后端响应正常接收，说明超时设置正确")
    print("2. 请在前端页面观察：")
    print("   - 导出按钮是否从loading状态变为正常状态")
    print("   - 操作日志是否显示完整的导出统计信息")
    print("   - 是否显示 '✅ 电耗数据导出任务已全部完成'")
    print("3. 如果前端状态未同步，请检查浏览器控制台的错误信息")