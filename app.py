from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import random

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a secure key in production
app.config['SESSION_COOKIE_SIZE_LIMIT'] = 4000  # Set a safe limit

# Sample quiz data - in a real app, you might load this from a database or file
QUIZ_DATA = [
    {
        "category": "Microsoft Fabric Lakehouse ",
        "questions": [
            {
                "question": "What is the primary purpose of OneLake in Microsoft Fabric?",
                "options": [
                    "To provide a unified storage solution for all analytics engines in Fabric",
                    "To act as a data integration tool for moving data between systems",
                    "To serve as a standalone data warehouse solution",
                    "To manage compute resources for Fabric workspaces"
                ],
                "correctAnswer": 0,
                "explanation": "OneLake is designed to provide a single, integrated storage environment for all analytics engines in Fabric, eliminating the need to move or copy data between systems.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/introduction-end-analytics-use-microsoft-fabric/2-explore-analytics-fabric"
            },
            {
                "question": "What feature of OneLake allows users to reference existing cloud data without copying it?",
                "options": [
                    "Data lineage",
                    "Shortcuts",
                    "Dataflows",
                    "Workspaces"
                ],
                "correctAnswer": 1,
                "explanation": "Shortcuts in OneLake enable users to create embedded references to existing data sources, facilitating easy access without duplication.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/introduction-end-analytics-use-microsoft-fabric/2-explore-analytics-fabric"
            },
            {
                "question": "What is the primary purpose of a workspace in Microsoft Fabric?",
                "options": [
                    "To store data permanently",
                    "To create and manage collaborative items",
                    "To perform data analysis",
                    "To configure Azure settings"
                ],
                "correctAnswer": 1,
                "explanation": "A workspace serves as a collaborative environment for creating and managing items like lakehouses, warehouses, and reports.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/introduction-end-analytics-use-microsoft-fabric/4-use-fabric"
            },
            {
                "question": "What feature do lakehouses support to ensure data consistency and integrity?",
                "options": [
                    "Schema-on-write",
                    "ACID transactions through Delta Lake formatted tables",
                    "Only read-only access",
                    "Data replication across multiple regions"
                ],
                "correctAnswer": 1,
                "explanation": "Lakehouses support ACID transactions, which are essential for maintaining data consistency and integrity.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-lakehouses/2-fabric-lakehouse"
            },
            {
                "question": "How is access to a Fabric lakehouse typically managed?",
                "options": [
                    "Through individual user accounts only",
                    "Using workspace roles and item-level sharing",
                    "Exclusively via API keys",
                    "Through Azure Active Directory groups only"
                ],
                "correctAnswer": 1,
                "explanation": "Access to a Fabric lakehouse is managed through workspace roles for collaborators and item-level sharing for read-only needs.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-lakehouses/2-fabric-lakehouse"
            },
            {
                "question": "What is the purpose of the partitionBy method when saving a DataFrame?",
                "options": [
                    "To specify the file format",
                    "To optimize performance by partitioning data",
                    "To define the schema",
                    "To overwrite existing files"
                ],
                "correctAnswer": 1,
                "explanation": "The partitionBy method is used to optimize performance by partitioning the data into separate folders based on the specified column values.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/use-apache-spark-work-files-lakehouse/4-dataframe"
            }
            ]
    },

{
        "category": "Microsoft Fabric Warehouse",
        "questions": [
            {
                "question": "Which schema design is characterized by a fact table directly related to dimension tables?",
                "options": [
                    "Snowflake schema",
                    "Star schema",
                    "Galaxy schema",
                    "Hybrid schema"
                ],
                "correctAnswer": 1,
                "explanation": "The star schema is defined by its structure where a central fact table is directly connected to multiple dimension tables, facilitating efficient queries.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-data-warehouse/2-understand-data-warehouse"
            },
            {
                "question": "What is the role of surrogate keys in dimension tables?",
                "options": [
                    "To provide a natural identifier from the source system",
                    "To uniquely identify each row in the dimension table",
                    "To track changes in dimension attributes over time",
                    "To aggregate data over temporal intervals"
                ],
                "correctAnswer": 1,
                "explanation": "Surrogate keys serve as unique identifiers for each row in a dimension table, ensuring consistency and accuracy within the data warehouse.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-data-warehouse/2-understand-data-warehouse"
            },
            {
                "question": "Which of the following is a benefit of using zero-copy table clones in a data warehouse?",
                "options": [
                    "Increased storage costs",
                    "Faster data ingestion",
                    "Minimal storage costs while referencing the same data",
                    "Automatic data cleansing"
                ],
                "correctAnswer": 2,
                "explanation": "Zero-copy table clones allow for minimal storage costs because they reference the same underlying data files without duplicating them.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-data-warehouse/3-understand-data-warehouse-fabric"
            },
            {
                "question": "What is the purpose of a semantic model in a data warehouse?",
                "options": [
                    "To define relationships and calculations for data insights",
                    "To store raw data without any transformations",
                    "To visualize data without any reporting tools",
                    "To manage user permissions in the data warehouse"
                ],
                "correctAnswer": 0,
                "explanation": "A semantic model is designed to define relationships between tables, aggregation rules, and calculations for deriving insights from data.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-data-warehouse/5-model-data"
            },
            {
                "question": "Which dynamic management view (DMV) would you use to get information about active requests in a session?",
                "options": [
                    "sys.dm_exec_connections",
                    "sys.dm_exec_sessions",
                    "sys.dm_exec_requests",
                    "sys.dm_exec_queries"
                ],
                "correctAnswer": 2,
                "explanation": "The sys.dm_exec_requests DMV provides details about each active request in a session, allowing for monitoring of ongoing operations.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-data-warehouse/6-security-monitor"
            },
            {
                "question": "What permission must a user have at a minimum to connect to the SQL analytics endpoint?",
                "options": [
                    "ReadData",
                    "ReadAll",
                    "Read",
                    "Write"
                ],
                "correctAnswer": 2,
                "explanation": "The Read permission is essential for establishing a connection to the SQL analytics endpoint, as it allows the user to connect using the SQL connection string.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/get-started-data-warehouse/6-security-monitor"
            },
            {
                "question": "Which type of slowly changing dimension (SCD) keeps full history for a given natural key?",
                "options": [
                    "Type 0 SCD",
                    "Type 1 SCD",
                    "Type 2 SCD",
                    "Type 3 SCD"
                ],
                "correctAnswer": 2,
                "explanation": "Type 2 SCD adds new records for changes and keeps full history for a given natural key, allowing for historical analysis.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/load-data-into-microsoft-fabric-data-warehouse/2-explore-data-load-strategies"
            },
            {
                "question": "What is the purpose of the REJECTED_ROW_LOCATION option in the COPY statement?",
                "options": [
                    "To specify the format of the source file",
                    "To store rejected rows separately",
                    "To skip header rows",
                    "To define the target table"
                ],
                "correctAnswer": 1,
                "explanation": "The REJECTED_ROW_LOCATION option allows for better error handling by storing rows that were not successfully imported.",
                "sourceUrl": "https://learn.microsoft.com/en-us/training/modules/load-data-into-microsoft-fabric-data-warehouse/4-load-data-using-tsql"
            }
            ]
},

{
    "category": "Microsoft Fabric RTI",
    "questions": [
        {
            "question": "Coming Soon",
            "options": [],
            "correctAnswer": "null",
            "explanation": "",
            "sourceUrl": ""
        }
    ]
}
]
# Store quiz data in a cache to avoid large session cookies
quiz_cache = {}


@app.route('/')
def index():
    """Render the homepage with category selection"""
    categories = [category['category'] for category in QUIZ_DATA]
    # Clear any existing quiz session data
    for key in ['quiz_id', 'current_question', 'score']:
        if key in session:
            session.pop(key)
    return render_template('index.html', categories=categories)


@app.route('/quiz/<category>')
def quiz(category):
    """Render the quiz page for a specific category"""
    # Find the category data
    category_data = None
    for cat in QUIZ_DATA:
        if cat['category'] == category:
            category_data = cat
            break

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
    if 'quiz_id' in session:
        session.pop('quiz_id')
    return redirect(url_for('index'))


# Cleanup old quiz cache entries (would be called periodically in production)
def cleanup_quiz_cache():
    # Remove quizzes older than X time
    pass


if __name__ == '__main__':
    app.run(debug=True)