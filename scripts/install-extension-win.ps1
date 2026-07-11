# 安装 Cursor Glass UI 中文扩展（运行时汉化，不修改安装目录）
# 用法: powershell -ExecutionPolicy Bypass -File .\scripts\install-extension-win.ps1

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$ExtSrc = Join-Path $Root "extension"
$ExtDest = Join-Path $env:USERPROFILE ".cursor\extensions\cursor-zh-local.cursor-glass-i18n-0.2.0"

if (-not (Test-Path (Join-Path $ExtSrc "package.json"))) {
    Write-Error "未找到扩展目录 $ExtSrc"
    exit 1
}

Write-Host "==> 安装 Glass UI 中文扩展"
if (Test-Path $ExtDest) {
    Remove-Item -Recurse -Force $ExtDest
}
New-Item -ItemType Directory -Force -Path (Split-Path $ExtDest) | Out-Null
Copy-Item -Recurse $ExtSrc $ExtDest
Write-Host "    已安装到 $ExtDest"
Write-Host "    提示: 请重新加载 Cursor 窗口或完全退出后重新打开使扩展生效"
