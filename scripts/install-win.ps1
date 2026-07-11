# Cursor Windows 简体中文一键安装
# 用法: 右键「使用 PowerShell 运行」，或在终端执行:
#   powershell -ExecutionPolicy Bypass -File .\scripts\install-win.ps1
# 自定义安装路径:
#   $env:CURSOR_INSTALL_PATH = "D:\Apps\cursor"
#   .\scripts\install-win.ps1

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$UserData = Join-Path $env:APPDATA "Cursor\User"
$LocaleFile = Join-Path $UserData "locale.json"
$ExtensionsDir = Join-Path $env:USERPROFILE ".cursor\extensions"
$ExtensionId = "MS-CEINTL.vscode-language-pack-zh-hans"
$BackupDir = Join-Path $Root "backups"

Write-Host "==> Cursor Windows 汉化安装"
Write-Host "    项目目录: $Root"

# 检查 Python
$Python = $null
$UsePyLauncher = $false
foreach ($name in @("python", "python3", "py")) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($cmd) {
        if ($name -eq "py") {
            $UsePyLauncher = $true
            $Python = "py"
        } else {
            $Python = $cmd.Source
        }
        break
    }
}
if (-not $Python) {
    Write-Error "未找到 Python 3。请先安装 Python 3 并确保可在 PATH 中调用 python。"
    exit 1
}

function Invoke-Python {
    param([Parameter(Mandatory = $true)][string[]]$PyArgs)
    if ($UsePyLauncher) {
        & py -3 @PyArgs
    } else {
        & $Python @PyArgs
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Python 命令失败: $($PyArgs -join ' ') (exit $LASTEXITCODE)"
    }
}

Write-Host "==> 检测 Cursor 安装目录..."
try {
    if ($UsePyLauncher) {
        $AppRoot = (& py -3 "$Root\scripts\paths.py" --app-root | Select-Object -Last 1).Trim()
    } else {
        $AppRoot = (& $Python "$Root\scripts\paths.py" --app-root | Select-Object -Last 1).Trim()
    }
    if (-not $AppRoot) { throw "empty app root" }
    Write-Host "    找到: $AppRoot"
} catch {
    Write-Error "未找到 Cursor 安装目录。请确认已安装 Cursor，或设置环境变量 CURSOR_INSTALL_PATH 指向安装根目录（含 resources\app）。常见路径: %LOCALAPPDATA%\Programs\cursor"
    exit 1
}

New-Item -ItemType Directory -Force -Path $UserData | Out-Null
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

# 1. 安装 VS Code 简体中文语言包
Write-Host "==> 检查中文语言包..."
$PackExists = Get-ChildItem -Path $ExtensionsDir -Directory -Filter "ms-ceintl.vscode-language-pack-zh-hans-*" -ErrorAction SilentlyContinue
if (-not $PackExists) {
    Write-Host "    正在安装 $ExtensionId ..."
    $cursorCmd = Get-Command cursor -ErrorAction SilentlyContinue
    if ($cursorCmd) {
        try {
            & cursor --install-extension $ExtensionId
        } catch {
            Write-Warning "自动安装语言包失败，请在 Cursor 扩展市场手动安装 Chinese (Simplified) Language Pack。"
        }
    } else {
        Write-Warning "未找到 cursor 命令行工具，请手动在扩展市场安装中文语言包: $ExtensionId"
    }
} else {
    Write-Host "    中文语言包已存在"
}

# 2. 设置显示语言
Write-Host "==> 设置显示语言为 zh-cn"
if (Test-Path $LocaleFile) {
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    Copy-Item $LocaleFile (Join-Path $BackupDir "locale.json.$stamp.bak") -Force
}
@'
{
  "locale": "zh-cn"
}
'@ | Set-Content -Path $LocaleFile -Encoding UTF8
Write-Host "    已写入 $LocaleFile"

# 3. 合并 Cursor 专有翻译（NLS）
Write-Host "==> 合并 Cursor 专有翻译（NLS）..."
Invoke-Python -PyArgs @("$Root\scripts\merge-overlay.py")

# 4. Glass UI 补丁
Write-Host "==> 应用 Glass UI 中文补丁..."
Invoke-Python -PyArgs @("$Root\scripts\patch-glass-ui.py", "--app-root", $AppRoot)

# 5. 提取字符串（维护用，失败不影响安装）
Write-Host "==> 提取当前版本待翻译字符串..."
try {
    Invoke-Python -PyArgs @("$Root\scripts\extract.py", $AppRoot)
} catch {
    Write-Warning "提取字符串失败（可忽略）: $_"
}

Write-Host ""
Write-Host "安装完成！"
Write-Host ""
Write-Host "请完全退出 Cursor（托盘图标右键退出）后重新打开。"
Write-Host "若界面未切换，可在 Cursor 中执行命令: Configure Display Language → 选择 zh-cn"
Write-Host ""
Write-Host "卸载汉化: .\scripts\uninstall-win.ps1"
