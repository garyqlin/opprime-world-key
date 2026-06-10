#!/usr/bin/env python3
# decision-handler.py — 处理主人对 Fairy 决策的回复
# 用法: python3 decision-handler.py approve <Fairy名字> <决策ID>
#       python3 decision-handler.py reject <Fairy名字> <决策ID>
#       python3 decision-handler.py list <Fairy名字>

import json
import os
import sys
import datetime

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def decisions_path(fairy_name):
    """待决策队列路径"""
    path = os.path.join(SKILL_DIR, "data", "fairies", fairy_name, "pending_decisions.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path

def history_path(fairy_name):
    """决策历史路径"""
    path = os.path.join(SKILL_DIR, "data", "fairies", fairy_name, "decision_history.jsonl")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path

def load_decisions(fairy_name):
    """读取待决策队列"""
    path = decisions_path(fairy_name)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"decisions": []}

def save_decisions(fairy_name, data):
    """保存待决策队列"""
    with open(decisions_path(fairy_name), "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def append_history(fairy_name, record):
    """追加决策历史"""
    with open(history_path(fairy_name), "a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def cmd_list(fairy_name):
    """列出所有待处理决策"""
    data = load_decisions(fairy_name)
    decisions = data.get("decisions", [])
    
    if not decisions:
        print(f"📋 {fairy_name}: 没有待处理的决策")
        return
    
    print(f"📋 {fairy_name} 待处理决策 ({len(decisions)} 项):")
    print("─" * 40)
    
    for d in decisions:
        did = d.get("id", "?")
        dtype = d.get("type", "?")
        summary = d.get("summary", "无描述")
        expires = d.get("expires_at", "无期限")
        
        print(f"  [{did}] {dtype}")
        print(f"    内容: {summary}")
        print(f"    期限: {expires}")
        print()

def cmd_approve(fairy_name, decision_id):
    """同意一个决策"""
    data = load_decisions(fairy_name)
    decisions = data.get("decisions", [])
    
    found = None
    remaining = []
    for d in decisions:
        if d.get("id") == decision_id:
            found = d
        else:
            remaining.append(d)
    
    if not found:
        print(f"❌ 未找到决策: {decision_id}")
        return
    
    # 记录历史
    now = datetime.datetime.now().isoformat()
    record = {
        "id": decision_id,
        "fairy": fairy_name,
        "decision": "approve",
        "type": found.get("type", ""),
        "summary": found.get("summary", ""),
        "processed_at": now
    }
    append_history(fairy_name, record)
    
    # 从待处理列表中移除
    data["decisions"] = remaining
    save_decisions(fairy_name, data)
    
    print(f"✅ 已同意决策 [{decision_id}]")
    print(f"   内容: {found.get('summary', '')}")
    print(f"   处理时间: {now}")
    
    # 返回决策详情，供后续调用实际操作的脚本
    return found

def cmd_reject(fairy_name, decision_id):
    """拒绝一个决策"""
    data = load_decisions(fairy_name)
    decisions = data.get("decisions", [])
    
    found = None
    remaining = []
    for d in decisions:
        if d.get("id") == decision_id:
            found = d
        else:
            remaining.append(d)
    
    if not found:
        print(f"❌ 未找到决策: {decision_id}")
        return
    
    now = datetime.datetime.now().isoformat()
    record = {
        "id": decision_id,
        "fairy": fairy_name,
        "decision": "reject",
        "type": found.get("type", ""),
        "summary": found.get("summary", ""),
        "reason": "主人拒绝",
        "processed_at": now
    }
    append_history(fairy_name, record)
    
    data["decisions"] = remaining
    save_decisions(fairy_name, data)
    
    print(f"❌ 已拒绝决策 [{decision_id}]")
    print(f"   内容: {found.get('summary', '')}")
    print(f"   处理时间: {now}")
    
    return found

def cmd_add(fairy_name, decision_type, summary, benefit="", risk="", expiry_hours=48):
    """添加一个新的待处理决策"""
    import uuid
    now = datetime.datetime.now()
    expires = now + datetime.timedelta(hours=expiry_hours)
    
    decision = {
        "id": f"dec_{now.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}",
        "type": decision_type,
        "summary": summary,
        "estimated_benefit": benefit,
        "risk": risk,
        "created_at": now.isoformat(),
        "expires_at": expires.isoformat(),
        "status": "pending"
    }
    
    data = load_decisions(fairy_name)
    data["decisions"].append(decision)
    save_decisions(fairy_name, data)
    
    print(f"➕ 已添加决策 [{decision['id']}]")
    print(f"   类型: {decision_type}")
    print(f"   内容: {summary}")
    print(f"   到期: {expires.isoformat()}")
    print(f"   待主人决定中...")

def main():
    if len(sys.argv) < 3:
        print("用法:")
        print("  python3 decision-handler.py list <Fairy名字>")
        print("  python3 decision-handler.py approve <Fairy名字> <决策ID>")
        print("  python3 decision-handler.py reject <Fairy名字> <决策ID>")
        print("  python3 decision-handler.py add <Fairy名字> <类型> <摘要> [收益] [风险]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    fairy_name = sys.argv[2]
    
    if cmd == "list":
        cmd_list(fairy_name)
    elif cmd == "approve":
        if len(sys.argv) < 4:
            print("❌ 请输入决策 ID")
            sys.exit(1)
        cmd_approve(fairy_name, sys.argv[3])
    elif cmd == "reject":
        if len(sys.argv) < 4:
            print("❌ 请输入决策 ID")
            sys.exit(1)
        cmd_reject(fairy_name, sys.argv[3])
    elif cmd == "add":
        if len(sys.argv) < 5:
            print("❌ 请输入决策类型和摘要")
            sys.exit(1)
        d_type = sys.argv[3]
        summary = sys.argv[4]
        benefit = sys.argv[5] if len(sys.argv) > 5 else ""
        risk = sys.argv[6] if len(sys.argv) > 6 else "未知"
        cmd_add(fairy_name, d_type, summary, benefit, risk)
    else:
        print(f"❌ 未知命令: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
