# Quick Setup Guide

Get the Quiz Application running with persistent sessions in 3 minutes!

## Prerequisites

- Python 3.11 or 3.12
- pip package manager

## Setup Steps

### 1. Install Dependencies (30 seconds)

```bash
pip install -r requirements.txt
```

### 2. Create Environment File (1 minute)

Create a `.env` file from the example:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**Windows (Command Prompt):**
```cmd
copy .env.example .env
```

**Git Bash / Linux / macOS:**
```bash
cp .env.example .env
```

Generate a secure secret key:

```bash
python -c "import secrets; print(f'SECRET_KEY={secrets.token_hex(32)}')"
```

Edit `.env` and replace the `SECRET_KEY` value with the generated output.

Your `.env` file should look like:

```bash
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
FLASK_DEBUG=False
LOG_LEVEL=INFO
LOG_TO_FILE=True
# ... (other settings can use defaults)
```

### 3. Run Application (10 seconds)

```bash
python app.py
```

Visit: http://localhost:5000

## What Changed?

### ✅ Sessions Now Persist
- User sessions survive server restarts
- No more random logouts after deployment

### ✅ Professional Logging
- All events logged to `logs/app.log`
- Console output for real-time monitoring
- Configurable log levels

### ✅ Environment-Based Configuration
- Easy to configure via `.env` file
- Different settings for dev/staging/prod
- Secure secret key management

## Verification

After starting the app, you should see:

```
✓ Loaded environment variables from .env
✓ Logging configured (level: INFO)
✓ Logging to file: logs/app.log
✓ Successfully loaded and validated 50 questions
 * Running on http://127.0.0.1:5000
```

If you see a warning about SECRET_KEY, make sure you:
1. Created `.env` file
2. Added `SECRET_KEY=<your-random-64-char-hex>` to it

## Quick Test

1. Start a quiz
2. Answer a question
3. Stop the server (Ctrl+C)
4. Restart the server
5. Go back to the same URL

**Expected**: Your quiz session should still be active! 🎉

**Before this fix**: Session would be lost, redirected to start page.

## Common Issues

### "Unable to import 'dotenv'"

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### "No SECRET_KEY found in environment"

**Solution**: Create `.env` file with SECRET_KEY (see step 2 above)

### Sessions still resetting

**Solution**: Ensure SECRET_KEY in `.env` is the same after restart (don't regenerate it each time!)

## Files You Need

- ✅ `.env` - Your configuration (DO NOT commit to git)
- ✅ `requirements.txt` - Already updated with python-dotenv
- ✅ `.env.example` - Template for reference

## For More Details

See [CONFIGURATION.md](CONFIGURATION.md) for complete documentation.

## Support

If issues persist:
1. Check `logs/app.log` for errors
2. Verify `.env` file is in project root
3. Ensure all dependencies installed
4. Review [CONFIGURATION.md](CONFIGURATION.md) troubleshooting section
