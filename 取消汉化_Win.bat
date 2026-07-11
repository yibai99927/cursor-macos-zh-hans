@echo off
chcp 65001 >nul 2>&1
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title Cursor zh-CN Uninstall

echo ============================================================
echo   Remove Cursor Simplified Chinese localization - Windows
echo ============================================================
echo.
set /p ANS=Restore English UI? [Y/N]: 
if /i not "!ANS!"=="Y" if /i not "!ANS!"=="YES" (
  echo Cancelled.
  pause
  exit /b 0
)

powershell -ExecutionPolicy Bypass -File "%~dp0scripts\uninstall-win.ps1"
echo.
pause
