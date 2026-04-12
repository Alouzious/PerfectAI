"""
AI Analyzer Service
Uses Groq (Llama 3.3 70B) to analyze pitch deck slides
Fast inference, no rate limit headaches like Gemini free tier
"""
import os
import json
import logging
import time
from django.conf import settings

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Analyze pitch deck slides using Groq"""

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

    def analyze_slide(self, slide_number, text_content, has_images=False, has_charts=False):
        """
        Analyze a single slide with Groq AI.

        Args:
            slide_number (int):   Slide number
            text_content (str):   Text extracted from slide
            has_images (bool):    Whether slide has images
            has_charts (bool):    Whether slide has charts

        Returns:
            dict: Analysis results
        """
        prompt = self._build_slide_analysis_prompt(
            slide_number, text_content, has_images, has_charts
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Analyzing slide {slide_number} with Groq "
                    f"(attempt {attempt + 1}/{max_retries})"
                )

                response = self.client.chat.completions.create(
                    model=self.MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert pitch coach. "
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
                    max_tokens=800,
                )

                response_text = response.choices[0].message.content
                analysis = self._parse_analysis_response(response_text)

                logger.info(f"✅ Slide {slide_number} analyzed successfully")
                return analysis

            except Exception as e:
                error_str = str(e)

                # Handle rate limit (Groq is generous but just in case)
                if '429' in error_str or 'rate' in error_str.lower():
                    wait_time = 10 * (attempt + 1)
                    logger.warning(
                        f"⏳ Rate limit on slide {slide_number}, "
                        f"waiting {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue

                logger.error(f"❌ Error on slide {slide_number}: {error_str}")
                return self._get_default_analysis()

        logger.error(f"❌ All retries exhausted for slide {slide_number}. Using default.")
        return self._get_default_analysis()

    def _build_slide_analysis_prompt(self, slide_number, text_content, has_images, has_charts):
        """Build the analysis prompt"""

        # Limit content to avoid token waste
        content = text_content[:500] if text_content else "[No text content]"

        prompt = f"""Analyze this startup pitch deck slide and return a JSON coaching report.

Slide #{slide_number}
Content: {content}
Has images: {"Yes" if has_images else "No"}
Has charts: {"Yes" if has_charts else "No"}

Return ONLY this exact JSON, nothing else:
{{
  "slide_type": "problem",
  "quality_score": 75,
  "strengths": ["Clear problem statement", "Uses concrete examples"],
  "weaknesses": ["Too much text", "No visual elements"],
  "suggestions": "Reduce text by 50% and add a visual representation of the problem.",
  "coaching_script": "The problem we are solving is...",
  "key_points": ["State the problem clearly", "Show market impact", "Connect to customer pain"],
  "estimated_speaking_time": 45
}}

Rules:
- slide_type must be one of: title, problem, solution, product, market, business_model, traction, competition, team, financials, ask, other
- quality_score is 0-100
- estimated_speaking_time is in seconds
- strengths and weaknesses are lists of 2-3 short strings
- Return ONLY valid JSON, no other text"""

        return prompt

    def _parse_analysis_response(self, response_text):
        """Parse Groq JSON response"""
        try:
            text = response_text.strip()

            # Strip accidental markdown fences
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()

            analysis = json.loads(text)

            # Ensure all required fields exist
            required_fields = [
                'slide_type', 'quality_score', 'strengths', 'weaknesses',
                'suggestions', 'coaching_script', 'key_points', 'estimated_speaking_time'
            ]
            for field in required_fields:
                if field not in analysis:
                    logger.warning(f"Missing field in analysis: {field}")
                    analysis[field] = self._get_default_value(field)

            # Clamp quality_score to 0-100
            analysis['quality_score'] = max(0, min(100, int(analysis['quality_score'])))

            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Groq: {str(e)}")
            logger.debug(f"Raw response: {response_text}")
            return self._get_default_analysis()

    def _get_default_value(self, field):
        """Default value for a single missing field"""
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
        """Full default analysis when Groq call fails"""
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