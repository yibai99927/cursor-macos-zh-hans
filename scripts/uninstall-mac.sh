#!/bin/bash
# 恢复 Cursor 语言设置与语言包备份
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
USER_DATA="$HOME/Library/Application Support/Cursor/User"
LOCALE_FILE="$USER_DATA/locale.json"
BACKUP_DIR="$ROOT/backups"

echo "==> Cursor macOS 汉化卸载"

# 恢复 Glass UI bundle
echo "==> 恢复 Glass UI 原始文件..."
python3 "$ROOT/scripts/patch-glass-ui.py" --restore || true

# 恢复 locale.json
latest_locale_backup="$(ls -t "$BACKUP_DIR"/locale.json.*.bak 2>/dev/null | head -1 || true)"
if [[ -n "$latest_locale_backup" ]]; then
  cp "$latest_locale_backup" "$LOCALE_FILE"
  echo "    已恢复 locale.json <- $latest_locale_backup"
elif [[ -f "$LOCALE_FILE" ]]; then
  rm "$LOCALE_FILE"
  echo "    已删除 locale.json"
else
  echo "    未找到 locale.json，跳过"
fi

# 恢复语言包 main.i18n.json
latest_main_backup="$(ls -t "$BACKUP_DIR"/main.i18n.json.*.bak 2>/dev/null | head -1 || true)"
if [[ -n "$latest_main_backup" ]]; then
  pack_dir="$(ls -td "$HOME/.cursor/extensions"/ms-ceintl.vscode-language-pack-zh-hans-* 2>/dev/null | head -1 || true)"
  if [[ -n "$pack_dir" ]]; then
    cp "$latest_main_backup" "$pack_dir/translations/main.i18n.json"
    echo "    已恢复语言包 <- $latest_main_backup"
  else
    echo "警告: 未找到中文语言包目录，请手动恢复备份" >&2
  fi
else
  echo "    未找到语言包备份，跳过"
fi

echo ""
echo "✅ 卸载完成。请完全退出 Cursor（Cmd+Q）后重新打开。"
