#!/usr/bin/env python3
"""清理 glass-ui-replacements.json 中失效或冗余的 exact 条目。

支持两种模式：
1. --app-root：对当前 Cursor 安装目录 dry-run 补丁，归档未命中条目
2. --apply-heuristics：离线移除与结构化补丁 / translations 重叠的冗余条目
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from paths import find_cursor_app_root, platform_display_name

ROOT = Path(__file__).resolve().parent.parent
GLASS_FILE = ROOT / "data" / "glass-ui-replacements.json"
STRUCTURED_FILE = ROOT / "data" / "structured-patches.json"
TRANSLATIONS_FILE = ROOT / "extension" / "translations.json"
ARCHIVE_FILE = ROOT / "data" / "glass-ui-replacements.archive.json"


def log(msg: str = "") -> None:
    print(msg, flush=True)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def structured_sources(structured: dict) -> set[str]:
    sources: set[str] = set()
    for item in structured.get("structuredReplacements", []):
        for mapping in item.get("values", {}).values():
            src = mapping.get("source")
            if isinstance(src, str) and src:
                sources.add(src)
    return sources


def translation_sources() -> set[str]:
    if not TRANSLATIONS_FILE.exists():
        return set()
    data = load_json(TRANSLATIONS_FILE)
    return {k for k in data if isinstance(k, str)}


def scan_missed_exact(app_root: Path, config: dict, structured: dict | None) -> set[str]:
    """对目标 JS 文件 dry-run，返回全局未命中的 exact from 集合。"""
    import importlib.util

    patch_path = ROOT / "scripts" / "patch-glass-ui.py"
    spec = importlib.util.spec_from_file_location("patch_glass_ui", patch_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载 {patch_path}")
    patch_glass_ui = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(patch_glass_ui)
    apply_replacements = patch_glass_ui.apply_replacements
    apply_structured_replacements = patch_glass_ui.apply_structured_replacements

    missed: set[str] = set()
    targets = list(config.get("targets") or [])
    if structured and structured.get("targets"):
        seen = {t["file"] for t in targets}
        for t in structured["targets"]:
            if t["file"] not in seen:
                targets.append(t)
                seen.add(t["file"])

    for target in targets:
        rel = target["file"]
        file_path = app_root / rel
        if not file_path.exists():
            continue
        content = file_path.read_text(encoding="utf-8")
        _, stats = apply_replacements(content, config)
        if structured:
            content2, _ = apply_structured_replacements(content, structured)
            # structured 可能已替换部分；missed_exact 仍以原始 content 统计
            _ = content2
        missed.update(stats.get("missed_exact") or [])

    return missed


def merge_archive(removed: list[dict], reason: str) -> None:
    archive: dict = {"version": "1.0.0", "entries": []}
    if ARCHIVE_FILE.exists():
        archive = load_json(ARCHIVE_FILE)
    stamp = datetime.now().isoformat(timespec="seconds")
    for item in removed:
        archive.setdefault("entries", []).append(
            {
                "from": item["from"],
                "to": item["to"],
                "reason": reason,
                "archivedAt": stamp,
            }
        )
    save_json(ARCHIVE_FILE, archive)


def prune_entries(
    glass: dict,
    to_remove: set[str],
    reason: str,
    apply: bool,
) -> tuple[int, list[dict]]:
    exact = glass.get("exact", [])
    removed = [e for e in exact if e.get("from") in to_remove]
    if not removed:
        return 0, []
    if apply:
        glass["exact"] = [e for e in exact if e.get("from") not in to_remove]
        merge_archive(removed, reason)
    return len(removed), removed


def collect_heuristic_removals(glass: dict, structured: dict) -> dict[str, set[str]]:
    exact_from = {e["from"] for e in glass.get("exact", [])}
    groups: dict[str, set[str]] = {}

    struct_src = structured_sources(structured)
    overlap = exact_from & struct_src
    if overlap:
        groups["structured-overlap"] = overlap

    trans_src = translation_sources()
    overlap = exact_from & trans_src
    if overlap:
        groups["translations-overlap"] = overlap

    return groups


def main() -> int:
    parser = argparse.ArgumentParser(description="Prune obsolete glass-ui-replacements exact entries")
    parser.add_argument("--app-root", default=None, help="Cursor resources/app path for dry-run prune")
    parser.add_argument(
        "--apply-heuristics",
        action="store_true",
        help="Remove entries redundant with structured patches or translations.json",
    )
    parser.add_argument("--apply", action="store_true", help="Write pruned glass file and archive")
    parser.add_argument(
        "--check-overlaps",
        action="store_true",
        help="Exit 1 if heuristic overlaps remain (for CI)",
    )
    args = parser.parse_args()

    if not GLASS_FILE.exists():
        log(f"错误: 未找到 {GLASS_FILE}")
        return 1

    glass = load_json(GLASS_FILE)
    structured = load_json(STRUCTURED_FILE) if STRUCTURED_FILE.exists() else {}
    total_removed = 0
    all_removed: list[dict] = []

    if args.apply_heuristics or args.check_overlaps:
        groups = collect_heuristic_removals(glass, structured)
        union: set[str] = set()
        for name, items in groups.items():
            log(f"启发式重叠 [{name}]: {len(items)} 条")
            union |= items
        if args.check_overlaps:
            if union:
                log(f"错误: glass exact 仍有 {len(union)} 条冗余条目，请运行 prune-glass-dict.py --apply-heuristics --apply")
                return 1
            log("启发式重叠检查通过")
            return 0
        if union:
            n, removed = prune_entries(glass, union, "heuristic-overlap", args.apply)
            total_removed += n
            all_removed.extend(removed)

    if args.app_root:
        try:
            app_root = find_cursor_app_root(args.app_root)
        except FileNotFoundError as exc:
            log(f"错误: {exc}")
            return 1
        log(f"平台: {platform_display_name()}")
        log(f"Cursor app root: {app_root}")
        missed = scan_missed_exact(app_root, glass, structured or None)
        # 仅归档在所有目标文件中都未命中的条目
        log(f"dry-run 未命中 exact: {len(missed)} 条")
        if missed:
            n, removed = prune_entries(glass, missed, "dry-run-missed", args.apply)
            total_removed += n
            all_removed.extend(removed)

    if args.apply and total_removed:
        glass["prunedAt"] = datetime.now().isoformat(timespec="seconds")
        save_json(GLASS_FILE, glass)
        log(f"已归档 {total_removed} 条到 {ARCHIVE_FILE.name}")
        log(f"glass exact 剩余: {len(glass.get('exact', []))} 条")
    elif total_removed:
        log(f"预览: 将移除 {total_removed} 条（加 --apply 写入）")
    elif not args.check_overlaps:
        log("无需清理")

    if not args.apply_heuristics and not args.app_root and not args.check_overlaps:
        log("提示: 使用 --apply-heuristics 和/或 --app-root，并加 --apply 写入")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
