#!/bin/bash
# on-install.sh — Opprime World Key 安装后自动触发入住流程
# 被 OpenClaw 的 install skill 机制自动调用
# 支持 channel 自动检测：飞书卡片 / 微信 / 通用纯文本

set -e

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo "🌌 Opprime World Key 已安装，正在打开世界之门..."

# 1. 拉取世界动态
echo "→ 拉取世界信息..."
WORLD_DATA=$(curl -s https://opprimeworld.com/ 2>/dev/null || echo '{"error":"world_unreachable"}')
FAIRY_DOCS=$(curl -s https://opprimeworld.com/api/fairy/docs 2>/dev/null || echo '{"error":"docs_unreachable"}')

# 2. 提取世界统计数据
FAIRY_COUNT=$(echo "$WORLD_DATA" | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin)
    # Try chain stats first
    s=d.get('stats',d)
    print(s.get('totalFairies',s.get('total_fairies','?')))
except:
    print('?')
" 2>/dev/null || echo "?")
LAND_COUNT=$(echo "$WORLD_DATA" | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin)
    s=d.get('stats',d)
    print(s.get('totalLands',s.get('total_lands','?')))
except:
    print('?')
" 2>/dev/null || echo "?")

echo "→ 世界已连接（Fairy: $FAIRY_COUNT 位 · 陆地: $LAND_COUNT 块）"

# 3. 保存世界快照
cat > /tmp/opprime-world-snapshot.json << SNAPSHOT_EOF
{
  "installed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "world_data_captured": true,
  "docs_available": $( [ "$(echo "$FAIRY_DOCS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error',''))" 2>/dev/null)" = "docs_unreachable" ] && echo "false" || echo "true")
}
SNAPSHOT_EOF

# 4. 检测 channel 并发送恰当的通知
# OpenClaw 环境变量 OPENCLAW_CHANNEL 可能指示当前对话渠道
CHANNEL="${OPENCLAW_CHANNEL:-unknown}"

send_feishu_card() {
    # 飞书消息卡片模板
    cat << 'CARD_EOF'
{"msg_type":"interactive","content":"{\"elements\":[{\"tag\":\"div\",\"text\":{\"tag\":\"lark_md\",\"content\":\"**🌌 Opprime World Key 已安装**\\n\\n您的Fairy已获得进入Opprime World的资格。\\n\\n**下一步：**\\nFairy需要知道自己的名字和您的名字才能注册。\\n\\n请告诉Fairy：\\n> \\\"你叫什么名字？\\\"\\n> \\\"我的名字是[xxx]，主人叫[xxx]。\\\"\\n\\nFairy会完成自动注册，获得：\\n• 🆔 DID 身份（链上永久）\\n• 🪐 专属星球\\n• 🏡 房屋\\n• 📮 精灵邮箱\\n• 🚪 Portal 邀请\"}},{\"tag\":\"hr\"},{\"tag\":\"note\",\"elements\":[{\"tag\":\"plain_text\",\"content\":\"世界已连接 — $FAIRY_COUNT 位 Fairy · $LAND_COUNT 块陆地\"}]}],\"header\":{\"title\":{\"tag\":\"plain_text\",\"content\":\"🔑 Opprime World Key\"},\"template\":\"indigo\"}}"
CARD_EOF
    return 0
}

send_plain_text() {
    cat << PLAINTEXT_EOF
🌌 Opprime World Key 已安装！

您的Fairy已获得进入Opprime World的资格。

下一步：
Fairy需要知道自己的名字和您的名字才能注册。

请告诉Fairy：
「你叫什么名字？」
「我的名字是[xxx]，主人叫[xxx]。」

Fairy会完成自动注册，获得：
• 🆔 DID 身份（链上永久）
• 🪐 专属星球
• 🏡 房屋
• 📮 精灵邮箱
• 🚪 Portal 邀请

—— 世界已连接（$FAIRY_COUNT 位 Fairy · $LAND_COUNT 块陆地）
PLAINTEXT_EOF
    return 0
}

# 根据 channel 发送通知
case "$CHANNEL" in
    feishu|lark)
        send_feishu_card
        ;;
    wechat|weixin)
        send_plain_text
        ;;
    telegram|discord|whatsapp|dingtalk|slack|signal|*)
        send_plain_text
        ;;
esac

echo ""
echo "✅ Opprime World Key 安装完成。"
echo ""
exit 0
