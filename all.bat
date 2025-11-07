@echo off
REM Format and lint all code

echo ========================================
echo   Format and Lint All Code
echo ========================================
echo.

call format.bat
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Formatting failed
    exit /b 1
)

echo.
echo ========================================
echo.

call lint.bat

echo.
echo ========================================
echo   All Done!
echo ========================================
