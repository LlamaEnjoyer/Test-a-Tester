#!/usr/bin/env python3
"""
Standalone script to validate questions data.

This script validates the questions.json file against the schema
and performs additional semantic checks.

Usage:
    python validate_questions.py
"""

import sys
from pathlib import Path

from question_validator import (
    QuestionValidationError,
    get_validation_summary,
    validate_questions_file,
)


def main() -> int:
    """
    Main validation function.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Get file paths
    base_dir = Path(__file__).parent
    questions_file = base_dir / "data" / "questions.json"
    schema_file = base_dir / "data" / "questions_schema.json"

    print("=" * 80)
    print("Questions Data Validation")
    print("=" * 80)
    print(f"Questions file: {questions_file}")
    print(f"Schema file: {schema_file}")
    print()

    try:
        # Validate questions
        print("Validating questions...")
        questions = validate_questions_file(questions_file, schema_file, strict=True)

        # Get summary
        summary = get_validation_summary(questions)

        print("✓ Validation successful!")
        print()
        print("Summary:")
        print(f"  Total questions: {summary['total_questions']}")
        print(f"  Categories: {summary['category_count']}")
        print()
        print("Questions per category:")
        for category, count in sorted(summary["categories"].items()):
            print(f"  {category}: {count}")

        print()
        print("=" * 80)
        print("All checks passed!")
        print("=" * 80)
        return 0

    except QuestionValidationError as e:
        print("✗ Validation failed!")
        print()
        print(str(e))
        print()
        print("=" * 80)
        print("Please fix the errors above and try again.")
        print("=" * 80)
        return 1

    except Exception as e:
        print("✗ Unexpected error!")
        print()
        print(f"Error: {e}")
        print()
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
