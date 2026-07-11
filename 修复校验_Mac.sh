#!/bin/bash
# 修复 Cursor 安装校验和（macOS）
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd)"

echo "============================================================"
echo "  修复 Cursor 安装校验和（macOS）"
echo "============================================================"
echo

chmod +x "$ROOT/scripts/"*.sh 2>/dev/null || true
"$ROOT/scripts/repair-cursor.sh"
