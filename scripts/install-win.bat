@echo off
REM Cursor Windows 汉化一键安装（调用 PowerShell 脚本）
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-win.ps1" %*
pause
