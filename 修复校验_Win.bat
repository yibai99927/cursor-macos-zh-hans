@echo off
chcp 65001 >nul 2>&1
setlocal EnableExtensions
cd /d "%~dp0"
title Cursor zh-CN Repair Checksum

echo ============================================================
echo   Repair Cursor install checksum - Windows
echo ============================================================
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\repair-cursor-win.ps1"
echo.
pause
