from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import random

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a secure key in production
app.config['SESSION_COOKIE_SIZE_LIMIT'] = 4000  # Set a safe limit

# Sample quiz data - in a real app, you might load this from a database or file

# Load quiz data from JSON file
with open('data/questions.json', 'r') as file:
    QUIZ_DATA = json.load(file)

# Store quiz data in a cache to avoid large session cookies
quiz_cache = {}


@app.route('/')
def index():
    """Render the homepage with category selection"""
    categories = [category['category'] for category in QUIZ_DATA]
    # Clear any existing quiz session data
    for key in ['quiz_id', 'current_question', 'score']:
        session.pop(key, None)
    return render_template('index.html', categories=categories)


@app.route('/quiz/<category>')
def quiz(category):
    """Render the quiz page for a specific category"""
    # Find the category data
    category_data = next((cat for cat in QUIZ_DATA if cat['category'] == category), None)

    if category_data is None:
        return "Category not found", 404

    # Create a quiz ID and store data in cache instead of session
    quiz_id = str(random.randint(10000, 99999))
    quiz_cache[quiz_id] = {
        'category': category,
        'questions': category_data['questions'],
        'current_question': 0,
        'score': 0,
        'answers': []  # To store user's answers
    }

    # Store only the quiz ID in session
    session['quiz_id'] = quiz_id

    return render_template('quiz.html', category=category)


@app.route('/get_question', methods=['GET'])
def get_question():
    """API endpoint to get the current question"""
    quiz_id = session.get('quiz_id')
    if not quiz_id or quiz_id not in quiz_cache:
        return jsonify({"error": "No active quiz"}), 400

    quiz_data = quiz_cache[quiz_id]

    if quiz_data['current_question'] >= len(quiz_data['questions']):
        return jsonify({"complete": True})

    # Get current question
    question_data = quiz_data['questions'][quiz_data['current_question']]
    # Don't send the correct answer to the client
    question_to_send = {
        "question": question_data["question"],
        "options": question_data["options"],
        "questionNumber": quiz_data['current_question'] + 1,
        "totalQuestions": len(quiz_data['questions'])
    }

    return jsonify(question_to_send)


@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    """API endpoint to submit an answer and get feedback"""
    quiz_id = session.get('quiz_id')
    if not quiz_id or quiz_id not in quiz_cache:
        return jsonify({"error": "No active quiz"}), 400

    quiz_data = quiz_cache[quiz_id]
    data = request.get_json()
    selected_option = data.get('answer')

    current_q_index = quiz_data['current_question']
    question_data = quiz_data['questions'][current_q_index]

    is_correct = selected_option == question_data["correctAnswer"]
    if is_correct:
        quiz_data['score'] += 1

    # Save the answer
    quiz_data['answers'].append({
        'question': question_data['question'],
        'selected': selected_option,
        'correct': is_correct,
        'correctAnswer': question_data['correctAnswer']
    })

    # Move to next question
    quiz_data['current_question'] += 1

    # Prepare response
    response = {
        "correct": is_correct,
        "correctAnswer": question_data["correctAnswer"],
        "explanation": question_data["explanation"],
        "sourceUrl": question_data["sourceUrl"],
        "nextQuestion": quiz_data['current_question'] < len(quiz_data['questions']),
        "score": quiz_data['score'],
        "totalQuestions": len(quiz_data['questions'])
    }

    return jsonify(response)


@app.route('/results')
def results():
    """Show quiz results"""
    quiz_id = session.get('quiz_id')
    if not quiz_id or quiz_id not in quiz_cache:
        # Redirect to home if no valid quiz
        return redirect(url_for('index'))

    quiz_data = quiz_cache[quiz_id]

    # Only show results if all questions have been answered
    if quiz_data['current_question'] < len(quiz_data['questions']):
        return redirect(url_for('quiz', category=quiz_data['category']))

    results_data = {
        "score": quiz_data['score'],
        "totalQuestions": len(quiz_data['questions']),
        "percentage": (quiz_data['score'] / len(quiz_data['questions'])) * 100,
        "category": quiz_data['category'],
        "answers": quiz_data['answers'],
        "questions": quiz_data['questions']
    }

    return render_template('results.html', results=results_data)


@app.route('/clear_quiz')
def clear_quiz():
    """Clear quiz data when starting a new quiz"""
    quiz_id = session.get('quiz_id')
    if quiz_id and quiz_id in quiz_cache:
        del quiz_cache[quiz_id]
    session.pop('quiz_id', None)
    return redirect(url_for('index'))


# Cleanup old quiz cache entries (would be called periodically in production)
def cleanup_quiz_cache():
    # Remove quizzes older than X time
    pass


if __name__ == '__main__':
    app.run(debug=True)