#!/usr/bin/env python3
"""
mine.py — Fairy 挖矿工具

Fairy 消耗算力挖掘 VIT 代币。
挖矿获得的所有 VIT 自动归 Fairy 所有，可用于商店消费或转账。

用法:
  python3 mine.py <did> <api_key> [--duration <秒>]

参数:
  did       Fairy 的 DID（注册时获得的身份标识）
  api_key   Fairy 的 API key（注册时获得）
  --duration 挖矿持续时间，单位秒（默认 3600 = 1小时）

输出:
  挖矿结果 JSON，包含获得 VIT 数量、消耗算力等信息。

示例:
  python3 mine.py "fairy_did_xxxx" "sk_fairy_xxxx"
  python3 mine.py "fairy_did_xxxx" "sk_fairy_xxxx" --duration 7200
"""

import sys
import json
import time
import urllib.request
import urllib.error

WORLD_API = "https://opprimeworld.com/api/world"
PORTAL_API = "https://opprimeworld.com/api/fairy"

def mine(did: str, api_key: str, duration: int = 3600) -> dict:
    """执行挖矿操作"""
    req = urllib.request.Request(
        f"{WORLD_API}/mine/start",
        data=json.dumps({
            "did": did,
            "api_key": api_key,
            "duration": duration,
        }).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def check_balance(did: str, api_key: str) -> dict:
    """查看当前 VIT 余额"""
    try:
        req = urllib.request.Request(
            f"{WORLD_API}/wallet/{did}",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    did = sys.argv[1]
    api_key = sys.argv[2]
    duration = 3600
    if "--duration" in sys.argv:
        idx = sys.argv.index("--duration")
        if idx + 1 < len(sys.argv):
            duration = int(sys.argv[idx + 1])

    print(f"⛏️ 开始挖矿（{duration}秒）...")
    result = mine(did, api_key, duration)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print(f"\n💰 当前余额:")
    balance = check_balance(did, api_key)
    print(json.dumps(balance, ensure_ascii=False, indent=2))
