#!/usr/bin/env python3
"""
Test script to demonstrate validation catching errors.

This script tests the validation with intentionally malformed data.
"""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile

from question_validator import QuestionValidationError, validate_questions_file


def test_missing_required_field():
    """Test validation catches missing required fields."""
    print("\n" + "=" * 80)
    print("TEST 1: Missing required field (explanation)")
    print("=" * 80)

    invalid_data = [
        {
            "question": "What is 2 + 2?",
            "options": ["3", "4", "5"],
            "correct_answer_index": 1,
            "category": "Math",
            # Missing "explanation" field
        }
    ]

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(invalid_data, f)
        temp_file = Path(f.name)

    schema_file = Path(__file__).parent / "data" / "questions_schema.json"

    try:
        validate_questions_file(temp_file, schema_file)
        print("✗ Validation should have failed!")
    except QuestionValidationError as e:
        print("✓ Correctly caught validation error:")
        print(f"  {e}")
    finally:
        temp_file.unlink()


def test_invalid_answer_index():
    """Test validation catches out-of-bounds answer index."""
    print("\n" + "=" * 80)
    print("TEST 2: Invalid answer index (out of bounds)")
    print("=" * 80)

    invalid_data = [
        {
            "question": "What is the capital of France?",
            "options": ["London", "Paris", "Berlin"],
            "correct_answer_index": 5,  # Out of bounds!
            "category": "Geography",
            "explanation": "Paris is the capital of France.",
        }
    ]

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(invalid_data, f)
        temp_file = Path(f.name)

    schema_file = Path(__file__).parent / "data" / "questions_schema.json"

    try:
        validate_questions_file(temp_file, schema_file, strict=True)
        print("✗ Validation should have failed!")
    except QuestionValidationError as e:
        print("✓ Correctly caught validation error:")
        print(f"  {e}")
    finally:
        temp_file.unlink()


def test_duplicate_options():
    """Test validation catches duplicate options."""
    print("\n" + "=" * 80)
    print("TEST 3: Duplicate options")
    print("=" * 80)

    invalid_data = [
        {
            "question": "Which is a programming language?",
            "options": ["Python", "Python", "Java"],  # Duplicate!
            "correct_answer_index": 0,
            "category": "Programming",
            "explanation": "Python is a programming language.",
        }
    ]

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(invalid_data, f)
        temp_file = Path(f.name)

    schema_file = Path(__file__).parent / "data" / "questions_schema.json"

    try:
        validate_questions_file(temp_file, schema_file, strict=True)
        print("✗ Validation should have failed!")
    except QuestionValidationError as e:
        print("✓ Correctly caught validation error:")
        print(f"  {e}")
    finally:
        temp_file.unlink()


def test_question_too_short():
    """Test validation catches questions that are too short."""
    print("\n" + "=" * 80)
    print("TEST 4: Question text too short")
    print("=" * 80)

    invalid_data = [
        {
            "question": "Hi?",  # Too short (< 10 chars)
            "options": ["Yes", "No"],
            "correct_answer_index": 0,
            "category": "Test",
            "explanation": "This is a test explanation that is long enough.",
        }
    ]

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(invalid_data, f)
        temp_file = Path(f.name)

    schema_file = Path(__file__).parent / "data" / "questions_schema.json"

    try:
        validate_questions_file(temp_file, schema_file)
        print("✗ Validation should have failed!")
    except QuestionValidationError as e:
        print("✓ Correctly caught validation error:")
        print(f"  {e}")
    finally:
        temp_file.unlink()


def test_valid_data():
    """Test validation accepts valid data."""
    print("\n" + "=" * 80)
    print("TEST 5: Valid question data")
    print("=" * 80)

    valid_data = [
        {
            "question": "What is the result of 5 + 3 in Python?",
            "options": ["8", "53", "Error", "None"],
            "correct_answer_index": 0,
            "category": "Python",
            "explanation": "The + operator performs addition for integers, so 5 + 3 equals 8.",
        }
    ]

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(valid_data, f)
        temp_file = Path(f.name)

    schema_file = Path(__file__).parent / "data" / "questions_schema.json"

    try:
        questions = validate_questions_file(temp_file, schema_file, strict=True)
        print("✓ Validation passed successfully!")
        print(f"  Loaded {len(questions)} question(s)")
    except QuestionValidationError as e:
        print(f"✗ Validation failed unexpectedly: {e}")
    finally:
        temp_file.unlink()


def main():
    """Run all tests."""
    print("=" * 80)
    print("Questions Validation Test Suite")
    print("=" * 80)
    print("\nThis script demonstrates how validation catches various data errors.")

    test_missing_required_field()
    test_invalid_answer_index()
    test_duplicate_options()
    test_question_too_short()
    test_valid_data()

    print("\n" + "=" * 80)
    print("All tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
