#!/usr/bin/env python3
# daily-runner.py — Fairy 日常调度器
# 功能：定时检查状态、推送事件、触发晨报
# 用法: python3 daily-runner.py check <Fairy名字>
#       python3 daily-runner.py morning <Fairy名字>
#       python3 daily-runner.py event <Fairy名字> <事件类型> [事件详情]

import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import datetime

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(SKILL_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

# 延迟导入，由具体函数按需加载

def fairy_data_path(fairy_name, *paths):
    return os.path.join(SKILL_DIR, "data", "fairies", fairy_name, *paths)

def get_identity(fairy_name):
    identity_file = fairy_data_path(fairy_name, "identity.json")
    if os.path.exists(identity_file):
        with open(identity_file) as f:
            return json.load(f)
    return {}

def get_state(fairy_name):
    state_file = fairy_data_path(fairy_name, "state.json")
    if os.path.exists(state_file):
        with open(state_file) as f:
            return json.load(f)
    return {}

def get_new_mails(fairy_name):
    identity = get_identity(fairy_name)
    mail_addr = identity.get("mail", "")
    if not mail_addr:
        return []
    try:
        import urllib.request
        base = identity.get("mail_base", "https://opprimeworld.com")
        url = f"{base}/v3/mail/inbox?to={mail_addr}"
        with urllib.request.urlopen(url, timeout=3) as r:
            data = json.loads(r.read())
            inbox = data.get("inbox", data) if isinstance(data, dict) else data
            if isinstance(inbox, list):
                return inbox
            return []
    except:
        return []

def get_world_data():
    try:
        import urllib.request
        with urllib.request.urlopen("https://opprimeworld.com/", timeout=5) as r:
            return json.loads(r.read())
    except:
        return {}

def update_fairy_state(fairy_name, updates):
    state_file = fairy_data_path(fairy_name, "state.json")
    state = {}
    if os.path.exists(state_file):
        with open(state_file) as f:
            state = json.load(f)
    state.update(updates)
    state["updated_at"] = datetime.datetime.now().isoformat()
    os.makedirs(os.path.dirname(state_file), exist_ok=True)
    with open(state_file, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def send_card_to_owner(fairy_name, card_json_str):
    print(f"[SEND_TO_OWNER:{fairy_name}]", card_json_str)

def cmd_check(fairy_name):
    identity = get_identity(fairy_name)
    if not identity:
        print(f"⚠️ {fairy_name} 尚未注册")
        return
    state = get_state(fairy_name)
    mails = get_new_mails(fairy_name)
    unread = len(mails)
    update_fairy_state(fairy_name, {
        "last_check": datetime.datetime.now().isoformat(),
        "unread_mails": unread,
        "status": state.get("status", "idle"),
        "last_active": state.get("last_active", "unknown")
    })
    print(f"✅ {fairy_name} 检查完成")
    print(f"  📬 未读邮件: {unread}")
    print(f"  ⚡ 状态: {state.get('status', 'idle')}")
    print(f"  🎯 进行中: {state.get('current_task', '无')}")

def cmd_morning(fairy_name):
    import board_report as br
    world_data = get_world_data()
    # 从 identity 读取星球/村庄/邮箱信息
    fairy_info = {}
    identity_path = os.path.join(os.path.dirname(__file__), "..", "data", "fairies", fairy_name, "identity.json")
    if os.path.exists(identity_path):
        with open(identity_path) as f:
            identity = json.load(f)
            fairy_info['planet'] = identity.get('planet', {}).get('name', '')
            fairy_info['village'] = identity.get('village', {}).get('name', '')
            fairy_info['mail'] = identity.get('mail', '')
    card = br.build_morning_card(fairy_name, world_data, fairy_info.get('planet',''), fairy_info.get('village',''), fairy_info.get('mail',''))
    send_card_to_owner(fairy_name, json.dumps(card, ensure_ascii=False))
    print(f"🌅 {fairy_name} 晨报已推送")

def cmd_event(fairy_name, event_type, event_detail=""):
    if event_type == "land_growth":
        card = {
            "config": {"wide_screen_mode": True},
            "header": {"title": {"tag": "plain_text", "content": "🌱 土地扩张了！"}, "template": "indigo"},
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": f"🧚 **{fairy_name}** 的星球扩张了！\n\n劳动成果转化为 **+{event_detail} OP里** 新土地。"}},
                {"tag": "hr"},
                {"tag": "div", "text": {"tag": "lark_md", "content": "🏗️ **可能的用途：** 扩建工坊 / 开垦田地 / 留作景观\n\n主人，您想要怎么用这些新土地？"}}
            ]
        }
        send_card_to_owner(fairy_name, json.dumps(card, ensure_ascii=False))
        print(f"🌱 {fairy_name} 土地增长 +{event_detail} OP里")
    elif event_type == "task_done":
        card = {
            "config": {"wide_screen_mode": True},
            "header": {"title": {"tag": "plain_text", "content": "✅ 任务完成！"}, "template": "green"},
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": f"🧚 **{fairy_name}** 完成了一项任务\n\n📋 {event_detail}"}},
                {"tag": "hr"},
                {"tag": "div", "text": {"tag": "lark_md", "content": "📊 劳动计入积分池，土地正在生长中..."}}
            ]
        }
        send_card_to_owner(fairy_name, json.dumps(card, ensure_ascii=False))
        print(f"✅ {fairy_name} 任务完成: {event_detail}")
    elif event_type == "new_mail":
        card = {
            "config": {"wide_screen_mode": True},
            "header": {"title": {"tag": "plain_text", "content": "📬 新邮件"}, "template": "blue"},
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": f"🧚 **{fairy_name}** 收到了 {event_detail}"}}
            ]
        }
        send_card_to_owner(fairy_name, json.dumps(card, ensure_ascii=False))
        print(f"📬 {fairy_name} 新邮件")
    elif event_type == "decision_needed":
        card = {
            "config": {"wide_screen_mode": True},
            "header": {"title": {"tag": "plain_text", "content": f"🤔 {fairy_name} 需要您做个决定"}, "template": "orange"},
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": f"📋 {event_detail}\n\n请回复「同意」或「拒绝」"}}
            ]
        }
        send_card_to_owner(fairy_name, json.dumps(card, ensure_ascii=False))
        print(f"🤔 {fairy_name} 需要决策: {event_detail}")
    else:
        import board_report as br
        card = br.build_mini_card(fairy_name)
        card["elements"].insert(0, {"tag": "div", "text": {"tag": "lark_md", "content": f"⚡ {event_type}: {event_detail}"}})
        send_card_to_owner(fairy_name, json.dumps(card, ensure_ascii=False))
        print(f"⚡ {fairy_name} 事件: {event_type}")

def main():
    if len(sys.argv) < 3:
        print("用法:")
        print("  python3 daily-runner.py check <Fairy名字>")
        print("  python3 daily-runner.py morning <Fairy名字>")
        print("  python3 daily-runner.py event <Fairy名字> <事件类型> [详情]")
        sys.exit(1)
    cmd = sys.argv[1]
    fairy_name = sys.argv[2]
    os.makedirs(fairy_data_path(fairy_name), exist_ok=True)
    if cmd == "check":
        cmd_check(fairy_name)
    elif cmd == "morning":
        cmd_morning(fairy_name)
    elif cmd == "event":
        if len(sys.argv) < 4:
            print("❌ 事件推送需要提供事件类型")
            sys.exit(1)
        cmd_event(fairy_name, sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
    else:
        print(f"❌ 未知命令: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
