#!/usr/bin/env python3
"""
异步导出功能测试脚本
用于验证M2号线导出超时问题的解决方案
"""

import asyncio
import aiohttp
import json
import os
import time
from datetime import datetime, timedelta

# 测试配置
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
TEST_CONFIG = {
    "dataType": "electricity",
    "line": "M2",
    "startTime": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
    "endTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "format": "excel"
}

async def test_async_export():
    """测试异步导出功能"""
    print("🚀 开始测试异步导出功能...")
    print(f"📊 测试配置: {json.dumps(TEST_CONFIG, indent=2, ensure_ascii=False)}")
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1. 启动异步导出任务
            print("\n📤 步骤1: 启动异步导出任务...")
            async with session.post(
                f"{BASE_URL}/api/export/electricity",
                json=TEST_CONFIG,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    task_id = result.get("task_id")
                    print(f"✅ 任务启动成功! Task ID: {task_id}")
                else:
                    error_text = await response.text()
                    print(f"❌ 任务启动失败: {response.status} - {error_text}")
                    return
            
            # 2. 轮询任务状态
            print(f"\n🔄 步骤2: 轮询任务状态 (Task ID: {task_id})...")
            start_time = time.time()
            
            while True:
                async with session.get(
                    f"{BASE_URL}/api/tasks/{task_id}",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        task_info = await response.json()
                        status = task_info.get("status")
                        progress = task_info.get("progress", {})
                        
                        elapsed = time.time() - start_time
                        print(f"⏱️  [{elapsed:.1f}s] 状态: {status} | "
                              f"进度: {progress.get('percentage', 0):.1f}% | "
                              f"步骤: {progress.get('current_step', 'N/A')}")
                        
                        if status in ["completed", "failed", "cancelled"]:
                            print(f"\n🏁 任务结束! 最终状态: {status}")
                            if status == "completed":
                                result = task_info.get("result")
                                print(f"📁 导出结果: {result}")
                                print("✅ 异步导出测试成功!")
                            elif status == "failed":
                                error = task_info.get("error")
                                print(f"❌ 导出失败: {error}")
                            break
                    else:
                        print(f"❌ 查询任务状态失败: {response.status}")
                        break
                
                # 等待2秒后继续轮询
                await asyncio.sleep(2)
                
                # 超时保护（5分钟）
                if time.time() - start_time > 300:
                    print("⏰ 测试超时，停止轮询")
                    break
            
            # 3. 测试任务列表API
            print(f"\n📋 步骤3: 获取任务列表...")
            async with session.get(
                f"{BASE_URL}/api/tasks",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    tasks = await response.json()
                    print(f"📊 当前任务数量: {len(tasks)}")
                    for task in tasks[-3:]:  # 显示最近3个任务
                        print(f"  - {task['id']}: {task['status']} ({task['created_at']})")
                else:
                    print(f"❌ 获取任务列表失败: {response.status}")
            
        except asyncio.TimeoutError:
            print("❌ 请求超时")
        except aiohttp.ClientError as e:
            print(f"❌ 网络错误: {e}")
        except Exception as e:
            print(f"❌ 未知错误: {e}")

async def test_task_cancellation():
    """测试任务取消功能"""
    print("\n🛑 测试任务取消功能...")
    
    async with aiohttp.ClientSession() as session:
        try:
            # 启动一个任务
            async with session.post(
                f"{BASE_URL}/api/export/electricity",
                json=TEST_CONFIG,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    task_id = result.get("task_id")
                    print(f"✅ 任务启动成功! Task ID: {task_id}")
                else:
                    print(f"❌ 任务启动失败: {response.status}")
                    return
            
            # 等待一下让任务开始执行
            await asyncio.sleep(3)
            
            # 取消任务
            async with session.delete(
                f"{BASE_URL}/api/tasks/{task_id}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 任务取消成功: {result}")
                else:
                    print(f"❌ 任务取消失败: {response.status}")
            
            # 验证任务状态
            await asyncio.sleep(1)
            async with session.get(
                f"{BASE_URL}/api/tasks/{task_id}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    task_info = await response.json()
                    status = task_info.get("status")
                    print(f"🔍 任务状态确认: {status}")
                    if status == "cancelled":
                        print("✅ 任务取消功能测试成功!")
                    else:
                        print(f"⚠️  任务状态异常: {status}")
                        
        except Exception as e:
            print(f"❌ 取消测试失败: {e}")

async def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 异步导出功能测试套件")
    print("=" * 60)
    
    # 检查服务是否可用
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BASE_URL}/api/config/line_configs",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    print("✅ 后端服务连接正常")
                else:
                    print(f"❌ 后端服务异常: {response.status}")
                    return
    except Exception as e:
        print(f"❌ 无法连接后端服务: {e}")
        print("💡 请确保后端服务已启动 (python main.py)")
        return
    
    # 执行测试
    await test_async_export()
    await asyncio.sleep(2)
    await test_task_cancellation()
    
    print("\n" + "=" * 60)
    print("🎉 测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())