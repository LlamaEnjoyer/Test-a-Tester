import os
import secrets
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from flask import Flask, redirect, render_template, request, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

from question_validator import QuestionValidationError, validate_questions_file
from services import (
    build_review_data,
    calculate_score_percentage,
    create_shuffle_mappings,
    filter_questions_by_categories,
    handle_answer_submission,
    prepare_question_for_display,
    select_random_questions,
    validate_and_parse_user_answer,
)
from session_helpers import (
    add_to_score,
    add_wrong_answer,
    get_current_question_data,
    get_review_data,
    get_score_data,
    increment_question_index,
    initialize_test_session,
    sanitize_score,
    validate_time_remaining,
)

# Import custom modules
from validators import (
    ValidationError,
    validate_categories,
    validate_num_questions,
    validate_session_question_index,
    validate_shuffle_option,
    validate_time_limit,
)

# Initialize the Flask application
app = Flask(__name__)

# CRITICAL SECURITY FIX: Use a persistent secret key
# The secret key MUST be persistent across server restarts to maintain sessions
# Set SECRET_KEY environment variable or this will generate one and warn you
secret_key: Optional[str] = os.environ.get("SECRET_KEY")
if not secret_key:
    # Generate a cryptographically secure random key
    secret_key = secrets.token_hex(32)
    print("=" * 80)
    print("WARNING: No SECRET_KEY environment variable set!")
    print("Using a temporary generated key. Sessions will be invalidated on restart.")
    print("For production, set SECRET_KEY environment variable to a secure random value.")
    print(f"Suggested: export SECRET_KEY='{secret_key}'")
    print("=" * 80)

app.secret_key = secret_key

# Production-ready session security settings
app.config.update(
    SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE", "False").lower() == "true",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
)

csrf = CSRFProtect(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window",
)

# Time limit settings
MAX_TIME_LIMIT_MINUTES = 120
MIN_TIME_LIMIT_MINUTES = 1
DEFAULT_TIME_LIMIT_MINUTES = 10


def load_questions() -> List[Dict[str, Any]]:
    """
    Load and validate questions from the JSON file.

    Returns:
        List of validated question dictionaries

    Raises:
        FileNotFoundError: If questions file is not found
        QuestionValidationError: If questions fail validation
        ValueError: For other data format errors
    """
    # Get the directory where app.py is located
    base_dir = Path(__file__).parent
    questions_file = base_dir / "data" / "questions.json"
    schema_file = base_dir / "data" / "questions_schema.json"

    # Validate and load questions with schema validation
    try:
        validated_questions = validate_questions_file(
            questions_file,
            schema_file,
            strict=True,  # Enable strict validation (answer indices, unique options)
        )

        # Additional basic validation
        if not isinstance(validated_questions, list) or len(validated_questions) == 0:
            raise ValueError("Questions file must contain a non-empty JSON array")

        print(f"✓ Successfully loaded and validated {len(validated_questions)} questions")
        return validated_questions

    except QuestionValidationError as e:
        print("=" * 80)
        print("ERROR: Questions data validation failed!")
        print("=" * 80)
        print(str(e))
        print("=" * 80)
        raise


def get_unique_categories(questions_list: List[Dict[str, Any]]) -> List[str]:
    """Extract unique categories from questions."""
    categories: Set[str] = set()
    for question in questions_list:
        if "category" in question:
            categories.add(question["category"])
    return sorted(categories)


def get_category_counts(questions_list: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count questions per category."""
    counts: Dict[str, int] = {}
    for question in questions_list:
        category = question.get("category", "Unknown")
        counts[category] = counts.get(category, 0) + 1
    return counts


questions: List[Dict[str, Any]] = load_questions()


@app.route("/")
@limiter.limit("30 per minute")
def start() -> str:
    """
    This is the landing page that displays the start screen.
    """
    categories: List[str] = get_unique_categories(questions)
    category_counts: Dict[str, int] = get_category_counts(questions)
    return render_template(
        "start.html",
        total_questions=len(questions),
        categories=categories,
        category_counts=category_counts,
    )


@app.route("/start-test", methods=["POST"])
@limiter.limit("10 per minute")
def start_test() -> Any:
    """
    Initialize the test state and redirect to the first question.
    """
    try:
        # Get and validate selected categories
        selected_categories: List[str] = request.form.getlist("categories")
        valid_categories: List[str] = get_unique_categories(questions)
        validate_categories(selected_categories, valid_categories)

        # Filter questions by selected categories
        filtered_questions: List[Dict[str, Any]] = filter_questions_by_categories(
            questions, selected_categories
        )

        if not filtered_questions:
            raise ValidationError("No questions available for selected categories")

        # Get and validate number of questions
        num_questions: Optional[int] = request.form.get("num_questions", type=int)
        num_questions = validate_num_questions(num_questions, len(filtered_questions))

        # Get and validate time limit
        time_limit: Optional[int] = request.form.get("time_limit", type=int)
        time_limit = validate_time_limit(time_limit)

        # Get and validate shuffle option
        shuffle_answers_str: str = request.form.get("shuffle_answers", "false")
        shuffle_answers: bool = validate_shuffle_option(shuffle_answers_str)

        # Select random questions
        selected_questions: List[Dict[str, Any]] = select_random_questions(
            filtered_questions, num_questions
        )
        selected_indices: List[int] = [questions.index(q) for q in selected_questions]

        # Create shuffle mappings if needed
        shuffle_mappings: Dict[int, Dict[str, Any]] = {}
        if shuffle_answers:
            shuffle_mappings = create_shuffle_mappings(selected_indices, questions)

        # Initialize session
        initialize_test_session(selected_indices, shuffle_mappings, time_limit, shuffle_answers)

        return redirect(url_for("show_question"))

    except ValidationError as e:
        app.logger.warning("Validation error: %s", e.message)
        return (
            render_template("error.html", error_code=e.code, error_message=e.message),
            e.code,
        )


@app.route("/question", methods=["GET"])
@limiter.limit("60 per minute")
def show_question() -> Any:
    """
    Display the current question.
    """
    try:
        # Validate time remaining
        time_valid, remaining_time = validate_time_remaining()
        if not time_valid:
            return redirect(url_for("show_score"))

        # Get and validate session data
        q_index, selected_indices, shuffle_mappings = get_current_question_data()
        q_index, selected_indices = validate_session_question_index(q_index, selected_indices)

        # Check if quiz is complete
        if q_index >= len(selected_indices):
            return redirect(url_for("show_score"))

        # Prepare question for display
        current_question = prepare_question_for_display(
            q_index, selected_indices, questions, shuffle_mappings
        )

        # Render question template
        return render_template(
            "question.html",
            question_data=current_question,
            question_number=q_index + 1,
            total_questions=len(selected_indices),
            remaining_time=remaining_time,
        )

    except ValidationError as e:
        app.logger.error("Validation error in show_question: %s", e.message)
        return (
            render_template("error.html", error_code=e.code, error_message=e.message),
            e.code,
        )


@app.route("/submit-answer", methods=["POST"])
@limiter.limit("60 per minute")
def submit_answer() -> Any:
    """
    Process the submitted answer and advance to the next question.
    """
    try:
        # Validate time remaining
        time_valid, _ = validate_time_remaining()
        if not time_valid:
            return redirect(url_for("show_score"))

        # Get and validate session data
        q_index, selected_indices, shuffle_mappings = get_current_question_data()
        q_index, selected_indices = validate_session_question_index(q_index, selected_indices)

        # Check if quiz is complete
        if q_index >= len(selected_indices):
            return redirect(url_for("show_score"))

        # Prepare current question (needed for validation)
        current_question = prepare_question_for_display(
            q_index, selected_indices, questions, shuffle_mappings
        )
        current_question_index = selected_indices[q_index]

        # Parse and validate user answer
        user_answer_str = request.form.get("option")
        num_options = len(current_question.get("options", []))
        user_answer_int = validate_and_parse_user_answer(user_answer_str, num_options)

        if user_answer_int is None:
            app.logger.warning("Invalid answer format: %s", user_answer_str)

        # Handle answer submission
        is_correct, wrong_answer_data = handle_answer_submission(
            user_answer_int,
            current_question_index,
            q_index,
            questions,
            shuffle_mappings,
            current_question,
        )

        # Update session based on answer
        if is_correct:
            add_to_score()
        elif wrong_answer_data is not None:
            add_wrong_answer(wrong_answer_data)

        # Move to next question
        increment_question_index()
        return redirect(url_for("show_question"))

    except ValidationError as e:
        app.logger.error("Validation error in submit_answer: %s", e.message)
        return (
            render_template("error.html", error_code=e.code, error_message=e.message),
            e.code,
        )


@app.route("/score")
@limiter.limit("30 per minute")
def show_score() -> str:
    """Displays the final score to the user."""
    score, selected_indices, wrong_answers = get_score_data()

    # Validate and sanitize score
    if not isinstance(score, int) or score < 0:
        app.logger.warning("Invalid score in session: %s", score)
        score = 0

    # Validate selected_indices is a list
    if not isinstance(selected_indices, list):
        app.logger.error("Invalid selected_question_indices type")
        selected_indices = []

    # Calculate total, ensuring it's at least 1 to avoid division by zero
    total = len(selected_indices) if selected_indices else 1

    # Sanitize score
    score = sanitize_score(score, total)

    # Calculate percentage
    percent = calculate_score_percentage(score, total)

    # Validate wrong_answers is a list
    has_wrong_answers = isinstance(wrong_answers, list) and len(wrong_answers) > 0

    return render_template(
        "score.html",
        percent=percent,
        score=score,
        total_questions=total,
        has_wrong_answers=has_wrong_answers,
    )


@app.route("/review")
@limiter.limit("30 per minute")
def review_wrong_answers() -> Any:
    """Display all wrong answers for review."""
    wrong_answers, shuffle_mappings = get_review_data()

    # BACKEND VALIDATION: Ensure wrong_answers is a list
    if not isinstance(wrong_answers, list):
        app.logger.error("Invalid wrong_answers data type in session")
        return redirect(url_for("show_score"))

    if not wrong_answers:
        return redirect(url_for("show_score"))

    # Build review data using service function
    review_data = build_review_data(wrong_answers, questions, shuffle_mappings)

    return render_template("review.html", review_data=review_data)


# Error Handlers
@app.errorhandler(429)
def ratelimit_handler(_error: Any) -> Tuple[str, int]:
    """Handle rate limit exceeded errors."""
    return (
        render_template(
            "error.html",
            error_code=429,
            error_message="Too many requests. Please slow down and try again later.",
        ),
        429,
    )


@app.errorhandler(404)
def page_not_found(_error: Any) -> Tuple[str, int]:
    """Handle 404 errors."""
    return render_template("error.html", error_code=404, error_message="Page not found"), 404


@app.errorhandler(500)
def internal_server_error(_error: Any) -> Tuple[str, int]:
    """Handle 500 errors."""
    return render_template("error.html", error_code=500, error_message="Internal server error"), 500


@app.errorhandler(Exception)
def handle_exception(e: Exception) -> Tuple[str, int]:
    """Handle all other exceptions."""
    # Log the error for debugging
    app.logger.error("Unhandled exception: %s", e, exc_info=True)

    # Return a generic error page
    return (
        render_template("error.html", error_code=500, error_message="An unexpected error occurred"),
        500,
    )


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "False").lower() == "true")
