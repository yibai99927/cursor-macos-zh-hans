# 安装守护扩展到 %USERPROFILE%\.cursor\extensions
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Src = Join-Path $Root "extension"
$DestDir = Join-Path $env:USERPROFILE ".cursor\extensions"
$Name = "cursor-zh-local.cursor-zh-hans-guard-0.3.0"
$Dest = Join-Path $DestDir $Name

New-Item -ItemType Directory -Force -Path $DestDir | Out-Null
if (Test-Path $Dest) { Remove-Item -Recurse -Force $Dest }
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
Copy-Item (Join-Path $Src "package.json") $Dest
Copy-Item (Join-Path $Src "extension.js") $Dest
if (Test-Path (Join-Path $Src "translations.json")) {
    Copy-Item (Join-Path $Src "translations.json") $Dest
}
Write-Host "已安装守护扩展: $Dest"
Write-Host "请重新加载 Cursor 窗口或完全重启。"
