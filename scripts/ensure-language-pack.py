#!/usr/bin/env python3
"""按 Cursor 内嵌 VS Code 版本匹配并安装简体中文语言包。"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from paths import (
    cursor_cli_path,
    cursor_extensions_dir,
    cursor_user_data_dir,
    cursor_vscode_version,
    find_cursor_app_root,
    platform_display_name,
)

ROOT = Path(__file__).resolve().parent.parent
VENDOR_DIR = ROOT / "vendor"
EXTENSION_ID = "MS-CEINTL.vscode-language-pack-zh-hans"
MARKETPLACE_QUERY_URL = (
    "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery"
)
MARKETPLACE_DOWNLOAD = (
    "https://marketplace.visualstudio.com/_apis/public/gallery/publishers/"
    "MS-CEINTL/vsextensions/vscode-language-pack-zh-hans/{version}/vspackage"
)


def log(msg: str = "") -> None:
    print(msg, flush=True)


def major_minor(version: str) -> str | None:
    m = re.match(r"^(\d+)\.(\d+)", version.strip())
    if not m:
        return None
    return f"{m.group(1)}.{m.group(2)}"


def versions_compatible(pack_version: str, vscode_version: str) -> bool:
    a = major_minor(pack_version)
    b = major_minor(vscode_version)
    return bool(a and b and a == b)


def find_installed_pack(extensions_dir: Path) -> Path | None:
    candidates = sorted(
        extensions_dir.glob("ms-ceintl.vscode-language-pack-zh-hans-*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def pack_version_from_dir(pack_dir: Path) -> str | None:
    # 目录名末尾版本，或 package.json
    pkg = pack_dir / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
            ver = data.get("version")
            if isinstance(ver, str):
                return ver
        except json.JSONDecodeError:
            pass
    m = re.search(r"(\d+\.\d+\.\d+(?:\.\d+)?)$", pack_dir.name)
    return m.group(1) if m else None


def read_vsix_version(vsix_path: Path) -> str | None:
    try:
        with zipfile.ZipFile(vsix_path, "r") as zf:
            with zf.open("extension/package.json") as f:
                data = json.loads(f.read().decode("utf-8"))
                ver = data.get("version")
                return ver if isinstance(ver, str) else None
    except (OSError, KeyError, json.JSONDecodeError):
        return None


def query_marketplace_versions() -> list[str]:
    body = {
        "filters": [
            {
                "criteria": [
                    {"filterType": 7, "value": EXTENSION_ID},
                ],
                "pageNumber": 1,
                "pageSize": 1,
            }
        ],
        "flags": 0x200,  # IncludeVersions
    }
    req = urllib.request.Request(
        MARKETPLACE_QUERY_URL + "?api-version=7.1-preview.1",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json;api-version=7.1-preview.1",
            "User-Agent": "cursor-zh-hans",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    versions: list[str] = []
    try:
        results = payload["results"][0]["extensions"][0]["versions"]
        for item in results:
            ver = item.get("version")
            if isinstance(ver, str):
                versions.append(ver)
    except (KeyError, IndexError, TypeError):
        pass
    return versions


def choose_matching_version(vscode_version: str, versions: list[str]) -> str | None:
    prefix = major_minor(vscode_version)
    if not prefix:
        return None
    matched = [v for v in versions if v.startswith(prefix + ".")]
    if not matched:
        return None
    # 版本字符串按点分段比较
    def key(v: str) -> tuple:
        parts = []
        for p in v.split("."):
            try:
                parts.append(int(p))
            except ValueError:
                parts.append(0)
        return tuple(parts)

    return sorted(matched, key=key, reverse=True)[0]


def download_vsix(version: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = MARKETPLACE_DOWNLOAD.format(version=version)
    req = urllib.request.Request(url, headers={"User-Agent": "cursor-zh-hans"})
    log(f"  下载语言包 {version} ...")
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = resp.read()
    # 市场有时返回 gzip 包装
    if data[:2] == b"\x1f\x8b":
        import gzip

        data = gzip.decompress(data)
    dest.write_bytes(data)
    # 校验是否为 zip/vsix
    if not zipfile.is_zipfile(dest):
        dest.unlink(missing_ok=True)
        raise RuntimeError("下载的文件不是有效的 VSIX")
    return dest


def find_bundled_vsix() -> Path | None:
    for path in [
        VENDOR_DIR / "VSCode-language-pack-zh-hans.vsix",
        ROOT / "VSCode-language-pack-zh-hans.vsix",
    ]:
        if path.is_file():
            return path
    return None


def install_vsix(vsix_path: Path, app_root: Path | None) -> bool:
    cli = cursor_cli_path(app_root)
    if not cli:
        log("警告: 未找到 cursor CLI，请手动安装语言包 VSIX")
        log(f"  文件: {vsix_path}")
        return False

    user_data = cursor_user_data_dir()
    cmd = [
        str(cli),
        "--install-extension",
        str(vsix_path),
        "--force",
        f"--user-data-dir={user_data}",
    ]
    log(f"  执行: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180, check=False)
    except OSError as exc:
        log(f"警告: 安装语言包失败: {exc}")
        return False
    out = ((result.stdout or "") + (result.stderr or "")).strip()
    if out:
        log(f"  CLI 输出: {out[:500]}")
    if result.returncode != 0:
        log(f"警告: cursor CLI 返回码 {result.returncode}")
        return False
    return True


def ensure_language_pack(app_root: Path | None = None, force_download: bool = False) -> int:
    try:
        root = app_root or find_cursor_app_root()
    except FileNotFoundError as exc:
        log(f"错误: {exc}")
        return 1

    log(f"平台: {platform_display_name()}")
    vscode_ver = cursor_vscode_version(root)
    log(f"Cursor 内嵌 VS Code 版本: {vscode_ver or '未知'}")

    extensions_dir = cursor_extensions_dir()
    installed = find_installed_pack(extensions_dir)
    if installed and vscode_ver and not force_download:
        pack_ver = pack_version_from_dir(installed)
        log(f"已安装语言包: {installed.name} (version={pack_ver})")
        if pack_ver and versions_compatible(pack_ver, vscode_ver):
            log("语言包版本匹配，跳过下载")
            return 0
        log("语言包版本与 Cursor 不匹配，将尝试下载匹配版本")

    vsix: Path | None = None
    bundled = find_bundled_vsix()
    if bundled and vscode_ver and not force_download:
        bver = read_vsix_version(bundled)
        if bver and versions_compatible(bver, vscode_ver):
            log(f"使用本地匹配 VSIX: {bundled} ({bver})")
            vsix = bundled

    if vsix is None and vscode_ver:
        try:
            versions = query_marketplace_versions()
            target = choose_matching_version(vscode_ver, versions)
            if target:
                dest = VENDOR_DIR / f"vscode-language-pack-zh-hans-{target}.vsix"
                if dest.exists() and read_vsix_version(dest) == target:
                    vsix = dest
                    log(f"使用缓存 VSIX: {dest}")
                else:
                    vsix = download_vsix(target, dest)
            else:
                log(f"警告: 市场未找到与 {vscode_ver} 匹配的语言包版本")
        except (urllib.error.URLError, TimeoutError, RuntimeError, json.JSONDecodeError) as exc:
            log(f"警告: 市场下载失败: {exc}")

    if vsix is None and bundled:
        log(f"回退使用本地 VSIX: {bundled}")
        vsix = bundled

    if vsix is None:
        # 最后尝试让 CLI 从市场直接安装（可能版本不完全匹配）
        cli = cursor_cli_path(root)
        if cli:
            log("尝试通过扩展 ID 在线安装官方语言包...")
            user_data = cursor_user_data_dir()
            cmd = [
                str(cli),
                "--install-extension",
                EXTENSION_ID,
                "--force",
                f"--user-data-dir={user_data}",
            ]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=180, check=False)
                if result.returncode == 0:
                    log("已通过扩展 ID 安装语言包")
                    return 0
            except OSError:
                pass
        log("错误: 无法获取语言包，请手动安装 Chinese (Simplified) Language Pack")
        return 1

    ok = install_vsix(vsix, root)
    if not ok:
        # 安装失败不一定致命：若目录已存在仍可继续后续步骤
        if find_installed_pack(extensions_dir):
            log("警告: CLI 安装可能失败，但检测到已有语言包目录，继续")
            return 0
        return 1

    installed = find_installed_pack(extensions_dir)
    if installed:
        log(f"语言包就绪: {installed.name}")
        return 0
    log("警告: 安装后仍未找到语言包目录，请重启 Cursor 后重试")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Ensure matching zh-hans language pack")
    parser.add_argument("--app-root", default=None)
    parser.add_argument("--force-download", action="store_true")
    args = parser.parse_args()
    app_root = Path(args.app_root) if args.app_root else None
    return ensure_language_pack(app_root, force_download=args.force_download)


if __name__ == "__main__":
    raise SystemExit(main())
