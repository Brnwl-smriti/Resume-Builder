"""
NeuraDoc - AI-Powered Research Assistant
Main Flask Application
"""

import os
import json
import tempfile
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Import our custom modules
from backend.utils.parser import DocumentParser
from backend.utils.summarizer import DocumentSummarizer
from backend.utils.qa_engine import QAEngine
from backend.utils.challenge_gen import ChallengeGenerator
from backend.utils.evaluator import AnswerEvaluator

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'neura_doc_secret_key_2024'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize AI components
document_parser = DocumentParser()
document_summarizer = DocumentSummarizer()
qa_engine = QAEngine()
challenge_generator = ChallengeGenerator()
answer_evaluator = AnswerEvaluator()

# Global session storage (in production, use Redis or database)
session_data = {}

@app.route('/')
def index():
    """Serve the main application"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('../frontend', filename)

@app.route('/api/upload', methods=['POST'])
def upload_document():
    """Handle document upload and return summary"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'pdf', 'txt'}
        if not file.filename.lower().endswith(tuple('.' + ext for ext in allowed_extensions)):
            return jsonify({'error': 'Invalid file type. Only PDF and TXT files are allowed.'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        file.save(filepath)
        
        # Parse document
        document_text = document_parser.parse(filepath)
        
        if not document_text or len(document_text.strip()) < 50:
            return jsonify({'error': 'Document is too short or could not be parsed'}), 400
        
        # Generate summary
        summary = document_summarizer.summarize(document_text)
        
        # Store in session
        session_id = request.headers.get('X-Session-ID', 'default')
        session_data[session_id] = {
            'document_text': document_text,
            'filename': filename,
            'upload_time': datetime.now().isoformat(),
            'conversation_history': []
        }
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'summary': summary,
            'filename': filename,
            'word_count': len(document_text.split()),
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Handle question asking with document-grounded answers"""
    try:
        data = request.get_json()
        question = data.get('question')
        session_id = request.headers.get('X-Session-ID', 'default')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        if session_id not in session_data:
            return jsonify({'error': 'No document uploaded. Please upload a document first.'}), 400
        
        document_text = session_data[session_id]['document_text']
        
        # Get answer with references
        answer, references, source_sentences = qa_engine.answer_question(question, document_text)
        
        # Store in conversation history
        session_data[session_id]['conversation_history'].append({
            'type': 'question',
            'content': question,
            'timestamp': datetime.now().isoformat()
        })
        
        session_data[session_id]['conversation_history'].append({
            'type': 'answer',
            'content': answer,
            'references': references,
            'source_sentences': source_sentences,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'success': True,
            'answer': answer,
            'references': references,
            'source_sentences': source_sentences
        })
        
    except Exception as e:
        return jsonify({'error': f'Question processing failed: {str(e)}'}), 500

@app.route('/api/challenge', methods=['POST'])
def generate_challenge():
    """Generate logic-based challenge questions"""
    try:
        session_id = request.headers.get('X-Session-ID', 'default')
        
        if session_id not in session_data:
            return jsonify({'error': 'No document uploaded. Please upload a document first.'}), 400
        
        document_text = session_data[session_id]['document_text']
        
        # Generate challenge questions
        questions = challenge_generator.generate_questions(document_text)
        
        # Store challenge in session
        session_data[session_id]['current_challenge'] = {
            'questions': questions,
            'generated_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'questions': questions
        })
        
    except Exception as e:
        return jsonify({'error': f'Challenge generation failed: {str(e)}'}), 500

@app.route('/api/evaluate', methods=['POST'])
def evaluate_answer():
    """Evaluate user's answer to challenge questions"""
    try:
        data = request.get_json()
        question_index = data.get('question_index')
        user_answer = data.get('answer')
        session_id = request.headers.get('X-Session-ID', 'default')
        
        if question_index is None or not user_answer:
            return jsonify({'error': 'Question index and answer are required'}), 400
        
        if session_id not in session_data or 'current_challenge' not in session_data[session_id]:
            return jsonify({'error': 'No active challenge found'}), 400
        
        challenge = session_data[session_id]['current_challenge']
        if question_index >= len(challenge['questions']):
            return jsonify({'error': 'Invalid question index'}), 400
        
        question = challenge['questions'][question_index]
        document_text = session_data[session_id]['document_text']
        
        # Evaluate answer
        evaluation = answer_evaluator.evaluate_answer(
            question, user_answer, document_text
        )
        
        return jsonify({
            'success': True,
            'evaluation': evaluation
        })
        
    except Exception as e:
        return jsonify({'error': f'Answer evaluation failed: {str(e)}'}), 500

@app.route('/api/reset', methods=['POST'])
def reset_session():
    """Reset the current session"""
    try:
        session_id = request.headers.get('X-Session-ID', 'default')
        
        if session_id in session_data:
            del session_data[session_id]
        
        return jsonify({
            'success': True,
            'message': 'Session reset successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Session reset failed: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'NeuraDoc AI Assistant'
    })

if __name__ == '__main__':
    print("🌌 Starting NeuraDoc AI Assistant...")
    print("📁 Upload folder:", app.config['UPLOAD_FOLDER'])
    print("🔧 Debug mode:", app.debug)
    app.run(debug=True, host='0.0.0.0', port=5000) 