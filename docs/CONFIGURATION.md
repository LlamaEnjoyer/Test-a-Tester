# Configuration Guide

This document explains the configuration management system for the Quiz Application.

## Overview

The application uses a centralized configuration system that:
- ✅ Loads settings from environment variables via `.env` files
- ✅ Provides persistent secret key storage (prevents session breaks on restart)
- ✅ Configures structured logging with file and console output
- ✅ Manages Flask app settings securely
- ✅ Provides sensible defaults for all settings

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install `python-dotenv` along with other required packages.

### 2. Create Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

### 3. Generate Secret Key

Generate a secure secret key:

```bash
python -c "import secrets; print(f'SECRET_KEY={secrets.token_hex(32)}')"
```

Copy the output and add it to your `.env` file.

### 4. Configure Settings

Edit `.env` to customize your settings (see Configuration Options below).

## Configuration Options

### Critical Settings

#### `SECRET_KEY` (Required for Production)

**Purpose**: Cryptographic key for Flask sessions and CSRF protection.

**Default**: Auto-generated temporary key (not persistent)

**Production**: MUST be set to a persistent random value

**Example**:
```bash
SECRET_KEY=your-64-character-random-hex-string-here
```

**Generate**:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

⚠️ **Warning**: Without a persistent SECRET_KEY, user sessions will be invalidated every time the server restarts!

### Flask Settings

#### `FLASK_DEBUG`

**Purpose**: Enable/disable Flask debug mode

**Default**: `False`

**Values**: `True` or `False`

**Example**:
```bash
FLASK_DEBUG=False  # Use True only for development
```

### Session Security

#### `SESSION_COOKIE_SECURE`

**Purpose**: Send cookies only over HTTPS

**Default**: `False`

**Values**: `True` or `False`

**Production**: Set to `True` when using HTTPS

**Example**:
```bash
SESSION_COOKIE_SECURE=True
```

#### `SESSION_LIFETIME_HOURS`

**Purpose**: How long sessions remain valid

**Default**: `2` hours

**Values**: Any positive integer

**Example**:
```bash
SESSION_LIFETIME_HOURS=4
```

### Logging Configuration

#### `LOG_LEVEL`

**Purpose**: Minimum logging level

**Default**: `INFO`

**Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

**Example**:
```bash
LOG_LEVEL=INFO
```

#### `LOG_TO_FILE`

**Purpose**: Enable/disable file logging

**Default**: `True`

**Values**: `True` or `False`

**Example**:
```bash
LOG_TO_FILE=True
```

#### `LOG_FILE_PATH`

**Purpose**: Path to log file (relative to project root)

**Default**: `logs/app.log`

**Example**:
```bash
LOG_FILE_PATH=logs/app.log
```

#### `LOG_FORMAT`

**Purpose**: Python logging format string

**Default**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

**Example**:
```bash
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

#### `LOG_DATE_FORMAT`

**Purpose**: Date/time format for log entries

**Default**: `%Y-%m-%d %H:%M:%S`

**Example**:
```bash
LOG_DATE_FORMAT=%Y-%m-%d %H:%M:%S
```

### Rate Limiting

#### `RATELIMIT_STORAGE_URI`

**Purpose**: Storage backend for rate limiting

**Default**: `memory://`

**Production**: Use Redis for distributed deployments

**Examples**:
```bash
# Development
RATELIMIT_STORAGE_URI=memory://

# Production with Redis
RATELIMIT_STORAGE_URI=redis://localhost:6379
```

### Quiz Settings

#### `MAX_TIME_LIMIT_MINUTES`

**Purpose**: Maximum allowed quiz time limit

**Default**: `120` minutes

**Example**:
```bash
MAX_TIME_LIMIT_MINUTES=120
```

#### `MIN_TIME_LIMIT_MINUTES`

**Purpose**: Minimum allowed quiz time limit

**Default**: `1` minute

**Example**:
```bash
MIN_TIME_LIMIT_MINUTES=1
```

#### `DEFAULT_TIME_LIMIT_MINUTES`

**Purpose**: Default quiz time limit

**Default**: `10` minutes

**Example**:
```bash
DEFAULT_TIME_LIMIT_MINUTES=10
```

## Architecture

### Config Class (`config.py`)

The `Config` class handles all configuration management:

```python
from config import Config

# Initialize configuration
config = Config()

# Setup logging
config.setup_logging()

# Apply to Flask app
config.apply_to_flask_app(app)
```

### Features

1. **Environment Variable Loading**
   - Automatically loads `.env` file
   - Falls back to system environment variables
   - Provides helpful error messages for missing required settings

2. **Secret Key Management**
   - Loads from `SECRET_KEY` environment variable
   - Auto-generates temporary key if not set (with warning)
   - Provides instructions for creating persistent key

3. **Logging Setup**
   - Configures both console and file logging
   - Creates log directory automatically
   - Supports customizable log levels and formats
   - Separate configuration for Flask's werkzeug logger

4. **Type Safety**
   - Proper type hints throughout
   - Validated configuration values
   - Clear error messages

## Logging

### Log Files

Logs are written to `logs/app.log` by default (configurable via `LOG_FILE_PATH`).

The `logs/` directory is tracked by git (via `.gitkeep`), but log files themselves are ignored.

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for serious problems
- **CRITICAL**: Critical errors requiring immediate attention

### Example Log Output

```
2025-11-07 10:30:15 - __main__ - INFO - Successfully loaded and validated 50 questions
2025-11-07 10:30:20 - __main__ - WARNING - Invalid answer format: abc
2025-11-07 10:30:25 - __main__ - ERROR - Validation error in submit_answer: Invalid question reference
```

## Migration from Old Configuration

### Before (app.py)

```python
import secrets
from datetime import timedelta

secret_key = os.environ.get("SECRET_KEY")
if not secret_key:
    secret_key = secrets.token_hex(32)
    print("WARNING: Using temporary secret key")

app.secret_key = secret_key
app.config.update(
    SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE", "False").lower() == "true",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
)
```

### After (app.py)

```python
from config import Config

config = Config()
config.setup_logging()
config.apply_to_flask_app(app)
```

## Production Deployment Checklist

- [ ] Create `.env` file with persistent `SECRET_KEY`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Set `SESSION_COOKIE_SECURE=True` (if using HTTPS)
- [ ] Configure `RATELIMIT_STORAGE_URI` to use Redis
- [ ] Set appropriate `LOG_LEVEL` (INFO or WARNING)
- [ ] Ensure `LOG_FILE_PATH` is writable
- [ ] Configure `SESSION_LIFETIME_HOURS` as needed
- [ ] Review and set quiz time limits
- [ ] Add `.env` to `.gitignore` (already done)
- [ ] Never commit `.env` to version control

## Troubleshooting

### Sessions Reset on Server Restart

**Cause**: No persistent `SECRET_KEY` configured

**Solution**: Add a persistent `SECRET_KEY` to your `.env` file

### Import Error: dotenv

**Cause**: `python-dotenv` not installed

**Solution**: Run `pip install -r requirements.txt`

### Logs Not Written to File

**Cause**: Log directory doesn't exist or isn't writable

**Solution**: Ensure `logs/` directory exists and is writable, or set `LOG_TO_FILE=False`

### Configuration Not Loading

**Cause**: `.env` file not in the correct location

**Solution**: Ensure `.env` is in the project root (same directory as `app.py`)

## Security Best Practices

1. **Never commit `.env` to version control**
2. **Use strong, random SECRET_KEY** (64+ characters)
3. **Enable SESSION_COOKIE_SECURE in production** (HTTPS only)
4. **Rotate SECRET_KEY periodically** (will invalidate existing sessions)
5. **Use Redis for rate limiting in production** (not memory://)
6. **Review logs regularly** for security issues
7. **Set appropriate session lifetime** (balance convenience vs security)

## Additional Resources

- [Flask Configuration Handling](https://flask.palletsprojects.com/en/3.0.x/config/)
- [Python Logging](https://docs.python.org/3/library/logging.html)
- [python-dotenv Documentation](https://github.com/theskumar/python-dotenv)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/3.0.x/security/)
