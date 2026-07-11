#!/usr/bin/env python3
"""为 Cursor Glass UI / Settings 界面打中文补丁（macOS）。"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data/glass-ui-replacements.json"
BACKUP_DIR = ROOT / "backups"
DEFAULT_CURSOR_APP = Path("/Applications/Cursor.app/Contents/Resources/app")


def load_config() -> dict:
    with DATA_FILE.open(encoding="utf-8") as f:
        return json.load(f)


def backup_file(source: Path) -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = BACKUP_DIR / f"{source.name}.{stamp}.bak"
    shutil.copy2(source, backup_path)
    return backup_path


def find_latest_backup(filename: str) -> Path | None:
    candidates = sorted(BACKUP_DIR.glob(f"{filename}.*.bak"), reverse=True)
    return candidates[0] if candidates else None


def apply_replacements(content: str, config: dict) -> tuple[str, dict]:
    stats = {"blocks": 0, "exact": 0, "missed_blocks": [], "missed_exact": []}

    for block in config.get("blocks", []):
        src = block["from"]
        dst = block["to"]
        if src in content:
            content = content.replace(src, dst)
            stats["blocks"] += 1
        else:
            stats["missed_blocks"].append(block.get("id", src[:40]))

    exact_items = sorted(config.get("exact", []), key=lambda x: len(x["from"]), reverse=True)
    for item in exact_items:
        src = item["from"]
        dst = item["to"]
        if src in content:
            count = content.count(src)
            content = content.replace(src, dst)
            stats["exact"] += count
        else:
            stats["missed_exact"].append(src)

    return content, stats


def patch_file(app_root: Path, rel_path: str, config: dict, dry_run: bool = False) -> dict | None:
    target = app_root / rel_path
    if not target.exists():
        return None

    original = target.read_text(encoding="utf-8")
    patched, stats = apply_replacements(original, config)

    if patched == original:
        return {"file": rel_path, "changed": False, **stats}

    if not dry_run:
        backup_file(target)
        target.write_text(patched, encoding="utf-8")

    return {"file": rel_path, "changed": True, **stats}


def restore_file(filename: str, app_root: Path, rel_path: str) -> bool:
    backup = find_latest_backup(filename)
    if not backup:
        return False
    target = app_root / rel_path
    if not target.parent.exists():
        return False
    shutil.copy2(backup, target)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch Cursor Glass UI strings for zh-cn")
    parser.add_argument("--app-root", default=str(DEFAULT_CURSOR_APP), help="Cursor app resources path")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--restore", action="store_true", help="Restore latest backups")
    args = parser.parse_args()

    app_root = Path(args.app_root)
    if not app_root.exists():
        print(f"错误: 未找到 Cursor 应用目录: {app_root}")
        return 1

    config = load_config()

    if args.restore:
        restored = 0
        for target in config["targets"]:
            rel = target["file"]
            filename = Path(rel).name
            if restore_file(filename, app_root, rel):
                print(f"已恢复 {rel}")
                restored += 1
        if restored == 0:
            print("未找到可恢复的备份文件")
            return 1
        print(f"共恢复 {restored} 个文件")
        return 0

    print("==> 应用 Glass UI 中文补丁")
    total_changed = 0
    for target in config["targets"]:
        rel = target["file"]
        required = target.get("required", True)
        result = patch_file(app_root, rel, config, dry_run=args.dry_run)
        if result is None:
            msg = f"跳过（文件不存在）: {rel}"
            if required:
                print(f"警告: {msg}")
            else:
                print(msg)
            continue

        status = "已更新" if result["changed"] else "无变化"
        print(f"  {rel}: {status}")
        if result["changed"]:
            total_changed += 1
            print(f"    - 块替换: {result['blocks']} 处")
            print(f"    - 精确替换: {result['exact']} 处")
        if result["missed_blocks"]:
            print(f"    - 未命中块: {', '.join(result['missed_blocks'][:5])}")
        if result["missed_exact"] and result["changed"]:
            missed = result["missed_exact"]
            print(f"    - 未命中条目: {len(missed)} 条")

    if args.dry_run:
        print("预览模式，未写入任何文件")
    elif total_changed == 0:
        print("没有文件被修改（可能已打过补丁或版本不匹配）")
    else:
        print(f"完成，共修改 {total_changed} 个文件")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
