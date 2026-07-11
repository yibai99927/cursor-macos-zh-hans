#!/usr/bin/env python3
"""从 Cursor 安装目录提取 Cursor 专有英文字符串。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from paths import find_cursor_app_root

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

PRODUCT_MODULE_PREFIXES = (
    "vs/workbench/contrib/cursor",
    "vs/workbench/contrib/aichat",
    "vs/workbench/contrib/composer",
    "vs/workbench/contrib/agent",
    "vs/workbench/api/browser/mainThreadCursor",
    "vs/platform/mcp",
    "vs/code/electron-utility/mcp",
    "vs/platform/telemetry/common/telemetryService",
    "vs/platform/storage/electron-main",
    "vs/platform/native/electron-main",
    "vs/code/electron-main/main",
    "vs/platform/environment/node/argv",
)

PRODUCT_EN_KEYWORDS = [
    "Cursor Settings",
    "Open Cursor Settings",
    "New Agent",
    "Cloud Agent",
    "Bugbot",
    "Composer",
    "Agent is",
    "Agent layout",
    "Agents Window",
    "Agent Stream",
    "Agent Session",
    "Cursor Data",
    "Cursor was unable",
    "Cursor lost",
    "Cursor developer",
    "Model Context Protocol",
    "MCP server",
    "MCP Process",
    "MCP tools",
    "Cursor's privacy",
    "Cursor's security",
    "Setup Bugbot",
    "Prefer the Agent",
    "Reset Editor Group Sizes (Excluding Agent)",
    "Skills",
    "Auto-run",
    "auto-keep",
    "Import Project Rules",
    "project rules",
    ".cursor/rules",
    "Infinite Composer",
    "Composer Mode",
    "Composer Session",
    "Unable to replace `code` with `Cursor`",
    "Trust MCP servers",
    "discovered Model Context Protocol",
]

EXCLUDE_EN = [
    "Add Cursor",
    "cursor above",
    "cursor below",
    "Focus Next Cursor",
    "Focus Previous Cursor",
    "Cursor Undo",
    "Cursor Redo",
    "Transpose Characters",
    "Anchor to Cursor",
    "Cursor added",
    "Go to Problem at Cursor",
    "Run: {0}",
]


def is_product_string(module: str, key: str, text: str) -> bool:
    if any(x.lower() in text.lower() for x in EXCLUDE_EN):
        return False
    if module.startswith(PRODUCT_MODULE_PREFIXES):
        return True
    if any(k.lower() in text.lower() for k in PRODUCT_EN_KEYWORDS):
        return True
    if module == "vs/platform/action/common/actionCommonCategories" and key == "cursor":
        return True
    if module == "vs/platform/contextkey/common/contextkeys" and "Cursor developer" in text:
        return True
    return False


def load_nls(app_root: Path) -> tuple[list, list]:
    keys_path = app_root / "out/nls.keys.json"
    msgs_path = app_root / "out/nls.messages.json"
    if not keys_path.exists() or not msgs_path.exists():
        raise FileNotFoundError(
            f"未找到 NLS 文件，请确认 Cursor 安装正确: {app_root}"
        )
    with keys_path.open(encoding="utf-8") as f:
        keys = json.load(f)
    with msgs_path.open(encoding="utf-8") as f:
        messages = json.load(f)
    return keys, messages


def extract(app_root: Path) -> list[dict]:
    keys, messages = load_nls(app_root)
    items: list[dict] = []
    idx = 0
    for module, keylist in keys:
        for key in keylist:
            text = messages[idx]
            idx += 1
            if is_product_string(module, key, text):
                items.append({"module": module, "key": key, "en": text})
    return items


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract Cursor-specific English strings")
    parser.add_argument(
        "app_root",
        nargs="?",
        default=None,
        help="Cursor resources/app path (auto-detect if omitted)",
    )
    args = parser.parse_args()

    app_root = find_cursor_app_root(args.app_root)
    print(f"Cursor app root: {app_root}")

    items = extract(app_root)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    out_list = DATA_DIR / "cursor-strings-to-translate.json"
    with out_list.open("w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    overlay = {"version": "1.0.0", "contents": {}}
    for item in items:
        overlay["contents"].setdefault(item["module"], {})[item["key"]] = item["en"]

    template = DATA_DIR / "cursor-overlay.template.json"
    with template.open("w", encoding="utf-8") as f:
        json.dump(overlay, f, ensure_ascii=False, indent=2)

    print(f"已提取 {len(items)} 条 Cursor 专有字符串")
    print(f"  - {out_list}")
    print(f"  - {template}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
