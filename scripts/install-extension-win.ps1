# 安装守护扩展到 %USERPROFILE%\.cursor\extensions，并捆绑回补所需脚本与数据
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Src = Join-Path $Root "extension"
$DestDir = Join-Path $env:USERPROFILE ".cursor\extensions"
$Name = "cursor-zh-local.cursor-zh-hans-guard-0.4.0"
$Dest = Join-Path $DestDir $Name
$Bundled = Join-Path $Dest "bundled"

New-Item -ItemType Directory -Force -Path $DestDir | Out-Null
if (Test-Path $Dest) { Remove-Item -Recurse -Force $Dest }
New-Item -ItemType Directory -Force -Path $Dest, (Join-Path $Bundled "scripts"), (Join-Path $Bundled "data\runtime-dicts"), (Join-Path $Bundled "runtime") | Out-Null

Copy-Item (Join-Path $Src "package.json") $Dest
Copy-Item (Join-Path $Src "extension.js") $Dest
if (Test-Path (Join-Path $Src "translations.json")) {
    Copy-Item (Join-Path $Src "translations.json") $Dest
}

Copy-Item (Join-Path $Root "scripts\patch-glass-ui.py") (Join-Path $Bundled "scripts")
Copy-Item (Join-Path $Root "scripts\inject-runtime.py") (Join-Path $Bundled "scripts")
Copy-Item (Join-Path $Root "scripts\paths.py") (Join-Path $Bundled "scripts")
Copy-Item (Join-Path $Root "data\glass-ui-replacements.json") (Join-Path $Bundled "data")
Copy-Item (Join-Path $Root "data\structured-patches.json") (Join-Path $Bundled "data")
Copy-Item (Join-Path $Root "data\runtime-dicts\*.json") (Join-Path $Bundled "data\runtime-dicts")
Copy-Item (Join-Path $Root "runtime\engine.js") (Join-Path $Bundled "runtime")

@{
    bundledAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    sourceRepo = $Root
} | ConvertTo-Json | Set-Content -Path (Join-Path $Bundled "manifest.json") -Encoding UTF8

Write-Host "已安装守护扩展: $Dest"
Write-Host "已捆绑回补资源: $Bundled"
Write-Host "请重新加载 Cursor 窗口或完全重启。"
