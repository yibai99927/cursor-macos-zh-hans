#!/usr/bin/env bash
# 安装守护扩展到 ~/.cursor/extensions
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/extension"
DEST_DIR="$HOME/.cursor/extensions"
NAME="cursor-zh-local.cursor-zh-hans-guard-0.3.0"
DEST="$DEST_DIR/$NAME"

mkdir -p "$DEST_DIR"
rm -rf "$DEST"
mkdir -p "$DEST"
cp "$SRC/package.json" "$SRC/extension.js" "$DEST/"
# translations.json 可选保留供参考
if [[ -f "$SRC/translations.json" ]]; then
  cp "$SRC/translations.json" "$DEST/"
fi
echo "已安装守护扩展: $DEST"
echo "请重新加载 Cursor 窗口或完全重启。"
