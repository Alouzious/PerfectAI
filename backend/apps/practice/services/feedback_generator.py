"""
Feedback Generator Service
Generates personalized coaching feedback using Google Gemini AI
"""
import google.generativeai as genai
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)


class FeedbackGenerator:
    """Generate personalized pitch coaching feedback"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
    
    def generate(self, session, metrics, pitch_deck=None):
        """
        Generate personalized feedback for a practice session
        
        Args:
            session: PracticeSession object
            metrics: Dict of analysis metrics
            pitch_deck: Optional PitchDeck object for context
            
        Returns:
            dict: Feedback with scores and suggestions
        """
        try:
            prompt = self._build_feedback_prompt(session, metrics, pitch_deck)
            
            logger.info(f"Generating feedback for session {session.id}")
            
            message = self.model.generate_content(prompt)
            response_text = message.text
            
            feedback_data = self._parse_feedback(response_text, metrics)
            
            logger.info(f"Feedback generated for session {session.id}")
            return feedback_data
            
        except Exception as e:
            logger.error(f"Error generating feedback: {str(e)}")
            return self._get_default_feedback(metrics)
    
    def _build_feedback_prompt(self, session, metrics, pitch_deck):
        """Build prompt for feedback generation"""
        
        pitch_context = ""
        if pitch_deck:
            pitch_context = f"\n**Pitch Title:** {pitch_deck.title}\n**Total Slides:** {pitch_deck.total_slides}"
        
        prompt = f"""You are an expert pitch coach providing feedback on a practice session.

**Practice Details:**
- Pitch Type: {session.get_pitch_type_display()}
- Duration: {session.duration_seconds} seconds ({session.duration_seconds // 60} minutes)
- Target Duration: {session.target_duration_seconds} seconds
{pitch_context}

**Performance Metrics:**
- Word Count: {metrics['word_count']}
- Speaking Pace: {metrics['speaking_pace_wpm']:.1f} words per minute
- Filler Words: {metrics['filler_words_count']} ({', '.join([f"{k}: {v}" for k, v in metrics['filler_words_detail'].items()][:5])})
- Pace Score: {metrics['pace_score']}/100
- Clarity Score: {metrics['clarity_score']}/100

**Transcript Excerpt:**
{session.transcript[:500]}...

**Your Task:**
Provide personalized coaching feedback in JSON format:

{{
  "confidence_score": 75,
  "content_score": 80,
  "structure_score": 70,
  "feedback": "A detailed paragraph of feedback (3-5 sentences)...",
  "strengths": ["Strength 1", "Strength 2", "Strength 3"],
  "improvements": ["Improvement 1", "Improvement 2", "Improvement 3"]
}}

**Scoring Guidelines:**
- confidence_score (0-100): Voice energy, conviction, hesitation
- content_score (0-100): Message clarity, value proposition, completeness
- structure_score (0-100): Logical flow, organization, transitions

**Feedback Guidelines:**
- Be specific and actionable
- Balance positivity with constructive criticism
- Reference actual metrics (pace, filler words, etc.)
- Suggest concrete next steps

Return ONLY valid JSON, no other text."""

        return prompt
    
    def _parse_feedback(self, response_text, metrics):
        """Parse AI feedback response"""
        try:
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            feedback = json.loads(response_text)
            
            feedback.setdefault('confidence_score', 75)
            feedback.setdefault('content_score', 75)
            feedback.setdefault('structure_score', 75)
            feedback.setdefault('feedback', 'Good effort on your practice session.')
            feedback.setdefault('strengths', ['Clear delivery'])
            feedback.setdefault('improvements', ['Keep practicing'])
            
            feedback['pace_score'] = metrics['pace_score']
            feedback['clarity_score'] = metrics['clarity_score']
            
            feedback['overall_score'] = round((
                feedback['pace_score'] +
                feedback['clarity_score'] +
                feedback['confidence_score'] +
                feedback['content_score'] +
                feedback['structure_score']
            ) / 5, 2)
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error parsing feedback: {str(e)}")
            return self._get_default_feedback(metrics)
    
    def _get_default_feedback(self, metrics):
        """Get default feedback when AI fails"""
        return {
            'overall_score': 70,
            'pace_score': metrics.get('pace_score', 70),
            'clarity_score': metrics.get('clarity_score', 70),
            'confidence_score': 70,
            'content_score': 70,
            'structure_score': 70,
            'feedback': 'Thank you for practicing your pitch. Keep working on your delivery and timing.',
            'strengths': [
                'Completed the practice session',
                'Demonstrated commitment to improvement'
            ],
            'improvements': [
                'Focus on reducing filler words',
                'Work on maintaining consistent pacing',
                'Practice more frequently for better results'
            ]
        }