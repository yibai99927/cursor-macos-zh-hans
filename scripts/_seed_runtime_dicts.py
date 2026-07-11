#!/usr/bin/env python3
"""一次性生成 data/runtime-dicts/ 初始词典（可重复运行覆盖）。"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "runtime-dicts"


def main() -> None:
    ext = json.loads((ROOT / "extension" / "translations.json").read_text(encoding="utf-8"))

    # 过短或歧义过大的词不放进精确词典，避免误伤代码/UI
    dangerous = {
        "On",
        "Off",
        "Open",
        "Close",
        "Update",
        "Default",
        "Search",
        "Manage",
        "Free",
        "Pro",
        "Total",
        "Fixed",
        "Tips",
        "Draft",
        "Context",
        "Settings",
        "Chats",
        "Loading",
        "Installing",
        "Enabled",
        "Disabled",
        "Account",
        "Privacy",
        "Network",
        "Beta",
        "Features",
        "Models",
        "Rules",
        "Docs",
        "Chat",
        "Tab",
        "Plugins",
        "Hooks",
        "Indexing",
        "Developer",
        "Worktrees",
    }

    core = {k: v for k, v in ext.items() if k not in dangerous and len(k) >= 3}
    keep_short = {
        "Agents": "Agent",
        "General": "通用",
        "Profile": "个人资料",
        "Appearance": "外观",
        "Automations": "自动化",
        "Repositories": "仓库",
        "Notifications": "通知",
        "Startup": "启动",
        "Marketplace": "市场",
    }
    core.update(keep_short)

    OUT.mkdir(parents=True, exist_ok=True)

    core_doc = {
        "description": "通用界面精确匹配词典（设置侧栏、Agent 窗口等）",
        "updatedAt": "2026-07-11",
        "entries": [[k, core[k]] for k in sorted(core, key=lambda x: (-len(x), x))],
    }
    (OUT / "core.json").write_text(
        json.dumps(core_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    patterns = {
        "description": "动态文案正则替换",
        "updatedAt": "2026-07-11",
        "patterns": [
            {"regex": r"^(\d+) files? indexed$", "flags": "i", "replacement": r"\1 个文件已索引"},
            {"regex": r"^(\d+) files? changed$", "flags": "i", "replacement": r"\1 个文件已更改"},
            {"regex": r"^(\d+) agents?$", "flags": "i", "replacement": r"\1 个 Agent"},
            {"regex": r"^(\d+) chats?$", "flags": "i", "replacement": r"\1 个对话"},
            {
                "regex": r"^Used (\d+)% of included usage$",
                "flags": "i",
                "replacement": r"已使用包含额度的 \1%",
            },
            {"regex": r"^(\d+) remaining$", "flags": "i", "replacement": r"剩余 \1"},
        ],
    }
    (OUT / "patterns.json").write_text(
        json.dumps(patterns, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    marketplace = {
        "description": "插件市场常见界面文案",
        "updatedAt": "2026-07-11",
        "entries": [
            ["Marketplace", "市场"],
            ["Browse Marketplace", "浏览市场"],
            ["Search Marketplace", "搜索市场"],
            ["Install", "安装"],
            ["Installed", "已安装"],
            ["Uninstall", "卸载"],
            ["Disable", "禁用"],
            ["Enable", "启用"],
            ["Extension", "扩展"],
            ["Extensions", "扩展"],
            ["Publisher", "发布者"],
            ["Featured", "精选"],
            ["Popular", "热门"],
            ["Recently Updated", "最近更新"],
            ["No results found", "未找到结果"],
            ["Install Extension", "安装扩展"],
            ["View Extension", "查看扩展"],
            ["More Actions", "更多操作"],
        ],
    }
    (OUT / "marketplace.json").write_text(
        json.dumps(marketplace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    notifications = {
        "description": "通知与推广弹层常见文案",
        "updatedAt": "2026-07-11",
        "entries": [
            ["Dismiss", "关闭"],
            ["Learn more", "了解更多"],
            ["Learn More", "了解更多"],
            ["Try again", "重试"],
            ["Got it", "知道了"],
            ["Don't show again", "不再显示"],
            ["Not now", "暂时不要"],
            ["Maybe later", "稍后再说"],
            ["Upgrade to Pro", "升级到 Pro"],
            ["Upgrade Plan", "升级套餐"],
            ["View Usage", "查看用量"],
            ["New Update Available", "有可用更新"],
            ["Reload to Update", "重新加载以更新"],
            ["Restart to Update", "重启以更新"],
        ],
    }
    (OUT / "notifications.json").write_text(
        json.dumps(notifications, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    fragments = {
        "description": "部分匹配片段（仅用于叶子节点整段文本的包含替换，慎用短词）",
        "updatedAt": "2026-07-11",
        "entries": [
            ["Open Agents Window", "打开 Agents 窗口"],
            ["Agents Window", "Agents 窗口"],
            ["Cloud Agents", "云端 Agent"],
            ["VS Code Settings", "VS Code 设置"],
            ["Plan & Usage", "套餐与用量"],
            ["Browser & Network", "浏览器与网络"],
            ["Git & PRs", "Git 与 PR"],
            ["Indexing & Docs", "索引与文档"],
            ["Tools & MCPs", "工具与 MCP"],
            ["Self-driving PRs", "自动驾驶 PR"],
        ],
    }
    (OUT / "fragments.json").write_text(
        json.dumps(fragments, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"core entries: {len(core_doc['entries'])}")
    print(f"written to {OUT}")


if __name__ == "__main__":
    main()
