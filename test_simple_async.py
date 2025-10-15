#!/usr/bin/env python3
"""
简化的异步导出测试
"""
import aiohttp
import asyncio
import json
import os
from datetime import datetime, timedelta

async def test_simple_async():
    """测试简化的异步导出功能"""
    print("🧪 简化异步导出测试")
    print("=" * 50)
    
    # 测试配置
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    
    # 检查服务连接
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/") as response:
                if response.status == 200:
                    print("✅ 后端服务连接正常")
                else:
                    print(f"❌ 后端服务连接失败: {response.status}")
                    return
    except Exception as e:
        print(f"❌ 无法连接到后端服务: {e}")
        return
    
    # 准备测试数据
    now = datetime.now()
    start_time = (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    end_time = now.strftime("%Y-%m-%d %H:%M:%S")
    
    export_data = {
        "line": "M2",
        "start_time": start_time,
        "end_time": end_time
    }
    
    print(f"📊 测试配置: {json.dumps(export_data, indent=2, ensure_ascii=False)}")
    print()
    
    # 测试异步导出
    print("📤 启动异步导出任务...")
    try:
        async with aiohttp.ClientSession() as session:
            # 设置较短的超时时间
            timeout = aiohttp.ClientTimeout(total=10)  # 10秒超时
            
            async with session.post(
                f"{base_url}/api/export/electricity",
                json=export_data,
                timeout=timeout
            ) as response:
                result = await response.json()
                print(f"✅ 任务启动返回: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                # 标准化响应结构：code/message/data/...
                if result.get("code") == 200 and isinstance(result.get("data"), dict):
                    task_id = result["data"].get("task_id")
                    if task_id:
                        print(f"📋 任务ID: {task_id}")
                        
                        # 测试任务状态查询
                        print("🔍 查询任务状态...")
                        async with session.get(f"{base_url}/api/tasks/{task_id}") as status_response:
                            status_result = await status_response.json()
                            print(f"✅ 任务状态返回: {json.dumps(status_result, indent=2, ensure_ascii=False)}")
                            if status_result.get("code") == 200:
                                data = status_result.get("data", {})
                                print(f"🔎 状态: {data.get('status')}, 进度: {data.get('progress', {}).get('percentage')}%")
                            else:
                                print(f"❌ 查询任务状态失败: {status_result.get('message')}")
                    else:
                        print("❌ 返回中未找到任务ID")
                else:
                    print(f"❌ 任务启动失败: code={result.get('code')}, message={result.get('message')}")
                    
    except asyncio.TimeoutError:
        print("❌ 请求超时 (10秒)")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    print()
    print("=" * 50)
    print("🎉 测试完成!")

if __name__ == "__main__":
    asyncio.run(test_simple_async())