import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import uuid
from utils.document_processor import DocumentProcessor
from utils.quiz_generator import QuizGenerator
from utils.session_manager import SessionManager
import traceback

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'xlsx', 'xls'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Render upload page."""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})

# Initialize utilities
document_processor = DocumentProcessor()
quiz_generator = QuizGenerator()
session_manager = SessionManager()

@app.route('/upload', methods=['POST'])
def upload_document():
    """Handle document upload and processing."""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload PDF or Excel files.'}), 400

        # Save uploaded file
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        file_extension = filename.rsplit('.', 1)[1].lower()
        saved_filename = f"{file_id}.{file_extension}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)

        file.save(file_path)

        # Process document
        try:
            result = document_processor.process_document(file_path, file_extension)

            # Return knowledge and file info
            return jsonify({
                'success': True,
                'file_id': file_id,
                'filename': filename,
                'knowledge': result['knowledge'],
                'document_type': result['type']
            })

        except Exception as e:
            # Clean up file on processing error
            if os.path.exists(file_path):
                os.remove(file_path)

            return jsonify({
                'error': f'Failed to process document: {str(e)}'
            }), 500

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/generate-quiz', methods=['POST'])
def generate_quiz():
    """Generate quiz questions from processed knowledge."""
    try:
        data = request.get_json()

        knowledge = data.get('knowledge')
        num_questions = data.get('num_questions', 10)
        user_id = data.get('user_id')
        document_name = data.get('document_name')
        file_id = data.get('file_id')

        if not knowledge:
            return jsonify({'error': 'No knowledge provided'}), 400

        if not user_id:
            return jsonify({'error': 'No user_id provided'}), 400

        # Generate quiz questions
        questions = quiz_generator.generate_quiz(knowledge, num_questions)

        # Create session
        session_id = session_manager.create_session(user_id, document_name, questions)

        # Clean up uploaded file
        if file_id:
            for ext in ['pdf', 'xlsx', 'xls']:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}.{ext}")
                if os.path.exists(file_path):
                    os.remove(file_path)

        return jsonify({
            'success': True,
            'session_id': session_id,
            'total_questions': len(questions)
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/question/<session_id>/<int:question_num>', methods=['GET'])
def get_question(session_id, question_num):
    """Get a specific question from the quiz session."""
    try:
        session = session_manager.get_session(session_id)

        if not session:
            return jsonify({'error': 'Session not found'}), 404

        questions = session['questions']

        if question_num < 0 or question_num >= len(questions):
            return jsonify({'error': 'Invalid question number'}), 400

        question = questions[question_num]

        # Return question without correct answer
        safe_question = {
            'id': question['id'],
            'type': question['type'],
            'question': question['question'],
            'question_num': question_num,
            'total_questions': len(questions),
            'current_score': session['correct_count']
        }

        if question['type'] == 'multiple_choice':
            safe_question['options'] = question['options']

        return jsonify(safe_question)

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/submit-answer', methods=['POST'])
def submit_answer():
    """Submit and check an answer."""
    try:
        data = request.get_json()

        session_id = data.get('session_id')
        question_num = data.get('question_num')
        user_answer = data.get('answer')

        if not session_id or question_num is None or user_answer is None:
            return jsonify({'error': 'Missing required fields'}), 400

        session = session_manager.get_session(session_id)

        if not session:
            return jsonify({'error': 'Session not found'}), 404

        questions = session['questions']
        question = questions[question_num]

        # Check if answer is correct
        is_correct = False

        if question['type'] == 'multiple_choice':
            is_correct = user_answer.strip() == question['correct_answer'].strip()
        elif question['type'] == 'fill_blank':
            # Case-insensitive comparison with acceptable answers
            user_answer_lower = user_answer.strip().lower()
            acceptable = [ans.lower() for ans in question.get('acceptable_answers', [question['correct_answer']])]
            is_correct = user_answer_lower in acceptable

        # Update session
        if is_correct:
            session['correct_count'] += 1

        # Record answer
        session['user_answers'].append({
            'question': question['question'],
            'user_answer': user_answer,
            'correct_answer': question['correct_answer'],
            'is_correct': is_correct,
            'explanation': question.get('explanation', '')
        })

        session['current_question'] = question_num + 1

        session_manager.update_session(session_id, session)

        # Return feedback
        return jsonify({
            'is_correct': is_correct,
            'correct_answer': question['correct_answer'],
            'explanation': question.get('explanation', ''),
            'current_score': session['correct_count'],
            'total_questions': len(questions)
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/complete-quiz/<session_id>', methods=['POST'])
def complete_quiz(session_id):
    """Complete quiz and save to history."""
    try:
        session = session_manager.get_session(session_id)

        if not session:
            return jsonify({'error': 'Session not found'}), 404

        # Save to history and delete session
        session_manager.save_to_history(session_id)

        return jsonify({'success': True})

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/results/<session_id>', methods=['GET'])
def get_results(session_id):
    """Get quiz results (before completion)."""
    try:
        session = session_manager.get_session(session_id)

        if not session:
            return jsonify({'error': 'Session not found'}), 404

        total = len(session['questions'])
        correct = session['correct_count']
        percentage = round((correct / total) * 100) if total > 0 else 0

        return jsonify({
            'document_name': session['document_name'],
            'total_questions': total,
            'correct_answers': correct,
            'score_percentage': percentage,
            'questions_review': session['user_answers']
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/history/<user_id>', methods=['GET'])
def get_history(user_id):
    """Get user's quiz history."""
    try:
        history = session_manager.get_user_history(user_id)
        return jsonify({'quizzes': history})

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def history_page():
    """Render history page."""
    return render_template('history.html')

@app.route('/quiz')
def quiz_page():
    """Render quiz page."""
    return render_template('quiz.html')

@app.route('/results')
def results_page():
    """Render results page."""
    return render_template('results.html')

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('data/sessions', exist_ok=True)
    os.makedirs('data/history', exist_ok=True)

    # Run on all interfaces to accept LAN connections
    app.run(host='0.0.0.0', port=5666, debug=True)
