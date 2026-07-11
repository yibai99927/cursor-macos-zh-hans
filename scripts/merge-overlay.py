#!/usr/bin/env python3
"""将 Cursor 专有中文翻译合并进已安装的 VS Code 简体中文语言包。"""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OVERLAY_PATH = ROOT / "data/cursor-overlay.zh-cn.json"
EXTENSIONS_DIR = Path.home() / ".cursor/extensions"
BACKUP_DIR = ROOT / "backups"


def find_language_pack() -> Path:
    candidates = sorted(
        EXTENSIONS_DIR.glob("ms-ceintl.vscode-language-pack-zh-hans-*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError(
            "未找到中文语言包。请先安装 MS-CEINTL.vscode-language-pack-zh-hans"
        )
    return candidates[0]


def merge_overlay(main_i18n: dict, overlay: dict) -> tuple[dict, int]:
    contents = main_i18n.setdefault("contents", {})
    merged = 0
    for module, keys in overlay.get("contents", {}).items():
        target = contents.setdefault(module, {})
        for key, value in keys.items():
            if target.get(key) != value:
                target[key] = value
                merged += 1
    return main_i18n, merged


def main() -> int:
    if not OVERLAY_PATH.exists():
        raise FileNotFoundError(f"未找到翻译文件: {OVERLAY_PATH}")

    with OVERLAY_PATH.open(encoding="utf-8") as f:
        overlay = json.load(f)

    pack_dir = find_language_pack()
    main_path = pack_dir / "translations/main.i18n.json"
    if not main_path.exists():
        raise FileNotFoundError(f"语言包中未找到 main.i18n.json: {main_path}")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = BACKUP_DIR / f"main.i18n.json.{stamp}.bak"
    shutil.copy2(main_path, backup_path)

    with main_path.open(encoding="utf-8") as f:
        main_i18n = json.load(f)

    merged_i18n, count = merge_overlay(main_i18n, overlay)
    with main_path.open("w", encoding="utf-8") as f:
        json.dump(merged_i18n, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"语言包: {pack_dir.name}")
    print(f"已合并 {count} 条 Cursor 翻译")
    print(f"备份: {backup_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
