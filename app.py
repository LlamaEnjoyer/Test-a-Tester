import json
import os
import random
import secrets
import time
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize the Flask application
app = Flask(__name__)

# CRITICAL SECURITY FIX: Use a persistent secret key
# The secret key MUST be persistent across server restarts to maintain sessions
# Set SECRET_KEY environment variable or this will generate one and warn you
secret_key = os.environ.get("SECRET_KEY")
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
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2)
)

csrf = CSRFProtect(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

# Time limit settings
MAX_TIME_LIMIT_MINUTES = 120
MIN_TIME_LIMIT_MINUTES = 1
DEFAULT_TIME_LIMIT_MINUTES = 10


def load_questions():
    """Load questions from the JSON file."""
    # Get the directory where app.py is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    questions_file = os.path.join(base_dir, "data", "questions.json")

    # Check if file exists
    if not os.path.exists(questions_file):
        raise FileNotFoundError(f"Questions file not found: {questions_file}")

    try:
        with open(questions_file, "r", encoding="utf-8") as f:
            data = json.load(f)

            # Validate that we got a list
            if not isinstance(data, list) or len(data) == 0:
                raise ValueError("Questions file must contain a non-empty JSON array")

            return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in questions file: {e}") from e


def get_unique_categories(questions_list):
    """Extract unique categories from questions."""
    categories = set()
    for question in questions_list:
        if "category" in question:
            categories.add(question["category"])
    return sorted(list(categories))


def get_category_counts(questions_list):
    """Count questions per category."""
    counts = {}
    for question in questions_list:
        category = question.get("category", "Unknown")
        counts[category] = counts.get(category, 0) + 1
    return counts


def validate_time_remaining():
    """
    Validate server-side timer to prevent client-side manipulation.
    Returns (is_valid, remaining_time) tuple.
    """
    start_time = session.get("start_time")
    time_limit = session.get("time_limit", 600)
    
    if start_time is None:
        return False, 0
    
    elapsed_time = time.time() - start_time
    remaining_time = int(time_limit - elapsed_time)
    
    # Time has expired
    if remaining_time <= 0:
        return False, 0
    
    return True, remaining_time


def apply_shuffle_mapping(question, question_index, shuffle_mappings):
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


def validate_test_configuration(selected_categories, num_questions, time_limit, filtered_questions):
    """
    Validate user test configuration inputs.
    
    Args:
        selected_categories: List of selected category names
        num_questions: Number of questions requested
        time_limit: Time limit in minutes
        filtered_questions: List of questions matching selected categories
    
    Returns:
        Tuple of (is_valid: bool, error_message: str or None)
    """
    # Validate categories
    if not selected_categories or len(selected_categories) == 0:
        return False, "Please select at least one category"
    
    # Validate number of questions
    if num_questions is None or num_questions < 1:
        return False, "Number of questions must be at least 1"
    
    if num_questions > len(filtered_questions):
        return False, f"Only {len(filtered_questions)} questions available for selected categories"
    
    # Validate time limit
    if time_limit is None or time_limit < MIN_TIME_LIMIT_MINUTES:
        return False, f"Time limit must be at least {MIN_TIME_LIMIT_MINUTES} minute(s)"
    
    if time_limit > MAX_TIME_LIMIT_MINUTES:
        return False, f"Time limit cannot exceed {MAX_TIME_LIMIT_MINUTES} minutes"
    
    return True, None


questions = load_questions()


@app.route("/")
@limiter.limit("30 per minute")
def start():
    """
    This is the landing page that displays the start screen.
    """
    categories = get_unique_categories(questions)
    category_counts = get_category_counts(questions)
    return render_template(
        "start.html",
        total_questions=len(questions),
        categories=categories,
        category_counts=category_counts,
    )


@app.route("/start-test", methods=["POST"])
@limiter.limit("10 per minute")
def start_test():
    """
    This route initializes the test state in the session
    and redirects to the first question.
    """
    # BACKEND VALIDATION: Get and validate selected categories
    selected_categories = request.form.getlist("categories")
    
    # Validate categories exist and are non-empty
    if not selected_categories:
        app.logger.warning("No categories selected - validation failed")
        return render_template(
            "error.html",
            error_code=400,
            error_message="Please select at least one category"
        ), 400
    
    # Validate all selected categories are valid
    valid_categories = get_unique_categories(questions)
    for category in selected_categories:
        if category not in valid_categories:
            app.logger.warning("Invalid category submitted: %s", category)
            return render_template(
                "error.html",
                error_code=400,
                error_message="Invalid category selection"
            ), 400

    # Filter questions by selected categories
    filtered_questions = [
        q for q in questions if q.get("category") in selected_categories
    ]

    # If no questions match the selected categories, reject the request
    if not filtered_questions:
        app.logger.warning("No questions available for selected categories")
        return render_template(
            "error.html",
            error_code=400,
            error_message="No questions available for selected categories"
        ), 400

    # BACKEND VALIDATION: Get and validate number of questions
    num_questions = request.form.get("num_questions", type=int)

    # Validate num_questions is a positive integer
    if num_questions is None or not isinstance(num_questions, int):
        app.logger.warning("Invalid num_questions format")
        return render_template(
            "error.html",
            error_code=400,
            error_message="Number of questions must be a valid number"
        ), 400
    
    if num_questions < 1:
        app.logger.warning("Invalid num_questions value: %s", num_questions)
        return render_template(
            "error.html",
            error_code=400,
            error_message="Number of questions must be at least 1"
        ), 400
    
    if num_questions > len(filtered_questions):
        app.logger.warning("Requested questions (%s) exceeds available (%s)", 
                         num_questions, len(filtered_questions))
        return render_template(
            "error.html",
            error_code=400,
            error_message=f"Only {len(filtered_questions)} questions available for selected categories"
        ), 400
    
    # BACKEND VALIDATION: Get and validate time limit
    time_limit = request.form.get("time_limit", type=int)
    
    if time_limit is None or not isinstance(time_limit, int):
        app.logger.warning("Invalid time_limit format")
        return render_template(
            "error.html",
            error_code=400,
            error_message="Time limit must be a valid number"
        ), 400
    
    if time_limit < MIN_TIME_LIMIT_MINUTES:
        app.logger.warning("Time limit too low: %s", time_limit)
        return render_template(
            "error.html",
            error_code=400,
            error_message=f"Time limit must be at least {MIN_TIME_LIMIT_MINUTES} minute(s)"
        ), 400
    
    if time_limit > MAX_TIME_LIMIT_MINUTES:
        app.logger.warning("Time limit too high: %s", time_limit)
        return render_template(
            "error.html",
            error_code=400,
            error_message=f"Time limit cannot exceed {MAX_TIME_LIMIT_MINUTES} minutes"
        ), 400

    # Ensure num_questions doesn't exceed available questions (defensive)
    num_questions = min(num_questions, len(filtered_questions))
    
    # Ensure time_limit is within bounds (defensive)
    time_limit = max(MIN_TIME_LIMIT_MINUTES, min(time_limit, MAX_TIME_LIMIT_MINUTES))

    # BACKEND VALIDATION: Validate shuffle_answers is a boolean value
    shuffle_answers_str = request.form.get("shuffle_answers", "false").lower()
    if shuffle_answers_str not in ["true", "false"]:
        app.logger.warning("Invalid shuffle_answers value: %s", shuffle_answers_str)
        return render_template(
            "error.html",
            error_code=400,
            error_message="Invalid shuffle option"
        ), 400
    
    shuffle_answers = shuffle_answers_str == "true"

    # Randomly select questions from the filtered pool
    selected_questions = random.sample(filtered_questions, num_questions)

    # Store only the indices of selected questions to reduce session size
    selected_indices = [questions.index(q) for q in selected_questions]

    # If shuffle is enabled, create a mapping for answer shuffling
    if shuffle_answers:
        shuffle_mappings = {}
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
        session["shuffle_mappings"] = shuffle_mappings
    else:
        session["shuffle_mappings"] = {}

    # Store the selected question indices and test state in the session
    session["selected_question_indices"] = selected_indices
    session["current_question_index"] = 0
    session["score"] = 0
    session["wrong_answers"] = []  # Track wrong answers for review
    session["time_limit"] = time_limit * 60  # Convert to seconds
    session["start_time"] = time.time()  # Store the start time
    session["shuffle_answers"] = shuffle_answers
    return redirect(url_for("show_question"))


@app.route("/question", methods=["GET", "POST"])
@limiter.limit("60 per minute")
def show_question():
    """
    This route handles both displaying the current question (GET) and
    checking the submitted answer (POST).
    """
    # SERVER-SIDE TIMER VALIDATION - prevents client-side timer manipulation
    time_valid, remaining_time = validate_time_remaining()
    if not time_valid:
        # Time expired - redirect to score
        return redirect(url_for("show_score"))
    
    # BACKEND VALIDATION: Validate session data integrity
    q_index = session.get("current_question_index")
    selected_indices = session.get("selected_question_indices")
    shuffle_mappings = session.get("shuffle_mappings")
    
    # Validate session contains required data
    if q_index is None:
        app.logger.error("Missing current_question_index in session")
        return render_template(
            "error.html",
            error_code=400,
            error_message="Invalid test session. Please start a new test."
        ), 400
    
    if not selected_indices or not isinstance(selected_indices, list):
        app.logger.error("Invalid or missing selected_question_indices in session")
        return render_template(
            "error.html",
            error_code=400,
            error_message="Invalid test session. Please start a new test."
        ), 400
    
    # Validate q_index is within valid range
    if not isinstance(q_index, int) or q_index < 0:
        app.logger.error("Invalid current_question_index: %s", q_index)
        return render_template(
            "error.html",
            error_code=400,
            error_message="Invalid question index"
        ), 400

    # Validate q_index is within valid range
    if not isinstance(q_index, int) or q_index < 0:
        app.logger.error("Invalid current_question_index: %s", q_index)
        return render_template(
            "error.html",
            error_code=400,
            error_message="Invalid question index"
        ), 400

    # If the quiz is over, redirect to the score page
    if q_index >= len(selected_indices):
        return redirect(url_for("show_score"))
    
    # BACKEND VALIDATION: Validate the selected question index is valid
    current_question_index = selected_indices[q_index]
    
    if not isinstance(current_question_index, int) or current_question_index < 0 or current_question_index >= len(questions):
        app.logger.error("Invalid question index in selected_indices: %s", current_question_index)
        return render_template(
            "error.html",
            error_code=400,
            error_message="Invalid question reference"
        ), 400
    
    current_question = questions[current_question_index].copy()

    # Apply shuffling if enabled using helper function
    current_question = apply_shuffle_mapping(
        current_question, current_question_index, shuffle_mappings
    )

    if request.method == "POST":
        # Re-validate time on POST to prevent manipulation
        time_valid, _ = validate_time_remaining()
        if not time_valid:
            return redirect(url_for("show_score"))

        # BACKEND VALIDATION: User has submitted an answer - validate it thoroughly
        user_answer = request.form.get("option")

        # Determine the correct answer index (considering shuffle)
        if shuffle_mappings and current_question_index in shuffle_mappings:
            correct_answer_index = shuffle_mappings[current_question_index][
                "correct_index"
            ]
            # BACKEND VALIDATION: Validate shuffle mapping integrity
            if not isinstance(correct_answer_index, int):
                app.logger.error("Invalid correct_answer_index in shuffle_mappings")
                return render_template(
                    "error.html",
                    error_code=500,
                    error_message="Invalid test configuration"
                ), 500
        else:
            correct_answer_index = questions[current_question_index][
                "correct_answer_index"
            ]
        
        # BACKEND VALIDATION: Validate correct_answer_index is within bounds
        num_options = len(current_question.get("options", []))
        if not isinstance(correct_answer_index, int) or correct_answer_index < 0 or correct_answer_index >= num_options:
            app.logger.error("Invalid correct_answer_index: %s for question with %s options", 
                           correct_answer_index, num_options)
            return render_template(
                "error.html",
                error_code=500,
                error_message="Invalid question configuration"
            ), 500

        # Validate that an answer was actually provided
        if user_answer is None or user_answer == "":
            # No answer selected - treat as wrong
            wrong_answers = session.get("wrong_answers", [])
            wrong_answers.append(
                {
                    "question_index": current_question_index,
                    "user_answer": None,
                    "question_number": q_index + 1,
                }
            )
            session["wrong_answers"] = wrong_answers
        else:
            # BACKEND VALIDATION: Validate user_answer is a valid integer
            try:
                user_answer_int = int(user_answer)
            except (ValueError, TypeError):
                app.logger.warning("Invalid answer format submitted: %s", user_answer)
                # Invalid answer format - treat as wrong
                wrong_answers = session.get("wrong_answers", [])
                wrong_answers.append(
                    {
                        "question_index": current_question_index,
                        "user_answer": None,
                        "question_number": q_index + 1,
                    }
                )
                session["wrong_answers"] = wrong_answers
            else:
                # BACKEND VALIDATION: Validate user_answer is within valid option range
                if user_answer_int < 0 or user_answer_int >= num_options:
                    app.logger.warning("Answer index out of range: %s (max: %s)", 
                                     user_answer_int, num_options - 1)
                    # Out of range answer - treat as wrong
                    wrong_answers = session.get("wrong_answers", [])
                    wrong_answers.append(
                        {
                            "question_index": current_question_index,
                            "user_answer": None,
                            "question_number": q_index + 1,
                        }
                    )
                    session["wrong_answers"] = wrong_answers
                else:
                    # Valid answer - check if correct
                    if user_answer_int == correct_answer_index:
                        session["score"] = session.get("score", 0) + 1
                    else:
                        # Store wrong answer details for review
                        wrong_answers = session.get("wrong_answers", [])
                        wrong_answers.append(
                            {
                                "question_index": current_question_index,
                                "user_answer": user_answer_int,
                                "question_number": q_index + 1,
                            }
                        )
                        session["wrong_answers"] = wrong_answers

        # Move to the next question
        session["current_question_index"] = q_index + 1
        return redirect(url_for("show_question"))

    # If it's a GET request, display the current question
    # remaining_time is already calculated from validate_time_remaining()
    return render_template(
        "question.html",
        question_data=current_question,
        question_number=q_index + 1,
        total_questions=len(selected_indices),
        remaining_time=remaining_time,
    )


@app.route("/score")
@limiter.limit("30 per minute")
def show_score():
    """Displays the final score to the user."""
    # BACKEND VALIDATION: Validate session data
    score = session.get("score", 0)
    selected_indices = session.get("selected_question_indices", [])
    wrong_answers = session.get("wrong_answers", [])
    
    # Validate score is a non-negative integer
    if not isinstance(score, int) or score < 0:
        app.logger.warning("Invalid score in session: %s", score)
        score = 0
    
    # Validate selected_indices is a list
    if not isinstance(selected_indices, list):
        app.logger.error("Invalid selected_question_indices type")
        selected_indices = []
    
    # Calculate total, ensuring it's at least 1 to avoid division by zero
    total = len(selected_indices) if selected_indices else 1
    
    # Validate score doesn't exceed total
    if score > total:
        app.logger.warning("Score (%s) exceeds total questions (%s)", score, total)
        score = total
    
    # Calculate percentage
    percent = int((score / total) * 100) if total > 0 else 0
    
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
def review_wrong_answers():
    """Display all wrong answers for review."""
    wrong_answers = session.get("wrong_answers", [])
    
    # BACKEND VALIDATION: Ensure wrong_answers is a list
    if not isinstance(wrong_answers, list):
        app.logger.error("Invalid wrong_answers data type in session")
        return redirect(url_for("show_score"))
    
    if not wrong_answers:
        return redirect(url_for("show_score"))

    shuffle_mappings = session.get("shuffle_mappings")

    # Build a list of wrong answer details
    review_data = []
    for wrong in wrong_answers:
        # BACKEND VALIDATION: Validate each wrong answer entry
        if not isinstance(wrong, dict):
            app.logger.warning("Invalid wrong answer entry format")
            continue
        
        question_index = wrong.get("question_index")
        
        # Validate question_index exists and is valid
        if question_index is None or not isinstance(question_index, int):
            app.logger.warning("Invalid question_index in wrong answer: %s", question_index)
            continue
        
        if question_index < 0 or question_index >= len(questions):
            app.logger.warning("Question index out of range: %s", question_index)
            continue
        
        question = questions[question_index].copy()

        # Apply shuffling if it was enabled using helper function
        question = apply_shuffle_mapping(question, question_index, shuffle_mappings)
        
        # BACKEND VALIDATION: Ensure question has required fields
        if "correct_answer_index" not in question or "options" not in question:
            app.logger.warning("Question missing required fields: %s", question_index)
            continue
        
        correct_answer_index = question["correct_answer_index"]
        
        # Validate correct_answer_index is within bounds
        num_options = len(question.get("options", []))
        if not isinstance(correct_answer_index, int) or correct_answer_index < 0 or correct_answer_index >= num_options:
            app.logger.warning("Invalid correct_answer_index for question %s", question_index)
            continue
        
        # Validate user_answer if it exists
        user_answer = wrong.get("user_answer")
        if user_answer is not None:
            if not isinstance(user_answer, int) or user_answer < 0 or user_answer >= num_options:
                app.logger.warning("Invalid user_answer: %s", user_answer)
                user_answer = None  # Treat as unanswered

        review_data.append(
            {
                "question_number": wrong.get("question_number", 0),
                "question": question,
                "user_answer": user_answer,
                "correct_answer_index": correct_answer_index,
            }
        )

    return render_template("review.html", review_data=review_data)


# Error Handlers
@app.errorhandler(429)
def ratelimit_handler(_error):
    """Handle rate limit exceeded errors."""
    return render_template(
        "error.html", 
        error_code=429, 
        error_message="Too many requests. Please slow down and try again later."
    ), 429


@app.errorhandler(404)
def page_not_found(_error):
    """Handle 404 errors."""
    return render_template("error.html", error_code=404, error_message="Page not found"), 404


@app.errorhandler(500)
def internal_server_error(_error):
    """Handle 500 errors."""
    return render_template("error.html", error_code=500, error_message="Internal server error"), 500


@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all other exceptions."""
    # Log the error for debugging
    app.logger.error("Unhandled exception: %s", e, exc_info=True)
    
    # Return a generic error page
    return render_template("error.html", error_code=500, error_message="An unexpected error occurred"), 500


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "False").lower() == "true")
