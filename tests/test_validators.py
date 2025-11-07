"""
Tests for validators.py module.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from validators import (  # noqa: E402
    ValidationError,
    validate_answer_index,
    validate_categories,
    validate_correct_answer_index,
    validate_num_questions,
    validate_question_data,
    validate_question_index_in_range,
    validate_session_question_index,
    validate_shuffle_option,
    validate_time_limit,
    validate_wrong_answer_entry,
)


def test_validate_categories():
    """Test category validation."""
    print("\n" + "=" * 80)
    print("TEST: Validate categories")
    print("=" * 80)

    valid_categories = ["Math", "Science", "History"]

    # Valid selections
    try:
        validate_categories(["Math"], valid_categories)
        print("✓ Single valid category passed")
    except ValidationError:
        raise AssertionError("Should not raise error for valid category")

    try:
        validate_categories(["Math", "Science"], valid_categories)
        print("✓ Multiple valid categories passed")
    except ValidationError:
        raise AssertionError("Should not raise error for valid categories")

    # Invalid selections
    try:
        validate_categories([], valid_categories)
        raise AssertionError("Should raise error for empty categories")
    except ValidationError as e:
        assert "at least one category" in e.message.lower()
        print("✓ Empty categories rejected")

    try:
        validate_categories(["InvalidCategory"], valid_categories)
        raise AssertionError("Should raise error for invalid category")
    except ValidationError as e:
        assert "invalid category" in e.message.lower()
        print("✓ Invalid category rejected")


def test_validate_num_questions():
    """Test number of questions validation."""
    print("\n" + "=" * 80)
    print("TEST: Validate number of questions")
    print("=" * 80)

    # Valid numbers
    result = validate_num_questions(5, 10)
    assert result == 5
    print("✓ Valid number within range")

    result = validate_num_questions(10, 10)
    assert result == 10
    print("✓ Max number of questions")

    # Invalid numbers
    try:
        validate_num_questions(0, 10)
        raise AssertionError("Should raise error for zero questions")
    except ValidationError as e:
        assert "at least 1" in e.message.lower()
        print("✓ Zero questions rejected")

    try:
        validate_num_questions(-5, 10)
        raise AssertionError("Should raise error for negative questions")
    except ValidationError as e:
        assert "at least 1" in e.message.lower()
        print("✓ Negative questions rejected")

    try:
        validate_num_questions(15, 10)
        raise AssertionError("Should raise error for exceeding available")
    except ValidationError as e:
        assert "10 questions available" in e.message
        print("✓ Too many questions rejected")

    try:
        validate_num_questions(None, 10)
        raise AssertionError("Should raise error for None")
    except ValidationError:
        print("✓ None value rejected")


def test_validate_time_limit():
    """Test time limit validation."""
    print("\n" + "=" * 80)
    print("TEST: Validate time limit")
    print("=" * 80)

    # Valid time limits
    result = validate_time_limit(10)
    assert result == 10
    print("✓ Valid time limit")

    result = validate_time_limit(1)
    assert result == 1
    print("✓ Minimum time limit")

    result = validate_time_limit(120)
    assert result == 120
    print("✓ Maximum time limit")

    # Invalid time limits
    try:
        validate_time_limit(0)
        raise AssertionError("Should raise error for zero")
    except ValidationError as e:
        assert "at least" in e.message.lower()
        print("✓ Zero time limit rejected")

    try:
        validate_time_limit(-5)
        raise AssertionError("Should raise error for negative")
    except ValidationError as e:
        assert "at least" in e.message.lower()
        print("✓ Negative time limit rejected")

    try:
        validate_time_limit(200)
        raise AssertionError("Should raise error for exceeding max")
    except ValidationError as e:
        assert "cannot exceed" in e.message.lower()
        print("✓ Excessive time limit rejected")

    try:
        validate_time_limit(None)
        raise AssertionError("Should raise error for None")
    except ValidationError:
        print("✓ None time limit rejected")


def test_validate_shuffle_option():
    """Test shuffle option validation."""
    print("\n" + "=" * 80)
    print("TEST: Validate shuffle option")
    print("=" * 80)

    # Valid options
    assert validate_shuffle_option("true") is True
    assert validate_shuffle_option("True") is True
    assert validate_shuffle_option("TRUE") is True
    print("✓ 'true' variations accepted")

    assert validate_shuffle_option("false") is False
    assert validate_shuffle_option("False") is False
    assert validate_shuffle_option("FALSE") is False
    print("✓ 'false' variations accepted")

    # Invalid options
    try:
        validate_shuffle_option("yes")
        raise AssertionError("Should raise error for invalid option")
    except ValidationError:
        print("✓ Invalid option 'yes' rejected")

    try:
        validate_shuffle_option("1")
        raise AssertionError("Should raise error for invalid option")
    except ValidationError:
        print("✓ Invalid option '1' rejected")


def test_validate_session_question_index():
    """Test session question index validation."""
    print("\n" + "=" * 80)
    print("TEST: Validate session question index")
    print("=" * 80)

    # Valid session data
    q_index, selected = validate_session_question_index(0, [1, 2, 3])
    assert q_index == 0
    assert selected == [1, 2, 3]
    print("✓ Valid session data")

    q_index, selected = validate_session_question_index(5, [0, 1, 2, 3, 4, 5, 6])
    assert q_index == 5
    print("✓ Valid higher index")

    # Invalid session data
    try:
        validate_session_question_index(None, [1, 2, 3])
        raise AssertionError("Should raise error for None index")
    except ValidationError as e:
        assert "invalid test session" in e.message.lower()
        print("✓ None index rejected")

    try:
        validate_session_question_index(0, None)
        raise AssertionError("Should raise error for None selected_indices")
    except ValidationError as e:
        assert "invalid test session" in e.message.lower()
        print("✓ None selected_indices rejected")

    try:
        validate_session_question_index(-1, [1, 2, 3])
        raise AssertionError("Should raise error for negative index")
    except ValidationError as e:
        assert "invalid question index" in e.message.lower()
        print("✓ Negative index rejected")

    try:
        validate_session_question_index(0, [])
        raise AssertionError("Should raise error for empty list")
    except ValidationError:
        print("✓ Empty selected_indices rejected")


def test_validate_question_index_in_range():
    """Test question index range validation."""
    print("\n" + "=" * 80)
    print("TEST: Validate question index in range")
    print("=" * 80)

    # Valid indices
    try:
        validate_question_index_in_range(0, 10)
        validate_question_index_in_range(5, 10)
        validate_question_index_in_range(9, 10)
        print("✓ Valid indices accepted")
    except ValidationError:
        raise AssertionError("Should not raise error for valid indices")

    # Invalid indices
    try:
        validate_question_index_in_range(-1, 10)
        raise AssertionError("Should raise error for negative index")
    except ValidationError as e:
        assert "invalid question reference" in e.message.lower()
        print("✓ Negative index rejected")

    try:
        validate_question_index_in_range(10, 10)
        raise AssertionError("Should raise error for out of range")
    except ValidationError as e:
        assert "invalid question reference" in e.message.lower()
        print("✓ Out of range index rejected")

    try:
        validate_question_index_in_range(100, 10)
        raise AssertionError("Should raise error for way out of range")
    except ValidationError:
        print("✓ Far out of range index rejected")


def test_validate_answer_index():
    """Test answer index validation."""
    print("\n" + "=" * 80)
    print("TEST: Validate answer index")
    print("=" * 80)

    # Valid indices
    assert validate_answer_index(0, 4) == 0
    assert validate_answer_index(2, 4) == 2
    assert validate_answer_index(3, 4) == 3
    print("✓ Valid answer indices accepted")

    # Invalid indices
    assert validate_answer_index(None, 4) is None
    print("✓ None returns None")

    assert validate_answer_index(-1, 4) is None
    print("✓ Negative index returns None")

    assert validate_answer_index(4, 4) is None
    assert validate_answer_index(10, 4) is None
    print("✓ Out of range indices return None")

    assert validate_answer_index("string", 4) is None
    print("✓ Non-integer returns None")


def test_validate_correct_answer_index():
    """Test correct answer index validation."""
    print("\n" + "=" * 80)
    print("TEST: Validate correct answer index")
    print("=" * 80)

    # Valid indices
    try:
        validate_correct_answer_index(0, 4)
        validate_correct_answer_index(2, 4)
        validate_correct_answer_index(3, 4)
        print("✓ Valid correct answer indices accepted")
    except ValidationError:
        raise AssertionError("Should not raise error for valid indices")

    # Invalid indices - should raise 500 errors
    try:
        validate_correct_answer_index(-1, 4)
        raise AssertionError("Should raise error for negative")
    except ValidationError as e:
        assert e.code == 500
        assert "invalid question configuration" in e.message.lower()
        print("✓ Negative index rejected with 500 error")

    try:
        validate_correct_answer_index(4, 4)
        raise AssertionError("Should raise error for out of range")
    except ValidationError as e:
        assert e.code == 500
        print("✓ Out of range rejected with 500 error")

    try:
        validate_correct_answer_index("string", 4)
        raise AssertionError("Should raise error for non-integer")
    except ValidationError as e:
        assert e.code == 500
        print("✓ Non-integer rejected with 500 error")


def test_validate_wrong_answer_entry():
    """Test wrong answer entry validation."""
    print("\n" + "=" * 80)
    print("TEST: Validate wrong answer entry")
    print("=" * 80)

    # Valid entries
    result = validate_wrong_answer_entry({"question_index": 0, "user_answer": 1}, 10)
    assert result == 0
    print("✓ Valid entry accepted")

    result = validate_wrong_answer_entry({"question_index": 5, "user_answer": 2}, 10)
    assert result == 5
    print("✓ Valid entry with higher index")

    # Invalid entries
    result = validate_wrong_answer_entry({"no_index": 0}, 10)
    assert result is None
    print("✓ Missing question_index returns None")

    result = validate_wrong_answer_entry({"question_index": None}, 10)
    assert result is None
    print("✓ None question_index returns None")

    result = validate_wrong_answer_entry({"question_index": -1}, 10)
    assert result is None
    print("✓ Negative index returns None")

    result = validate_wrong_answer_entry({"question_index": 100}, 10)
    assert result is None
    print("✓ Out of range index returns None")

    result = validate_wrong_answer_entry("not a dict", 10)
    assert result is None
    print("✓ Non-dict returns None")


def test_validate_question_data():
    """Test question data validation."""
    print("\n" + "=" * 80)
    print("TEST: Validate question data")
    print("=" * 80)

    # Valid question data
    try:
        validate_question_data(
            {
                "question": "Test?",
                "options": ["A", "B"],
                "correct_answer_index": 0,
            }
        )
        print("✓ Valid question data accepted")
    except ValidationError:
        raise AssertionError("Should not raise error for valid data")

    # Missing correct_answer_index
    try:
        validate_question_data(
            {
                "question": "Test?",
                "options": ["A", "B"],
            }
        )
        raise AssertionError("Should raise error for missing correct_answer_index")
    except ValidationError as e:
        assert e.code == 500
        assert "invalid question data" in e.message.lower()
        print("✓ Missing correct_answer_index rejected")

    # Missing options
    try:
        validate_question_data(
            {
                "question": "Test?",
                "correct_answer_index": 0,
            }
        )
        raise AssertionError("Should raise error for missing options")
    except ValidationError as e:
        assert e.code == 500
        print("✓ Missing options rejected")


def main():
    """Run all tests."""
    print("=" * 80)
    print("Validators Module Test Suite")
    print("=" * 80)

    test_validate_categories()
    test_validate_num_questions()
    test_validate_time_limit()
    test_validate_shuffle_option()
    test_validate_session_question_index()
    test_validate_question_index_in_range()
    test_validate_answer_index()
    test_validate_correct_answer_index()
    test_validate_wrong_answer_entry()
    test_validate_question_data()

    print("\n" + "=" * 80)
    print("✓ All validators tests passed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
