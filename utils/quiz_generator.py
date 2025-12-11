import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class QuizGenerator:
    """Generate quiz questions from extracted knowledge using Claude."""

    def __init__(self):
        """Initialize Anthropic client."""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        self.client = Anthropic(api_key=api_key)

    def generate_quiz(self, knowledge, num_questions=10):
        """
        Generate quiz questions from extracted knowledge.

        Args:
            knowledge: Extracted knowledge text from document
            num_questions: Number of questions to generate

        Returns:
            list: Quiz questions in structured format
        """
        prompt = f"""Based on the following extracted knowledge, create {num_questions} quiz questions.

KNOWLEDGE:
{knowledge}

REQUIREMENTS:
- Mix multiple-choice (60%) and fill-in-blank (40%) questions
- For multiple choice, provide exactly 4 options (A, B, C, D) with only one correct answer
- Make questions test understanding, not just memorization
- Ensure questions are clear and unambiguous
- For fill-in-blank, provide acceptable variations of the answer (case-insensitive)
- Include brief explanations for correct answers

Return ONLY valid JSON in this exact format:
{{
  "questions": [
    {{
      "id": 1,
      "type": "multiple_choice",
      "question": "What is the main function of chloroplasts?",
      "options": ["Photosynthesis", "Respiration", "Protein synthesis", "Cell division"],
      "correct_answer": "Photosynthesis",
      "explanation": "Chloroplasts are the organelles where photosynthesis occurs in plant cells."
    }},
    {{
      "id": 2,
      "type": "fill_blank",
      "question": "The process by which plants convert sunlight into energy is called ___",
      "correct_answer": "photosynthesis",
      "acceptable_answers": ["photosynthesis", "Photosynthesis"],
      "explanation": "Photosynthesis is the process plants use to convert light energy into chemical energy."
    }}
  ]
}}

Generate exactly {num_questions} questions following this format."""

        # Call Claude API
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Extract and parse JSON response
        response_text = message.content[0].text

        # Find JSON in response (handle cases where Claude adds explanation)
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1

        if json_start == -1 or json_end == 0:
            raise ValueError("No JSON found in Claude response")

        json_str = response_text[json_start:json_end]
        quiz_data = json.loads(json_str)

        return quiz_data['questions']
