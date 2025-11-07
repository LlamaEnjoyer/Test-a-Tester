"""
Business logic services for quiz application.

This module contains all business logic separated from route handlers.
"""

import random
from typing import Any, Dict, List, Optional, Tuple

from validators import ValidationError


def filter_questions_by_categories(
    all_questions: List[Dict[str, Any]], selected_categories: List[str]
) -> List[Dict[str, Any]]:
    """
    Filter questions by selected categories.

    Args:
        all_questions: List of all available questions
        selected_categories: List of category names to filter by

    Returns:
        List of questions matching the selected categories
    """
    return [q for q in all_questions if q.get("category") in selected_categories]


def select_random_questions(
    questions: List[Dict[str, Any]], num_questions: int
) -> List[Dict[str, Any]]:
    """
    Randomly select questions from a list.

    Args:
        questions: List of questions to select from
        num_questions: Number of questions to select

    Returns:
        List of randomly selected questions
    """
    return random.sample(questions, num_questions)


def create_shuffle_mappings(
    selected_indices: List[int], questions: List[Dict[str, Any]]
) -> Dict[int, Dict[str, Any]]:
    """
    Create shuffle mappings for answer options.

    Args:
        selected_indices: List of question indices
        questions: List of all questions

    Returns:
        Dictionary mapping question indices to shuffle information
    """
    shuffle_mappings: Dict[int, Dict[str, Any]] = {}

    for idx in selected_indices:
        question = questions[idx]
        num_options = len(question["options"])

        # Create a shuffled order
        shuffled_indices = list(range(num_options))
        random.shuffle(shuffled_indices)

        # Find where the correct answer ended up
        correct_answer_index = question["correct_answer_index"]
        new_correct_index = shuffled_indices.index(correct_answer_index)

        shuffle_mappings[idx] = {
            "order": shuffled_indices,
            "correct_index": new_correct_index,
        }

    return shuffle_mappings


def apply_shuffle_mapping(
    question: Dict[str, Any],
    question_index: int,
    shuffle_mappings: Optional[Dict[int, Dict[str, Any]]],
) -> Dict[str, Any]:
    """
    Apply shuffle mapping to a question's options if shuffling is enabled.

    Args:
        question: Dictionary containing question data (will be modified in place)
        question_index: Index of the question in the original questions list
        shuffle_mappings: Dictionary mapping question indices to shuffle data

    Returns:
        The modified question dictionary
    """
    if shuffle_mappings and question_index in shuffle_mappings:
        mapping = shuffle_mappings[question_index]
        shuffled_order = mapping["order"]
        original_options = question["options"]
        question["options"] = [original_options[i] for i in shuffled_order]
        question["correct_answer_index"] = mapping["correct_index"]
    return question


def get_correct_answer_index(
    question_index: int,
    questions: List[Dict[str, Any]],
    shuffle_mappings: Optional[Dict[int, Dict[str, Any]]],
) -> int:
    """
    Get the correct answer index, accounting for shuffling.

    Args:
        question_index: Index of the question
        questions: List of all questions
        shuffle_mappings: Shuffle mappings if shuffling is enabled

    Returns:
        The correct answer index
    """
    if shuffle_mappings and question_index in shuffle_mappings:
        correct_idx: int = shuffle_mappings[question_index]["correct_index"]
        return correct_idx
    correct_idx_direct: int = questions[question_index]["correct_answer_index"]
    return correct_idx_direct


def process_answer(
    user_answer_int: Optional[int],
    correct_answer_index: int,
    current_question_index: int,
    q_index: int,
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Process a user's answer and determine if it's correct.

    Args:
        user_answer_int: User's answer index (None if unanswered/invalid)
        correct_answer_index: The correct answer index
        current_question_index: Index of current question in global list
        q_index: Sequential question number

    Returns:
        Tuple of (is_correct, wrong_answer_data or None)
    """
    if user_answer_int is None:
        # Unanswered or invalid answer
        return False, {
            "question_index": current_question_index,
            "user_answer": None,
            "question_number": q_index + 1,
        }

    if user_answer_int == correct_answer_index:
        # Correct answer
        return True, None

    # Wrong answer
    return False, {
        "question_index": current_question_index,
        "user_answer": user_answer_int,
        "question_number": q_index + 1,
    }


def build_review_data(
    wrong_answers: List[Dict[str, Any]],
    questions: List[Dict[str, Any]],
    shuffle_mappings: Optional[Dict[int, Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """
    Build review data for wrong answers.

    Args:
        wrong_answers: List of wrong answer entries from session
        questions: List of all questions
        shuffle_mappings: Shuffle mappings if enabled

    Returns:
        List of review data dictionaries
    """
    from validators import (
        validate_answer_index,
        validate_correct_answer_index,
        validate_question_data,
        validate_wrong_answer_entry,
    )

    review_data: List[Dict[str, Any]] = []

    for wrong in wrong_answers:
        question_index = validate_wrong_answer_entry(wrong, len(questions))
        if question_index is None:
            continue

        question = questions[question_index].copy()

        # Apply shuffling if it was enabled
        question = apply_shuffle_mapping(question, question_index, shuffle_mappings)

        # Validate question has required fields
        try:
            validate_question_data(question)
        except ValidationError:
            continue

        correct_answer_index = question["correct_answer_index"]
        num_options = len(question.get("options", []))

        # Validate correct answer index
        try:
            validate_correct_answer_index(correct_answer_index, num_options)
        except ValidationError:
            continue

        # Validate and sanitize user answer
        user_answer = wrong.get("user_answer")
        user_answer = validate_answer_index(user_answer, num_options)

        review_data.append(
            {
                "question_number": wrong.get("question_number", 0),
                "question": question,
                "user_answer": user_answer,
                "correct_answer_index": correct_answer_index,
            }
        )

    return review_data


def calculate_score_percentage(score: int, total: int) -> int:
    """
    Calculate score percentage.

    Args:
        score: Number of correct answers
        total: Total number of questions

    Returns:
        Percentage score (0-100)
    """
    if total <= 0:
        return 0
    return int((score / total) * 100)


def prepare_question_for_display(
    q_index: int,
    selected_indices: List[int],
    questions: List[Dict[str, Any]],
    shuffle_mappings: Optional[Dict[int, Dict[str, Any]]],
) -> Dict[str, Any]:
    """
    Prepare a question for display by retrieving and applying shuffle mappings.

    Args:
        q_index: Current question index in the test sequence
        selected_indices: List of selected question indices
        questions: List of all questions
        shuffle_mappings: Shuffle mappings if enabled

    Returns:
        Dictionary containing the prepared question data

    Raises:
        ValidationError: If question index is invalid
    """
    from validators import validate_question_index_in_range

    current_question_index = selected_indices[q_index]
    validate_question_index_in_range(current_question_index, len(questions))

    current_question = questions[current_question_index].copy()
    current_question = apply_shuffle_mapping(
        current_question, current_question_index, shuffle_mappings
    )

    return current_question


def validate_and_parse_user_answer(answer_str: Optional[str], num_options: int) -> Optional[int]:
    """
    Validate and parse user's answer from form data.

    Args:
        answer_str: Raw answer string from form
        num_options: Number of available options

    Returns:
        Validated answer index or None if invalid/missing
    """
    from validators import validate_answer_index

    if not answer_str:
        return None

    try:
        user_answer_int = int(answer_str)
        return validate_answer_index(user_answer_int, num_options)
    except (ValueError, TypeError):
        return None


def handle_answer_submission(
    user_answer_int: Optional[int],
    current_question_index: int,
    q_index: int,
    questions: List[Dict[str, Any]],
    shuffle_mappings: Optional[Dict[int, Dict[str, Any]]],
    current_question: Dict[str, Any],
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Handle the complete answer submission workflow.

    Args:
        user_answer_int: User's validated answer index
        current_question_index: Index of current question
        q_index: Sequential question number
        questions: List of all questions
        shuffle_mappings: Shuffle mappings if enabled
        current_question: The current question dict

    Returns:
        Tuple of (is_correct, wrong_answer_data or None)

    Raises:
        ValidationError: If validation fails
    """
    from validators import validate_correct_answer_index

    # Get correct answer index
    correct_answer_index = get_correct_answer_index(
        current_question_index, questions, shuffle_mappings
    )

    # Validate correct answer index
    num_options = len(current_question.get("options", []))
    validate_correct_answer_index(correct_answer_index, num_options)

    # Process the answer
    return process_answer(user_answer_int, correct_answer_index, current_question_index, q_index)
