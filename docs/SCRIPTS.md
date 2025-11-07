# Quick Reference - Linting Scripts

## Windows (Command Prompt / PowerShell)

| Script | Description |
|--------|-------------|
| `scripts\format.bat` | Format code with isort and black |
| `scripts\lint.bat` | Run flake8 and mypy linters |
| `scripts\check.bat` | Check formatting without making changes |
| `scripts\clean.bat` | Remove Python cache files |
| `scripts\all.bat` | Format + lint everything |

**Usage:**
```cmd
scripts\all.bat
```

## Git Bash / Linux / macOS

| Script | Description |
|--------|-------------|
| `scripts/format.sh` | Format code with isort and black |
| `scripts/lint.sh` | Run flake8 and mypy linters |
| `scripts/check.sh` | Check formatting without making changes |
| `scripts/all.sh` | Format + lint everything |

**Usage:**
```bash
./scripts/all.sh
```

## Recommended Workflow

Before committing code:
1. **Windows:** Run `scripts\all.bat`
2. **Bash:** Run `./scripts/all.sh`

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

For full documentation, see [LINTING.md](LINTING.md).
