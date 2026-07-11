#!/bin/bash
# 取消 Cursor 简体中文汉化（macOS）
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd)"

echo "============================================================"
echo "  取消 Cursor 简体中文汉化（macOS）"
echo "============================================================"
echo
read -r -p "确认恢复英文界面？[Y/N]: " CONFIRM
case "$CONFIRM" in
  Y|y|YES|yes) ;;
  *) echo "已取消。"; exit 0 ;;
esac

chmod +x "$ROOT/scripts/"*.sh 2>/dev/null || true
"$ROOT/scripts/uninstall-mac.sh"
