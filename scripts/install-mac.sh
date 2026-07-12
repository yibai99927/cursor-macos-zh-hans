#!/bin/bash
# macOS 一键安装 Cursor 简体中文界面
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
USER_DATA="${CURSOR_USER_DATA_DIR:-$HOME/Library/Application Support/Cursor}/User"
LOCALE_FILE="$USER_DATA/locale.json"

echo "==> Cursor macOS 汉化安装"
echo "    项目目录: $ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "错误: 未找到 python3，请先安装 Python 3（例如: brew install python3）" >&2
  exit 1
fi

APP_ROOT="$(python3 "$ROOT/scripts/paths.py" --app-root)"
echo "    Cursor app root: $APP_ROOT"

mkdir -p "$USER_DATA"
mkdir -p "$ROOT/backups"

# 1. 按版本匹配安装语言包
echo "==> 确保中文语言包版本匹配..."
python3 "$ROOT/scripts/ensure-language-pack.py" --app-root "$APP_ROOT"

# 2. 设置显示语言
echo "==> 设置显示语言为 zh-cn"
if [[ -f "$LOCALE_FILE" ]]; then
  cp "$LOCALE_FILE" "$ROOT/backups/locale.json.$(date +%Y%m%d-%H%M%S).bak"
fi
cat > "$LOCALE_FILE" <<'EOF'
{
  "locale": "zh-cn"
}
EOF
echo "    已写入 $LOCALE_FILE"

# 3. 合并 NLS overlay
echo "==> 合并 Cursor 专有翻译（NLS）..."
python3 "$ROOT/scripts/merge-overlay.py"

# 4. 私有扩展桥接
echo "==> 桥接私有扩展翻译..."
python3 "$ROOT/scripts/bridge-private-extensions.py" || echo "警告: 私有扩展桥接失败（可忽略）"

# 5. 运行时注入
echo "==> 注入 workbench 运行时翻译..."
python3 "$ROOT/scripts/inject-runtime.py" --app-root "$APP_ROOT"

# 5.5 清理失效 Glass 词典（需已安装 Cursor）
echo "==> 清理失效 Glass 词典条目..."
python3 "$ROOT/scripts/prune-glass-dict.py" --app-root "$APP_ROOT" --apply-heuristics --apply 2>/dev/null || true

# 6. Glass UI / 结构化静态补丁
echo "==> 应用 Glass UI / 结构化静态补丁..."
python3 "$ROOT/scripts/patch-glass-ui.py" --app-root "$APP_ROOT"

# 7. 安装守护扩展
echo "==> 安装汉化守护扩展..."
bash "$ROOT/scripts/install-extension.sh" || echo "警告: 守护扩展安装失败（可忽略）"

# 8. 提取字符串（仅维护者模式）
if [[ "${CURSOR_ZH_MAINTAINER:-}" == "1" ]]; then
  echo "==> 提取当前版本待翻译字符串（维护者模式）..."
  python3 "$ROOT/scripts/extract.py" "$APP_ROOT" || true
fi

echo ""
echo "安装完成！"
echo ""
echo "请完全退出 Cursor（Cmd+Q），然后重新打开。"
echo "若界面未切换，可在 Cursor 中执行命令: Configure Display Language → 选择 zh-cn"
echo ""
echo "卸载汉化: $ROOT/scripts/uninstall-mac.sh  或  ./取消汉化_Mac.sh"
