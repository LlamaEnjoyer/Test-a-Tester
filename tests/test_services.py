"""
Tests for services.py module.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services import (  # noqa: E402
    apply_shuffle_mapping,
    build_review_data,
    calculate_score_percentage,
    create_shuffle_mappings,
    filter_questions_by_categories,
    get_correct_answer_index,
    prepare_question_for_display,
    process_answer,
    select_random_questions,
    validate_and_parse_user_answer,
)
from validators import ValidationError  # noqa: E402


def test_filter_questions_by_categories():
    """Test filtering questions by categories."""
    print("\n" + "=" * 80)
    print("TEST: Filter questions by categories")
    print("=" * 80)

    questions = [
        {"question": "Q1", "category": "Math"},
        {"question": "Q2", "category": "Science"},
        {"question": "Q3", "category": "Math"},
        {"question": "Q4", "category": "History"},
    ]

    # Test single category
    result = filter_questions_by_categories(questions, ["Math"])
    assert len(result) == 2
    assert all(q["category"] == "Math" for q in result)
    print("✓ Single category filter passed")

    # Test multiple categories
    result = filter_questions_by_categories(questions, ["Math", "Science"])
    assert len(result) == 3
    print("✓ Multiple categories filter passed")

    # Test no matching categories
    result = filter_questions_by_categories(questions, ["Geography"])
    assert len(result) == 0
    print("✓ Empty category filter passed")


def test_select_random_questions():
    """Test random question selection."""
    print("\n" + "=" * 80)
    print("TEST: Select random questions")
    print("=" * 80)

    questions = [{"question": f"Q{i}", "category": "Test"} for i in range(10)]

    # Test selecting subset
    result = select_random_questions(questions, 5)
    assert len(result) == 5
    assert all(q in questions for q in result)
    print("✓ Random selection of 5 questions passed")

    # Test selecting all
    result = select_random_questions(questions, 10)
    assert len(result) == 10
    print("✓ Selection of all questions passed")


def test_create_shuffle_mappings():
    """Test creation of shuffle mappings."""
    print("\n" + "=" * 80)
    print("TEST: Create shuffle mappings")
    print("=" * 80)

    questions = [
        {
            "question": "Q1",
            "options": ["A", "B", "C", "D"],
            "correct_answer_index": 2,
        },
        {
            "question": "Q2",
            "options": ["X", "Y", "Z"],
            "correct_answer_index": 0,
        },
    ]

    selected_indices = [0, 1]
    mappings = create_shuffle_mappings(selected_indices, questions)

    # Check mappings exist
    assert 0 in mappings
    assert 1 in mappings
    print("✓ Mappings created for all questions")

    # Check structure
    assert "order" in mappings[0]
    assert "correct_index" in mappings[0]
    assert len(mappings[0]["order"]) == 4
    print("✓ Mapping structure is correct")

    # Verify correct answer index is mapped correctly
    original_correct = questions[0]["correct_answer_index"]
    shuffled_order = mappings[0]["order"]
    new_correct = mappings[0]["correct_index"]
    assert shuffled_order[new_correct] == original_correct
    print("✓ Correct answer index properly mapped")


def test_apply_shuffle_mapping():
    """Test applying shuffle mapping to questions."""
    print("\n" + "=" * 80)
    print("TEST: Apply shuffle mapping")
    print("=" * 80)

    question = {
        "question": "Test question",
        "options": ["A", "B", "C", "D"],
        "correct_answer_index": 2,
    }

    # Test without shuffle mappings
    result = apply_shuffle_mapping(question.copy(), 0, None)
    assert result["options"] == ["A", "B", "C", "D"]
    assert result["correct_answer_index"] == 2
    print("✓ No shuffle mapping applied correctly")

    # Test with shuffle mappings
    mappings = {
        0: {
            "order": [3, 1, 0, 2],  # Specific shuffle order
            "correct_index": 3,
        }
    }
    result = apply_shuffle_mapping(question.copy(), 0, mappings)
    assert result["options"] == ["D", "B", "A", "C"]
    assert result["correct_answer_index"] == 3
    print("✓ Shuffle mapping applied correctly")


def test_get_correct_answer_index():
    """Test getting correct answer index with and without shuffling."""
    print("\n" + "=" * 80)
    print("TEST: Get correct answer index")
    print("=" * 80)

    questions = [
        {"correct_answer_index": 2},
        {"correct_answer_index": 0},
    ]

    # Without shuffle
    result = get_correct_answer_index(0, questions, None)
    assert result == 2
    print("✓ Correct index without shuffle")

    # With shuffle
    mappings = {0: {"correct_index": 3}}
    result = get_correct_answer_index(0, questions, mappings)
    assert result == 3
    print("✓ Correct index with shuffle")


def test_process_answer():
    """Test answer processing logic."""
    print("\n" + "=" * 80)
    print("TEST: Process answer")
    print("=" * 80)

    # Test correct answer
    is_correct, wrong_data = process_answer(2, 2, 5, 0)
    assert is_correct is True
    assert wrong_data is None
    print("✓ Correct answer processed")

    # Test wrong answer
    is_correct, wrong_data = process_answer(1, 2, 5, 0)
    assert is_correct is False
    assert wrong_data is not None
    assert wrong_data["question_index"] == 5
    assert wrong_data["user_answer"] == 1
    assert wrong_data["question_number"] == 1
    print("✓ Wrong answer processed")

    # Test unanswered (None)
    is_correct, wrong_data = process_answer(None, 2, 5, 0)
    assert is_correct is False
    assert wrong_data is not None
    assert wrong_data["user_answer"] is None
    print("✓ Unanswered question processed")


def test_calculate_score_percentage():
    """Test score percentage calculation."""
    print("\n" + "=" * 80)
    print("TEST: Calculate score percentage")
    print("=" * 80)

    assert calculate_score_percentage(8, 10) == 80
    assert calculate_score_percentage(10, 10) == 100
    assert calculate_score_percentage(0, 10) == 0
    assert calculate_score_percentage(3, 4) == 75
    assert calculate_score_percentage(5, 0) == 0  # Edge case: divide by zero
    print("✓ All percentage calculations passed")


def test_validate_and_parse_user_answer():
    """Test user answer validation and parsing."""
    print("\n" + "=" * 80)
    print("TEST: Validate and parse user answer")
    print("=" * 80)

    # Valid answers
    assert validate_and_parse_user_answer("0", 4) == 0
    assert validate_and_parse_user_answer("2", 4) == 2
    print("✓ Valid answers parsed correctly")

    # Invalid answers
    assert validate_and_parse_user_answer("", 4) is None
    assert validate_and_parse_user_answer(None, 4) is None
    assert validate_and_parse_user_answer("abc", 4) is None
    assert validate_and_parse_user_answer("5", 4) is None  # Out of range
    assert validate_and_parse_user_answer("-1", 4) is None  # Negative
    print("✓ Invalid answers handled correctly")


def test_prepare_question_for_display():
    """Test question preparation for display."""
    print("\n" + "=" * 80)
    print("TEST: Prepare question for display")
    print("=" * 80)

    questions = [
        {
            "question": "Q1",
            "options": ["A", "B", "C"],
            "correct_answer_index": 1,
        },
        {
            "question": "Q2",
            "options": ["X", "Y"],
            "correct_answer_index": 0,
        },
    ]

    selected_indices = [1, 0]

    # Test without shuffle
    result = prepare_question_for_display(0, selected_indices, questions, None)
    assert result["question"] == "Q2"
    assert result["options"] == ["X", "Y"]
    print("✓ Question prepared without shuffle")

    # Test with shuffle
    mappings = {1: {"order": [1, 0], "correct_index": 1}}
    result = prepare_question_for_display(0, selected_indices, questions, mappings)
    assert result["question"] == "Q2"
    assert result["options"] == ["Y", "X"]
    print("✓ Question prepared with shuffle")

    # Test invalid index
    try:
        prepare_question_for_display(10, selected_indices, questions, None)
        raise AssertionError("Should have raised ValidationError")
    except (ValidationError, IndexError):
        print("✓ Invalid index raises error")


def test_build_review_data():
    """Test building review data for wrong answers."""
    print("\n" + "=" * 80)
    print("TEST: Build review data")
    print("=" * 80)

    questions = [
        {
            "question": "Q1",
            "options": ["A", "B", "C"],
            "correct_answer_index": 1,
        },
        {
            "question": "Q2",
            "options": ["X", "Y", "Z"],
            "correct_answer_index": 0,
        },
    ]

    wrong_answers = [
        {
            "question_index": 0,
            "user_answer": 2,
            "question_number": 1,
        },
        {
            "question_index": 1,
            "user_answer": 1,
            "question_number": 2,
        },
    ]

    # Test without shuffle
    review_data = build_review_data(wrong_answers, questions, None)
    assert len(review_data) == 2
    assert review_data[0]["question"]["question"] == "Q1"
    assert review_data[0]["user_answer"] == 2
    assert review_data[0]["correct_answer_index"] == 1
    print("✓ Review data built without shuffle")

    # Test with invalid entries (should be skipped)
    invalid_wrong = [
        {"question_index": 999, "user_answer": 0, "question_number": 1},
        {"question_index": 0, "user_answer": 1, "question_number": 2},
    ]
    review_data = build_review_data(invalid_wrong, questions, None)
    assert len(review_data) == 1  # Only valid entry
    print("✓ Invalid review entries skipped")


def main():
    """Run all tests."""
    print("=" * 80)
    print("Services Module Test Suite")
    print("=" * 80)

    test_filter_questions_by_categories()
    test_select_random_questions()
    test_create_shuffle_mappings()
    test_apply_shuffle_mapping()
    test_get_correct_answer_index()
    test_process_answer()
    test_calculate_score_percentage()
    test_validate_and_parse_user_answer()
    test_prepare_question_for_display()
    test_build_review_data()

    print("\n" + "=" * 80)
    print("✓ All services tests passed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
