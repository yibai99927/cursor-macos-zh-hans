@echo off
REM 修复 Cursor Windows 安装完整性
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0repair-cursor-win.ps1" %*
pause
