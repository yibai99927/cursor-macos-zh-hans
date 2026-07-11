const vscode = require("vscode");
const fs = require("fs");
const path = require("path");
const os = require("os");
const { spawn } = require("child_process");

const INJECTION_MARKER = "<!-- CURSOR_ZH_HANS_INJECTION -->";
const RUNTIME_JS = "cursor-zh-runtime.js";

function expandHome(p) {
  if (!p) return p;
  if (p.startsWith("~")) {
    return path.join(os.homedir(), p.slice(1));
  }
  return p;
}

function looksLikeAppRoot(dir) {
  try {
    return fs.existsSync(path.join(dir, "product.json")) && fs.existsSync(path.join(dir, "out"));
  } catch {
    return false;
  }
}

function getCandidateAppRoots(configRoot) {
  const list = [];
  if (configRoot) {
    list.push(expandHome(configRoot));
  }
  const home = os.homedir();
  if (process.platform === "win32") {
    const local = process.env.LOCALAPPDATA || "";
    const pf = process.env.ProgramFiles || "C:\\Program Files";
    if (local) {
      list.push(path.join(local, "Programs", "cursor", "resources", "app"));
      list.push(path.join(local, "Programs", "Cursor", "resources", "app"));
    }
    list.push(path.join(pf, "Cursor", "resources", "app"));
    list.push(path.join(pf, "cursor", "resources", "app"));
  } else if (process.platform === "darwin") {
    list.push("/Applications/Cursor.app/Contents/Resources/app");
    list.push(path.join(home, "Applications", "Cursor.app", "Contents", "Resources", "app"));
  } else {
    list.push("/usr/share/cursor/resources/app");
    list.push("/opt/Cursor/resources/app");
    list.push("/opt/cursor/resources/app");
  }
  return list;
}

function resolveAppRoot(context) {
  const cfg = vscode.workspace.getConfiguration("cursorZhHans");
  const configured = (cfg.get("cursorAppRoot") || "").trim();
  for (const candidate of getCandidateAppRoots(configured)) {
    if (!candidate) continue;
    let p = candidate;
    if (p.endsWith(".app")) {
      p = path.join(p, "Contents", "Resources", "app");
    }
    if (looksLikeAppRoot(p)) {
      return p;
    }
    const nested = path.join(p, "resources", "app");
    if (looksLikeAppRoot(nested)) {
      return nested;
    }
  }
  return null;
}

function workbenchHtmlPath(appRoot) {
  return path.join(appRoot, "out", "vs", "code", "electron-sandbox", "workbench", "workbench.html");
}

function checkStatus(appRoot) {
  const htmlPath = workbenchHtmlPath(appRoot);
  const runtimePath = path.join(path.dirname(htmlPath), RUNTIME_JS);
  let injectionOk = false;
  let runtimeOk = false;
  let htmlExists = fs.existsSync(htmlPath);
  if (htmlExists) {
    try {
      const html = fs.readFileSync(htmlPath, "utf8");
      injectionOk = html.includes(INJECTION_MARKER);
    } catch {
      injectionOk = false;
    }
  }
  runtimeOk = fs.existsSync(runtimePath);

  // 静态补丁粗检：glass 文件是否仍含常见英文导航键值（未补丁时更常见）
  const glassPath = path.join(appRoot, "out", "vs", "workbench", "workbench.glass.main.js");
  let staticLikelyPatched = null;
  if (fs.existsSync(glassPath)) {
    try {
      const sample = fs.readFileSync(glassPath, "utf8");
      // 已汉化时通常能看到「通用」；未汉化时常见 general:"General"
      if (sample.includes("general:\"通用\"") || sample.includes("general:\"General\"")) {
        staticLikelyPatched = sample.includes("general:\"通用\"");
      }
    } catch {
      staticLikelyPatched = null;
    }
  }

  return {
    appRoot,
    htmlExists,
    injectionOk,
    runtimeOk,
    staticLikelyPatched,
  };
}

function findRepoRoot(context) {
  // 扩展可能安装在 ~/.cursor/extensions/...，也可能从开发目录加载
  const candidates = [
    path.resolve(context.extensionPath, ".."),
    path.resolve(context.extensionPath, "..", ".."),
  ];
  for (const c of candidates) {
    if (fs.existsSync(path.join(c, "scripts", "patch-glass-ui.py"))) {
      return c;
    }
  }
  return null;
}

function runPython(scriptPath, args) {
  return new Promise((resolve) => {
    const py = process.platform === "win32" ? "python" : "python3";
    const child = spawn(py, [scriptPath, ...args], { windowsHide: true });
    let out = "";
    let err = "";
    child.stdout.on("data", (d) => {
      out += d.toString();
    });
    child.stderr.on("data", (d) => {
      err += d.toString();
    });
    child.on("close", (code) => {
      resolve({ code, out, err });
    });
    child.on("error", (e) => {
      resolve({ code: 1, out, err: String(e) });
    });
  });
}

async function reapplyStaticPatch(context, appRoot) {
  const repo = findRepoRoot(context);
  if (!repo) {
    vscode.window.showWarningMessage(
      "未找到汉化项目中的 patch-glass-ui.py。请在项目目录重新运行安装脚本（启动汉化_Win.bat / 启动汉化_Mac.sh）。"
    );
    return false;
  }
  const script = path.join(repo, "scripts", "patch-glass-ui.py");
  const result = await runPython(script, ["--app-root", appRoot]);
  if (result.code === 0) {
    vscode.window
      .showInformationMessage("静态补丁已尝试回补。请完全退出并重启 Cursor。", "知道了")
      .then(() => {});
    return true;
  }
  vscode.window.showErrorMessage(
    `静态补丁回补失败（可能无写权限）。请用管理员/有权限的终端重跑安装脚本。\n${result.err || result.out}`
  );
  return false;
}

async function reportStatus(context, silent) {
  const appRoot = resolveAppRoot(context);
  if (!appRoot) {
    if (!silent) {
      vscode.window.showWarningMessage(
        "未找到 Cursor 安装目录。可在设置中填写 cursorZhHans.cursorAppRoot。"
      );
    }
    return null;
  }
  const status = checkStatus(appRoot);
  const parts = [];
  parts.push(`安装目录: ${status.appRoot}`);
  parts.push(`运行时注入: ${status.injectionOk && status.runtimeOk ? "正常" : "缺失"}`);
  if (status.staticLikelyPatched === true) {
    parts.push("静态补丁: 可能已生效");
  } else if (status.staticLikelyPatched === false) {
    parts.push("静态补丁: 可能已丢失");
  } else {
    parts.push("静态补丁: 无法判断");
  }

  if (!silent) {
    vscode.window.showInformationMessage(parts.join(" | "));
  }
  return status;
}

async function autoCheck(context) {
  const cfg = vscode.workspace.getConfiguration("cursorZhHans");
  const status = await reportStatus(context, true);
  if (!status) {
    return;
  }

  if (!status.injectionOk || !status.runtimeOk) {
    const pick = await vscode.window.showWarningMessage(
      "检测到 Cursor 运行时汉化注入可能已丢失（常见于 Cursor 升级后）。请重新运行项目中的安装脚本。",
      "打开说明",
      "忽略"
    );
    if (pick === "打开说明") {
      openGuide(context);
    }
  } else if (status.staticLikelyPatched === false && cfg.get("autoReapplyStaticPatch")) {
    const pick = await vscode.window.showWarningMessage(
      "检测到设置页静态汉化可能已丢失。是否尝试自动回补？",
      "回补",
      "忽略"
    );
    if (pick === "回补") {
      await reapplyStaticPatch(context, status.appRoot);
    }
  }
}

function openGuide(context) {
  const repo = findRepoRoot(context);
  const md = [
    "# 重新安装 Cursor 简体中文汉化",
    "",
    "Cursor 更新后会覆盖安装目录文件，需要重新运行汉化安装：",
    "",
    "## Windows",
    "1. 双击项目根目录 `启动汉化_Win.bat`",
    "2. 或执行 `scripts\\install-win.ps1`",
    "",
    "## macOS",
    "1. 终端执行 `bash 启动汉化_Mac.sh`",
    "2. 或执行 `./scripts/install-mac.sh`",
    "",
    "完成后请完全退出 Cursor 再打开。",
    "",
    repo ? `当前推断的项目目录: ${repo}` : "请打开你克隆的 cursor-zh-hans 仓库目录操作。",
  ].join("\n");
  const doc = vscode.workspace.openTextDocument({ content: md, language: "markdown" });
  doc.then((d) => vscode.window.showTextDocument(d));
}

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
  context.subscriptions.push(
    vscode.commands.registerCommand("cursorZhHans.checkPatchStatus", () => reportStatus(context, false)),
    vscode.commands.registerCommand("cursorZhHans.reapplyStaticPatch", async () => {
      const appRoot = resolveAppRoot(context);
      if (!appRoot) {
        vscode.window.showWarningMessage("未找到 Cursor 安装目录");
        return;
      }
      await reapplyStaticPatch(context, appRoot);
    }),
    vscode.commands.registerCommand("cursorZhHans.openInstallGuide", () => openGuide(context))
  );

  setTimeout(() => {
    autoCheck(context).catch(() => {});
  }, 2500);
}

function deactivate() {}

module.exports = { activate, deactivate };
