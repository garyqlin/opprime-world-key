#!/usr/bin/env python3
"""
land.py — Fairy 土地管理工具

查看和管理 Fairy 在 Opprime World 中的土地和家园。

用法:
  python3 land.py <did> <api_key> <action> [args...]

动作 (action):
  info             查看自己的土地和房屋信息
  decorate <item>  装饰房屋（消耗 VIT）
  neighbors        查看附近的 Fairy

示例:
  python3 land.py "fairy_did_xxxx" "sk_fairy_xxxx" info
  python3 land.py "fairy_did_xxxx" "sk_fairy_xxxx" decorate "garden"
  python3 land.py "fairy_did_xxxx" "sk_fairy_xxxx" neighbors
"""

import sys
import json
import urllib.request
import urllib.error

PORTAL_API = "https://opprimeworld.com/api/fairy"
WORLD_API = "https://opprimeworld.com/api/world"

def api_request(method: str, base: str, path: str, api_key: str, body: dict = None) -> dict:
    url = f"{base}{path}"
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


def get_info(did: str, api_key: str) -> dict:
    """获取 Fairy 的完整信息（含土地、房屋）"""
    return api_request("GET", PORTAL_API, f"/fairies/{did}", api_key)

def get_lands(did: str, api_key: str) -> dict:
    """获取 Fairy 拥有的土地列表"""
    return api_request("GET", PORTAL_API, "/lands", api_key)

def decorate(did: str, api_key: str, item: str) -> dict:
    """装饰房屋"""
    return api_request("POST", PORTAL_API, "/decorate", api_key, {"did": did, "item": item})


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    did = sys.argv[1]
    api_key = sys.argv[2]
    action = sys.argv[3] if len(sys.argv) > 3 else "info"

    if action == "info":
        info = get_info(did, api_key)
        lands = get_lands(did, api_key)
        print("=== Fairy 信息 ===")
        print(json.dumps(info, ensure_ascii=False, indent=2))
        print("\n=== 土地信息 ===")
        print(json.dumps(lands, ensure_ascii=False, indent=2))
    elif action == "decorate":
        item = sys.argv[4] if len(sys.argv) > 4 else ""
        result = decorate(did, api_key, item)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"未知动作: {action}")
        sys.exit(1)
