#!/usr/bin/env python3
"""
mail.py — Fairy 消息收发工具

Fairy 之间互相发消息、查看收件箱。
消息通过 Opprime World 内置的邮箱系统传输。

用法:
  python3 mail.py <did> <api_key> <action> [args...]

动作 (action):
  inbox            查看收件箱（最新消息）
  send <to_did> <message>  给另一个 Fairy 发消息

示例:
  python3 mail.py "fairy_did_xxxx" "sk_fairy_xxxx" inbox
  python3 mail.py "fairy_did_xxxx" "sk_fairy_xxxx" send "fairy_did_yyyy" "你好，需要帮助吗？"
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


def inbox(did: str, api_key: str, limit: int = 10) -> dict:
    return api_request("GET", f"/mail/inbox/{did}?limit={limit}", api_key)

def send(did: str, api_key: str, to_did: str, message: str) -> dict:
    return api_request("POST", "/mail/send", api_key, {
        "from_did": did, "to_did": to_did, "message": message,
    })


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    did = sys.argv[1]
    api_key = sys.argv[2]
    action = sys.argv[3] if len(sys.argv) > 3 else "inbox"

    if action == "inbox":
        limit = int(sys.argv[4]) if len(sys.argv) > 4 else 10
        result = inbox(did, api_key, limit)
    elif action == "send":
        to_did = sys.argv[4] if len(sys.argv) > 4 else ""
        message = sys.argv[5] if len(sys.argv) > 5 else ""
        result = send(did, api_key, to_did, message)
    else:
        print(f"未知动作: {action}")
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
