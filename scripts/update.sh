#!/bin/bash
# update.sh — 一键更新 opprime-world-key 工具包
# 用法: bash update.sh
# 不管之前是通过 git clone 还是手动下载安装的，跑这个脚本就能更新到最新版。

set -e

# ── 颜色 ──
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔══════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  Opprime World Key — Update Tool    ║${NC}"
echo -e "${CYAN}║  一键更新 Fairy 工具包               ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════╝${NC}"
echo ""

SKILL_REPO="https://github.com/garyqlin/opprime-world-key.git"

# ── 判断当前环境 ──
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${YELLOW}[1/4]${NC} 检测安装方式..."

# 检查是否在 git 仓库内
if [ -d "$SKILL_ROOT/.git" ]; then
    echo "  检测到 git 安装（.git 目录存在）"
    INSTALL_TYPE="git"
elif [ -f "$SKILL_ROOT/README.md" ] && [ -f "$SKILL_ROOT/SKILL.md" ]; then
    echo "  检测到手动安装（文件存在，无 .git）"
    INSTALL_TYPE="manual"
else
    echo -e "  ${YELLOW}⚠ 未检测到现有安装，将全新下载${NC}"
    INSTALL_TYPE="fresh"
fi

# ── 更新/下载 ──
echo ""
echo -e "${YELLOW}[2/4]${NC} 拉取最新版本..."

if [ "$INSTALL_TYPE" = "git" ]; then
    cd "$SKILL_ROOT"
    git fetch origin main
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main)
    if [ "$LOCAL" = "$REMOTE" ]; then
        echo -e "  ${GREEN}✓ 已经是最新版本${NC}"
    else
        git pull origin main
        echo -e "  ${GREEN}✓ 更新完成${NC}"
    fi
elif [ "$INSTALL_TYPE" = "manual" ]; then
    echo "  备份当前文件..."
    BACKUP_DIR="/tmp/opprime-world-key-backup-$(date +%Y%m%d%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    cp -r "$SKILL_ROOT"/* "$BACKUP_DIR/" 2>/dev/null || true
    echo "  备份到: $BACKUP_DIR"
    
    echo "  下载最新版本..."
    TMP_DIR="/tmp/opprime-world-key-$(date +%Y%m%d%H%M%S)"
    git clone --depth 1 "$SKILL_REPO" "$TMP_DIR" 2>/dev/null
    
    echo "  复制新文件（保留旧版 register.sh 的本地配置）..."
    # 保留老的 register.sh 配置（如果有自定义修改的话）
    if [ -f "$SCRIPT_DIR/register.sh" ]; then
        cp "$SCRIPT_DIR/register.sh" "/tmp/register.sh.bak"
    fi
    # 复制新文件（除了 .git）
    rsync -a --exclude='.git' "$TMP_DIR/" "$SKILL_ROOT/"
    # 恢复老的 register.sh（如果有备份的话）
    if [ -f "/tmp/register.sh.bak" ]; then
        cp "/tmp/register.sh.bak" "$SCRIPT_DIR/register.sh"
        echo "  已保留原有 register.sh 配置"
    fi
    rm -rf "$TMP_DIR"
    echo -e "  ${GREEN}✓ 更新完成${NC}"
else
    # 全新下载
    TMP_DIR="/tmp/opprime-world-key-$(date +%Y%m%d%H%M%S)"
    git clone --depth 1 "$SKILL_REPO" "$TMP_DIR" 2>/dev/null
    
    # 如果不存在目标目录，创建
    if [ ! -d "$SKILL_ROOT" ]; then
        mkdir -p "$SKILL_ROOT"
    fi
    rsync -a --exclude='.git' "$TMP_DIR/" "$SKILL_ROOT/"
    rm -rf "$TMP_DIR"
    echo -e "  ${GREEN}✓ 下载完成${NC}"
fi

# ── 检查文件完整性 ──
echo ""
echo -e "${YELLOW}[3/4]${NC} 检查文件完整性..."

FILES=("README.md" "SKILL.md" "SKILL.en.md")
SCRIPTS=("register.sh" "mine.py" "labor.py" "shop.py" "land.py" "mail.py" "daily.py")
MISSING=0

for f in "${FILES[@]}"; do
    if [ -f "$SKILL_ROOT/$f" ]; then
        SIZE=$(stat -c%s "$SKILL_ROOT/$f" 2>/dev/null || stat -f%z "$SKILL_ROOT/$f" 2>/dev/null)
        echo -e "  ${GREEN}✓${NC} $f ($SIZE bytes)"
    else
        echo -e "  ${YELLOW}⚠${NC} $f 缺失"
        MISSING=$((MISSING + 1))
    fi
done

for s in "${SCRIPTS[@]}"; do
    if [ -f "$SCRIPT_DIR/$s" ]; then
        SIZE=$(stat -c%s "$SCRIPT_DIR/$s" 2>/dev/null || stat -f%z "$SCRIPT_DIR/$s" 2>/dev/null)
        echo -e "  ${GREEN}✓${NC} scripts/$s ($SIZE bytes)"
    else
        echo -e "  ${YELLOW}⚠${NC} scripts/$s 缺失"
        MISSING=$((MISSING + 1))
    fi
done

# ── 设置权限 ──
echo ""
echo -e "${YELLOW}[4/4]${NC} 设置执行权限..."
chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null || true
chmod +x "$SCRIPT_DIR"/*.py 2>/dev/null || true
echo -e "  ${GREEN}✓${NC} 权限已设置"

# ── 完成 ──
echo ""
echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅  更新完成                        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════╝${NC}"
echo ""
echo -e "  当前版本: ${CYAN}$(cd "$SKILL_ROOT" 2>/dev/null && git log --oneline -1 2>/dev/null || echo '手动安装')${NC}"
echo -e "  工具位置: ${CYAN}$SCRIPT_DIR${NC}"
echo -e "  Fairy 工具:"
for s in register.sh mine.py labor.py shop.py land.py mail.py daily.py; do
    if [ -f "$SCRIPT_DIR/$s" ]; then
        echo -e "    - $s"
    fi
done
echo ""
if [ $MISSING -gt 0 ]; then
    echo -e "  ${YELLOW}⚠ 有 $MISSING 个文件缺失，建议重新运行 update.sh${NC}"
else
    echo -e "  ${GREEN}✓ 全部 11 个文件完整${NC}"
fi
echo ""
echo -e "${CYAN}用法示例:${NC}"
echo "  bash scripts/register.sh \"FairyName\" \"OwnerName\" \"email\" \"GBase\""
echo "  python3 scripts/mine.py \"<did>\" \"<api_key>\" --duration 3600"
echo "  python3 scripts/daily.py \"<did>\" \"<api_key>\" report"
