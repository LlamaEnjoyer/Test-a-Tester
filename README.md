# Test-a-Tester

A Flask-based web application for testing knowledge of Python, Selenium, and test automation concepts.

## Overview

Test-a-Tester is an educational quiz application designed for QA engineers, test automation developers, and anyone learning Selenium, Python, or test automation frameworks. The application features a customizable quiz system with timed tests, category filtering, and answer review.

## Features

- 55+ questions covering Selenium WebDriver, Python, and test automation best practices
- Customizable tests with category selection, configurable question count, and time limits
- Real-time countdown timer with automatic submission
- Score tracking with percentage-based results
- Comprehensive review of incorrect answers with explanations
- Code snippet examples for practical learning

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
   pip install flask
   ```

3. Run the application
   ```bash
   python app.py
   ```

4. Navigate to `http://127.0.0.1:5000/` in your browser

## Usage

1. Select desired categories, number of questions, and time limit on the start page
2. Answer questions one at a time with the timer running
3. View your performance percentage after completion
4. Review incorrect answers with detailed explanations

## Project Structure

```
Test-a-Tester/
├── app.py                 # Main Flask application
├── data/
│   └── questions.json     # Question bank with categories
├── templates/
│   ├── start.html         # Landing page with test configuration
│   ├── question.html      # Question display with timer
│   ├── score.html         # Results page
│   └── review.html        # Wrong answer review page
├── static/                # Static assets
└── README.md
```

## Configuration

### Adding Questions

Questions are stored in `data/questions.json`. Each question follows this structure:

```json
{
  "question": "Question text here",
  "code_snippet": "Optional code example",
  "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
  "correct_answer_index": 0,
  "category": "Python|Selenium|Automation",
  "explanation": "Explanation of correct answer"
}
```

### Security

For production deployment, change the secret key in `app.py`:

```python
app.secret_key = 'your_very_secret_key'
```

## Technologies

- Flask (Python web framework)
- HTML, CSS, JavaScript
- JSON for data storage
- Flask sessions for state management

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/NewFeature`)
3. Commit your changes (`git commit -m 'Add NewFeature'`)
4. Push to the branch (`git push origin feature/NewFeature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Author

LlamaEnjoyer - [@LlamaEnjoyer](https://github.com/LlamaEnjoyer)

## Support

For issues or questions, please [open an issue](https://github.com/LlamaEnjoyer/Test-a-Tester/issues) on GitHub.
