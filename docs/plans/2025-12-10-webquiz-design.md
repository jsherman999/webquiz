# WebQuiz Application Design
**Date:** 2025-12-10
**Platform:** Mac Mini M4 (Local LAN deployment)

## Overview
A local web application that allows users on a LAN to upload study materials (PDFs or spreadsheets), then takes AI-generated quizzes based on the document content. Uses Claude Sonnet 4.5 via Anthropic API for document understanding and quiz generation.

## Core Requirements
- Run on Mac Mini M4, serve to local LAN users
- Accept PDF or Excel file uploads via drag-and-drop or file picker
- Use Claude Sonnet 4.5 (via Anthropic API) to understand documents and generate quizzes
- Present quiz questions one at a time with immediate feedback
- Track running score and provide detailed results
- Show correct answers for incorrect responses
- Store quiz history for users
- Simple, stylish, educational-friendly UI

## Architecture & Tech Stack

### Technology Choices
- **Backend:** Python 3.11+ with Flask web framework
- **Document Processing:**
  - PDFs: `pdf2image` (convert to images for Claude vision)
  - Spreadsheets: `openpyxl` (parse and convert to markdown)
- **AI Integration:** Anthropic Python SDK for Claude Sonnet 4.5 API
- **Frontend:** Vanilla HTML/CSS/JavaScript (no build process)
- **Styling:** Tailwind CSS via CDN
- **Data Storage:** JSON files for sessions and history
- **API Key Management:** Environment variable in `.env` file

### Project Structure
```
webquiz/
├── app.py                    # Main Flask application
├── static/
│   ├── css/
│   │   └── style.css         # Custom styles
│   ├── js/
│   │   └── quiz.js           # Quiz interaction logic
│   └── images/               # UI assets
├── templates/
│   ├── index.html            # Upload page
│   ├── quiz.html             # Quiz interface
│   ├── results.html          # Results summary
│   └── history.html          # Quiz history view
├── uploads/                  # Temporary document storage
├── data/
│   ├── sessions/             # Active quiz sessions (JSON)
│   └── history/              # Completed quiz records (JSON)
├── .env                      # ANTHROPIC_API_KEY
├── requirements.txt          # Python dependencies
└── docs/
    └── plans/
        └── 2025-12-10-webquiz-design.md
```

### Network Configuration
- Flask binds to `0.0.0.0:5000` to accept LAN connections
- Users access via `http://[mac-mini-ip]:5000` from any device on LAN
- No authentication required (trusted LAN environment)

## Document Processing Flow

### Upload & Validation
1. User drags/drops or selects file via file picker
2. Frontend validates:
   - File type: `.pdf`, `.xlsx`, `.xls`
   - Size limit: 10MB (suitable for small study docs)
3. Valid files sent to Flask backend via multipart form data
4. Backend stores temporarily in `uploads/` directory

### Document Parsing Strategy

**For PDFs (Vision-based):**
1. Use `pdf2image` library to convert each page to PNG images
2. Send images to Claude API using vision capabilities
3. Claude analyzes visual content (preserves formatting, tables, diagrams)
4. Prompt: *"Analyze this study material and extract all factual information, key concepts, definitions, relationships, and testable knowledge. Organize findings by topic/category."*

**For Spreadsheets (Text-based):**
1. Use `openpyxl` to read Excel file
2. Convert each sheet to clean markdown table format
3. Send markdown text to Claude API
4. Same extraction prompt as PDFs

### Content Extraction
- Claude response contains structured knowledge extraction
- Response cached in session for quiz generation
- Avoids redundant API calls for same document

## Quiz Generation & Delivery

### Quiz Setup
1. After document processing, user selects quiz length from dropdown:
   - 5 questions
   - 10 questions
   - 15 questions
   - 20 questions
2. Selection triggers quiz generation API call

### Question Generation
**Prompt to Claude:**
```
Based on the extracted knowledge, create [N] quiz questions.
Mix multiple-choice (60%) and fill-in-blank (40%) questions.
For multiple choice, provide 4 options with only one correct answer.
Make questions test understanding, not just memorization.
Return as JSON in the specified format.
```

**JSON Response Format:**
```json
{
  "questions": [
    {
      "id": 1,
      "type": "multiple_choice",
      "question": "What is photosynthesis?",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "A",
      "explanation": "Brief explanation of the answer"
    },
    {
      "id": 2,
      "type": "fill_blank",
      "question": "The capital of France is ___",
      "correct_answer": "Paris",
      "acceptable_answers": ["paris", "Paris"],
      "explanation": "Paris is the capital and largest city of France"
    }
  ]
}
```

### Quiz Delivery Flow
1. **Question Display:** One question at a time in centered panel
2. **Answer Input:**
   - Multiple choice: Radio buttons with 4 options
   - Fill-in-blank: Text input field
3. **Submission:** User clicks "Submit Answer" button
4. **Immediate Feedback:**
   - ✓ Correct: Green checkmark with encouragement
   - ✗ Incorrect: Show correct answer with explanation
5. **Navigation:** "Next Question" button appears after feedback
6. **Score Tracking:** Running score displayed at top (e.g., "7/10 correct")
7. **Completion:** Final question leads to results page

## UI/UX Design (Educational/Friendly Style)

### Color Palette
- **Primary:** Warm blue `#4A90E2` (buttons, accents)
- **Success:** Friendly green `#7ED321` (correct answers)
- **Error:** Soft coral `#FF6B6B` (incorrect answers)
- **Background:** Light cream `#FAFAF8`
- **Text:** Warm dark gray `#2C3E50`
- **Cards:** White `#FFFFFF` with soft shadows

### Design Principles
- Generous whitespace and padding
- Rounded corners everywhere (12px border-radius)
- Friendly, conversational copy
- Emoji for emotional engagement
- Large, readable fonts (18px+ for body text)
- Smooth animations and transitions

### Page Designs

**Home/Upload Page:**
- Large centered upload area with dashed border
- Copy: "Drop your study material here! 📚"
- Drag-and-drop highlight effect (border changes to blue)
- Supported formats shown below: "Accepts PDF and Excel files (max 10MB)"
- After upload: Processing indicator with friendly message

**Quiz Interface:**
- **Header Bar:**
  - Progress: "Question 3 of 10"
  - Score badge: "😊 7/10" (emoji changes based on performance)
- **Question Panel:**
  - White card with soft shadow
  - Generous padding (32px)
  - Question text in large, readable font (20px)
- **Answer Area:**
  - Multiple choice: Big rounded buttons with hover effects
  - Fill-in-blank: Friendly text input with placeholder "Type your answer..."
- **Feedback Panel:**
  - Slides in below question after submission
  - Animated checkmark ✓ or X ✗
  - Correct answer display (if wrong)
  - Explanation in conversational tone
- **Navigation:**
  - "Next Question" button (bright blue, prominent)

**Results Page:**
- **Summary Section:**
  - Large score display: "You scored 7 out of 10! 🎉"
  - Celebratory message based on score:
    - 90-100%: "Outstanding! 🌟"
    - 70-89%: "Great job! 👏"
    - 50-69%: "Good effort! 💪"
    - <50%: "Keep practicing! 📚"
- **Detailed Breakdown:**
  - Table showing each question
  - User's answer vs. correct answer
  - Color-coded (green/red) for quick scan
- **Actions:**
  - "Try Another Quiz" button (returns to upload)
  - "View History" link

**History Page:**
- Table of past quizzes:
  - Date/time
  - Document name
  - Score (X/Y)
  - Percentage
- Click any row to see detailed question review
- "Back to Home" button

## Data Persistence & History Tracking

### File Structure
```
data/
├── sessions/
│   └── session_[uuid].json          # Active quiz sessions
└── history/
    └── user_[browser-uuid]_history.json  # Completed quiz records
```

### Session Management
**Active Session (during quiz):**
```json
{
  "session_id": "uuid-v4",
  "user_id": "browser-uuid",
  "document_name": "Biology Chapter 3.pdf",
  "created_at": "2025-12-10T19:30:00Z",
  "questions": [...],
  "user_answers": [],
  "current_question": 0,
  "correct_count": 0
}
```
- Created when quiz starts
- Updated as user answers questions
- Deleted after completion or 24-hour timeout

### History Storage
**Quiz History (after completion):**
```json
{
  "user_id": "browser-uuid",
  "quizzes": [
    {
      "quiz_id": "uuid-v4",
      "document_name": "Biology Chapter 3.pdf",
      "completed_at": "2025-12-10T19:45:00Z",
      "total_questions": 10,
      "correct_answers": 7,
      "score_percentage": 70,
      "time_taken_seconds": 245,
      "questions_review": [
        {
          "question": "What is photosynthesis?",
          "user_answer": "A",
          "correct_answer": "A",
          "is_correct": true
        }
      ]
    }
  ]
}
```
- Appended after each quiz completion
- Persistent across sessions
- Limited to last 50 quizzes per user

### User Identification
- Browser-based UUID generated on first visit
- Stored in browser `localStorage`
- Links quiz history to specific device/browser
- No login/authentication required
- Simple, frictionless for trusted LAN environment

### Cleanup Strategy
- Background task (or manual script) removes:
  - Session files older than 24 hours
  - History entries beyond 50 per user (keep most recent)
- Uploaded files deleted after quiz generation

## API Integration

### Anthropic API Usage
**Configuration:**
```python
import anthropic

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)
```

**Document Analysis Call (PDF with Vision):**
```python
message = client.messages.create(
    model="claude-sonnet-4-5-20241022",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": base64_image_data
                    }
                },
                {
                    "type": "text",
                    "text": "Analyze this study material..."
                }
            ]
        }
    ]
)
```

**Quiz Generation Call:**
```python
message = client.messages.create(
    model="claude-sonnet-4-5-20241022",
    max_tokens=8192,
    messages=[
        {
            "role": "user",
            "content": f"Based on the extracted knowledge: {content_summary}\n\nCreate {num_questions} quiz questions..."
        }
    ]
)
```

### Error Handling
- API rate limits: Show friendly "Please try again in a moment"
- Invalid API key: Show setup instructions
- Document processing failures: Clear error message with retry option
- Network issues: Graceful degradation with user notification

## Security & Privacy Considerations

### Data Privacy
- All data stored locally on Mac Mini
- No external database or cloud storage
- Quiz history tied to browser, not personally identifiable
- Documents deleted after processing

### API Key Security
- Stored in `.env` file (not committed to git)
- `.gitignore` includes `.env` and `uploads/` directory
- Only accessible to Flask backend, never exposed to frontend

### LAN Security
- Assumes trusted network environment
- No authentication (appropriate for home/small office LAN)
- Could add basic password protection if needed

### Input Validation
- File type whitelist (PDF, Excel only)
- File size limits (10MB max)
- Sanitize filenames to prevent directory traversal
- Validate JSON responses from Claude API

## Future Enhancements (Out of Scope for v1)
- Multi-user leaderboards
- Timed quiz mode
- Difficulty levels
- Custom question types (true/false, matching)
- Export quiz results to PDF
- Admin dashboard for quiz management
- Support for more file types (DOCX, PPTX)

## Success Criteria
- ✅ Users can upload PDF or Excel files from any LAN device
- ✅ Quiz questions accurately reflect document content
- ✅ Quiz interface is intuitive and responsive
- ✅ Immediate feedback with correct answers shown
- ✅ Running score displayed throughout quiz
- ✅ Quiz history persists across sessions
- ✅ UI feels friendly and educational (not sterile)
- ✅ Entire process from upload to results takes < 2 minutes for small docs

## Dependencies (requirements.txt)
```
flask==3.0.0
anthropic==0.18.0
python-dotenv==1.0.0
pdf2image==1.17.0
openpyxl==3.1.2
pillow==10.2.0
```

**System Requirements:**
- Python 3.11+
- poppler-utils (for pdf2image)
- Mac Mini M4 with macOS

## Deployment Steps
1. Clone/create project directory
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Install poppler: `brew install poppler`
6. Create `.env` file with `ANTHROPIC_API_KEY=your_key_here`
7. Create necessary directories: `mkdir -p uploads data/sessions data/history`
8. Run Flask app: `python app.py`
9. Access from LAN devices via `http://[mac-mini-ip]:5000`

---

**End of Design Document**
