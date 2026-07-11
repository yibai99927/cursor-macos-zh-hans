# 修复因 JS 补丁导致的 Cursor Windows 安装完整性问题
# 用法: powershell -ExecutionPolicy Bypass -File .\scripts\repair-cursor-win.ps1

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

Write-Host "==> 修复 Cursor 安装完整性"
Write-Host "    恢复安装目录内被修改的 workbench 文件..."

$Python = $null
$UsePyLauncher = $false
foreach ($name in @("python", "python3", "py")) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($cmd) {
        if ($name -eq "py") { $UsePyLauncher = $true; $Python = "py" } else { $Python = $cmd.Source }
        break
    }
}
if (-not $Python) {
    Write-Error "未找到 Python 3"
    exit 1
}

$exitCode = 0
if ($UsePyLauncher) {
    & py -3 "$Root\scripts\patch-glass-ui.py" --restore
    $exitCode = $LASTEXITCODE
} else {
    & $Python "$Root\scripts\patch-glass-ui.py" --restore
    $exitCode = $LASTEXITCODE
}

if ($exitCode -ne 0) {
    Write-Warning "自动恢复失败，请从 https://cursor.com 重新下载安装 Cursor"
    exit 1
}

Write-Host ""
Write-Host "已恢复原始 JS 文件。"
Write-Host "请完全退出 Cursor 后重新打开。"
Write-Host "若仍提示安装错误，请从 https://cursor.com 重新安装 Cursor。"
