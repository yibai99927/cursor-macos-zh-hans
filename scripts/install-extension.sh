#!/usr/bin/env bash
# 安装守护扩展到 ~/.cursor/extensions，并捆绑回补所需脚本与数据
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/extension"
DEST_DIR="$HOME/.cursor/extensions"
NAME="cursor-zh-local.cursor-zh-hans-guard-0.4.0"
DEST="$DEST_DIR/$NAME"
BUNDLED="$DEST/bundled"

mkdir -p "$DEST_DIR"
rm -rf "$DEST"
mkdir -p "$DEST" "$BUNDLED/scripts" "$BUNDLED/data/runtime-dicts" "$BUNDLED/runtime"

cp "$SRC/package.json" "$SRC/extension.js" "$DEST/"
if [[ -f "$SRC/translations.json" ]]; then
  cp "$SRC/translations.json" "$DEST/"
fi

cp "$ROOT/scripts/patch-glass-ui.py" "$ROOT/scripts/inject-runtime.py" "$ROOT/scripts/paths.py" "$BUNDLED/scripts/"
cp "$ROOT/data/glass-ui-replacements.json" "$ROOT/data/structured-patches.json" "$BUNDLED/data/"
cp "$ROOT/data/runtime-dicts/"*.json "$BUNDLED/data/runtime-dicts/"
cp "$ROOT/runtime/engine.js" "$BUNDLED/runtime/"

cat > "$BUNDLED/manifest.json" <<EOF
{
  "bundledAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "sourceRepo": "$ROOT"
}
EOF

echo "已安装守护扩展: $DEST"
echo "已捆绑回补资源: $BUNDLED"
echo "请重新加载 Cursor 窗口或完全重启。"
