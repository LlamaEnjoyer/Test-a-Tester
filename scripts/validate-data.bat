@echo off
REM validate-data.bat
REM Validation script for CI/CD pipelines (Windows)

echo ==================================
echo Data Validation Check
echo ==================================
echo.

python validate_questions.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [92m✓ Data validation passed![0m
    exit /b 0
) else (
    echo.
    echo [91m✗ Data validation failed![0m
    exit /b 1
)
