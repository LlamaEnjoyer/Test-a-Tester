@echo off
REM Format and lint all code

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

echo ========================================
echo   Format, Lint, and Test All Code
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
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Linting failed
    exit /b 1
)

echo.
echo ========================================
echo.

call "%SCRIPT_DIR%test.bat"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Tests failed
    exit /b 1
)

echo.
echo ========================================
echo   All Done!
echo ========================================
