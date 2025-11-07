@echo off
REM Run all tests

echo ========================================
echo   Running All Tests
echo ========================================
echo.

REM Track failures
set FAILED=0

REM Run each test file
for %%f in (tests\test_*.py) do (
    echo Running %%~nxf...
    python %%f
    if %ERRORLEVEL% NEQ 0 (
        set FAILED=1
        echo ❌ %%~nxf failed!
    )
    echo.
)

echo ========================================
if %FAILED% EQU 0 (
    echo ✅ All tests passed!
) else (
    echo ❌ Some tests failed!
    exit /b 1
)
echo ========================================
