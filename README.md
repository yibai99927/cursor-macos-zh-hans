# Cursor 界面汉化

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-blue.svg)](#快速开始)
[![Language](https://img.shields.io/badge/locale-zh--CN-red.svg)](#)

**中文** | [English](./README.en.md)

为 [Cursor](https://cursor.com) 提供简体中文界面，覆盖编辑器基础 UI、**设置页**、**Agents 窗口**、插件市场与通知等。支持 **Windows** 与 **macOS**。

> 本项目会修改 Cursor 安装目录中的少量文件（`workbench.html`、必要 JS、`product.json` 校验和），并自动备份。Cursor 更新后需重新运行安装。

## 功能特性

- 按 Cursor 内嵌 VS Code 版本**自动匹配**官方简体中文语言包
- Phase 1：合并 NLS 覆盖层，汉化菜单、命令面板等
- Phase 2：结构化静态补丁 + Glass UI 替换，覆盖设置页硬编码文案
- Phase 3：向 `workbench.html` **注入轻量运行时**，用 MutationObserver 兜底动态界面
- 私有扩展翻译桥接；安装后可选守护扩展，升级后提示回补
- 根目录中文一键脚本（Win / Mac 成对提供）

## 快速开始

### Windows（推荐）

**依赖**：已安装 [Cursor](https://cursor.com)、[Python 3](https://www.python.org/downloads/)（勾选 Add to PATH；不要用 Store 占位版）

1. 双击根目录 `启动汉化_Win.bat`
2. 按提示确认；若 Cursor 在 `Program Files`，请**以管理员身份**运行
3. **完全退出** Cursor（含托盘）后重新打开

也可：

```powershell
git clone https://github.com/yibai99927/cursor-zh-hans.git
cd cursor-zh-hans
powershell -ExecutionPolicy Bypass -File .\scripts\install-win.ps1
```

自定义路径：

```powershell
$env:CURSOR_INSTALL_PATH = "D:\Apps\cursor"
powershell -ExecutionPolicy Bypass -File .\scripts\install-win.ps1
```

卸载：双击 `取消汉化_Win.bat`，或运行 `scripts\uninstall-win.ps1`。  
出现安装完整性提示：双击 `修复校验_Win.bat`。

### macOS（推荐）

**依赖**：已安装 [Cursor](https://cursor.com)、Python 3（`brew install python3`）

```bash
git clone https://github.com/yibai99927/cursor-zh-hans.git
cd cursor-zh-hans
chmod +x 启动汉化_Mac.sh 取消汉化_Mac.sh 修复校验_Mac.sh scripts/*.sh
./启动汉化_Mac.sh
```

完成后请 `Cmd+Q` 完全退出再打开。

卸载：`./取消汉化_Mac.sh`  
修复校验：`./修复校验_Mac.sh`

自定义路径：

```bash
export CURSOR_INSTALL_PATH="/Applications/Cursor.app"
./scripts/install-mac.sh
```

## 工作原理

| 层级 | 机制 | 覆盖范围 |
|------|------|----------|
| 语言包 | 版本匹配安装 `zh-hans` + `locale=zh-cn` | VS Code 标准菜单与命令 |
| NLS 覆盖 | `data/cursor-overlay.zh-cn.json` 合并进语言包 | Cursor 专有 NLS 键 |
| 静态补丁 | `structured-patches.json` + `glass-ui-replacements.json` | 设置页对象字面量、硬编码串 |
| 运行时注入 | `workbench.html` + `cursor-zh-runtime.js` | 市场、通知、动态 DOM 文案 |

```
匹配语言包 → locale → 合并 NLS → 私有扩展桥接 → 注入运行时 → 静态补丁 → 同步校验和 → 重启
```

## 目录结构

```
cursor-zh-hans/
├── 启动汉化_Win.bat / 取消汉化_Win.bat / 修复校验_Win.bat
├── 启动汉化_Mac.sh / 取消汉化_Mac.sh / 修复校验_Mac.sh
├── scripts/                 # 安装、注入、补丁、语言包、桥接
├── data/
│   ├── cursor-overlay.zh-cn.json
│   ├── glass-ui-replacements.json
│   ├── structured-patches.json
│   └── runtime-dicts/       # 分场景运行时词典
├── runtime/engine.js        # 轻量运行时模板
└── extension/               # 汉化守护扩展（巡检 / 回补提示）
```

## 参与翻译

1. 运行时文案：编辑 `data/runtime-dicts/*.json`，然后 `python scripts/validate-dicts.py`
2. NLS：编辑 `data/cursor-overlay.zh-cn.json`
3. 静态补丁：优先改 `data/structured-patches.json`；必要时再改 `glass-ui-replacements.json`
4. 重新运行对应平台的安装脚本

Cursor 大版本更新后可提取漏译：

```bash
python scripts/extract.py
```

## 故障排查

| 现象 | 处理 |
|------|------|
| 界面仍是英文 | 确认 `locale.json` 为 `zh-cn`，并已安装匹配版本语言包 |
| 设置页英文、编辑器中文 | 重新运行安装（需完成静态补丁 + 运行时） |
| Windows 权限错误 | Program Files 下用管理员运行 |
| Store 伪 Python | 安装官网 Python，关闭应用执行别名 |
| 安装完整性报错 | 运行 `修复校验_*`；仍不行则卸载汉化后重装 |
| Cursor 升级后失效 | 再跑一次 `启动汉化_*` |

## 注意事项

- 会修改安装目录文件；备份在 `backups/`
- Cursor 更新后需重跑安装
- Agent 对话内容、模型输出、部分在线市场长描述可能无法覆盖
- 本项目与 Cursor / Anysphere 官方无关；第三方说明见 [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md)

## 许可证

本项目采用 [MIT License](./LICENSE) 开源。

```
Copyright (c) 2026 亦白 薛 (yibai99927)
```
