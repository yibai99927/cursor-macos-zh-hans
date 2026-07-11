#!/usr/bin/env python3
"""双平台安装链路一致性自检（不实际改文件）。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_ROOT_LAUNCHERS = [
    "启动汉化_Win.bat",
    "取消汉化_Win.bat",
    "修复校验_Win.bat",
    "启动汉化_Mac.sh",
    "取消汉化_Mac.sh",
    "修复校验_Mac.sh",
]

REQUIRED_SCRIPTS = [
    "paths.py",
    "ensure-language-pack.py",
    "merge-overlay.py",
    "bridge-private-extensions.py",
    "inject-runtime.py",
    "patch-glass-ui.py",
    "validate-dicts.py",
    "extract.py",
    "install-win.ps1",
    "install-mac.sh",
    "uninstall-win.ps1",
    "uninstall-mac.sh",
    "repair-cursor-win.ps1",
    "repair-cursor.sh",
]

# 两边安装脚本都应出现的关键步骤关键词
INSTALL_STEP_MARKERS = [
    "ensure-language-pack",
    "merge-overlay",
    "bridge-private-extensions",
    "inject-runtime",
    "patch-glass-ui",
]


def main() -> int:
    errors: list[str] = []

    for name in REQUIRED_ROOT_LAUNCHERS:
        if not (ROOT / name).exists():
            errors.append(f"缺少根目录入口: {name}")

    for name in REQUIRED_SCRIPTS:
        if not (ROOT / "scripts" / name).exists():
            errors.append(f"缺少脚本: scripts/{name}")

    for name in ("core.json", "patterns.json", "marketplace.json", "notifications.json", "fragments.json"):
        if not (ROOT / "data" / "runtime-dicts" / name).exists():
            errors.append(f"缺少词典: data/runtime-dicts/{name}")

    if not (ROOT / "data" / "structured-patches.json").exists():
        errors.append("缺少 data/structured-patches.json")
    if not (ROOT / "runtime" / "engine.js").exists():
        errors.append("缺少 runtime/engine.js")
    if not (ROOT / "THIRD_PARTY_NOTICES.md").exists():
        errors.append("缺少 THIRD_PARTY_NOTICES.md")

    win = (ROOT / "scripts" / "install-win.ps1").read_text(encoding="utf-8")
    mac = (ROOT / "scripts" / "install-mac.sh").read_text(encoding="utf-8")
    for marker in INSTALL_STEP_MARKERS:
        if marker not in win:
            errors.append(f"install-win.ps1 缺少步骤: {marker}")
        if marker not in mac:
            errors.append(f"install-mac.sh 缺少步骤: {marker}")

    # 卸载应同时恢复注入与静态补丁
    for path in (ROOT / "scripts" / "uninstall-win.ps1", ROOT / "scripts" / "uninstall-mac.sh"):
        text = path.read_text(encoding="utf-8")
        if "inject-runtime" not in text:
            errors.append(f"{path.name} 未调用 inject-runtime --restore")
        if "patch-glass-ui" not in text:
            errors.append(f"{path.name} 未调用 patch-glass-ui --restore")

    if errors:
        print("双平台一致性检查失败:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("双平台一致性检查通过:")
    print(f"  根目录入口: {len(REQUIRED_ROOT_LAUNCHERS)}")
    print(f"  核心脚本: {len(REQUIRED_SCRIPTS)}")
    print("  Win/Mac 安装步骤标记对齐")
    print("  Win/Mac 卸载均恢复 runtime + glass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
