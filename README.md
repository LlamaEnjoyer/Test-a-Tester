# Test-a-Tester

A Flask-based web application for testing knowledge of Python, Selenium, and test automation concepts.

## Overview

Test-a-Tester is an educational quiz application designed for QA engineers, test automation developers, and anyone learning Selenium, Python, or test automation frameworks. The application features a customizable quiz system with timed tests, category filtering, and answer review.

## Features

- 185+ questions covering Selenium WebDriver, Python, ISTQB concepts, and test automation best practices
- **Comprehensive data validation** with JSON Schema ensuring data integrity at load time
- Customizable tests with category selection, configurable question count, and time limits (1-120 minutes)
- Optional answer shuffling to randomize option order for each question
- Real-time countdown timer with automatic submission
- Score tracking with percentage-based results
- Comprehensive review of incorrect answers with explanations
- Code snippet examples for practical learning
- Dark/Light theme toggle with system preference detection and localStorage persistence
- Robust input validation and security features (CSRF protection, rate limiting)

## Getting Started

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/LlamaEnjoyer/Test-a-Tester.git
   cd Test-a-Tester
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application
   ```bash
   python app.py
   ```

   The app will automatically validate all questions on startup. If validation fails, detailed error messages will be displayed.

4. Navigate to `http://127.0.0.1:5000/` in your browser

## Usage

1. Select desired categories, number of questions, time limit, and answer shuffling preference on the start page
2. Answer questions one at a time with the timer running
3. View your performance percentage after completion
4. Review incorrect answers with detailed explanations
5. Toggle between light and dark themes using the theme button in the top-right corner

## Project Structure

```
Test-a-Tester/
├── app.py                     # Main Flask application
├── services.py                # Business logic services
├── session_helpers.py         # Session management utilities
├── validators.py              # Input validation functions
├── question_validator.py      # Questions data validation with JSON Schema
├── validate_questions.py      # Standalone validation script
├── test_validation.py         # Validation test suite
├── requirements.txt           # Python dependencies
├── data/
│   ├── questions.json         # Question bank (validated)
│   └── questions_schema.json  # JSON Schema for questions
├── templates/
│   ├── base.html              # Base template with theme support
│   ├── start.html             # Landing page with test configuration
│   ├── question.html          # Question display with timer
│   ├── score.html             # Results page
│   ├── review.html            # Wrong answer review page
│   └── error.html             # Error page
├── static/
│   ├── css/
│   │   └── style.css          # Application styling with dark/light themes
│   └── js/
│       ├── theme.js           # Theme toggle functionality
│       ├── start.js           # Start page logic
│       └── question.js        # Question page timer
├── scripts/                   # Utility scripts for development
│   ├── format.bat/sh          # Code formatting scripts
│   ├── lint.bat/sh            # Linting scripts
│   ├── check.bat/sh           # Format checking scripts
│   └── all.bat/sh             # Run all checks
├── docs/                      # Documentation
│   ├── CONFIGURATION.md       # Configuration guide
│   ├── VALIDATION.md          # Data validation documentation
│   ├── LINTING.md             # Code quality documentation
│   └── QUICKSTART.md          # Quick setup guide
└── README.md                  # This file
```

## Configuration

### Validating Questions

Before adding or modifying questions, run the validation script:

```bash
python validate_questions.py
```

This validates:
- JSON structure against schema
- All required fields present
- Answer indices within bounds
- No duplicate options
- String length constraints

See [docs/VALIDATION.md](docs/VALIDATION.md) for detailed documentation.

### Adding Questions

Questions are stored in `data/questions.json` and must conform to the schema in `data/questions_schema.json`.

**Required fields**:
```json
{
  "question": "Question text (10-1000 chars)",
  "options": ["Option 1", "Option 2", "Option 3"],
  "correct_answer_index": 0,
  "category": "Python|Selenium|Automation|ISTQB",
  "explanation": "Explanation of correct answer (10-2000 chars)"
}
```

**Optional fields**:
```json
{
  "code_snippet": "Optional code example",
  "new": true
}
```

**Important**: 
- `correct_answer_index` must be within `options` array bounds (0-based)
- All options must be unique within a question
- Always validate after editing: `python validate_questions.py`

### Security

For production deployment, set environment variables:

```bash
export SECRET_KEY='your_very_secret_random_key_here'
export FLASK_DEBUG='false'
export SESSION_COOKIE_SECURE='true'  # For HTTPS deployments
```

Security features:
- CSRF protection on all forms
- Rate limiting (200/day, 50/hour)
- Secure session cookies (HttpOnly, SameSite)
- Input validation and sanitization
- Questions data validation at startup

## Technologies

- **Backend**: Flask 3.0.0 (Python web framework)
- **Data Validation**: JSON Schema (jsonschema 4.23.0)
- **Security**: Flask-WTF (CSRF), Flask-Limiter (rate limiting)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Data Storage**: JSON with schema validation
- **State Management**: Flask sessions with secure cookie-based storage
- **Theming**: CSS custom properties with localStorage and system preference detection
- **Code Quality**: Black, Flake8, MyPy, Pylint, isort

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/NewFeature`)
3. Make your changes
4. Run validation and linting:
   ```bash
   python validate_questions.py  # If modifying questions
   ./scripts/check.sh            # Run all checks (Linux/Mac/Git Bash)
   scripts\check.bat             # Run all checks (Windows)
   ```
5. Commit your changes (`git commit -m 'Add NewFeature'`)
6. Push to the branch (`git push origin feature/NewFeature`)
7. Open a Pull Request

### Code Quality

This project uses:
- **Black** for code formatting
- **isort** for import sorting
- **Flake8** for linting
- **MyPy** for type checking
- **Pylint** for additional checks

Run all checks: `./scripts/check.sh` or `scripts\check.bat`

See [docs/LINTING.md](docs/LINTING.md) for detailed documentation.

## License

This project is open source and available under the MIT License.

## Author

LlamaEnjoyer - [@LlamaEnjoyer](https://github.com/LlamaEnjoyer)

## Support

For issues or questions, please [open an issue](https://github.com/LlamaEnjoyer/Test-a-Tester/issues) on GitHub.
