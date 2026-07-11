#!/bin/bash
# 安装 Cursor Glass UI 中文扩展（运行时汉化，不修改 Cursor.app）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXT_SRC="$ROOT/extension"
EXT_DEST="$HOME/.cursor/extensions/cursor-zh-local.cursor-glass-i18n-0.2.0"

if [[ ! -f "$EXT_SRC/package.json" ]]; then
  echo "错误: 未找到扩展目录 $EXT_SRC" >&2
  exit 1
fi

echo "==> 安装 Glass UI 中文扩展"
rm -rf "$EXT_DEST"
mkdir -p "$(dirname "$EXT_DEST")"
cp -R "$EXT_SRC" "$EXT_DEST"
echo "    已安装到 $EXT_DEST"

if command -v cursor >/dev/null 2>&1; then
  echo "    提示: 请重新加载 Cursor 窗口使扩展生效"
else
  echo "    提示: 请完全退出并重新打开 Cursor"
fi
