"""
Tests for session_helpers.py module.

Note: These tests mock the Flask session object for testing purposes.
"""

import sys
import time
from pathlib import Path
from unittest.mock import MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock Flask session before importing session_helpers
sys.modules["flask"] = MagicMock()
mock_session = {}


def mock_session_get(key, default=None):
    """Mock session.get() method."""
    return mock_session.get(key, default)


def mock_session_setitem(key, value):
    """Mock session[key] = value."""
    mock_session[key] = value


def mock_session_getitem(key):
    """Mock session[key]."""
    if key not in mock_session:
        raise KeyError(key)
    return mock_session[key]


# Configure mock session
mock_session_obj = MagicMock()
mock_session_obj.get = mock_session_get
mock_session_obj.__setitem__ = lambda self, k, v: mock_session_setitem(k, v)
mock_session_obj.__getitem__ = lambda self, k: mock_session_getitem(k)
sys.modules["flask"].session = mock_session_obj

from session_helpers import (  # noqa: E402
    add_to_score,
    add_wrong_answer,
    get_current_question_data,
    get_review_data,
    get_score_data,
    get_server_timestamp,
    increment_question_index,
    initialize_test_session,
    sanitize_score,
    validate_client_timestamp,
    validate_time_remaining,
)


def reset_session():
    """Reset mock session between tests."""
    global mock_session
    mock_session = {}


def test_get_server_timestamp():
    """Test getting server timestamp."""
    print("\n" + "=" * 80)
    print("TEST: Get server timestamp")
    print("=" * 80)

    timestamp1 = get_server_timestamp()
    time.sleep(0.1)
    timestamp2 = get_server_timestamp()

    assert isinstance(timestamp1, float)
    assert isinstance(timestamp2, float)
    assert timestamp2 > timestamp1
    assert timestamp1 > 0
    print("✓ Server timestamp working correctly")


def test_validate_client_timestamp():
    """Test client timestamp validation for clock skew."""
    print("\n" + "=" * 80)
    print("TEST: Validate client timestamp")
    print("=" * 80)

    current_time = time.time()

    # Valid timestamps within tolerance
    assert validate_client_timestamp(current_time) is True
    assert validate_client_timestamp(current_time + 2) is True
    assert validate_client_timestamp(current_time - 3) is True
    print("✓ Timestamps within tolerance accepted")

    # Invalid timestamps beyond tolerance (default is 5 seconds)
    assert validate_client_timestamp(current_time + 10) is False
    assert validate_client_timestamp(current_time - 10) is False
    print("✓ Timestamps beyond tolerance rejected")

    # Custom tolerance
    past_time = current_time - 8
    assert validate_client_timestamp(past_time, tolerance_seconds=10) is True
    assert validate_client_timestamp(past_time, tolerance_seconds=5) is False
    print("✓ Custom tolerance works")

    # None handling
    assert validate_client_timestamp(None) is False
    print("✓ None timestamp rejected")


def test_initialize_test_session():
    """Test session initialization."""
    print("\n" + "=" * 80)
    print("TEST: Initialize test session")
    print("=" * 80)

    reset_session()

    selected_indices = [0, 3, 5, 7]
    shuffle_mappings = {0: {"order": [1, 0, 2], "correct_index": 1}}
    time_limit_minutes = 15
    shuffle_answers = True

    initialize_test_session(
        selected_indices,
        shuffle_mappings,
        time_limit_minutes,
        shuffle_answers,
    )

    # Check all session values are set correctly
    assert mock_session["selected_question_indices"] == selected_indices
    assert mock_session["current_question_index"] == 0
    assert mock_session["score"] == 0
    assert mock_session["wrong_answers"] == []
    assert mock_session["time_limit"] == 15 * 60  # 900 seconds
    assert mock_session["shuffle_mappings"] == shuffle_mappings
    assert mock_session["shuffle_answers"] is True
    assert "start_time" in mock_session
    assert isinstance(mock_session["start_time"], float)
    print("✓ Session initialized correctly")


def test_get_current_question_data():
    """Test getting current question data from session."""
    print("\n" + "=" * 80)
    print("TEST: Get current question data")
    print("=" * 80)

    reset_session()
    mock_session["current_question_index"] = 3
    mock_session["selected_question_indices"] = [1, 2, 3, 4]
    mock_session["shuffle_mappings"] = {1: {"order": [0, 1]}}

    q_index, selected, mappings = get_current_question_data()

    assert q_index == 3
    assert selected == [1, 2, 3, 4]
    assert mappings == {1: {"order": [0, 1]}}
    print("✓ Current question data retrieved correctly")


def test_increment_question_index():
    """Test incrementing question index."""
    print("\n" + "=" * 80)
    print("TEST: Increment question index")
    print("=" * 80)

    reset_session()
    mock_session["current_question_index"] = 0

    increment_question_index()
    assert mock_session["current_question_index"] == 1

    increment_question_index()
    assert mock_session["current_question_index"] == 2

    increment_question_index()
    assert mock_session["current_question_index"] == 3
    print("✓ Question index increments correctly")

    # Test when not set
    reset_session()
    increment_question_index()
    assert mock_session["current_question_index"] == 1
    print("✓ Handles missing initial index")


def test_add_to_score():
    """Test adding to score."""
    print("\n" + "=" * 80)
    print("TEST: Add to score")
    print("=" * 80)

    reset_session()
    mock_session["score"] = 0

    add_to_score()
    assert mock_session["score"] == 1

    add_to_score()
    assert mock_session["score"] == 2

    add_to_score()
    assert mock_session["score"] == 3
    print("✓ Score increments correctly")

    # Test when not set
    reset_session()
    add_to_score()
    assert mock_session["score"] == 1
    print("✓ Handles missing initial score")


def test_add_wrong_answer():
    """Test adding wrong answers."""
    print("\n" + "=" * 80)
    print("TEST: Add wrong answer")
    print("=" * 80)

    reset_session()
    mock_session["wrong_answers"] = []

    wrong1 = {"question_index": 0, "user_answer": 2}
    add_wrong_answer(wrong1)
    assert len(mock_session["wrong_answers"]) == 1
    assert mock_session["wrong_answers"][0] == wrong1

    wrong2 = {"question_index": 3, "user_answer": 1}
    add_wrong_answer(wrong2)
    assert len(mock_session["wrong_answers"]) == 2
    assert mock_session["wrong_answers"][1] == wrong2
    print("✓ Wrong answers added correctly")

    # Test when not set
    reset_session()
    add_wrong_answer(wrong1)
    assert len(mock_session["wrong_answers"]) == 1
    print("✓ Handles missing initial wrong_answers list")


def test_get_score_data():
    """Test getting score data."""
    print("\n" + "=" * 80)
    print("TEST: Get score data")
    print("=" * 80)

    reset_session()
    mock_session["score"] = 8
    mock_session["selected_question_indices"] = [0, 1, 2, 3, 4]
    mock_session["wrong_answers"] = [{"question_index": 2}]

    score, selected, wrong = get_score_data()

    assert score == 8
    assert selected == [0, 1, 2, 3, 4]
    assert wrong == [{"question_index": 2}]
    print("✓ Score data retrieved correctly")


def test_get_review_data():
    """Test getting review data."""
    print("\n" + "=" * 80)
    print("TEST: Get review data")
    print("=" * 80)

    reset_session()
    wrong_answers = [{"question_index": 1}, {"question_index": 3}]
    mappings = {1: {"order": [2, 0, 1]}}
    mock_session["wrong_answers"] = wrong_answers
    mock_session["shuffle_mappings"] = mappings

    wrong, shuffle = get_review_data()

    assert wrong == wrong_answers
    assert shuffle == mappings
    print("✓ Review data retrieved correctly")


def test_sanitize_score():
    """Test score sanitization."""
    print("\n" + "=" * 80)
    print("TEST: Sanitize score")
    print("=" * 80)

    # Valid scores
    assert sanitize_score(5, 10) == 5
    assert sanitize_score(0, 10) == 0
    assert sanitize_score(10, 10) == 10
    print("✓ Valid scores pass through")

    # Invalid scores
    assert sanitize_score(-5, 10) == 0
    assert sanitize_score("invalid", 10) == 0
    assert sanitize_score(None, 10) == 0
    print("✓ Invalid scores sanitized to 0")

    # Score exceeds total
    assert sanitize_score(15, 10) == 10
    assert sanitize_score(100, 10) == 10
    print("✓ Excessive scores capped to total")


def test_validate_time_remaining():
    """Test time remaining validation."""
    print("\n" + "=" * 80)
    print("TEST: Validate time remaining")
    print("=" * 80)

    # Test with valid time remaining
    reset_session()
    mock_session["start_time"] = time.time()
    mock_session["time_limit"] = 60  # 60 seconds

    is_valid, remaining = validate_time_remaining()
    assert is_valid is True
    assert remaining > 0
    assert remaining <= 60
    print("✓ Valid time remaining")

    # Test with expired time
    reset_session()
    mock_session["start_time"] = time.time() - 100  # 100 seconds ago
    mock_session["time_limit"] = 60  # 60 seconds limit

    is_valid, remaining = validate_time_remaining()
    assert is_valid is False
    assert remaining == 0
    print("✓ Expired time detected")

    # Test with missing start_time
    reset_session()
    is_valid, remaining = validate_time_remaining()
    assert is_valid is False
    assert remaining == 0
    print("✓ Missing start_time handled")


def main():
    """Run all tests."""
    print("=" * 80)
    print("Session Helpers Module Test Suite")
    print("=" * 80)

    test_get_server_timestamp()
    test_validate_client_timestamp()
    test_initialize_test_session()
    test_get_current_question_data()
    test_increment_question_index()
    test_add_to_score()
    test_add_wrong_answer()
    test_get_score_data()
    test_get_review_data()
    test_sanitize_score()
    test_validate_time_remaining()

    print("\n" + "=" * 80)
    print("✓ All session helpers tests passed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
