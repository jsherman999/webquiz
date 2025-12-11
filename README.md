# WebQuiz

A local LAN quiz application that uses Claude Sonnet 4.5 to analyze uploaded study materials (PDFs and Excel files) and generate interactive quizzes with immediate feedback and history tracking.

## Features

- 📚 **Upload Study Materials** - Support for PDF and Excel files (up to 10MB)
- 🤖 **AI-Powered Analysis** - Uses Claude Sonnet 4.5 to extract knowledge from documents
- ❓ **Mixed Question Types** - Multiple-choice (60%) and fill-in-blank (40%) questions
- ✅ **Immediate Feedback** - Get instant results with explanations after each answer
- 📊 **Quiz History** - Track your progress with detailed history of past quizzes
- 🎨 **Friendly UI** - Clean, educational interface built with Tailwind CSS
- 🌐 **LAN Access** - Available to all devices on your local network

## Tech Stack

- **Backend:** Python 3.11+, Flask 3.0
- **AI:** Anthropic Claude Sonnet 4.5 API
- **Document Processing:** pdf2image, openpyxl, Pillow
- **Frontend:** Vanilla JavaScript, Tailwind CSS
- **Data Storage:** JSON files (sessions and history)

## Requirements

- Python 3.11 or higher
- macOS (tested on Mac Mini M4)
- Anthropic API key ([Get one here](https://console.anthropic.com/))
- Homebrew (for installing system dependencies)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/jsherman999/webquiz.git
cd webquiz
```

### 2. Install System Dependencies

Install poppler (required for PDF processing):

```bash
brew install poppler
```

### 3. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Set Up Environment Variables

Create a `.env` file with your Anthropic API key:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

## Usage

### Starting the Server

1. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Start the application:
   ```bash
   python app.py
   ```

3. You should see output like:
   ```
   * Running on all addresses (0.0.0.0)
   * Running on http://127.0.0.1:5666
   * Running on http://192.168.x.x:5666
   ```

### Accessing the Application

- **From your Mac:** http://localhost:5666
- **From other devices on your LAN:** http://[your-mac-ip]:5666
  - Find your Mac's IP: System Settings → Network
  - Or use `ifconfig | grep "inet " | grep -v 127.0.0.1`

### Taking a Quiz

1. **Upload a Document**
   - Click or drag-and-drop a PDF or Excel file
   - Wait for Claude to process and extract knowledge
   - Files are automatically deleted after processing

2. **Configure Quiz**
   - Choose number of questions (5, 10, 15, or 20)
   - Click "Start Quiz"

3. **Answer Questions**
   - Select answers for multiple-choice questions
   - Type answers for fill-in-blank questions
   - Get immediate feedback with explanations

4. **View Results**
   - See your score and percentage
   - Review all questions with correct answers
   - Access detailed explanations

5. **Track History**
   - View all past quizzes
   - See scores, dates, and time taken
   - Re-review any previous quiz

## Project Structure

```
webquiz/
├── app.py                      # Flask application and API routes
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (API key)
├── utils/                      # Utility modules
│   ├── document_processor.py  # PDF/Excel processing with Claude
│   ├── quiz_generator.py      # Quiz generation with Claude
│   └── session_manager.py     # Session and history management
├── templates/                  # HTML templates
│   ├── base.html              # Base template with Tailwind
│   ├── index.html             # Upload page
│   ├── quiz.html              # Quiz interface
│   ├── results.html           # Results page
│   └── history.html           # History page
├── static/                     # Static assets
│   ├── css/style.css          # Custom CSS and animations
│   └── js/                    # JavaScript files
│       ├── upload.js          # Upload functionality
│       ├── quiz.js            # Quiz interface logic
│       ├── results.js         # Results display
│       └── history.js         # History tracking
├── data/                       # Data storage (auto-created)
│   ├── sessions/              # Active quiz sessions
│   └── history/               # User quiz history
└── uploads/                    # Temporary file storage (auto-created)
```

## API Endpoints

- `GET /` - Upload page
- `GET /health` - Health check endpoint
- `POST /upload` - Upload and process document
- `POST /generate-quiz` - Generate quiz from processed knowledge
- `GET /question/<session_id>/<num>` - Get specific question
- `POST /submit-answer` - Submit answer and get feedback
- `POST /complete-quiz/<session_id>` - Complete quiz and save to history
- `GET /results/<session_id>` - Get quiz results
- `GET /history/<user_id>` - Get user's quiz history
- `GET /quiz` - Quiz interface page
- `GET /results` - Results page
- `GET /history` - History page

## Configuration

### Application Settings

- **Port:** 5666 (configured in app.py)
- **Host:** 0.0.0.0 (accepts connections from any network interface)
- **Max File Size:** 10MB
- **Allowed File Types:** PDF (.pdf), Excel (.xlsx, .xls)
- **Session Timeout:** 24 hours (auto-cleanup)
- **History Limit:** 50 quizzes per user

### Claude API Settings

- **Model:** claude-sonnet-4-5-20241022
- **Max Tokens (Analysis):** 4096
- **Max Tokens (Quiz Generation):** 8192

## Data Storage

- **User Identification:** Browser localStorage UUID (no authentication required)
- **Sessions:** JSON files in `data/sessions/`
- **History:** JSON files in `data/history/`
- **Uploaded Files:** Temporarily stored in `uploads/`, deleted after processing

## Running in Background

To run the server in the background:

```bash
# Start in background
nohup python app.py > webquiz.log 2>&1 &

# View logs
tail -f webquiz.log

# Stop the server
ps aux | grep "python app.py"
kill <process_id>
```

## Firewall Configuration

If devices on your LAN can't connect:

1. Go to **System Settings** → **Network** → **Firewall**
2. Click **Options**
3. Ensure Python is allowed to accept incoming connections

## Security Notes

- This application is designed for **trusted LAN environments only**
- No authentication is implemented
- API key is stored in `.env` file (never commit to Git)
- Uploaded files are processed and immediately deleted
- User data is stored locally on the server

## Troubleshooting

### Can't connect from other devices
- Check firewall settings
- Verify devices are on the same network
- Confirm Mac's IP address hasn't changed

### PDF processing fails
- Ensure poppler is installed: `brew list poppler`
- Check PDF file is not corrupted
- Verify file size is under 10MB

### Claude API errors
- Verify API key is correct in `.env`
- Check API key has available credits
- Ensure internet connection is active

## Development

The application runs in debug mode by default (`debug=True` in app.py). For production use on a trusted LAN:

1. Set `debug=False` in app.py
2. Use a proper WSGI server like Gunicorn
3. Consider adding authentication if needed

## License

MIT

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgments

- Powered by [Anthropic Claude](https://www.anthropic.com/)
- Built with [Flask](https://flask.palletsprojects.com/)
- UI styled with [Tailwind CSS](https://tailwindcss.com/)
