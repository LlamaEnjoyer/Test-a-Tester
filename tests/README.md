# Tests Directory

This directory contains all test files for the quiz application.

## Test Files

### Unit Tests

- **test_services.py** - Tests for business logic functions in `services.py`
  - Question filtering by categories
  - Random question selection
  - Shuffle mapping creation and application
  - Answer processing logic
  - Score calculation
  - Review data building

- **test_validators.py** - Tests for validation functions in `validators.py`
  - Category validation
  - Number of questions validation
  - Time limit validation
  - Shuffle option validation
  - Session state validation
  - Answer index validation

- **test_session_helpers.py** - Tests for session management in `session_helpers.py`
  - Server timestamp generation
  - Client timestamp validation (clock skew detection)
  - Session initialization
  - Score management
  - Question navigation
  - Time remaining validation

- **test_clock_skew.py** - Tests for clock skew detection functionality
  - Valid timestamp acceptance
  - Future/past timestamp handling within tolerance
  - Detection of timestamps beyond tolerance
  - Custom tolerance parameters

- **test_validation.py** - Integration tests for question validation
  - Missing required fields
  - Invalid answer indices
  - Duplicate options
  - Question text length validation
  - Valid data acceptance

## Running Tests

### Run all tests:
```bash
# Windows
scripts\test.bat

# Git Bash / Linux / macOS
./scripts/test.sh

# Or using Makefile
make test
```

### Run individual test files:
```bash
python tests/test_services.py
python tests/test_validators.py
python tests/test_session_helpers.py
python tests/test_clock_skew.py
python tests/test_validation.py
```

## Test Coverage

Current test coverage includes:
- ✅ Business logic (services.py)
- ✅ Input validation (validators.py)
- ✅ Session management (session_helpers.py)
- ✅ Clock skew detection
- ✅ Question validation
- ⚠️ Flask routes (app.py) - Would benefit from integration tests
- ⚠️ Frontend JavaScript - Would benefit from browser/E2E tests

## Future Test Improvements

### Integration Tests
- Add tests for Flask routes using `pytest` and `Flask.test_client()`
- Test complete user flows (start test → answer questions → view score)
- Test error handling and edge cases in routes

### End-to-End Tests
- Browser-based tests using Selenium or Playwright
- Test timer functionality in real browser environment
- Test CSRF protection and rate limiting

### Performance Tests
- Test with large question sets (1000+ questions)
- Load testing with concurrent users
- Memory usage profiling

### Additional Unit Tests
- Test `config.py` configuration loading
- Test `constants.py` if it contains logic
- Test `question_validator.py` edge cases
