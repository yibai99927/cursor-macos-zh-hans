# 修复 Cursor Windows 安装完整性（校验和 / 注入 / 补丁）
# 用法: powershell -ExecutionPolicy Bypass -File .\scripts\repair-cursor-win.ps1

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

Write-Host "==> 修复 Cursor 安装完整性"

$Python = $null
$UsePyLauncher = $false
foreach ($name in @("python", "python3", "py")) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if (-not $cmd) { continue }
    if ($cmd.Source -match '(?i)WindowsApps') { continue }
    if ($name -eq "py") { $UsePyLauncher = $true; $Python = "py" } else { $Python = $cmd.Source }
    break
}
if (-not $Python) {
    Write-Error "未找到 Python 3"
    exit 1
}

function Invoke-Python {
    param([Parameter(Mandatory = $true)][string[]]$PyArgs)
    if ($UsePyLauncher) {
        & py -3 @PyArgs
    } else {
        & $Python @PyArgs
    }
}

Write-Host "==> 仅修复 workbench.html 校验和..."
try {
    Invoke-Python -PyArgs @("$Root\scripts\inject-runtime.py", "--fix-checksum")
} catch {
    Write-Warning "校验和修复失败: $_"
}

Write-Host ""
Write-Host "若仍提示 installation corrupt，可完整恢复后重装汉化:"
Write-Host "  .\scripts\uninstall-win.ps1"
Write-Host "  .\scripts\install-win.ps1"
Write-Host "请完全退出 Cursor 后重新打开。"
