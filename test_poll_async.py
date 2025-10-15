import os
import time
import json
from datetime import datetime, timedelta
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")

def pretty(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)

def start_export(line: str, hours: int = 24):
    now = datetime.now()
    start_time = (now - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
    end_time = now.strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "line": line,
        "start_time": start_time,
        "end_time": end_time,
    }
    resp = requests.post(f"{BASE_URL}/api/export/electricity", json=payload, timeout=10)
    data = resp.json()
    if resp.status_code != 200:
        raise RuntimeError(f"启动任务失败: {pretty(data)}")
    task_id = data.get("data", {}).get("task_id")
    if not task_id:
        raise RuntimeError(f"未返回 task_id: {pretty(data)}")
    return task_id, payload

def get_task(task_id: str):
    resp = requests.get(f"{BASE_URL}/api/tasks/{task_id}", timeout=10)
    return resp.status_code, resp.json()

def main():
    print("🧪 轮询异步导出直至完成")
    print("=" * 50)
    # 启动任务
    task_id, payload = start_export("M2", hours=24)
    print(f"📋 任务ID: {task_id}")
    print(f"📊 时间范围: {pretty(payload)}")

    # 轮询
    max_wait_seconds = 180
    interval_seconds = 3
    waited = 0
    last_progress = None
    terminal_status = {"completed", "failed", "cancelled", "done", "success"}

    while waited <= max_wait_seconds:
        status_code, body = get_task(task_id)
        code = body.get("code")
        data = body.get("data", {})
        status = data.get("status")
        progress = data.get("progress", {})
        percentage = progress.get("percentage")
        message = progress.get("message")

        if status_code == 200 and code == 200:
            # 打印进度变化
            prog_str = f"{percentage}%" if percentage is not None else "N/A"
            if prog_str != last_progress:
                print(f"⏱️ 进度: {prog_str} - {message}")
                last_progress = prog_str

            if status and status.lower() in terminal_status:
                print("✅ 任务已结束")
                print(pretty(body))
                return
        else:
            detail = body.get("data", {}).get("detail") or body.get("message")
            print(f"⚠️ 查询异常({status_code}): {detail}")

        time.sleep(interval_seconds)
        waited += interval_seconds

    # 超时未结束
    print("⏰ 超时未完成，输出最新状态:")
    print(pretty(get_task(task_id)[1]))

if __name__ == "__main__":
    try:
        # 连接测试
        ping = requests.get(f"{BASE_URL}/", timeout=5)
        if ping.status_code == 200:
            print("✅ 后端服务连接正常")
        else:
            print(f"⚠️ 后端返回非200: {ping.status_code}")
        main()
    except Exception as e:
        print(f"❌ 执行失败: {e}")