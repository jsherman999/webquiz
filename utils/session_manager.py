import json
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path

class SessionManager:
    """Manage quiz sessions and history."""

    def __init__(self, sessions_dir='data/sessions', history_dir='data/history'):
        """Initialize session manager."""
        self.sessions_dir = Path(sessions_dir)
        self.history_dir = Path(history_dir)

        # Ensure directories exist
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self, user_id, document_name, questions):
        """
        Create a new quiz session.

        Args:
            user_id: Browser-generated user UUID
            document_name: Name of uploaded document
            questions: List of quiz questions

        Returns:
            str: Session ID
        """
        session_id = str(uuid.uuid4())

        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'document_name': document_name,
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'questions': questions,
            'user_answers': [],
            'current_question': 0,
            'correct_count': 0,
            'start_time': datetime.utcnow().isoformat() + 'Z'
        }

        # Save session file
        session_file = self.sessions_dir / f'session_{session_id}.json'
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)

        return session_id

    def get_session(self, session_id):
        """
        Retrieve session data.

        Args:
            session_id: Session UUID

        Returns:
            dict: Session data or None if not found
        """
        session_file = self.sessions_dir / f'session_{session_id}.json'

        if not session_file.exists():
            return None

        with open(session_file, 'r') as f:
            return json.load(f)

    def update_session(self, session_id, updates):
        """
        Update session data.

        Args:
            session_id: Session UUID
            updates: Dict of fields to update
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.update(updates)

        session_file = self.sessions_dir / f'session_{session_id}.json'
        with open(session_file, 'w') as f:
            json.dump(session, f, indent=2)

    def delete_session(self, session_id):
        """
        Delete session file.

        Args:
            session_id: Session UUID
        """
        session_file = self.sessions_dir / f'session_{session_id}.json'
        if session_file.exists():
            session_file.unlink()

    def save_to_history(self, session_id):
        """
        Save completed quiz to history and delete session.

        Args:
            session_id: Session UUID
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        user_id = session['user_id']

        # Calculate metrics
        total_questions = len(session['questions'])
        correct_answers = session['correct_count']
        score_percentage = round((correct_answers / total_questions) * 100)

        # Calculate time taken
        start_time = datetime.fromisoformat(session['start_time'].replace('Z', ''))
        end_time = datetime.utcnow()
        time_taken_seconds = int((end_time - start_time).total_seconds())

        # Create quiz record
        quiz_record = {
            'quiz_id': session_id,
            'document_name': session['document_name'],
            'completed_at': datetime.utcnow().isoformat() + 'Z',
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'score_percentage': score_percentage,
            'time_taken_seconds': time_taken_seconds,
            'questions_review': session['user_answers']
        }

        # Load or create user history
        history_file = self.history_dir / f'user_{user_id}_history.json'

        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = {'user_id': user_id, 'quizzes': []}

        # Append quiz record
        history['quizzes'].insert(0, quiz_record)  # Most recent first

        # Keep only last 50 quizzes
        history['quizzes'] = history['quizzes'][:50]

        # Save history
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)

        # Delete session
        self.delete_session(session_id)

    def get_user_history(self, user_id):
        """
        Get user's quiz history.

        Args:
            user_id: Browser-generated user UUID

        Returns:
            list: Quiz history or empty list
        """
        history_file = self.history_dir / f'user_{user_id}_history.json'

        if not history_file.exists():
            return []

        with open(history_file, 'r') as f:
            history = json.load(f)

        return history.get('quizzes', [])

    def cleanup_old_sessions(self, hours=24):
        """
        Delete session files older than specified hours.

        Args:
            hours: Age threshold in hours (default 24)
        """
        threshold = datetime.utcnow() - timedelta(hours=hours)

        for session_file in self.sessions_dir.glob('session_*.json'):
            # Check file modification time
            mtime = datetime.fromtimestamp(session_file.stat().st_mtime)

            if mtime < threshold:
                session_file.unlink()
