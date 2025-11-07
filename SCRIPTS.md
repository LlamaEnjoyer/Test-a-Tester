# Quick Reference - Linting Scripts

## Windows (Command Prompt / PowerShell)

| Script | Description |
|--------|-------------|
| `format.bat` | Format code with isort and black |
| `lint.bat` | Run flake8 and mypy linters |
| `check.bat` | Check formatting without making changes |
| `clean.bat` | Remove Python cache files |
| `all.bat` | Format + lint everything |

**Usage:**
```cmd
all.bat
```

## Git Bash / Linux / macOS

| Script | Description |
|--------|-------------|
| `format.sh` | Format code with isort and black |
| `lint.sh` | Run flake8 and mypy linters |
| `check.sh` | Check formatting without making changes |
| `all.sh` | Format + lint everything |

**Usage:**
```bash
./all.sh
```

## Recommended Workflow

Before committing code:
1. **Windows:** Run `all.bat`
2. **Bash:** Run `./all.sh`

This will:
- ✅ Format your code with Black
- ✅ Sort imports with isort
- ✅ Check for code issues with Flake8
- ✅ Check types with mypy

## Individual Commands

If you prefer to run tools separately:

```bash
# Just format
python -m black .
python -m isort .

# Just lint
python -m flake8 .
python -m mypy app.py

# Just check (no changes)
python -m black --check .
python -m isort --check-only .
```

## Note about Makefile

The `Makefile` is included but requires GNU Make which is not typically available on Windows by default. Use the `.bat` or `.sh` scripts instead for better cross-platform compatibility.

For full documentation, see `LINTING.md`.
