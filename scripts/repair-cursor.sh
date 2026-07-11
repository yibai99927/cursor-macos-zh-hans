#!/bin/bash
# 修复 Cursor 安装完整性（校验和）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> 修复 Cursor 安装完整性"
echo "    同步 workbench.html 的 product.json 校验和..."

python3 "$ROOT/scripts/inject-runtime.py" --fix-checksum || {
  echo "警告: 校验和修复失败。可尝试完整卸载后重装汉化。" >&2
  echo "  $ROOT/scripts/uninstall-mac.sh" >&2
  echo "  $ROOT/scripts/install-mac.sh" >&2
  exit 1
}

echo ""
echo "校验和已更新。"
echo "请完全退出 Cursor（Cmd+Q）后重新打开。"
echo "若仍提示安装错误，请先卸载汉化再重装，或从 https://cursor.com 重装 Cursor。"
