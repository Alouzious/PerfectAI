"""
Question Generator Service
Generates investor questions based on pitch deck content
"""
import google.generativeai as genai
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """Generate investor questions for pitch decks"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
    
    def generate(self, pitch_deck):
        """
        Generate questions based on pitch deck content
        
        Args:
            pitch_deck: PitchDeck object with slides
            
        Returns:
            list: Generated questions with metadata
        """
        try:
            slides_content = self._get_slides_content(pitch_deck)
            prompt = self._build_generation_prompt(pitch_deck, slides_content)
            
            logger.info(f"Generating questions for pitch deck: {pitch_deck.title}")
            
            message = self.model.generate_content(prompt)
            response_text = message.text
            
            questions = self._parse_questions(response_text)
            
            logger.info(f"Generated {len(questions)} questions")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            return self._get_default_questions()
    
    def _get_slides_content(self, pitch_deck):
        """Extract content from all slides"""
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
        """Build prompt for question generation"""
        
        slides_text = "\n".join([
            f"Slide {s['number']} ({s['type']}): {s['text']}"
            for s in slides_content
        ])
        
        prompt = f"""You are an experienced venture capital investor reviewing a startup pitch deck.

**Pitch Deck:** {pitch_deck.title}
**Total Slides:** {pitch_deck.total_slides}

**Slide Content Summary:**
{slides_text}

**Your Task:**
Generate 8-12 tough but fair investor questions that would be asked during or after this pitch. 

**Question Requirements:**
- Mix of difficulty levels (easy, medium, hard)
- Cover multiple categories:
  - market: Market size, opportunity, growth
  - competition: Competitive landscape, differentiation
  - business_model: Revenue model, pricing, unit economics
  - team: Team capabilities, experience, roles
  - traction: Metrics, growth, customer acquisition
  - financials: Projections, burn rate, path to profitability
  - product: Technology, features, roadmap
  - risks: Challenges, threats, mitigation

- Each question should:
  - Be specific and probing
  - Test the founder's knowledge
  - Reveal potential weaknesses
  - Require thoughtful answers

**Format:**
Return a JSON array of questions:

[
  {{
    "question_text": "What is your customer acquisition cost and how does it compare to lifetime value?",
    "category": "business_model",
    "difficulty": "hard",
    "related_slide_number": 5,
    "key_points_to_cover": ["CAC metric", "LTV calculation", "Unit economics", "Payback period"]
  }},
  ...
]

Return ONLY valid JSON array, no other text."""

        return prompt
    
    def _parse_questions(self, response_text):
        """Parse AI response into question objects"""
        try:
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            questions = json.loads(response_text)
            
            validated_questions = []
            for q in questions:
                if 'question_text' in q and 'category' in q:
                    validated_questions.append({
                        'question_text': q['question_text'],
                        'category': q.get('category', 'other'),
                        'difficulty': q.get('difficulty', 'medium'),
                        'related_slide_number': q.get('related_slide_number'),
                        'key_points_to_cover': q.get('key_points_to_cover', [])
                    })
            
            return validated_questions
            
        except Exception as e:
            logger.error(f"Error parsing questions: {str(e)}")
            return self._get_default_questions()
    
    def _get_default_questions(self):
        """Return default questions when AI fails"""
        return [
            {
                'question_text': 'What is the total addressable market for your solution?',
                'category': 'market',
                'difficulty': 'easy',
                'related_slide_number': None,
                'key_points_to_cover': ['TAM size', 'Market segments', 'Growth rate']
            },
            {
                'question_text': 'How do you differentiate from your main competitors?',
                'category': 'competition',
                'difficulty': 'medium',
                'related_slide_number': None,
                'key_points_to_cover': ['Unique features', 'Competitive advantages', 'Market positioning']
            },
            {
                'question_text': 'What are your customer acquisition costs?',
                'category': 'business_model',
                'difficulty': 'hard',
                'related_slide_number': None,
                'key_points_to_cover': ['CAC metric', 'LTV ratio', 'Unit economics']
            },
            {
                'question_text': 'What experience does your team have in this industry?',
                'category': 'team',
                'difficulty': 'easy',
                'related_slide_number': None,
                'key_points_to_cover': ['Founder backgrounds', 'Domain expertise', 'Track record']
            },
            {
                'question_text': 'What are your key metrics and how are they trending?',
                'category': 'traction',
                'difficulty': 'medium',
                'related_slide_number': None,
                'key_points_to_cover': ['Revenue', 'Users', 'Growth rate', 'Retention']
            },
        ]