import requests
import time
from datetime import datetime, timedelta

def test_api():
    """测试API接口"""
    base_url = "http://localhost:8000"
    
    print("测试环控平台维护工具Web版API")
    print("=" * 40)
    
    # 1. 测试根路径
    print("1. 测试根路径...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   错误: {e}")
    
    # 2. 测试获取线路列表
    print("\n2. 测试获取线路列表...")
    try:
        response = requests.get(f"{base_url}/api/lines")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            lines = response.json()["lines"]
            print(f"   线路列表: {lines}")
            
            if lines:
                # 3. 测试获取线路配置详情
                print(f"\n3. 测试获取线路'{lines[0]}'配置详情...")
                response = requests.get(f"{base_url}/api/line-config/{lines[0]}")
                print(f"   状态码: {response.status_code}")
                if response.status_code == 200:
                    config = response.json()["config"]
                    print(f"   车站数量: {len(config)}")
                    # 显示前两个车站信息
                    stations = list(config.keys())[:2]
                    for station in stations:
                        print(f"   车站: {station} - IP: {config[station]['ip']}")
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\nAPI测试完成")

if __name__ == "__main__":
    test_api()