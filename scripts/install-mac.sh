#!/bin/bash
# macOS 一键安装 Cursor 简体中文界面
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CURSOR_APP="/Applications/Cursor.app"
USER_DATA="$HOME/Library/Application Support/Cursor/User"
LOCALE_FILE="$USER_DATA/locale.json"
EXTENSION_ID="MS-CEINTL.vscode-language-pack-zh-hans"

echo "==> Cursor macOS 汉化安装"
echo "    项目目录: $ROOT"

if [[ ! -d "$CURSOR_APP" ]]; then
  echo "错误: 未找到 Cursor.app，请先安装 Cursor 到 /Applications" >&2
  exit 1
fi

mkdir -p "$USER_DATA"

# 1. 安装 VS Code 简体中文语言包
echo "==> 检查中文语言包..."
if ! ls "$HOME/.cursor/extensions"/ms-ceintl.vscode-language-pack-zh-hans-* >/dev/null 2>&1; then
  echo "    正在安装 $EXTENSION_ID ..."
  if command -v cursor >/dev/null 2>&1; then
    cursor --install-extension "$EXTENSION_ID" || true
  else
    echo "警告: 未找到 cursor 命令行工具，请手动在扩展市场安装中文语言包" >&2
  fi
else
  echo "    中文语言包已存在"
fi

# 2. 设置显示语言
echo "==> 设置显示语言为 zh-cn"
if [[ -f "$LOCALE_FILE" ]]; then
  cp "$LOCALE_FILE" "$ROOT/backups/locale.json.$(date +%Y%m%d-%H%M%S).bak" 2>/dev/null || mkdir -p "$ROOT/backups"
  cp "$LOCALE_FILE" "$ROOT/backups/locale.json.$(date +%Y%m%d-%H%M%S).bak"
fi
cat > "$LOCALE_FILE" <<'EOF'
{
  "locale": "zh-cn"
}
EOF
echo "    已写入 $LOCALE_FILE"

# 3. 合并 Cursor 专有翻译（NLS 语言包）
echo "==> 合并 Cursor 专有翻译（NLS）..."
python3 "$ROOT/scripts/merge-overlay.py"

# 4. 打 Glass UI 补丁（并同步 product.json 校验和，避免安装完整性报错）
echo "==> 应用 Glass UI 中文补丁..."
python3 "$ROOT/scripts/patch-glass-ui.py"

# 5. 提取当前版本字符串（供维护者参考，不影响安装）
echo "==> 提取当前版本待翻译字符串..."
python3 "$ROOT/scripts/extract.py" || true

echo ""
echo "✅ 安装完成！"
echo ""
echo "请完全退出 Cursor（Cmd+Q），然后重新打开。"
echo "若界面未切换，可在 Cursor 中执行命令: Configure Display Language → 选择 zh-cn"
echo ""
echo "卸载汉化: $ROOT/scripts/uninstall-mac.sh"
