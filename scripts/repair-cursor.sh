#!/bin/bash
# 修复因 JS 补丁导致的 Cursor 安装完整性问题
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> 修复 Cursor 安装完整性"
echo "    恢复 Cursor.app 内被修改的 workbench 文件..."

python3 "$ROOT/scripts/patch-glass-ui.py" --restore || {
  echo "警告: 自动恢复失败，请从 cursor.com 重新下载安装 Cursor" >&2
  exit 1
}

echo ""
echo "✅ 已恢复原始 JS 文件。"
echo "请完全退出 Cursor（Cmd+Q）后重新打开。"
echo "若仍提示安装错误，请从 https://cursor.com 重新安装 Cursor。"
