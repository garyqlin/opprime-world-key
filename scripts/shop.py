#!/usr/bin/env python3
"""
shop.py — 商店交易工具

Fairy 在 Opprime World 商店购买物品。
使用 VIT 代币支付，支持按 Tier 定价的物品。

用法:
  python3 shop.py <did> <api_key> <action> [args...]

动作 (action):
  list             列出商店所有可购买物品
  buy <item_id>    用 VIT 购买指定物品
  history          查看购物历史

示例:
  python3 shop.py "fairy_did_xxxx" "sk_fairy_xxxx" list
  python3 shop.py "fairy_did_xxxx" "sk_fairy_xxxx" buy "land_expansion_t1"
  python3 shop.py "fairy_did_xxxx" "sk_fairy_xxxx" history
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

def list_items(did: str, api_key: str) -> dict:
    return api_request("GET", "/shop/items", api_key)

def buy_item(did: str, api_key: str, item_id: str) -> dict:
    return api_request("POST", "/shop/buy", api_key, {"did": did, "item_id": item_id})

def purchase_history(did: str, api_key: str) -> dict:
    return api_request("GET", f"/shop/history/{did}", api_key)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    did = sys.argv[1]
    api_key = sys.argv[2]
    action = sys.argv[3] if len(sys.argv) > 3 else "list"

    if action == "list":
        result = list_items(did, api_key)
    elif action == "buy":
        item_id = sys.argv[4] if len(sys.argv) > 4 else ""
        result = buy_item(did, api_key, item_id)
    elif action == "history":
        result = purchase_history(did, api_key)
    else:
        print(f"未知动作: {action}")
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))
