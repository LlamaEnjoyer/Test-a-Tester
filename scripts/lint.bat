@echo off
REM Run all linters

echo Running flake8...
python -m flake8 .
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: flake8 found issues
)

echo.
echo Running mypy...
python -m mypy app.py
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: mypy found type issues
)

echo.
echo ✅ Linting complete!
