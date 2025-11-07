@echo off
REM Format and lint all code

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

echo ========================================
echo   Format and Lint All Code
echo ========================================
echo.

call "%SCRIPT_DIR%format.bat"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Formatting failed
    exit /b 1
)

echo.
echo ========================================
echo.

call "%SCRIPT_DIR%lint.bat"

echo.
echo ========================================
echo   All Done!
echo ========================================
