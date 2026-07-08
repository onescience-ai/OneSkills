@echo off
REM SCNet Chat Launcher for Windows

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "SCNET_PY=%SCRIPT_DIR%scnet.py"

where python >nul 2>&1
if %errorlevel% == 0 (
    python "%SCNET_PY%" %*
    exit /b %errorlevel%
)

where python3 >nul 2>&1
if %errorlevel% == 0 (
    python3 "%SCNET_PY%" %*
    exit /b %errorlevel%
)

echo Error: Python not found. Please install Python 3. >&2
exit /b 1
