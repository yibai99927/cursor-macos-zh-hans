# Third Party Notices

本仓库为社区维护的 Cursor 简体中文界面方案，与 Cursor、Anysphere、Microsoft、Visual Studio Code 官方无关。

## 本项目原创代码与数据

- 安装/卸载/修复脚本、`scripts/*.py`、`runtime/engine.js`、词典与补丁表、文档等
- License: MIT（见 [LICENSE](./LICENSE)）

## Microsoft VS Code 简体中文语言包

安装流程可能下载或安装 `MS-CEINTL.vscode-language-pack-zh-hans`。该扩展版权归 Microsoft，按其上游 MIT / Marketplace 条款使用。本仓库不捆绑微软语言包源码；`vendor/` 下的 VSIX 缓存（若存在）仅作本地安装缓存，不作为本项目原创内容宣称。

## 思路致谢（未直接复制其代码）

以下项目的公开方案对本仓库架构有参考价值。除注明外，本仓库实现为独立重写：

| 项目 | 许可 | 参考点 |
|------|------|--------|
| [YeYu-Wang/cursor-zh-hans-language-pack](https://github.com/YeYu-Wang/cursor-zh-hans-language-pack) | MIT | 对象字面量 key 锚定的结构化补丁、启动巡检/回补思路 |
| [vibepm666/cursor-localization-zh](https://github.com/vibepm666/cursor-localization-zh) | 未声明明确许可证 | `workbench.html` 注入、语言包版本匹配、分场景词典、中文一键入口等产品思路（**未复制其代码/词典**） |
| [lz123xiansheng/cursor-zh](https://github.com/lz123xiansheng/cursor-zh) | CC BY-NC-SA 4.0 | 轻量 MutationObserver 运行时思路（**未复制其代码/词典**；因其 NC-SA 条款与本仓库 MIT 不兼容） |
| [isdoge/cursor-chinese](https://github.com/isdoge/cursor-chinese) | MIT | DOM 属性翻译、词典分层等运行时技巧（官网 userscript，非本仓库产品范围） |

## 商标

Cursor、Visual Studio Code 等名称仅用于说明兼容目标与上游来源。
