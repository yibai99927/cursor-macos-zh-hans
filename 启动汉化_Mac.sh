#!/bin/bash
# 启动 Cursor 简体中文汉化（macOS）
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd)"

echo "============================================================"
echo "  Cursor 简体中文汉化（macOS）"
echo "  将安装语言包、注入运行时、并应用静态补丁"
echo "============================================================"
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "[错误] 未找到 python3。请先安装（例如: brew install python3）"
  exit 1
fi

echo "将修改 Cursor 安装目录中的少量文件（自动备份）。"
read -r -p "确认继续？[Y/N]: " CONFIRM
case "$CONFIRM" in
  Y|y|YES|yes) ;;
  *) echo "已取消。"; exit 0 ;;
esac

chmod +x "$ROOT/scripts/"*.sh 2>/dev/null || true
"$ROOT/scripts/install-mac.sh"

echo
read -r -p "是否现在启动 Cursor？[Y/N]: " STARTC
case "$STARTC" in
  Y|y|YES|yes)
    if [[ -n "${CURSOR_INSTALL_DIR:-}" && -d "$CURSOR_INSTALL_DIR" ]]; then
      open "$CURSOR_INSTALL_DIR"
    elif [[ -n "${CURSOR_INSTALL_PATH:-}" ]]; then
      open "$CURSOR_INSTALL_PATH"
    elif [[ -d "/Applications/Cursor.app" ]]; then
      open -a Cursor
    else
      echo "未找到 Cursor.app，请手动启动。"
    fi
    ;;
  *)
    echo "请手动完全退出（Cmd+Q）后重新打开 Cursor。"
    ;;
esac
