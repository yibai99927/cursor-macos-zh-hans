# Cursor UI Chinese Localization

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-blue.svg)](#quick-start)
[![Language](https://img.shields.io/badge/locale-zh--CN-red.svg)](#)

[中文](./README.md) | **English**

Simplified Chinese localization for [Cursor](https://cursor.com), covering the editor UI, **Settings**, the **Agents** window, and Cursor-specific copy. Supports **macOS** and **Windows**.

> This project patches files inside your Cursor install (with automatic backups). Re-run the installer after every Cursor update.

## Features

- **Phase 1** — Merge an NLS overlay into the VS Code Chinese language pack (~95% of the UI)
- **Phase 2** — Patch Glass UI bundles for hardcoded Settings / Agents strings
- Syncs `product.json` checksums to reduce “Installation has been modified on disk” warnings
- One-click install / uninstall / repair scripts for macOS and Windows

## Quick Start

### Windows

**Requirements:** [Cursor](https://cursor.com), [Python 3](https://www.python.org/downloads/) (check “Add to PATH”)

```powershell
git clone https://github.com/yibai99927/cursor-zh-hans.git
cd cursor-zh-hans
powershell -ExecutionPolicy Bypass -File .\scripts\install-win.ps1
```

You can also double-click `scripts\install-win.bat`.

If Cursor is installed under `C:\Program Files\Cursor`, run PowerShell **as Administrator**.  
Custom install path:

```powershell
$env:CURSOR_INSTALL_PATH = "D:\Apps\cursor"
powershell -ExecutionPolicy Bypass -File .\scripts\install-win.ps1
```

Fully quit Cursor (including the tray icon), then reopen it.

Uninstall:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\uninstall-win.ps1
```

### macOS

**Requirements:** [Cursor](https://cursor.com)

```bash
git clone https://github.com/yibai99927/cursor-zh-hans.git
cd cursor-zh-hans
chmod +x scripts/*.sh
./scripts/install-mac.sh
```

Fully quit Cursor (`Cmd+Q`), then reopen it.

Uninstall:

```bash
./scripts/uninstall-mac.sh
```

## How It Works

Cursor is based on VS Code. Most strings load through NLS; some Cursor-only UI is hardcoded in JS bundles.

| Phase | Mechanism | Coverage |
|------|-----------|----------|
| Phase 1 | Merge `data/cursor-overlay.zh-cn.json` into the zh-hans language pack | Editor, menus, command palette, some Agent prompts |
| Phase 2 | Patch `workbench.*.js` and update `product.json` checksums | Settings page, Agents sidebar, etc. |

```
Install language pack → set locale=zh-cn → merge NLS → patch Glass UI → restart
```

If you see an installation integrity warning:

| Platform | Repair command |
|----------|----------------|
| Windows | `.\scripts\repair-cursor-win.ps1` |
| macOS | `./scripts/repair-cursor.sh` |

## Repository Layout

```
cursor-zh-hans/
├── README.md / README.en.md
├── LICENSE
├── scripts/          # installers, patchers, extractors, path detection
├── data/             # NLS overlay + Glass UI replacement maps
└── extension/        # optional runtime extension (experimental)
```

| Script | Purpose |
|--------|---------|
| `paths.py` | Cross-platform path detection |
| `merge-overlay.py` | Phase 1 NLS merge |
| `patch-glass-ui.py` | Phase 2 Glass UI patch / restore |
| `extract.py` | Extract untranslated strings from an install |
| `install-win.ps1` / `install-mac.sh` | One-click install |
| `uninstall-*.ps1` / `uninstall-mac.sh` | Restore backups |

## Key Paths

<details>
<summary>Windows</summary>

| Purpose | Path |
|---------|------|
| Common install dirs | `%LOCALAPPDATA%\Programs\cursor` or `C:\Program Files\Cursor` |
| App resources | `...\resources\app` |
| User data | `%APPDATA%\Cursor\User\` |
| Language pack | `%USERPROFILE%\.cursor\extensions\ms-ceintl.vscode-language-pack-zh-hans-*` |
| Override | `CURSOR_INSTALL_PATH` |

</details>

<details>
<summary>macOS</summary>

| Purpose | Path |
|---------|------|
| App | `/Applications/Cursor.app` |
| App resources | `.../Contents/Resources/app` |
| User data | `~/Library/Application Support/Cursor/User/` |
| Language pack | `~/.cursor/extensions/ms-ceintl.vscode-language-pack-zh-hans-*` |

</details>

Detect paths on the current machine:

```bash
python3 scripts/paths.py --all
```

## Contributing Translations

1. Edit `data/cursor-overlay.zh-cn.json` (NLS) and/or `data/glass-ui-replacements.json` (Glass UI)
2. Re-run the installer for your platform

NLS example:

```json
{
  "version": "1.0.0",
  "contents": {
    "vs/workbench/browser/parts/titlebar/titlebarPart": {
      "cursorSettings": "Cursor 设置",
      "titlebarOpenCursorSettings": "打开 Cursor 设置"
    }
  }
}
```

After a major Cursor update, extract fresh strings first:

```bash
python3 scripts/extract.py
```

## Troubleshooting

| Symptom | What to try |
|---------|-------------|
| UI still English | Ensure `locale.json` is `zh-cn` and the Chinese language pack is installed |
| Settings English, editor Chinese | Re-run the installer (Phase 2 required) |
| Windows permission errors | Use an elevated PowerShell for Program Files installs |
| Cursor not found | Set `CURSOR_INSTALL_PATH`, or run `paths.py --all` |
| Integrity warning | Run the platform `repair-cursor` script |

## Notes

- Re-run the installer after every Cursor update
- Phase 2 modifies JS under the install directory (backups go to `backups/`)
- Dynamically generated or third-party extension strings may remain English
- Unofficial community project; not affiliated with Cursor / Anysphere

## License

Released under the [MIT License](./LICENSE).

```
Copyright (c) 2026 亦白 薛 (yibai99927)
```
