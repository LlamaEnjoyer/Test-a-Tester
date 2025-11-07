"""
Validation functions for quiz application.

This module contains all input validation logic separated from route handlers.
"""

from typing import Any, Dict, List, Optional, Tuple

# Time limit constants
MAX_TIME_LIMIT_MINUTES = 120
MIN_TIME_LIMIT_MINUTES = 1
DEFAULT_TIME_LIMIT_MINUTES = 10


class ValidationError(Exception):
    """Custom exception for validation errors."""

    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(self.message)


def validate_categories(selected_categories: List[str], valid_categories: List[str]) -> None:
    """
    Validate selected categories.

    Args:
        selected_categories: List of categories selected by user
        valid_categories: List of all valid category names

    Raises:
        ValidationError: If validation fails
    """
    if not selected_categories or len(selected_categories) == 0:
        raise ValidationError("Please select at least one category")

    for category in selected_categories:
        if category not in valid_categories:
            raise ValidationError("Invalid category selection")


def validate_num_questions(num_questions: Optional[int], available_questions: int) -> int:
    """
    Validate number of questions requested.

    Args:
        num_questions: Number of questions requested
        available_questions: Number of questions available

    Returns:
        Validated number of questions

    Raises:
        ValidationError: If validation fails
    """
    if num_questions is None or not isinstance(num_questions, int):
        raise ValidationError("Number of questions must be a valid number")

    if num_questions < 1:
        raise ValidationError("Number of questions must be at least 1")

    if num_questions > available_questions:
        raise ValidationError(
            f"Only {available_questions} questions available for selected categories"
        )

    return num_questions


def validate_time_limit(time_limit: Optional[int]) -> int:
    """
    Validate time limit.

    Args:
        time_limit: Time limit in minutes

    Returns:
        Validated time limit

    Raises:
        ValidationError: If validation fails
    """
    if time_limit is None or not isinstance(time_limit, int):
        raise ValidationError("Time limit must be a valid number")

    if time_limit < MIN_TIME_LIMIT_MINUTES:
        raise ValidationError(f"Time limit must be at least {MIN_TIME_LIMIT_MINUTES} minute(s)")

    if time_limit > MAX_TIME_LIMIT_MINUTES:
        raise ValidationError(f"Time limit cannot exceed {MAX_TIME_LIMIT_MINUTES} minutes")

    return time_limit


def validate_shuffle_option(shuffle_str: str) -> bool:
    """
    Validate shuffle answers option.

    Args:
        shuffle_str: String value for shuffle option

    Returns:
        Boolean shuffle value

    Raises:
        ValidationError: If validation fails
    """
    shuffle_lower = shuffle_str.lower()
    if shuffle_lower not in ["true", "false"]:
        raise ValidationError("Invalid shuffle option")

    return shuffle_lower == "true"


def validate_session_question_index(
    q_index: Optional[int], selected_indices: Optional[List[int]]
) -> Tuple[int, List[int]]:
    """
    Validate session question index and selected indices.

    Args:
        q_index: Current question index from session
        selected_indices: List of selected question indices from session

    Returns:
        Tuple of (validated q_index, validated selected_indices)

    Raises:
        ValidationError: If validation fails
    """
    if q_index is None:
        raise ValidationError("Invalid test session. Please start a new test.")

    if not selected_indices or not isinstance(selected_indices, list):
        raise ValidationError("Invalid test session. Please start a new test.")

    if not isinstance(q_index, int) or q_index < 0:
        raise ValidationError("Invalid question index")

    return q_index, selected_indices


def validate_question_index_in_range(question_index: int, total_questions: int) -> None:
    """
    Validate that a question index is within valid range.

    Args:
        question_index: Index to validate
        total_questions: Total number of questions available

    Raises:
        ValidationError: If validation fails
    """
    if (
        not isinstance(question_index, int)
        or question_index < 0
        or question_index >= total_questions
    ):
        raise ValidationError("Invalid question reference")


def validate_answer_index(answer_index: Any, num_options: int) -> Optional[int]:
    """
    Validate user's answer index.

    Args:
        answer_index: User's answer index
        num_options: Number of available options

    Returns:
        Validated answer index or None if invalid

    Raises:
        ValidationError: For invalid format (not for out-of-range)
    """
    if answer_index is None:
        return None

    if not isinstance(answer_index, int):
        return None

    if answer_index < 0 or answer_index >= num_options:
        return None

    return answer_index


def validate_correct_answer_index(correct_index: int, num_options: int) -> None:
    """
    Validate correct answer index from question data.

    Args:
        correct_index: Correct answer index
        num_options: Number of options available

    Raises:
        ValidationError: If validation fails (500 error - data integrity issue)
    """
    if not isinstance(correct_index, int) or correct_index < 0 or correct_index >= num_options:
        raise ValidationError("Invalid question configuration", code=500)


def validate_wrong_answer_entry(wrong_answer: Any, total_questions: int) -> Optional[int]:
    """
    Validate a wrong answer entry from session.

    Args:
        wrong_answer: Wrong answer dictionary from session
        total_questions: Total number of questions

    Returns:
        Valid question_index or None if invalid
    """
    if not isinstance(wrong_answer, dict):
        return None

    question_index: Any = wrong_answer.get("question_index")

    if question_index is None or not isinstance(question_index, int):
        return None

    # At this point, mypy knows question_index is int due to isinstance check
    validated_index: int = question_index

    if validated_index < 0 or validated_index >= total_questions:
        return None

    return validated_index


def validate_question_data(question: Dict[str, Any]) -> None:
    """
    Validate that question data has required fields.

    Args:
        question: Question dictionary

    Raises:
        ValidationError: If question is missing required fields
    """
    if "correct_answer_index" not in question or "options" not in question:
        raise ValidationError("Invalid question data", code=500)
