# Code Quality & Linting Setup

This project uses several tools to maintain code quality and consistency.

## Tools Included

- **Black** - Opinionated code formatter
- **isort** - Import statement organizer
- **Flake8** - Style guide enforcement
  - flake8-bugbear - Additional bug and design problem checks
  - flake8-comprehensions - Comprehension improvements
  - flake8-simplify - Code simplification suggestions
- **mypy** - Static type checker
- **pylint** - Comprehensive code analyzer

## Configuration Files

- `pyproject.toml` - Configuration for Black, isort, mypy, and pylint
- `.flake8` - Flake8 configuration
- `.editorconfig` - Editor-agnostic coding styles
- `.vscode/settings.json` - VS Code integration

## Usage

### Quick Commands (Windows - Batch Scripts)

```cmd
# Format code automatically
format.bat

# Run all linters
lint.bat

# Check formatting without changes
check.bat

# Clean cache files
clean.bat

# Format and lint (recommended before commit)
all.bat
```

### Quick Commands (Git Bash / Linux - Shell Scripts)

```bash
# Format code automatically
./format.sh

# Run all linters
./lint.sh

# Check formatting without changes
./check.sh

# Format and lint (recommended before commit)
./all.sh
```

### Manual Commands

```bash
# Format code with Black
python -m black .

# Sort imports with isort
python -m isort .

# Check code with Flake8
python -m flake8 .

# Type check with mypy
python -m mypy app.py

# Analyze with pylint
python -m pylint app.py
```

### Checking Before Commit

**Windows (Command Prompt):**
```cmd
check.bat
```

**Git Bash / Linux:**
```bash
./check.sh
```

**Or manually:**
```bash
# Check formatting (without changing files)
python -m black --check .
python -m isort --check-only .

# Run linters
python -m flake8 .
python -m mypy app.py
```

## VS Code Integration

The project includes VS Code settings that:
- Enable Python linting (Flake8, mypy, pylint)
- Format code on save with Black
- Organize imports on save with isort
- Show lint errors in the Problems panel

Recommended VS Code extensions:
- Python (ms-python.python)
- Black Formatter (ms-python.black-formatter)
- Flake8 (ms-python.flake8)
- Mypy Type Checker (ms-python.mypy-type-checker)
- isort (ms-python.isort)

## Configuration Details

### Black
- Line length: 100 characters
- Target: Python 3.11+
- Skip: venv, __pycache__, build directories

### isort
- Profile: black (compatible with Black formatting)
- Line length: 100 characters
- Trailing commas enforced

### Flake8
- Max line length: 100 characters
- Max complexity: 10
- Ignores: E203, E501, W503 (Black compatibility)
- Plugins: bugbear, comprehensions, simplify

### mypy
- Check untyped definitions
- Warn on redundant casts, unused ignores
- Strict equality checks
- Ignore missing imports for third-party libraries

### pylint
- Max line length: 100 characters
- Disabled: C0111 (missing-docstring), C0103 (invalid-name for Flask), R0903 (too-few-public-methods)

## Current Linting Status

After running formatters:
- ✅ Black formatting applied
- ✅ isort import sorting applied
- ⚠️ Flake8 warnings (complexity in some functions)
- ⚠️ mypy type annotation needed for one variable

See individual tool output for details.
