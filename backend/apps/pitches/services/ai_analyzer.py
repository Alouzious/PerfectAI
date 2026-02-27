"""
AI Analyzer Service
Uses Google Gemini API to analyze pitch deck slides
With proper rate limiting for free tier (15 RPM)
"""
import google.generativeai as genai
from django.conf import settings
import json
import logging
import time

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Analyze slides using Gemini AI"""

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        # Free tier = 15 requests/min → wait 5s between slides to stay safe
        self.delay_between_slides = 5

    def analyze_slide(self, slide_number, text_content, has_images=False, has_charts=False):
        """
        Analyze a single slide with AI

        Args:
            slide_number (int): Slide number
            text_content (str): Text extracted from slide
            has_images (bool): Whether slide has images
            has_charts (bool): Whether slide has charts

        Returns:
            dict: Analysis results
        """
        prompt = self._build_slide_analysis_prompt(
            slide_number, text_content, has_images, has_charts
        )

        # Always wait before EVERY API call to respect free tier rate limit
        logger.info(f"Waiting {self.delay_between_slides}s before slide {slide_number} to respect rate limit...")
        time.sleep(self.delay_between_slides)

        max_retries = 5
        for attempt in range(max_retries):
            try:
                logger.info(f"Analyzing slide {slide_number} with Gemini (attempt {attempt + 1}/{max_retries})")

                message = self.model.generate_content(prompt)
                response_text = message.text
                analysis = self._parse_analysis_response(response_text)

                logger.info(f"✅ Slide {slide_number} analyzed successfully")
                return analysis

            except Exception as e:
                error_str = str(e)

                if '429' in error_str or 'quota' in error_str.lower() or 'rate' in error_str.lower():
                    # Exponential backoff: 60s → 90s → 120s → 150s → 180s
                    wait_time = 60 + (attempt * 30)
                    logger.warning(
                        f"⏳ Rate limit hit on slide {slide_number} "
                        f"(attempt {attempt + 1}/{max_retries}). "
                        f"Waiting {wait_time}s before retry..."
                    )
                    time.sleep(wait_time)
                    continue  # retry

                # Non-rate-limit error → log and use default immediately
                logger.error(f"❌ Non-rate-limit error on slide {slide_number}: {error_str}")
                return self._get_default_analysis()

        # All retries exhausted
        logger.error(f"❌ All {max_retries} retries exhausted for slide {slide_number}. Using default.")
        return self._get_default_analysis()

    def _build_slide_analysis_prompt(self, slide_number, text_content, has_images, has_charts):
        """Build the prompt for Gemini — kept concise to save tokens"""

        # Limit text to 500 chars to reduce token usage on free tier
        content = text_content[:500] if text_content else "[No text content]"

        prompt = f"""You are an expert pitch coach analyzing a startup pitch deck slide.

Slide #{slide_number}
Content: {content}
Has images: {"Yes" if has_images else "No"}
Has charts: {"Yes" if has_charts else "No"}

Analyze this slide and return ONLY this exact JSON format, no other text:
{{
  "slide_type": "problem",
  "quality_score": 75,
  "strengths": ["Clear problem statement", "Uses concrete examples"],
  "weaknesses": ["Too much text", "No visual elements"],
  "suggestions": "Reduce text by 50% and add a visual representation...",
  "coaching_script": "The problem we are solving is...",
  "key_points": ["State the problem clearly", "Show market impact", "Connect to customer pain"],
  "estimated_speaking_time": 45
}}

slide_type must be one of: title, problem, solution, product, market, business_model, traction, competition, team, financials, ask, other
quality_score is 0-100
estimated_speaking_time is in seconds
Return ONLY valid JSON, no other text."""

        return prompt

    def _parse_analysis_response(self, response_text):
        """Parse Gemini's JSON response"""
        try:
            response_text = response_text.strip()

            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()

            analysis = json.loads(response_text)

            required_fields = [
                'slide_type', 'quality_score', 'strengths', 'weaknesses',
                'suggestions', 'coaching_script', 'key_points', 'estimated_speaking_time'
            ]

            for field in required_fields:
                if field not in analysis:
                    logger.warning(f"Missing field in analysis: {field}")
                    analysis[field] = self._get_default_value(field)

            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Response was: {response_text}")
            return self._get_default_analysis()

    def _get_default_value(self, field):
        """Get default value for a field"""
        defaults = {
            'slide_type': 'other',
            'quality_score': 70,
            'strengths': ['Content is present'],
            'weaknesses': ['Needs improvement'],
            'suggestions': 'Review and refine this slide for clarity and impact.',
            'coaching_script': 'Present this slide with confidence and clarity.',
            'key_points': ['Main point 1', 'Main point 2'],
            'estimated_speaking_time': 30,
        }
        return defaults.get(field, '')

    def _get_default_analysis(self):
        """Return default analysis when AI fails"""
        return {
            'slide_type': 'other',
            'quality_score': 70,
            'strengths': ['Slide content is present'],
            'weaknesses': ['Automated analysis unavailable'],
            'suggestions': 'Please review this slide manually for improvements.',
            'coaching_script': 'Present the key points from this slide clearly and confidently.',
            'key_points': ['Review slide content', 'Identify main message', 'Practice delivery'],
            'estimated_speaking_time': 30,
        }