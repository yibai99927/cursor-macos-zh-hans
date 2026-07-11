#!/usr/bin/env python3
"""校验 data/runtime-dicts/ 词典质量。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DICT_DIR = ROOT / "data" / "runtime-dicts"

# 单独作为精确匹配时极易误伤
DANGEROUS_EXACT = {
    "on",
    "off",
    "open",
    "close",
    "in",
    "to",
    "for",
    "and",
    "or",
    "the",
    "a",
    "an",
    "new",
    "all",
    "yes",
    "no",
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def validate_entries(name: str, entries: list, errors: list[str], warnings: list[str]) -> None:
    seen: dict[str, str] = {}
    for i, item in enumerate(entries):
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            errors.append(f"{name}: entries[{i}] 必须是 [英文, 中文]")
            continue
        en, zh = item[0], item[1]
        if not isinstance(en, str) or not isinstance(zh, str):
            errors.append(f"{name}: entries[{i}] 的键值必须是字符串")
            continue
        if not en.strip():
            errors.append(f"{name}: entries[{i}] 英文为空")
        if not zh.strip():
            errors.append(f"{name}: entries[{i}] 中文为空: {en!r}")
        if en in seen and seen[en] != zh:
            errors.append(f"{name}: 英文键冲突 {en!r}: {seen[en]!r} vs {zh!r}")
        seen[en] = zh
        if en.strip().lower() in DANGEROUS_EXACT:
            warnings.append(f"{name}: 危险短词精确匹配 {en!r}（建议移到 fragments 或删除）")
        if len(en.strip()) <= 2:
            warnings.append(f"{name}: 过短键 {en!r}")


def validate_patterns(name: str, patterns: list, errors: list[str]) -> None:
    for i, pat in enumerate(patterns):
        if not isinstance(pat, dict):
            errors.append(f"{name}: patterns[{i}] 必须是对象")
            continue
        regex = pat.get("regex")
        replacement = pat.get("replacement")
        if not regex or not isinstance(regex, str):
            errors.append(f"{name}: patterns[{i}] 缺少 regex")
            continue
        if not isinstance(replacement, str) or not replacement:
            errors.append(f"{name}: patterns[{i}] 缺少 replacement")
        flags = pat.get("flags", "")
        flag_bits = 0
        if "i" in flags:
            flag_bits |= re.IGNORECASE
        if "m" in flags:
            flag_bits |= re.MULTILINE
        if "s" in flags:
            flag_bits |= re.DOTALL
        try:
            re.compile(regex, flag_bits)
        except re.error as exc:
            errors.append(f"{name}: patterns[{i}] 正则无效: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate runtime dictionaries")
    parser.add_argument("--strict", action="store_true", help="把警告也当作错误")
    args = parser.parse_args()

    if not DICT_DIR.is_dir():
        print(f"错误: 未找到词典目录 {DICT_DIR}", file=sys.stderr)
        return 1

    errors: list[str] = []
    warnings: list[str] = []
    cross: dict[str, tuple[str, str]] = {}

    for path in sorted(DICT_DIR.glob("*.json")):
        data = load_json(path)
        name = path.name
        if "entries" in data:
            validate_entries(name, data["entries"], errors, warnings)
            for en, zh in data.get("entries", []):
                if not isinstance(en, str):
                    continue
                if en in cross and cross[en][1] != zh:
                    warnings.append(
                        f"跨文件键冲突: {en!r} 在 {cross[en][0]}={cross[en][1]!r} 与 {name}={zh!r}"
                    )
                else:
                    cross[en] = (name, zh)
        if "patterns" in data:
            validate_patterns(name, data["patterns"], errors)

    for msg in warnings:
        print(f"警告: {msg}")
    for msg in errors:
        print(f"错误: {msg}", file=sys.stderr)

    if errors or (args.strict and warnings):
        print(f"校验失败: {len(errors)} 错误, {len(warnings)} 警告")
        return 1

    print(f"校验通过: {len(list(DICT_DIR.glob('*.json')))} 个词典文件, {len(warnings)} 警告")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
