"""
Question data validation using JSON Schema.

This module provides comprehensive validation for quiz questions data,
ensuring data integrity at load time rather than runtime.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from jsonschema import Draft7Validator
from jsonschema.exceptions import SchemaError


class QuestionValidationError(Exception):
    """Custom exception for question validation errors."""

    def __init__(self, message: str, errors: List[str] | None = None):
        self.message = message
        self.errors = errors or []
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.errors:
            error_list = "\n  - ".join(self.errors)
            return f"{self.message}\n  - {error_list}"
        return self.message


def load_schema(schema_path: Path) -> Dict[str, Any]:
    """
    Load JSON schema from file.

    Args:
        schema_path: Path to the schema file

    Returns:
        Schema dictionary

    Raises:
        QuestionValidationError: If schema file is invalid
    """
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema: Dict[str, Any] = json.load(f)
        return schema
    except FileNotFoundError as e:
        raise QuestionValidationError(f"Schema file not found: {schema_path}") from e
    except json.JSONDecodeError as e:
        raise QuestionValidationError(f"Invalid JSON in schema file: {e}") from e


def validate_questions_against_schema(
    questions: List[Dict[str, Any]], schema: Dict[str, Any]
) -> None:
    """
    Validate questions data against JSON schema.

    Args:
        questions: List of question dictionaries
        schema: JSON schema dictionary

    Raises:
        QuestionValidationError: If validation fails
    """
    try:
        # Create validator
        validator = Draft7Validator(schema)

        # Collect all validation errors
        errors = []
        for error in validator.iter_errors(questions):
            # Build a clear error message
            path = ".".join(str(p) for p in error.path) if error.path else "root"
            errors.append(f"{path}: {error.message}")

        if errors:
            raise QuestionValidationError("Questions data does not match schema", errors=errors)

    except SchemaError as e:
        raise QuestionValidationError(f"Invalid schema: {e}") from e


def validate_answer_indices(questions: List[Dict[str, Any]]) -> None:
    """
    Validate that correct_answer_index is within bounds of options array.

    This is a semantic validation that goes beyond schema validation.

    Args:
        questions: List of question dictionaries

    Raises:
        QuestionValidationError: If any answer index is out of bounds
    """
    errors = []

    for idx, question in enumerate(questions):
        correct_idx = question.get("correct_answer_index")
        options = question.get("options", [])
        num_options = len(options)

        if correct_idx is not None and (correct_idx < 0 or correct_idx >= num_options):
            errors.append(
                f"Question {idx}: correct_answer_index ({correct_idx}) is out of bounds "
                f"(0-{num_options - 1})"
            )

    if errors:
        raise QuestionValidationError("Invalid answer indices found", errors=errors)


def validate_unique_options(questions: List[Dict[str, Any]]) -> None:
    """
    Validate that each question has unique options (no duplicates).

    Args:
        questions: List of question dictionaries

    Raises:
        QuestionValidationError: If duplicate options are found
    """
    errors = []

    for idx, question in enumerate(questions):
        options = question.get("options", [])
        unique_options = set(options)

        if len(unique_options) < len(options):
            duplicates = [opt for opt in options if options.count(opt) > 1]
            unique_duplicates = list(set(duplicates))
            errors.append(f"Question {idx}: Duplicate options found: {unique_duplicates}")

    if errors:
        raise QuestionValidationError("Duplicate options found in questions", errors=errors)


def validate_questions_data(
    questions: List[Dict[str, Any]],
    schema_path: Path,
    strict: bool = True,
) -> None:
    """
    Comprehensive validation of questions data.

    Args:
        questions: List of question dictionaries
        schema_path: Path to JSON schema file
        strict: If True, performs additional semantic validations

    Raises:
        QuestionValidationError: If validation fails
    """
    # Load and validate against schema
    schema = load_schema(schema_path)
    validate_questions_against_schema(questions, schema)

    if strict:
        # Additional semantic validations
        validate_answer_indices(questions)
        validate_unique_options(questions)


def validate_questions_file(
    questions_path: Path,
    schema_path: Path,
    strict: bool = True,
) -> List[Dict[str, Any]]:
    """
    Load and validate a questions JSON file.

    Args:
        questions_path: Path to questions JSON file
        schema_path: Path to schema JSON file
        strict: If True, performs additional semantic validations

    Returns:
        Validated list of questions

    Raises:
        QuestionValidationError: If file loading or validation fails
    """
    # Load questions file
    try:
        with open(questions_path, "r", encoding="utf-8") as f:
            questions: List[Dict[str, Any]] = json.load(f)
    except FileNotFoundError as e:
        raise QuestionValidationError(f"Questions file not found: {questions_path}") from e
    except json.JSONDecodeError as e:
        raise QuestionValidationError(f"Invalid JSON in questions file: {e}") from e

    # Validate questions data
    validate_questions_data(questions, schema_path, strict=strict)

    return questions


def get_validation_summary(questions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get a summary of the questions data for reporting.

    Args:
        questions: List of question dictionaries

    Returns:
        Dictionary with validation summary
    """
    categories: Dict[str, int] = {}
    total_questions = len(questions)

    for question in questions:
        category = question.get("category", "Unknown")
        categories[category] = categories.get(category, 0) + 1

    return {
        "total_questions": total_questions,
        "categories": categories,
        "category_count": len(categories),
    }
