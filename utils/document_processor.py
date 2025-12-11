import base64
import os
from pdf2image import convert_from_path
from anthropic import Anthropic
from dotenv import load_dotenv
import io
from PIL import Image

load_dotenv()

class DocumentProcessor:
    """Process uploaded documents and extract knowledge using Claude."""

    def __init__(self):
        """Initialize Anthropic client."""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        self.client = Anthropic(api_key=api_key)

    def process_pdf(self, file_path):
        """
        Convert PDF to images and send to Claude for analysis.

        Args:
            file_path: Path to PDF file

        Returns:
            dict: Extracted knowledge from document
        """
        # Convert PDF pages to images
        images = convert_from_path(file_path, dpi=150)

        # Prepare content for Claude with all pages
        content = []
        for i, image in enumerate(images):
            # Convert PIL Image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

            # Add image to content
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": img_base64
                }
            })

        # Add text prompt after all images
        content.append({
            "type": "text",
            "text": """Analyze this study material and extract all factual information, key concepts, definitions, relationships, and testable knowledge.

Organize your findings by topic/category. Include:
- Key facts and definitions
- Important concepts and their relationships
- Processes and how they work
- Dates, names, and specific details
- Any testable information

Be thorough and precise. This will be used to generate quiz questions."""
        })

        # Call Claude API
        message = self.client.messages.create(
            model="claude-sonnet-4-5-20241022",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ]
        )

        # Extract text response
        knowledge = message.content[0].text

        return {
            "type": "pdf",
            "pages": len(images),
            "knowledge": knowledge
        }
