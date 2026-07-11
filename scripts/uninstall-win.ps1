# Cursor Windows 汉化卸载 / 恢复
# 用法: powershell -ExecutionPolicy Bypass -File .\scripts\uninstall-win.ps1

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$UserData = Join-Path $env:APPDATA "Cursor\User"
$LocaleFile = Join-Path $UserData "locale.json"
$BackupDir = Join-Path $Root "backups"
$ExtensionsDir = Join-Path $env:USERPROFILE ".cursor\extensions"

Write-Host "==> Cursor Windows 汉化卸载"

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

# 1. 移除运行时注入
Write-Host "==> 移除 workbench 运行时注入..."
try {
    Invoke-Python -PyArgs @("$Root\scripts\inject-runtime.py", "--restore")
} catch {
    Write-Warning "运行时恢复失败: $_"
}

# 2. 恢复 Glass UI / product.json
Write-Host "==> 恢复 Cursor 安装目录原始 JS..."
try {
    Invoke-Python -PyArgs @("$Root\scripts\patch-glass-ui.py", "--restore")
} catch {
    Write-Warning "Glass UI 恢复失败: $_"
}

# 移除旧版实验扩展（若存在）
Get-ChildItem -Path $ExtensionsDir -Directory -Filter "cursor-zh-local.cursor-glass-i18n-*" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item -Recurse -Force $_.FullName
    Write-Host "    已移除扩展: $($_.Name)"
}
Get-ChildItem -Path $ExtensionsDir -Directory -Filter "cursor-zh-local.cursor-zh-hans-guard-*" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item -Recurse -Force $_.FullName
    Write-Host "    已移除守护扩展: $($_.Name)"
}

# 恢复 locale.json
$localeBackups = @(Get-ChildItem -Path $BackupDir -Filter "locale.json.*.bak" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending)
if ($localeBackups.Count -gt 0) {
    Copy-Item $localeBackups[0].FullName $LocaleFile -Force
    Write-Host "    已恢复 locale.json <- $($localeBackups[0].Name)"
} elseif (Test-Path $LocaleFile) {
    Remove-Item $LocaleFile -Force
    Write-Host "    已删除 locale.json"
} else {
    Write-Host "    未找到 locale.json，跳过"
}

# 恢复语言包 main.i18n.json
$mainBackups = @(Get-ChildItem -Path $BackupDir -Filter "main.i18n.json.*.bak" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending)
if ($mainBackups.Count -gt 0) {
    $packDirs = @(Get-ChildItem -Path $ExtensionsDir -Directory -Filter "ms-ceintl.vscode-language-pack-zh-hans-*" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending)
    if ($packDirs.Count -gt 0) {
        $dest = Join-Path $packDirs[0].FullName "translations\main.i18n.json"
        Copy-Item $mainBackups[0].FullName $dest -Force
        Write-Host "    已恢复语言包 <- $($mainBackups[0].Name)"
    } else {
        Write-Warning "未找到中文语言包目录，请手动恢复备份"
    }
} else {
    Write-Host "    未找到语言包备份，跳过"
}

Write-Host ""
Write-Host "卸载完成。请完全退出 Cursor 后重新打开。"
