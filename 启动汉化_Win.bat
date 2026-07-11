@echo off
chcp 65001 >nul 2>&1
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title Cursor zh-CN Install

echo ============================================================
echo   Cursor Simplified Chinese Installer for Windows
echo   language pack + runtime inject + static patches
echo ============================================================
echo.

where python >nul 2>&1
if errorlevel 1 (
  where py >nul 2>&1
  if errorlevel 1 (
    echo [ERROR] Python 3 not found. Install from python.org and check Add to PATH.
    echo         https://www.python.org/downloads/
    pause
    exit /b 1
  )
)

echo This will modify a few files under the Cursor install dir. Backups are created.
set /p ANS=Continue? [Y/N]: 
if /i not "!ANS!"=="Y" if /i not "!ANS!"=="YES" (
  echo Cancelled.
  pause
  exit /b 0
)

powershell -ExecutionPolicy Bypass -File "%~dp0scripts\install-win.ps1"
if errorlevel 1 (
  echo.
  echo [ERROR] Install failed. If Cursor is under Program Files, right-click this bat and Run as administrator.
  pause
  exit /b 1
)

echo.
set /p STARTC=Launch Cursor now? [Y/N]: 
if /i "!STARTC!"=="Y" goto StartCursor
if /i "!STARTC!"=="YES" goto StartCursor
echo Please fully quit Cursor and reopen it manually.
pause
exit /b 0

:StartCursor
if defined CURSOR_INSTALL_DIR (
  if exist "!CURSOR_INSTALL_DIR!\Cursor.exe" start "" "!CURSOR_INSTALL_DIR!\Cursor.exe"
  goto :EOF
)
if defined CURSOR_INSTALL_PATH (
  if exist "!CURSOR_INSTALL_PATH!\Cursor.exe" start "" "!CURSOR_INSTALL_PATH!\Cursor.exe"
  goto :EOF
)
if exist "%LOCALAPPDATA%\Programs\cursor\Cursor.exe" (
  start "" "%LOCALAPPDATA%\Programs\cursor\Cursor.exe"
  goto :EOF
)
if exist "%ProgramFiles%\Cursor\Cursor.exe" (
  start "" "%ProgramFiles%\Cursor\Cursor.exe"
  goto :EOF
)
echo Cursor.exe not found automatically. Please launch it manually.
pause
