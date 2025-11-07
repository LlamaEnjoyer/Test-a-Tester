import json
import os
import random
import secrets
import time
from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf.csrf import CSRFProtect

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
csrf = CSRFProtect(app)

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


questions = load_questions()


@app.route("/")
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
def start_test():
    """
    This route initializes the test state in the session
    and redirects to the first question.
    """
    # Get the selected categories
    selected_categories = request.form.getlist("categories")

    # Validate that at least one category is selected
    if not selected_categories:
        # Redirect back to start if no categories selected
        return redirect(url_for("start"))

    # Filter questions by selected categories
    filtered_questions = [
        q for q in questions if q.get("category") in selected_categories
    ]

    # If no questions match the selected categories, use all questions
    if not filtered_questions:
        filtered_questions = questions

    # Get the number of questions requested (default to all filtered questions)
    num_questions = request.form.get("num_questions", type=int)

    # Validate the input
    if num_questions is None or num_questions < 1:
        num_questions = len(filtered_questions)
    elif num_questions > len(filtered_questions):
        num_questions = len(filtered_questions)

    # Get the time limit in minutes (default to 10, min 1, max 120)
    time_limit = request.form.get("time_limit", type=int)
    if time_limit is None or time_limit < 1:
        time_limit = DEFAULT_TIME_LIMIT_MINUTES
    elif time_limit > MAX_TIME_LIMIT_MINUTES:
        time_limit = MAX_TIME_LIMIT_MINUTES

    # Get the shuffle answers option
    shuffle_answers = request.form.get("shuffle_answers") == "true"

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
        session["shuffle_mappings"] = None

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
    
    q_index = session.get("current_question_index", 0)
    selected_indices = session.get("selected_question_indices", [])
    shuffle_mappings = session.get("shuffle_mappings")

    # If no indices stored, use all questions (fallback)
    if not selected_indices:
        selected_indices = list(range(len(questions)))

    # If the quiz is over, redirect to the score page
    if q_index >= len(selected_indices):
        return redirect(url_for("show_score"))

    current_question_index = selected_indices[q_index]
    current_question = questions[current_question_index].copy()

    # Apply shuffling if enabled
    if shuffle_mappings and current_question_index in shuffle_mappings:
        mapping = shuffle_mappings[current_question_index]
        shuffled_order = mapping["order"]
        # Reorder options according to the shuffle mapping
        original_options = current_question["options"]
        current_question["options"] = [original_options[i] for i in shuffled_order]
        # Use the new correct answer index for display
        current_question["correct_answer_index"] = mapping["correct_index"]

    if request.method == "POST":
        # Re-validate time on POST to prevent manipulation
        time_valid, _ = validate_time_remaining()
        if not time_valid:
            return redirect(url_for("show_score"))

        # User has submitted an answer
        user_answer = request.form.get("option")

        # Determine the correct answer index (considering shuffle)
        if shuffle_mappings and current_question_index in shuffle_mappings:
            correct_answer_index = shuffle_mappings[current_question_index][
                "correct_index"
            ]
        else:
            correct_answer_index = questions[current_question_index][
                "correct_answer_index"
            ]

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
            # Check if the submitted answer is correct
            try:
                user_answer_int = int(user_answer)
                if user_answer_int == correct_answer_index:
                    session["score"] += 1
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
            except ValueError:
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
def show_score():
    """Displays the final score to the user."""
    score = session.get("score", 0)
    selected_indices = session.get("selected_question_indices", [])
    wrong_answers = session.get("wrong_answers", [])
    total = len(selected_indices) if selected_indices else len(questions)
    percent = int((score / total) * 100) if total > 0 else 0
    has_wrong_answers = len(wrong_answers) > 0
    return render_template(
        "score.html",
        percent=percent,
        score=score,
        total_questions=total,
        has_wrong_answers=has_wrong_answers,
    )


@app.route("/review")
def review_wrong_answers():
    """Display all wrong answers for review."""
    wrong_answers = session.get("wrong_answers", [])
    if not wrong_answers:
        return redirect(url_for("show_score"))

    shuffle_mappings = session.get("shuffle_mappings")

    # Build a list of wrong answer details
    review_data = []
    for wrong in wrong_answers:
        question_index = wrong["question_index"]
        question = questions[question_index].copy()

        # Apply shuffling if it was enabled
        if shuffle_mappings and question_index in shuffle_mappings:
            mapping = shuffle_mappings[question_index]
            shuffled_order = mapping["order"]
            original_options = question["options"]
            question["options"] = [original_options[i] for i in shuffled_order]
            correct_answer_index = mapping["correct_index"]
        else:
            correct_answer_index = question["correct_answer_index"]

        review_data.append(
            {
                "question_number": wrong["question_number"],
                "question": question,
                "user_answer": wrong["user_answer"],
                "correct_answer_index": correct_answer_index,
            }
        )

    return render_template("review.html", review_data=review_data)


# Error Handlers
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
