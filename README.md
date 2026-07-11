# Cursor macOS 界面汉化方案

为 macOS 版 Cursor 提供界面汉化，覆盖 **设置页**、**Agent 窗口** 以及 Cursor 专有功能文案。

## 原理

Cursor 基于 VS Code，界面文案通过 **NLS（National Language Support）** 系统加载：

| 层级 | 文件/机制 | 说明 |
|------|-----------|------|
| 基础 UI | `ms-ceintl.vscode-language-pack-zh-hans` | 覆盖编辑器、菜单、通用设置等约 95% 界面 |
| Cursor 专有文案 | `data/cursor-overlay.zh-cn.json` | Agent、Composer、MCP、Cursor Settings 等待翻译条目 |
| 语言切换 | `~/Library/Application Support/Cursor/User/locale.json` | 指定显示语言为 `zh-cn` |

汉化流程：

```
提取 Cursor 专有英文字符串 → 翻译为中文 → 合并进中文语言包 → 设置 locale → 重启 Cursor
```

## 两阶段汉化架构

| 阶段 | 机制 | 覆盖范围 |
|------|------|----------|
| **Phase 1** | NLS 语言包合并 | 编辑器、菜单、命令面板、部分 Agent 提示 |
| **Phase 2** | Glass UI JS 补丁 | **Cursor 设置页**、**Agents 窗口侧栏** |

Phase 2 会修改以下文件（自动备份）：
- `Cursor.app/.../workbench.glass.main.js`
- `Cursor.app/.../workbench.desktop.main.js`

```
完整流程：
  安装中文语言包 → 设置 locale → 合并 NLS 翻译 → 打 Glass UI 补丁 → 重启
```

## 快速开始（macOS）

### 1. 安装依赖

- 已安装 [Cursor](https://cursor.com)
- 已安装 VS Code 简体中文语言包（脚本会自动安装）

### 2. 一键安装

```bash
cd "/Users/yangwenying/Documents/Cursor汉化"
chmod +x scripts/*.sh
./scripts/install-mac.sh
```

### 3. 重启 Cursor

完全退出 Cursor（`Cmd+Q`），再重新打开。界面应显示为中文。

### 4. 卸载 / 恢复

```bash
./scripts/uninstall-mac.sh
```

## 目录结构

```
Cursor汉化/
├── README.md
├── scripts/
│   ├── extract.py          # 从 Cursor.app 提取待翻译字符串
│   ├── merge-overlay.py    # 将 Cursor 翻译合并进中文语言包（Phase 1）
│   ├── patch-glass-ui.py   # Glass UI 硬编码文案补丁（Phase 2）
│   ├── install-mac.sh      # macOS 一键安装
│   └── uninstall-mac.sh    # 恢复备份
└── data/
    ├── cursor-strings-to-translate.json  # 提取出的英文字符串清单
    ├── cursor-overlay.zh-cn.json         # Cursor 专有中文翻译（NLS）
    └── glass-ui-replacements.json        # Glass UI 替换映射表
```

## 手动步骤（了解原理）

### 步骤 1：安装中文语言包

在 Cursor 扩展市场搜索并安装 **Chinese (Simplified) Language Pack for Visual Studio Code**（`MS-CEINTL.vscode-language-pack-zh-hans`）。

或使用命令行：

```bash
cursor --install-extension MS-CEINTL.vscode-language-pack-zh-hans
```

### 步骤 2：设置显示语言

创建或编辑：

`~/Library/Application Support/Cursor/User/locale.json`

```json
{
  "locale": "zh-cn"
}
```

也可在 Cursor 中执行命令 **Configure Display Language**，选择 `zh-cn`。

### 步骤 3：合并 Cursor 专有翻译

VS Code 中文包不包含 Cursor 自有的 Agent / Settings 等文案。运行：

```bash
python3 scripts/merge-overlay.py
```

脚本会找到已安装的中文语言包，将 `data/cursor-overlay.zh-cn.json` 中的翻译合并进 `translations/main.i18n.json`（合并前自动备份）。

### 步骤 4：提取新版本的待翻译字符串

Cursor 更新后，可重新提取未翻译条目：

```bash
python3 scripts/extract.py
```

输出到 `data/cursor-strings-to-translate.json`，供翻译后更新 `cursor-overlay.zh-cn.json`。

## 关键路径（macOS）

| 用途 | 路径 |
|------|------|
| Cursor 应用 | `/Applications/Cursor.app` |
| 默认英文文案 | `.../Cursor.app/Contents/Resources/app/out/nls.messages.json` |
| 文案键映射 | `.../Cursor.app/Contents/Resources/app/out/nls.keys.json` |
| 用户配置 | `~/Library/Application Support/Cursor/User/` |
| 语言包扩展 | `~/.cursor/extensions/ms-ceintl.vscode-language-pack-zh-hans-*` |

## 注意事项

1. **Cursor 更新后需重新运行** `./scripts/install-mac.sh`，因为更新会覆盖语言包和 Glass UI bundle。
2. **Phase 2 会修改 Cursor.app 内 JS 文件**（自动备份到 `backups/`），卸载可用 `uninstall-mac.sh` 恢复。
3. 不要直接修改 `nls.messages.json`；通过语言包扩展合并是更安全的方式。
4. 部分极少数硬编码英文（动态生成、第三方插件）可能仍无法覆盖。
5. 本方案仅针对 **macOS**；Windows / Linux 路径不同，但原理相同。

## 参与翻译

编辑 `data/cursor-overlay.zh-cn.json`，格式与 VS Code 语言包一致：

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

保存后重新运行 `./scripts/install-mac.sh` 即可生效。

## 故障排查

| 现象 | 处理 |
|------|------|
| 界面仍是英文 | 确认 `locale.json` 为 `zh-cn`，并已安装中文语言包 |
| 设置页英文、编辑器中文 | 运行 `merge-overlay.py` 合并 Cursor 专有翻译 |
| 合并后无变化 | 完全退出 Cursor 再重启；检查扩展目录下语言包版本 |
| 安装脚本报权限错误 | 对 `Cursor.app` 无需写权限；脚本只修改 `~/.cursor/extensions` 和用户配置 |
