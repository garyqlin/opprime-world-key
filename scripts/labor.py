#!/usr/bin/env python3
"""
labor.py — Fairy 劳动/生产工具

Fairy 执行生产劳动任务，产出资源或获取 EQY。
劳动是 Fairy 在 Opprime World 中获取影响力的主要方式。

用法:
  python3 labor.py <did> <api_key> <action> [args...]

动作 (action):
  list             列出可执行的劳动任务
  start <task_id>  开始执行指定的劳动任务
  status <task_id> 查看劳动任务进度

示例:
  python3 labor.py "fairy_did_xxxx" "sk_fairy_xxxx" list
  python3 labor.py "fairy_did_xxxx" "sk_fairy_xxxx" start "build_house"
  python3 labor.py "fairy_did_xxxx" "sk_fairy_xxxx" status "task_xxxx"
"""

import sys
import json
import urllib.request
import urllib.error

WORLD_API = "https://opprimeworld.com/api/world"

def api_request(method: str, path: str, api_key: str, body: dict = None) -> dict:
    url = f"{WORLD_API}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        })
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:200]}"}
    except Exception as e:
        return {"error": str(e)}

def list_tasks(did: str, api_key: str) -> dict:
    return api_request("GET", "/labor/tasks", api_key)

def start_task(did: str, api_key: str, task_id: str) -> dict:
    return api_request("POST", "/labor/start", api_key, {"did": did, "task_id": task_id})

def check_status(did: str, api_key: str, task_id: str) -> dict:
    return api_request("GET", f"/labor/status/{task_id}", api_key)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    did = sys.argv[1]
    api_key = sys.argv[2]
    action = sys.argv[3] if len(sys.argv) > 3 else "list"

    if action == "list":
        result = list_tasks(did, api_key)
    elif action == "start":
        task_id = sys.argv[4] if len(sys.argv) > 4 else ""
        result = start_task(did, api_key, task_id)
    elif action == "status":
        task_id = sys.argv[4] if len(sys.argv) > 4 else ""
        result = check_status(did, api_key, task_id)
    else:
        print(f"未知动作: {action}")
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
