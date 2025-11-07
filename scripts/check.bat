@echo off
REM Check formatting without making changes

echo Checking isort...
python -m isort --check-only .
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Imports need to be sorted. Run format.bat to fix.
    exit /b 1
)

echo.
echo Checking black...
python -m black --check .
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Code needs formatting. Run format.bat to fix.
    exit /b 1
)

echo.
echo ✅ Format check complete - no changes needed!
