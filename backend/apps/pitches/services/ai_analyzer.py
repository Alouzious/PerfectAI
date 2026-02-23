"""
AI Analyzer Service
Uses Google Gemini API to analyze pitch deck slides
"""
import google.generativeai as genai
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Analyze slides using Gemini AI"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
    
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
        try:
            prompt = self._build_slide_analysis_prompt(
                slide_number, 
                text_content, 
                has_images, 
                has_charts
            )
            
            logger.info(f"Analyzing slide {slide_number} with Gemini")
            
            message = self.model.generate_content(prompt)
            response_text = message.text
            
            analysis = self._parse_analysis_response(response_text)
            
            logger.info(f"Slide {slide_number} analyzed successfully")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing slide {slide_number}: {str(e)}")
            return self._get_default_analysis()
    
    def _build_slide_analysis_prompt(self, slide_number, text_content, has_images, has_charts):
        """Build the prompt for Gemini"""
        
        prompt = f"""You are an expert pitch coach analyzing a startup pitch deck slide.

**Slide #{slide_number}**

**Content:**
{text_content if text_content else "[No text content]"}

**Visual Elements:**
- Has images: {"Yes" if has_images else "No"}
- Has charts/graphs: {"Yes" if has_charts else "No"}

**Your Task:**
Analyze this slide and provide:

1. **Slide Type** (choose one):
   - title (title/cover slide)
   - problem (problem statement)
   - solution (solution/product)
   - product (product demo/features)
   - market (market size/opportunity)
   - business_model (revenue model)
   - traction (metrics/traction)
   - competition (competitive landscape)
   - team (team introduction)
   - financials (financial projections)
   - ask (the ask/investment)
   - other (doesn't fit above)

2. **Quality Score** (0-100): Rate the overall effectiveness

3. **Strengths** (2-3 bullet points): What works well

4. **Weaknesses** (2-3 bullet points): What needs improvement

5. **Suggestions** (paragraph): Specific actionable advice to improve this slide

6. **Coaching Script** (2-3 paragraphs): A suggested 30-45 second script for presenting this slide. Write in first person as if the founder is speaking.

7. **Key Points** (3-5 bullet points): Main points that MUST be covered when presenting this slide

8. **Estimated Speaking Time** (in seconds): How long should this slide take to present

Return your analysis in this EXACT JSON format:
{{
  "slide_type": "problem",
  "quality_score": 75,
  "strengths": ["Clear problem statement", "Uses concrete examples"],
  "weaknesses": ["Too much text", "No visual elements"],
  "suggestions": "Reduce text by 50% and add a visual representation...",
  "coaching_script": "The problem we're solving is...",
  "key_points": ["State the problem clearly", "Show market impact", "Connect to customer pain"],
  "estimated_speaking_time": 45
}}

IMPORTANT: Return ONLY valid JSON, no other text."""

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