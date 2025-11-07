# Questions Data Validation

This project implements comprehensive validation for quiz questions data using JSON Schema and semantic validation.

## Overview

Questions are validated at multiple levels:

1. **Schema Validation**: Ensures data structure matches the defined JSON schema
2. **Semantic Validation**: Validates logical constraints (e.g., answer indices, unique options)
3. **Runtime Validation**: Additional safety checks during quiz execution

## Schema

The questions schema is defined in `data/questions_schema.json` and enforces:

### Required Fields

Every question MUST have:

- `question` (string, 10-1000 chars): The question text
- `options` (array, 2-10 items): Answer options (each 1-500 chars)
- `correct_answer_index` (integer, >= 0): Index of correct answer
- `category` (string, 1-100 chars): Question category
- `explanation` (string, 10-2000 chars): Explanation of correct answer

### Optional Fields

- `code_snippet` (string): Code to display with the question
- `new` (boolean): Flag to mark new questions

### Constraints

- Minimum 1 question in the array
- No additional properties allowed
- All strings must be within specified length limits

## Validation Levels

### 1. Schema Validation

Validates the JSON structure matches the schema:

```python
from question_validator import validate_questions_data

validate_questions_data(questions, schema_path)
```

### 2. Semantic Validation

Performs additional logical checks:

- **Answer Index Validation**: `correct_answer_index` must be within `options` array bounds
- **Unique Options**: No duplicate options within a single question

Enable with `strict=True`:

```python
validate_questions_data(questions, schema_path, strict=True)
```

### 3. Runtime Validation

Additional validation happens during quiz execution in `validators.py` and `services.py`.

## Running Validation

### Standalone Script

Validate questions file independently:

**Windows:**
```cmd
scripts\validate-data.bat
```

**Git Bash / Linux / macOS:**
```bash
./scripts/validate-data.sh
```

**Or directly:**
```bash
python validate_questions.py
```

Output example:
```
================================================================================
Questions Data Validation
================================================================================
Questions file: F:\PythonProjects\Tester\data\questions.json
Schema file: F:\PythonProjects\Tester\data\questions_schema.json

Validating questions...
✓ Validation successful!

Summary:
  Total questions: 150
  Categories: 5

Questions per category:
  Automation: 30
  ISTQB: 40
  Python: 35
  Selenium: 45

================================================================================
All checks passed!
================================================================================
```

### Application Startup

Questions are automatically validated when the Flask app starts:

```bash
python app.py
```

If validation fails, the app won't start and will display detailed error messages.

## Adding New Questions

When adding questions to `data/questions.json`:

1. Follow the schema structure
2. Ensure all required fields are present
3. Verify `correct_answer_index` is within options bounds (0-based)
4. Avoid duplicate options
5. Run validation before committing:
   ```bash
   # Windows
   scripts\validate-data.bat
   
   # Git Bash / Linux / macOS
   ./scripts/validate-data.sh
   ```

## Example Question Format

```json
{
  "question": "What is the output of print(2 + 2)?",
  "options": [
    "3",
    "4",
    "22",
    "Error"
  ],
  "correct_answer_index": 1,
  "category": "Python",
  "explanation": "The + operator performs addition for integers, so 2 + 2 equals 4."
}
```

### With Code Snippet

```json
{
  "question": "What will this code print?",
  "code_snippet": "x = [1, 2, 3]\nprint(len(x))",
  "options": [
    "1",
    "2",
    "3",
    "Error"
  ],
  "correct_answer_index": 2,
  "category": "Python",
  "explanation": "The len() function returns the number of items in the list, which is 3."
}
```

## Common Validation Errors

### Missing Required Field

```
Questions data does not match schema
  - 0: 'explanation' is a required property
```

**Fix**: Add the missing field to the question.

### Invalid Answer Index

```
Invalid answer indices found
  - Question 5: correct_answer_index (4) is out of bounds (0-3)
```

**Fix**: Ensure `correct_answer_index` is less than the number of options.

### Duplicate Options

```
Duplicate options found in questions
  - Question 10: Duplicate options found: ['True', 'False']
```

**Fix**: Make all options unique within each question.

### String Too Short/Long

```
Questions data does not match schema
  - 2.question: 'Hi' is too short
```

**Fix**: Ensure strings meet minimum/maximum length requirements.

## Integration with CI/CD

Add validation to your CI pipeline:

```yaml
# .github/workflows/test.yml
- name: Validate Questions Data
  run: python validate_questions.py
```

This ensures data integrity before deployment.

## Benefits

1. **Early Error Detection**: Catch issues before runtime
2. **Data Integrity**: Ensure consistent question format
3. **Developer Experience**: Clear error messages guide fixes
4. **Production Safety**: Prevent malformed data from reaching users
5. **Documentation**: Schema serves as living documentation
6. **Automation**: Can be integrated into CI/CD pipelines

## Files

- `data/questions_schema.json` - JSON Schema definition
- `question_validator.py` - Validation logic
- `validate_questions.py` - Standalone validation script
- `data/questions.json` - Questions data (validated)
- `docs/VALIDATION.md` - This documentation
