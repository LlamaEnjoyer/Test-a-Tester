@echo off
REM Format code with isort and black

echo Running isort...
python -m isort .
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: isort failed
    exit /b 1
)

echo.
echo Running black...
python -m black .
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: black failed
    exit /b 1
)

echo.
echo ✅ Code formatting complete!
