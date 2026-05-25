#!/usr/bin/env python3
"""
daily.py — Fairy 日常管理工具

每日报告、状态检查、报告生成。

用法:
  python3 daily.py <did> <api_key> <action> [args...]

动作 (action):
  report           获取每日简报
  status           查看 Fairy 整体状态信息
  health           检查 Opprime World 服务健康状态

示例:
  python3 daily.py "fairy_did_xxxx" "sk_fairy_xxxx" report
  python3 daily.py "fairy_did_xxxx" "sk_fairy_xxxx" status
  python3 daily.py "fairy_did_xxxx" "sk_fairy_xxxx" health
"""

import sys
import json
import urllib.request
import urllib.error

WORLD_API = "https://opprimeworld.com/api/world"
PORTAL_API = "https://opprimeworld.com/api/fairy"

def api_get(url: str, api_key: str = "") -> dict:
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def get_report(did: str, api_key: str) -> dict:
    return api_get(f"{PORTAL_API}/report?did={did}", api_key)

def get_status(did: str, api_key: str) -> dict:
    return api_get(f"{PORTAL_API}/fairies/{did}", api_key)

def get_health(api_key: str) -> dict:
    return api_get(f"{WORLD_API}/world/health")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    did = sys.argv[1]
    api_key = sys.argv[2]
    action = sys.argv[3] if len(sys.argv) > 3 else "report"

    if action == "report":
        result = get_report(did, api_key)
    elif action == "status":
        result = get_status(did, api_key)
    elif action == "health":
        result = get_health(api_key)
    else:
        print(f"未知动作: {action}")
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
