import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import uuid

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

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('data/sessions', exist_ok=True)
    os.makedirs('data/history', exist_ok=True)

    # Run on all interfaces to accept LAN connections
    app.run(host='0.0.0.0', port=5000, debug=True)
