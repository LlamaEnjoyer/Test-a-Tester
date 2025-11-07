"""
Session management helpers for quiz application.

This module contains session-related helper functions.
"""

import time
from typing import Any, Dict, List, Optional, Tuple

from flask import session

from constants import CLOCK_SKEW_TOLERANCE_SECONDS, DEFAULT_TIME_LIMIT_SECONDS, SECONDS_PER_MINUTE


def validate_time_remaining() -> Tuple[bool, int]:
    """
    Validate server-side timer to prevent client-side manipulation.

    Returns:
        Tuple of (is_valid, remaining_time)
    """
    start_time: Optional[float] = session.get("start_time")
    time_limit: int = session.get("time_limit", DEFAULT_TIME_LIMIT_SECONDS)

    if start_time is None:
        return False, 0

    elapsed_time = time.time() - start_time
    remaining_time = int(time_limit - elapsed_time)

    # Time has expired
    if remaining_time <= 0:
        return False, 0

    return True, remaining_time


def get_server_timestamp() -> float:
    """
    Get the current server timestamp.

    Returns:
        Current server time as Unix timestamp (seconds since epoch)
    """
    return time.time()


def validate_client_timestamp(
    client_timestamp: Optional[float],
    tolerance_seconds: int = CLOCK_SKEW_TOLERANCE_SECONDS,
) -> bool:
    """
    Validate client timestamp to detect significant clock skew.

    Args:
        client_timestamp: Timestamp from client (Unix timestamp in seconds)
        tolerance_seconds: Maximum acceptable time difference in seconds

    Returns:
        True if client timestamp is within tolerance, False otherwise
    """
    if client_timestamp is None:
        return False

    server_timestamp = get_server_timestamp()
    time_diff = abs(server_timestamp - client_timestamp)

    # Allow for small differences due to network latency and processing time
    return time_diff <= tolerance_seconds


def initialize_test_session(
    selected_indices: List[int],
    shuffle_mappings: Dict[int, Dict[str, Any]],
    time_limit_minutes: int,
    shuffle_answers: bool,
) -> None:
    """
    Initialize the test session with all required data.

    Args:
        selected_indices: List of selected question indices
        shuffle_mappings: Shuffle mappings for answers
        time_limit_minutes: Time limit in minutes
        shuffle_answers: Whether answers are shuffled
    """
    session["selected_question_indices"] = selected_indices
    session["current_question_index"] = 0
    session["score"] = 0
    session["wrong_answers"] = []
    session["time_limit"] = time_limit_minutes * SECONDS_PER_MINUTE  # Convert to seconds
    session["start_time"] = time.time()
    session["shuffle_mappings"] = shuffle_mappings
    session["shuffle_answers"] = shuffle_answers


def get_current_question_data() -> (
    Tuple[Optional[int], Optional[List[int]], Optional[Dict[int, Dict[str, Any]]]]
):
    """
    Get current question data from session.

    Returns:
        Tuple of (current_index, selected_indices, shuffle_mappings)
    """
    q_index: Optional[int] = session.get("current_question_index")
    selected_indices: Optional[List[int]] = session.get("selected_question_indices")
    shuffle_mappings: Optional[Dict[int, Dict[str, Any]]] = session.get("shuffle_mappings")

    return q_index, selected_indices, shuffle_mappings


def increment_question_index() -> None:
    """Increment the current question index in session."""
    current = session.get("current_question_index", 0)
    session["current_question_index"] = current + 1


def add_to_score() -> None:
    """Increment the score by 1."""
    session["score"] = session.get("score", 0) + 1


def add_wrong_answer(wrong_answer_data: Dict[str, Any]) -> None:
    """
    Add a wrong answer to the session.

    Args:
        wrong_answer_data: Dictionary containing wrong answer information
    """
    wrong_answers = session.get("wrong_answers", [])
    wrong_answers.append(wrong_answer_data)
    session["wrong_answers"] = wrong_answers


def get_score_data() -> Tuple[Any, Any, Any]:
    """
    Get score-related data from session.

    Returns:
        Tuple of (score, selected_indices, wrong_answers)
    """
    score = session.get("score", 0)
    selected_indices = session.get("selected_question_indices", [])
    wrong_answers = session.get("wrong_answers", [])

    return score, selected_indices, wrong_answers


def get_review_data() -> Tuple[Any, Any]:
    """
    Get review-related data from session.

    Returns:
        Tuple of (wrong_answers, shuffle_mappings)
    """
    wrong_answers = session.get("wrong_answers", [])
    shuffle_mappings = session.get("shuffle_mappings")

    return wrong_answers, shuffle_mappings


def sanitize_score(score: int, total: int) -> int:
    """
    Sanitize and validate score value.

    Args:
        score: Score value from session
        total: Total number of questions

    Returns:
        Validated score value
    """
    if not isinstance(score, int) or score < 0:
        return 0

    if score > total:
        return total

    return score
