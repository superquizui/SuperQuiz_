import requests
from flask import Blueprint, request, jsonify
from .models import User, Quiz, Question, UserAnswer, db
from .solana import SolanaService

main_bp = Blueprint('main', __name__)

# Initialize SolanaService with config
solana_service = SolanaService(
    url=Config.SOLANA_URL,
    secret_key=os.getenv('SOLANA_PRIVATE_KEY')
)

# Example Crypto Quiz API endpoint
CRYPTO_QUIZ_API_URL = "https://example.com/api/crypto-quiz"  # Replace with actual API URL

# Tatum API URL for token data
TATUM_API_URL = "https://api.tatum.io/v4/data/tokens?chain=ethereum"

# Tatum API key
TATUM_API_KEY = "t-66a730ccccfd17001c479705-2f597d14ad7543f289a03418"

# User registration route
@main_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    new_user = User(username=data['username'], wallet_address=data['wallet_address'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

# Take quiz and send Blinks as reward
@main_bp.route('/quiz/<int:quiz_id>/take', methods=['POST'])
def take_quiz(quiz_id):
    user_id = request.json.get('user_id')
    answers = request.json.get('answers')

    correct_answers = 0

    # Evaluate the user's answers
    for answer in answers:
        question = Question.query.get(answer['question_id'])
        is_correct = (question.correct_answer == answer['answer'])
        correct_answers += 1 if is_correct else 0

        # Record the user's answer
        user_answer = UserAnswer(
            user_id=user_id,
            question_id=answer['question_id'],
            answer=answer['answer'],
            is_correct=is_correct
        )
        db.session.add(user_answer)

    db.session.commit()

    # Calculate reward based on correct answers
    reward = correct_answers * 0.1  # Example: 0.1 Blink per correct answer
    user = User.query.get(user_id)
    user.blinks += reward
    db.session.commit()

    # Send Blinks to the user's wallet
    if solana_service.send_blinks(user.wallet_address, reward):
        return jsonify({'message': 'Quiz completed, Blinks sent!'}), 200
    else:
        return jsonify({'message': 'Failed to send Blinks'}), 500

# Route to fetch and add crypto quiz questions from an external API
@main_bp.route('/quiz/<int:quiz_id>/add_crypto_questions', methods=['POST'])
def add_crypto_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    # Fetch questions from the external API
    try:
        response = requests.get(CRYPTO_QUIZ_API_URL)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch questions from the external API: {str(e)}'}), 500

    questions_data = response.json()

    for question_data in questions_data:
        question = Question(
            quiz_id=quiz.id,
            text=question_data['question'],
            correct_answer=question_data['correct_answer']
        )
        db.session.add(question)

    db.session.commit()

    return jsonify({'message': 'Crypto questions added successfully'}), 201

# Route to fetch token data from Tatum API
@main_bp.route('/tokens', methods=['GET'])
def get_tokens():
    try:
        response = requests.get(TATUM_API_URL, headers={"accept": "application/json", "x-api-key": TATUM_API_KEY})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch tokens from Tatum API: {str(e)}'}), 500

    tokens_data = response.json()
    return jsonify(tokens_data), 200

# Example: Create a new quiz
@main_bp.route('/quiz', methods=['POST'])
def create_quiz():
    data = request.json
    new_quiz = Quiz(title=data['title'], description=data['description'])
    db.session.add(new_quiz)
    db.session.commit()
    return jsonify({'message': 'Quiz created successfully', 'quiz_id': new_quiz.id}), 201
