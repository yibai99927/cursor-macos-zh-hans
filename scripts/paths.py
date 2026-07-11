#!/usr/bin/env python3
"""跨平台 Cursor 安装路径与用户数据目录检测。"""

from __future__ import annotations

import os
import platform
import shutil
from pathlib import Path


def is_windows() -> bool:
    return platform.system() == "Windows"


def is_macos() -> bool:
    return platform.system() == "Darwin"


def is_linux() -> bool:
    return platform.system() == "Linux"


def cursor_user_data_dir() -> Path:
    """返回 Cursor 用户配置目录（含 User/ 的父级）。"""
    if is_windows():
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "Cursor"
        return Path.home() / "AppData" / "Roaming" / "Cursor"
    if is_macos():
        return Path.home() / "Library" / "Application Support" / "Cursor"
    # Linux / 其他
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "Cursor"
    return Path.home() / ".config" / "Cursor"


def cursor_locale_file() -> Path:
    return cursor_user_data_dir() / "User" / "locale.json"


def cursor_extensions_dir() -> Path:
    """扩展目录（语言包等）。"""
    # Cursor 在各平台均使用 ~/.cursor/extensions
    return Path.home() / ".cursor" / "extensions"


def _windows_candidate_roots() -> list[Path]:
    local = os.environ.get("LOCALAPPDATA", "")
    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    candidates: list[Path] = []
    if local:
        candidates.extend(
            [
                Path(local) / "Programs" / "cursor",
                Path(local) / "Programs" / "Cursor",
            ]
        )
    candidates.extend(
        [
            Path(program_files) / "Cursor",
            Path(program_files) / "cursor",
            Path(program_files_x86) / "Cursor",
            Path(program_files_x86) / "cursor",
        ]
    )
    # 自定义环境变量覆盖
    custom = os.environ.get("CURSOR_INSTALL_PATH")
    if custom:
        candidates.insert(0, Path(custom))
    return candidates


def _macos_candidate_roots() -> list[Path]:
    candidates = [
        Path("/Applications/Cursor.app/Contents/Resources/app"),
        Path.home() / "Applications" / "Cursor.app" / "Contents" / "Resources" / "app",
    ]
    custom = os.environ.get("CURSOR_INSTALL_PATH")
    if custom:
        p = Path(custom)
        # 允许传入 .app 或 Resources/app
        if p.name.endswith(".app"):
            candidates.insert(0, p / "Contents" / "Resources" / "app")
        else:
            candidates.insert(0, p)
    return candidates


def _linux_candidate_roots() -> list[Path]:
    candidates = [
        Path("/usr/share/cursor/resources/app"),
        Path("/opt/Cursor/resources/app"),
        Path("/opt/cursor/resources/app"),
        Path.home() / ".local" / "share" / "cursor" / "resources" / "app",
    ]
    custom = os.environ.get("CURSOR_INSTALL_PATH")
    if custom:
        candidates.insert(0, Path(custom))
    return candidates


def _looks_like_app_root(path: Path) -> bool:
    """判断是否为 Cursor resources/app 目录。"""
    return (path / "product.json").exists() and (path / "out").is_dir()


def _normalize_to_app_root(path: Path) -> Path | None:
    """将安装根目录或 .app 路径规范化为 resources/app。"""
    if _looks_like_app_root(path):
        return path
    # Windows/Linux: install/resources/app
    candidate = path / "resources" / "app"
    if _looks_like_app_root(candidate):
        return candidate
    # macOS: Cursor.app/Contents/Resources/app
    if path.name.endswith(".app"):
        candidate = path / "Contents" / "Resources" / "app"
        if _looks_like_app_root(candidate):
            return candidate
    # 已指向 Contents/Resources
    candidate = path / "app"
    if _looks_like_app_root(candidate):
        return candidate
    return None


def find_cursor_app_root(explicit: str | Path | None = None) -> Path:
    """定位 Cursor 的 resources/app 目录。

    可通过参数或环境变量 CURSOR_INSTALL_PATH 指定安装位置。
    """
    if explicit:
        normalized = _normalize_to_app_root(Path(explicit))
        if normalized:
            return normalized
        raise FileNotFoundError(f"指定的路径不是有效的 Cursor 安装目录: {explicit}")

    if is_windows():
        candidates = _windows_candidate_roots()
    elif is_macos():
        candidates = _macos_candidate_roots()
    else:
        candidates = _linux_candidate_roots()

    for root in candidates:
        normalized = _normalize_to_app_root(root)
        if normalized:
            return normalized

    # 尝试从 PATH 中的 cursor 可执行文件反推
    exe = shutil.which("cursor") or shutil.which("cursor.cmd")
    if exe:
        exe_path = Path(exe).resolve()
        # Windows: .../cursor/resources/app/bin/cursor.cmd 或 .../cursor/Cursor.exe 旁
        for parent in [exe_path.parent, *exe_path.parents]:
            normalized = _normalize_to_app_root(parent)
            if normalized:
                return normalized
            # 常见布局: install/Cursor.exe 与 install/resources/app
            sibling = parent / "resources" / "app"
            if _looks_like_app_root(sibling):
                return sibling

    platform_hint = {
        "Windows": r"%LOCALAPPDATA%\Programs\cursor 或设置 CURSOR_INSTALL_PATH",
        "Darwin": "/Applications/Cursor.app 或设置 CURSOR_INSTALL_PATH",
        "Linux": "/usr/share/cursor 或设置 CURSOR_INSTALL_PATH",
    }.get(platform.system(), "设置 CURSOR_INSTALL_PATH")
    raise FileNotFoundError(f"未找到 Cursor 安装目录。请确认已安装 Cursor（常见路径: {platform_hint}）")


def platform_display_name() -> str:
    return {"Windows": "Windows", "Darwin": "macOS", "Linux": "Linux"}.get(
        platform.system(), platform.system()
    )


def quit_hint() -> str:
    if is_windows():
        return "请完全退出 Cursor（托盘图标右键退出，或任务管理器结束进程）后重新打开。"
    if is_macos():
        return "请完全退出 Cursor（Cmd+Q）后重新打开。"
    return "请完全退出 Cursor 后重新打开。"


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Print Cursor paths for the current platform")
    parser.add_argument(
        "--app-root",
        action="store_true",
        help="Print Cursor resources/app path",
    )
    parser.add_argument(
        "--user-data",
        action="store_true",
        help="Print Cursor user data directory",
    )
    parser.add_argument(
        "--extensions",
        action="store_true",
        help="Print Cursor extensions directory",
    )
    parser.add_argument(
        "--locale",
        action="store_true",
        help="Print locale.json path",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Print all known paths",
    )
    args = parser.parse_args()

    try:
        if args.all or not any([args.app_root, args.user_data, args.extensions, args.locale]):
            print(f"platform={platform_display_name()}")
            print(f"app_root={find_cursor_app_root()}")
            print(f"user_data={cursor_user_data_dir()}")
            print(f"extensions={cursor_extensions_dir()}")
            print(f"locale={cursor_locale_file()}")
        else:
            if args.app_root:
                print(find_cursor_app_root())
            if args.user_data:
                print(cursor_user_data_dir())
            if args.extensions:
                print(cursor_extensions_dir())
            if args.locale:
                print(cursor_locale_file())
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
