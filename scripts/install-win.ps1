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
$BackupDir = Join-Path $Root "backups"

Write-Host "==> Cursor Windows 汉化安装"
Write-Host "    项目目录: $Root"

# 检查 Python（排除 Windows Store 占位）
$Python = $null
$UsePyLauncher = $false
foreach ($name in @("python", "python3", "py")) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if (-not $cmd) { continue }
    $src = $cmd.Source
    if ($src -match '(?i)WindowsApps') {
        Write-Host "    跳过 Store 占位: $src" -ForegroundColor Yellow
        continue
    }
    if ($name -eq "py") {
        $UsePyLauncher = $true
        $Python = "py"
    } else {
        $Python = $src
    }
    break
}
if (-not $Python) {
    Write-Error "未找到可用的 Python 3。请从 https://www.python.org/downloads/ 安装，并勾选 Add python.exe to PATH。不要使用 Microsoft Store 占位版。"
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
    Write-Error "未找到 Cursor 安装目录。请确认已安装 Cursor，或设置环境变量 CURSOR_INSTALL_PATH / CURSOR_INSTALL_DIR。"
    exit 1
}

if ($AppRoot -match '(?i)Program Files') {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Host ""
        Write-Host "错误: Cursor 安装在 Program Files，当前 PowerShell 不是管理员。" -ForegroundColor Red
        Write-Host "请右键「以管理员身份运行」PowerShell，然后重新执行:" -ForegroundColor Yellow
        Write-Host "  cd `"$Root`""
        Write-Host "  powershell -ExecutionPolicy Bypass -File .\scripts\install-win.ps1"
        exit 1
    }
    Write-Host "    已检测到管理员权限（Program Files 可写）"
}

New-Item -ItemType Directory -Force -Path $UserData | Out-Null
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

# 1. 按版本匹配安装语言包
Write-Host "==> 确保中文语言包版本匹配..."
Invoke-Python -PyArgs @("$Root\scripts\ensure-language-pack.py", "--app-root", $AppRoot)

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

# 3. 合并 NLS overlay
Write-Host "==> 合并 Cursor 专有翻译（NLS）..."
Invoke-Python -PyArgs @("$Root\scripts\merge-overlay.py")

# 4. 私有扩展桥接
Write-Host "==> 桥接私有扩展翻译..."
try {
    Invoke-Python -PyArgs @("$Root\scripts\bridge-private-extensions.py")
} catch {
    Write-Warning "私有扩展桥接失败（可忽略）: $_"
}

# 5. 运行时注入
Write-Host "==> 注入 workbench 运行时翻译..."
Invoke-Python -PyArgs @("$Root\scripts\inject-runtime.py", "--app-root", $AppRoot)

# 6. Glass UI / 结构化静态补丁
Write-Host "==> 应用 Glass UI / 结构化静态补丁..."
Invoke-Python -PyArgs @("$Root\scripts\patch-glass-ui.py", "--app-root", $AppRoot)

# 7. 安装守护扩展（可选，失败不影响主流程）
Write-Host "==> 安装汉化守护扩展..."
try {
    & powershell -ExecutionPolicy Bypass -File "$Root\scripts\install-extension-win.ps1"
} catch {
    Write-Warning "守护扩展安装失败（可忽略）: $_"
}

# 8. 提取字符串（维护用）
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
Write-Host "卸载汉化: .\scripts\uninstall-win.ps1  或  双击 取消汉化_Win.bat"
