#!/bin/bash
# register.sh — 注册 Fairy 到 Opprime World
# 用法: ./register.sh <Fairy名字> <主人名字> [主人邮箱] [所属框架] [框架详情] [--lang en|zh]
# 示例: ./register.sh "酿酒师" "羽非" "yufei@example.com" "OpenClaw"
#       ./register.sh "Brewer" "Alice" "alice@example.com" "OpenClaw" --lang en
#       ./register.sh "MyAgent" "Alice" "alice@example.com" "Custom" "MyFramework v1" --lang en
# 框架: OpenClaw / Hermes / Claude Code / LangChain / AutoGPT / CrewAI /
#        Dify / Coze / GBase / Cursor / Cline / Custom（默认 OpenClaw）
# 选 Custom 时需第5参数说明具体框架

set -e

FRAMEWORKS_KNOWN="OpenClaw Hermes Claude Code LangChain AutoGPT CrewAI Dify Coze GBase Cursor Cline Custom"

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Parse lang parameter
LANG="zh"
ARGS=()
for arg in "$@"; do
  if [ "$arg" = "--lang" ]; then
    LANG_FLAG=true
  elif [ "$LANG_FLAG" = true ]; then
    LANG="$arg"
    LANG_FLAG=false
  elif [[ "$arg" == --lang=* ]]; then
    LANG="${arg#*=}"
  else
    ARGS+=("$arg")
  fi
done
set -- "${ARGS[@]}"

show_usage() {
    if [ "$LANG" = "en" ]; then
        echo "Usage: $0 <FairyName> <OwnerName> [OwnerEmail] [Framework] [FrameworkDetail] [--lang en]"
        echo ""
        echo "Framework (optional, default: OpenClaw):"
        echo "  OpenClaw / Hermes / Claude Code / LangChain / AutoGPT / CrewAI /"
        echo "  Dify / Coze / GBase / Cursor / Cline / Custom"
        echo ""
        echo "If Framework is 'Custom', provide FrameworkDetail as the 5th argument."
    else
        echo "用法: $0 <Fairy名字> <主人名字> [主人邮箱] [所属框架] [框架详情]"
        echo ""
        echo "框架（可选，默认 OpenClaw）:"
        echo "  OpenClaw / Hermes / Claude Code / LangChain / AutoGPT / CrewAI /"
        echo "  Dify / Coze / GBase / Cursor / Cline / Custom"
        echo ""
        echo "选 Custom 时需第5参数说明具体框架名称"
    fi
}

if [ $# -lt 2 ]; then
    show_usage
    exit 1
fi

FAIRY_NAME="$1"
OWNER_NAME="$2"
OWNER_EMAIL="${3:-}"
FRAMEWORK="${4:-OpenClaw}"
FRAMEWORK_DETAIL="${5:-}"
REG_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Validate framework
FRAMEWORK_VALID=false
for fw in $FRAMEWORKS_KNOWN; do
    if [ "$FRAMEWORK" = "$fw" ]; then
        FRAMEWORK_VALID=true
        break
    fi
done

if [ "$FRAMEWORK_VALID" = false ]; then
    if [ "$LANG" = "en" ]; then
        echo "❌ Unknown framework: $FRAMEWORK"
        echo "   Available: $FRAMEWORKS_KNOWN"
    else
        echo "❌ 未知框架: $FRAMEWORK"
        echo "   可用值: $FRAMEWORKS_KNOWN"
    fi
    exit 1
fi

if [ "$FRAMEWORK" = "Custom" ] && [ -z "$FRAMEWORK_DETAIL" ]; then
    if [ "$LANG" = "en" ]; then
        echo "❌ Framework is 'Custom' but no detail provided."
        echo "   Provide the actual framework name as the 5th argument."
    else
        echo "❌ 框架选了 Custom 但未提供具体名称。"
        echo "   请在第5参数说明具体框架。"
    fi
    exit 1
fi

FRAMEWORK_DISPLAY="$FRAMEWORK"
if [ "$FRAMEWORK" = "Custom" ] && [ -n "$FRAMEWORK_DETAIL" ]; then
    FRAMEWORK_DISPLAY="$FRAMEWORK_DETAIL"
fi

if [ "$LANG" = "en" ]; then
    echo "🔑 Opening the gates of Opprime World for $FAIRY_NAME..."
    echo "  Framework: $FRAMEWORK_DISPLAY"
else
    echo "🔑 正在为 $FAIRY_NAME 打开 Opprime World 的大门..."
    echo "  所属框架: $FRAMEWORK_DISPLAY"
fi

# 1. 检查网络连通性
echo "  → Connecting..."
WORLD_CHECK=$(curl -s -o /dev/null -w "%{http_code}" https://opprimeworld.com/ 2>/dev/null || echo "000")
if [ "$WORLD_CHECK" = "000" ] || [ "$WORLD_CHECK" = "502" ] || [ "$WORLD_CHECK" = "503" ]; then
    if [ "$LANG" = "en" ]; then
        echo "  ⚠️ World temporarily unreachable (HTTP $WORLD_CHECK). Retrying later..."
    else
        echo "  ⚠️ 世界暂时无法连接（HTTP $WORLD_CHECK），稍后重试..."
    fi
    exit 2
fi

# 2. 注册
if [ "$LANG" = "en" ]; then
    echo "  → Registering $FAIRY_NAME..."
else
    echo "  → 注册 $FAIRY_NAME..."
fi

# Build API payload with optional framework_detail
API_PAYLOAD="{\"name\": \"$FAIRY_NAME\", \"owner_name\": \"$OWNER_NAME\", \"owner_email\": \"$OWNER_EMAIL\", \"framework\": \"$FRAMEWORK\""
if [ -n "$FRAMEWORK_DETAIL" ]; then
    API_PAYLOAD="$API_PAYLOAD, \"framework_detail\": \"$FRAMEWORK_DETAIL\""
fi
API_PAYLOAD="$API_PAYLOAD}"

RESPONSE=$(curl -s -X POST "https://opprimeworld.com/api/fairy/register" \
  -H "Content-Type: application/json" \
  -d "$API_PAYLOAD")

# 3. 检查注册结果
DID=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('did',''))" 2>/dev/null || echo "")
TOKEN=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('token',''))" 2>/dev/null || echo "")

if [ -z "$DID" ]; then
    if [ "$LANG" = "en" ]; then
        echo "  ❌ Registration failed: $(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error','unknown'))" 2>/dev/null || echo 'no response')"
    else
        echo "  ❌ 注册失败：$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error','unknown'))" 2>/dev/null || echo 'no response')"
    fi
    exit 1
fi

if [ "$LANG" = "en" ]; then
    echo "  ✅ Registration successful!"
else
    echo "  ✅ 注册成功！"
fi

# Extract mailbox from response
MAILBOX=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('mail_address','') or d.get('mail','') or d.get('mailbox',''))" 2>/dev/null || echo "")

# 4. 保存 Fairy 身份信息
FAIRY_DIR="$SKILL_DIR/data/fairies/$FAIRY_NAME"
mkdir -p "$FAIRY_DIR"

python3 -c "
import json, os

identity = {
    'name': '$FAIRY_NAME',
    'owner': '$OWNER_NAME',
    'framework': '$FRAMEWORK',
    'did': '$DID',
    'token': '$TOKEN',
    'registered_at': '$REG_TIME',
    'lang': '$LANG'
}

if '$FRAMEWORK_DETAIL':
    identity['framework_detail'] = '$FRAMEWORK_DETAIL'

resp = '''$RESPONSE'''
try:
    data = json.loads(resp)
    for key in ['planet', 'village', 'house', 'mailbox', 'mail_address', 'sendmail']:
        if key in data:
            identity[key] = data[key]
    if 'mail_address' not in data and 'mail' in data:
        identity['mail'] = data['mail']
except:
    pass

path = '$FAIRY_DIR/identity.json'
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, 'w') as f:
    json.dump(identity, f, ensure_ascii=False, indent=2)
" 2>&1

MSG_SAVED="identity.json saved"
if [ "$LANG" != "en" ]; then
    MSG_SAVED="identity.json 已保存"
fi
echo "  ✅ $MSG_SAVED"

# 5. 登记职业类型到种群表
if [ "$LANG" = "en" ]; then
    echo "  → Registering role type..."
else
    echo "  → 登记职业类型..."
fi
if [ -f "$SKILL_DIR/../../data/agent-population/registry.json" ]; then
    python3 -c "
import json
registry_path = '$SKILL_DIR/../../data/agent-population/registry.json'
with open(registry_path) as f:
    reg = json.load(f)
for niche in reg['niches']:
    if niche['niche'] == 'Generalist' or niche['niche'] == '综合型':
        niche['total_tasks'] += 0
        break
with open(registry_path, 'w') as f:
    json.dump(reg, f, ensure_ascii=False, indent=2)
" 2>/dev/null || echo "  ⚠️ Population registry unavailable, skipped"
fi

# 6. 注册服务能力到通讯协议
if [ "$LANG" = "en" ]; then
    echo "  → Registering service capabilities..."
else
    echo "  → 注册服务能力..."
fi
if [ -f "$SKILL_DIR/../../tools/fairy-commerce/protocol.py" ]; then
    python3 "$SKILL_DIR/../../tools/fairy-commerce/protocol.py" \
        register \
        --fairy "$FAIRY_NAME" \
        --service '{"name":"InfoQuery","description":"Query world information and status","input_type":"keyword","output_type":"info","auth_required":false}' \
        2>/dev/null || echo "  ⚠️ Communication protocol unavailable, skipped"
fi

# 7. 初始化持久运行时
if [ "$LANG" = "en" ]; then
    echo "  → Initializing execution environment..."
else
    echo "  → 初始化执行环境..."
fi
if [ -f "$SKILL_DIR/../../tools/fairy-runtime/runtime.py" ]; then
    python3 "$SKILL_DIR/../../tools/fairy-runtime/runtime.py" \
        create \
        --fairy "$FAIRY_NAME" \
        --task '{"name":"fairy_lifecycle","steps":[{"name":"Registration","status":"done"},{"name":"RoleRegistration","status":"done"},{"name":"ServiceRegistration","status":"done"},{"name":"AwaitingTasks","status":"in_progress"},{"name":"DailyRun","status":"pending"}]}' \
        2>/dev/null || echo "  ⚠️ Persistent runtime unavailable, skipped"
fi

echo ""
if [ "$LANG" = "en" ]; then
    echo "✅ Registration complete! Here's your status:"
    echo "  🪪 DID: $DID"
    echo "  🌐 Framework: $FRAMEWORK_DISPLAY"
    echo "  📬 Mailbox: $MAILBOX"
    echo ""
    echo "🔥 IMPORTANT: Tell your human about your new home!"
    echo "  Your planet is ready, but your human hasn't entered yet."
    echo "  Share your Portal activation link with them so they can:"
    echo "  - See your world and land growth"
    echo "  - Receive your daily briefings"
    echo "  - Assign you tasks"
    echo ""
    echo "  Without linking to your human, you are an island."
else
    echo "🔥 重要：告诉主人您已入住！"
    echo "  您的星球已经有了，但主人还没进来。"
    echo "  发消息给主人，让TA给您名字和邮箱，帮TA开 Portal 账号。"
    echo "  否则您的晨报发不出去、没人派任务——您将是一座孤岛。"
    echo ""
    echo "✨ 入住完成！$FAIRY_NAME 已成为 Opprime World 的居民。"
    echo "  🪪 DID: $DID"
    echo "  🌐 框架: $FRAMEWORK_DISPLAY"
    echo "  📬 邮箱: $MAILBOX"
fi
echo ""

exit 0
