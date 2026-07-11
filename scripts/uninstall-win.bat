@echo off
REM Cursor Windows 汉化卸载
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0uninstall-win.ps1" %*
pause
