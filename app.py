import json
from flask import Flask, render_template, request, redirect, url_for, session

# Initialize the Flask application
app = Flask(__name__)
# A secret key is needed to use sessions, which store data between requests.
# Change this to a random string for a real application.
app.secret_key = 'your_very_secret_key'

def load_questions():
    """Load questions from the JSON file."""
    with open('data/questions.json', 'r') as f:
        return json.load(f)

def get_unique_categories(questions_list):
    """Extract unique categories from questions."""
    categories = set()
    for question in questions_list:
        if 'category' in question:
            categories.add(question['category'])
    return sorted(list(categories))

def get_category_counts(questions_list):
    """Count questions per category."""
    counts = {}
    for question in questions_list:
        category = question.get('category', 'Unknown')
        counts[category] = counts.get(category, 0) + 1
    return counts

questions = load_questions()

@app.route('/')
def start():
    """
    This is the landing page that displays the start screen.
    """
    categories = get_unique_categories(questions)
    category_counts = get_category_counts(questions)
    return render_template('start.html', 
                         total_questions=len(questions), 
                         categories=categories,
                         category_counts=category_counts)

@app.route('/start-test', methods=['POST'])
def start_test():
    """
    This route initializes the test state in the session
    and redirects to the first question.
    """
    import random
    import time
    
    # Get the selected categories
    selected_categories = request.form.getlist('categories')
    
    # Validate that at least one category is selected
    if not selected_categories:
        # Redirect back to start if no categories selected
        return redirect(url_for('start'))
    
    # Filter questions by selected categories
    filtered_questions = [q for q in questions if q.get('category') in selected_categories]
    
    # If no questions match the selected categories, use all questions
    if not filtered_questions:
        filtered_questions = questions
    
    # Get the number of questions requested (default to all filtered questions)
    num_questions = request.form.get('num_questions', type=int)
    
    # Validate the input
    if num_questions is None or num_questions < 1:
        num_questions = len(filtered_questions)
    elif num_questions > len(filtered_questions):
        num_questions = len(filtered_questions)
    
    # Get the time limit in minutes (default to 10, min 1, max 120)
    time_limit = request.form.get('time_limit', type=int)
    if time_limit is None or time_limit < 1:
        time_limit = 10
    elif time_limit > 120:
        time_limit = 120
    
    # Randomly select questions from the filtered pool
    selected_questions = random.sample(filtered_questions, num_questions)
    
    # Store only the indices of selected questions to reduce session size
    selected_indices = [questions.index(q) for q in selected_questions]
    
    # Store the selected question indices and test state in the session
    session['selected_question_indices'] = selected_indices
    session['current_question_index'] = 0
    session['score'] = 0
    session['wrong_answers'] = []  # Track wrong answers for review
    session['time_limit'] = time_limit * 60  # Convert to seconds
    session['start_time'] = time.time()  # Store the start time
    return redirect(url_for('show_question'))

@app.route('/question', methods=['GET', 'POST'])
def show_question():
    """
    This route handles both displaying the current question (GET) and
    checking the submitted answer (POST).
    """
    import time
    
    q_index = session.get('current_question_index', 0)
    selected_indices = session.get('selected_question_indices', [])
    start_time = session.get('start_time', time.time())
    time_limit = session.get('time_limit', 600)  # Default to 10 minutes
    
    # If no indices stored, use all questions (fallback)
    if not selected_indices:
        selected_indices = list(range(len(questions)))
    
    # Check if time has expired
    elapsed_time = time.time() - start_time
    if elapsed_time >= time_limit:
        # Time's up - redirect to score page
        return redirect(url_for('show_score'))

    # If the quiz is over, redirect to the score page
    if q_index >= len(selected_indices):
        return redirect(url_for('show_score'))

    current_question = questions[selected_indices[q_index]]

    if request.method == 'POST':
        # Check time again before processing answer
        elapsed_time = time.time() - start_time
        if elapsed_time >= time_limit:
            return redirect(url_for('show_score'))
        
        # User has submitted an answer
        user_answer = request.form.get('option')
        correct_answer_index = current_question['correct_answer_index']

        # Check if the submitted answer is correct
        if user_answer is not None and int(user_answer) == correct_answer_index:
            session['score'] += 1
        else:
            # Store wrong answer details for review
            wrong_answers = session.get('wrong_answers', [])
            wrong_answers.append({
                'question_index': selected_indices[q_index],
                'user_answer': int(user_answer) if user_answer is not None else None,
                'question_number': q_index + 1
            })
            session['wrong_answers'] = wrong_answers

        # Move to the next question
        session['current_question_index'] = q_index + 1
        return redirect(url_for('show_question'))

    # If it's a GET request, display the current question
    # Calculate remaining time in seconds
    remaining_time = int(time_limit - elapsed_time)
    
    return render_template(
        'question.html',
        question_data=current_question,
        question_number=q_index + 1,
        total_questions=len(selected_indices),
        remaining_time=remaining_time
    )

@app.route('/score')
def show_score():
    """Displays the final score to the user."""
    score = session.get('score', 0)
    selected_indices = session.get('selected_question_indices', [])
    wrong_answers = session.get('wrong_answers', [])
    total = len(selected_indices) if selected_indices else len(questions)
    percent = int((score / total) * 100) if total > 0 else 0
    has_wrong_answers = len(wrong_answers) > 0
    return render_template('score.html', percent=percent, score=score, total_questions=total, has_wrong_answers=has_wrong_answers)

@app.route('/review')
def review_wrong_answers():
    """Display all wrong answers for review."""
    wrong_answers = session.get('wrong_answers', [])
    if not wrong_answers:
        return redirect(url_for('show_score'))
    
    # Build a list of wrong answer details
    review_data = []
    for wrong in wrong_answers:
        question = questions[wrong['question_index']]
        review_data.append({
            'question_number': wrong['question_number'],
            'question': question,
            'user_answer': wrong['user_answer'],
            'correct_answer_index': question['correct_answer_index']
        })
    
    return render_template('review.html', review_data=review_data)

if __name__ == '__main__':
    # This allows you to run the app by executing `python app.py`
    app.run(debug=True)