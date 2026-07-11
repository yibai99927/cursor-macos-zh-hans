# Cursor UI Localization (zh-CN)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-blue.svg)](#quick-start)

[中文](./README.md) | **English**

Simplified Chinese UI for [Cursor](https://cursor.com) on **Windows** and **macOS**. Covers editor chrome, Settings, Agents, marketplace labels, and more.

> This project modifies a small set of files under the Cursor install directory (`workbench.html`, some JS bundles, `product.json` checksums) with automatic backups. Re-run after Cursor updates.

## Features

- Auto-match the official `zh-hans` language pack to Cursor’s embedded VS Code version
- NLS overlay merge for Cursor-specific strings
- Structured static patches + Glass UI replacements for hardcoded Settings UI
- Lightweight `workbench.html` runtime injection (MutationObserver fallback)
- Private-extension i18n bridge + optional guard extension after install
- Root-level one-click launchers for Windows and macOS

## Quick start

### Windows

Requires Cursor and [Python 3](https://www.python.org/downloads/) (Add to PATH; avoid Store stub).

Double-click `启动汉化_Win.bat`, or:

```powershell
git clone https://github.com/yibai99927/cursor-zh-hans.git
cd cursor-zh-hans
powershell -ExecutionPolicy Bypass -File .\scripts\install-win.ps1
```

If Cursor is under `Program Files`, run PowerShell **as Administrator**.  
Uninstall: `取消汉化_Win.bat`. Repair checksums: `修复校验_Win.bat`.

### macOS

```bash
git clone https://github.com/yibai99927/cursor-zh-hans.git
cd cursor-zh-hans
chmod +x 启动汉化_Mac.sh 取消汉化_Mac.sh 修复校验_Mac.sh scripts/*.sh
./启动汉化_Mac.sh
```

Fully quit with `Cmd+Q`, then reopen. Uninstall: `./取消汉化_Mac.sh`.

## How it works

1. Match & install language pack → set `locale=zh-cn`
2. Merge NLS overlay → bridge private extensions
3. Inject runtime into `workbench.html`
4. Apply structured / Glass static patches → sync checksums

## License

[MIT License](./LICENSE). Third-party notices: [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md).

Not affiliated with Cursor / Anysphere.
