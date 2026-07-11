# Cursor 界面汉化

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-blue.svg)](#快速开始)
[![Language](https://img.shields.io/badge/locale-zh--CN-red.svg)](#)

**中文** | [English](./README.en.md)

为 [Cursor](https://cursor.com) 提供简体中文界面，覆盖编辑器基础 UI、**设置页**、**Agents 窗口** 以及 Cursor 专有功能文案。支持 **macOS** 与 **Windows**。

> 本项目会修改 Cursor 安装目录中的部分文件（自动备份）。Cursor 更新后需重新安装汉化。

## 功能特性

- Phase 1：合并 NLS 中文语言包，覆盖菜单、命令面板、编辑器等约 95% 界面
- Phase 2：Glass UI 补丁，汉化 Cursor 设置页与 Agents 窗口硬编码文案
- 自动同步 `product.json` 校验和，降低「Installation has been modified on disk」提示
- 一键安装 / 卸载 / 修复脚本（macOS Shell、Windows PowerShell）

## 快速开始

### Windows

**依赖**：已安装 [Cursor](https://cursor.com)、[Python 3](https://www.python.org/downloads/)（勾选 Add to PATH）

```powershell
git clone https://github.com/yibai99927/cursor-zh-hans.git
cd cursor-zh-hans
powershell -ExecutionPolicy Bypass -File .\scripts\install-win.ps1
```

也可双击 `scripts\install-win.bat`。

若 Cursor 位于 `C:\Program Files\Cursor`，请**以管理员身份**运行 PowerShell。  
自定义安装路径：

```powershell
$env:CURSOR_INSTALL_PATH = "D:\Apps\cursor"
powershell -ExecutionPolicy Bypass -File .\scripts\install-win.ps1
```

完成后请**完全退出** Cursor（含托盘图标）再重新打开。

卸载：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\uninstall-win.ps1
```

### macOS

**依赖**：已安装 [Cursor](https://cursor.com)

```bash
git clone https://github.com/yibai99927/cursor-zh-hans.git
cd cursor-zh-hans
chmod +x scripts/*.sh
./scripts/install-mac.sh
```

完成后请完全退出 Cursor（`Cmd+Q`）再重新打开。

卸载：

```bash
./scripts/uninstall-mac.sh
```

## 工作原理

Cursor 基于 VS Code，界面文案通过 NLS 加载；专有界面另有硬编码字符串。

| 阶段 | 机制 | 覆盖范围 |
|------|------|----------|
| Phase 1 | 合并 `data/cursor-overlay.zh-cn.json` 到中文语言包 | 编辑器、菜单、命令面板、部分 Agent 提示 |
| Phase 2 | 修补 `workbench.*.js` 并更新 `product.json` 校验和 | 设置页、Agents 窗口侧栏等 |

```
安装中文语言包 → 设置 locale=zh-cn → 合并 NLS → Glass UI 补丁 → 重启
```

出现安装完整性提示时：

| 平台 | 修复命令 |
|------|----------|
| Windows | `.\scripts\repair-cursor-win.ps1` |
| macOS | `./scripts/repair-cursor.sh` |

## 目录结构

```
cursor-zh-hans/
├── README.md / README.en.md
├── LICENSE
├── scripts/          # 安装、补丁、提取、路径检测
├── data/             # NLS 翻译与 Glass UI 替换表
└── extension/        # 可选运行时扩展（实验，效果有限）
```

主要脚本：

| 脚本 | 说明 |
|------|------|
| `paths.py` | 跨平台路径检测 |
| `merge-overlay.py` | Phase 1：合并 NLS 翻译 |
| `patch-glass-ui.py` | Phase 2：Glass UI 补丁 / 恢复 |
| `extract.py` | 从安装目录提取待翻译字符串 |
| `install-win.ps1` / `install-mac.sh` | 一键安装 |
| `uninstall-*.ps1` / `uninstall-mac.sh` | 卸载恢复 |

## 关键路径

<details>
<summary>Windows</summary>

| 用途 | 路径 |
|------|------|
| 常见安装目录 | `%LOCALAPPDATA%\Programs\cursor` 或 `C:\Program Files\Cursor` |
| 资源根目录 | `...\resources\app` |
| 用户配置 | `%APPDATA%\Cursor\User\` |
| 语言包 | `%USERPROFILE%\.cursor\extensions\ms-ceintl.vscode-language-pack-zh-hans-*` |
| 自定义路径 | 环境变量 `CURSOR_INSTALL_PATH` |

</details>

<details>
<summary>macOS</summary>

| 用途 | 路径 |
|------|------|
| 应用 | `/Applications/Cursor.app` |
| 资源根目录 | `.../Contents/Resources/app` |
| 用户配置 | `~/Library/Application Support/Cursor/User/` |
| 语言包 | `~/.cursor/extensions/ms-ceintl.vscode-language-pack-zh-hans-*` |

</details>

查看当前检测到的路径：

```bash
python3 scripts/paths.py --all
```

## 参与翻译

1. 编辑 `data/cursor-overlay.zh-cn.json`（NLS）或 `data/glass-ui-replacements.json`（Glass UI）
2. 重新运行对应平台的安装脚本

NLS 示例：

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

Cursor 大版本更新后，可先提取再补译：

```bash
python3 scripts/extract.py
```

## 故障排查

| 现象 | 处理 |
|------|------|
| 界面仍是英文 | 确认 `locale.json` 为 `zh-cn`，并已安装中文语言包 |
| 设置页英文、编辑器中文 | 重新运行安装脚本（需完成 Phase 2） |
| Windows 权限错误 | 对 `Program Files` 安装使用管理员 PowerShell |
| 找不到 Cursor | 设置 `CURSOR_INSTALL_PATH`，或运行 `paths.py --all` |
| 安装完整性报错 | 运行对应平台的 `repair-cursor` 脚本 |

## 注意事项

- Cursor 更新后需重新运行安装脚本
- Phase 2 会修改安装目录内 JS（备份在 `backups/`）
- 动态生成或第三方扩展文案可能无法覆盖
- 本项目与 Cursor / Anysphere 官方无关，为社区维护方案

## 许可证

本项目采用 [MIT License](./LICENSE) 开源。

```
Copyright (c) 2026 亦白 薛 (yibai99927)
```
