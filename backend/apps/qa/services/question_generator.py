"""
Question Generator Service
Generates investor questions based on pitch deck content using Groq (Llama 3.3 70B)
"""
import os
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """Generate investor questions for pitch decks using Groq"""

    MODEL = "llama-3.3-70b-versatile"

    def __init__(self):
        try:
            from groq import Groq
            api_key = getattr(settings, 'GROQ_API_KEY', None) or os.getenv('GROQ_API_KEY')
            if not api_key:
                raise ValueError("GROQ_API_KEY is not set in settings or .env")
            self.client = Groq(api_key=api_key)
        except ImportError:
            raise ImportError(
                "groq package is required. Install with: pip install groq"
            )

    def generate(self, pitch_deck):
        """
        Generate investor questions based on pitch deck content.

        Args:
            pitch_deck: PitchDeck object with slides

        Returns:
            list: Generated questions with metadata
        """
        try:
            slides_content = self._get_slides_content(pitch_deck)
            prompt = self._build_generation_prompt(pitch_deck, slides_content)

            logger.info(f"Generating questions for pitch deck: {pitch_deck.title}")

            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an experienced venture capital investor. "
                            "Always respond with valid JSON only — "
                            "no markdown, no code fences, no extra text."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            response_text = response.choices[0].message.content
            questions = self._parse_questions(response_text)

            logger.info(f"Generated {len(questions)} questions")
            return questions

        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            return self._get_default_questions()

    def _get_slides_content(self, pitch_deck):
        """Extract content summary from all slides"""
        slides = pitch_deck.slides.all().order_by('slide_number')

        content_summary = []
        for slide in slides:
            content_summary.append({
                'number': slide.slide_number,
                'type': slide.slide_type,
                'text': slide.text_content[:200],
            })

        return content_summary

    def _build_generation_prompt(self, pitch_deck, slides_content):
        """Build the question generation prompt"""

        slides_text = "\n".join([
            f"Slide {s['number']} ({s['type']}): {s['text']}"
            for s in slides_content
        ])

        prompt = f"""You are an experienced venture capital investor reviewing a startup pitch deck.

Pitch Deck: {pitch_deck.title}
Total Slides: {pitch_deck.total_slides}

Slide Content:
{slides_text}

Generate 8-12 tough but fair investor questions covering these categories:
market, competition, business_model, team, traction, financials, product, risks

Return ONLY a JSON array in this exact format:
[
  {{
    "question_text": "What is your customer acquisition cost compared to lifetime value?",
    "category": "business_model",
    "difficulty": "hard",
    "related_slide_number": 5,
    "key_points_to_cover": ["CAC metric", "LTV calculation", "Payback period"]
  }}
]

Rules:
- difficulty must be: easy, medium, or hard
- category must be one of: market, competition, business_model, team, traction, financials, product, risks
- Mix difficulty levels across questions
- Be specific to the actual deck content where possible
- Return ONLY the JSON array, nothing else"""

        return prompt

    def _parse_questions(self, response_text):
        """Parse Groq response into question objects"""
        try:
            text = response_text.strip()

            # Strip accidental markdown fences
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()

            questions = json.loads(text)

            validated = []
            for q in questions:
                if 'question_text' in q and 'category' in q:
                    validated.append({
                        'question_text': q['question_text'],
                        'category': q.get('category', 'other'),
                        'difficulty': q.get('difficulty', 'medium'),
                        'related_slide_number': q.get('related_slide_number'),
                        'key_points_to_cover': q.get('key_points_to_cover', []),
                    })

            return validated

        except Exception as e:
            logger.error(f"Error parsing questions: {str(e)}")
            logger.debug(f"Raw response: {response_text}")
            return self._get_default_questions()

    def _get_default_questions(self):
        """Fallback questions when Groq call fails"""
        return [
            {
                'question_text': 'What is the total addressable market for your solution?',
                'category': 'market',
                'difficulty': 'easy',
                'related_slide_number': None,
                'key_points_to_cover': ['TAM size', 'Market segments', 'Growth rate'],
            },
            {
                'question_text': 'How do you differentiate from your main competitors?',
                'category': 'competition',
                'difficulty': 'medium',
                'related_slide_number': None,
                'key_points_to_cover': ['Unique features', 'Competitive advantages', 'Positioning'],
            },
            {
                'question_text': 'What are your customer acquisition costs?',
                'category': 'business_model',
                'difficulty': 'hard',
                'related_slide_number': None,
                'key_points_to_cover': ['CAC metric', 'LTV ratio', 'Unit economics'],
            },
            {
                'question_text': 'What experience does your team have in this industry?',
                'category': 'team',
                'difficulty': 'easy',
                'related_slide_number': None,
                'key_points_to_cover': ['Founder backgrounds', 'Domain expertise', 'Track record'],
            },
            {
                'question_text': 'What are your key metrics and how are they trending?',
                'category': 'traction',
                'difficulty': 'medium',
                'related_slide_number': None,
                'key_points_to_cover': ['Revenue', 'Users', 'Growth rate', 'Retention'],
            },
        ]