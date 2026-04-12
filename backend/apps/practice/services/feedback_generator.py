"""
Feedback Generator Service
Generates personalized coaching feedback using Groq (Llama 3.3 70B)
"""
import os
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class FeedbackGenerator:
    """Generate personalized pitch coaching feedback using Groq"""

    MODEL = "llama-3.3-70b-versatile"

    def __init__(self):
        try:
            from groq import Groq
            self.client = Groq(api_key=self._get_api_key())
        except ImportError:
            raise ImportError(
                "groq package is required. Install it with: pip install groq"
            )

    def _get_api_key(self):
        """Get Groq API key from Django settings or environment"""
        api_key = getattr(settings, 'GROQ_API_KEY', None) or os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. Add it to your .env file."
            )
        return api_key

    def generate(self, session, metrics, pitch_deck=None):
        """
        Generate personalized feedback for a practice session.

        Args:
            session:    PracticeSession object
            metrics:    Dict of analysis metrics from TextAnalyzer
            pitch_deck: Optional PitchDeck object for context

        Returns:
            dict: Feedback with scores and suggestions
        """
        try:
            prompt = self._build_feedback_prompt(session, metrics, pitch_deck)

            logger.info(f"Generating feedback for session {session.id} via Groq")

            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert pitch coach. "
                            "You always respond with valid JSON only — "
                            "no markdown, no code fences, no extra text."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.7,
                max_tokens=1000,
            )

            response_text = response.choices[0].message.content
            feedback_data = self._parse_feedback(response_text, metrics)

            logger.info(
                f"Feedback generated for session {session.id}, "
                f"overall score: {feedback_data['overall_score']}"
            )
            return feedback_data

        except Exception as e:
            logger.error(f"Error generating feedback: {str(e)}")
            return self._get_default_feedback(metrics)

    def _build_feedback_prompt(self, session, metrics, pitch_deck):
        """Build the coaching feedback prompt"""

        pitch_context = ""
        if pitch_deck:
            pitch_context = (
                f"\nPitch Title: {pitch_deck.title}"
                f"\nTotal Slides: {pitch_deck.total_slides}"
            )

        # Truncate transcript to avoid exceeding token limits
        transcript_excerpt = session.transcript[:500]
        if len(session.transcript) > 500:
            transcript_excerpt += "..."

        # Format filler words nicely
        top_fillers = ", ".join(
            f"{k}: {v}"
            for k, v in list(metrics['filler_words_detail'].items())[:5]
        ) or "none detected"

        prompt = f"""Analyze this pitch practice session and return a JSON coaching report.

PRACTICE DETAILS:
- Pitch Type: {session.get_pitch_type_display()}
- Duration: {session.duration_seconds}s (target: {session.target_duration_seconds}s)
{pitch_context}

PERFORMANCE METRICS:
- Word Count: {metrics['word_count']}
- Speaking Pace: {metrics['speaking_pace_wpm']:.1f} WPM (ideal: 140-160 WPM)
- Filler Words: {metrics['filler_words_count']} total ({top_fillers})
- Pace Score: {metrics['pace_score']}/100
- Clarity Score: {metrics['clarity_score']}/100
- Vocabulary Richness: {metrics['vocabulary_ratio']:.2f} (unique/total words)

TRANSCRIPT EXCERPT:
{transcript_excerpt}

Return ONLY this JSON structure, nothing else:
{{
  "confidence_score": <0-100 int>,
  "content_score": <0-100 int>,
  "structure_score": <0-100 int>,
  "feedback": "<3-5 sentence coaching paragraph referencing actual metrics>",
  "strengths": ["<specific strength 1>", "<specific strength 2>", "<specific strength 3>"],
  "improvements": ["<actionable improvement 1>", "<actionable improvement 2>", "<actionable improvement 3>"]
}}

SCORING GUIDE:
- confidence_score: voice energy, conviction, absence of hesitation
- content_score: clarity of message, value proposition, completeness
- structure_score: logical flow, transitions, opening and closing strength

Be specific. Reference the actual numbers. Be encouraging but honest."""

        return prompt

    def _parse_feedback(self, response_text, metrics):
        """Parse Groq JSON response into feedback dict"""
        try:
            # Strip any accidental markdown fences
            text = response_text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()

            feedback = json.loads(text)

            # Fill in any missing keys with safe defaults
            feedback.setdefault('confidence_score', 70)
            feedback.setdefault('content_score', 70)
            feedback.setdefault('structure_score', 70)
            feedback.setdefault('feedback', 'Good effort on your practice session.')
            feedback.setdefault('strengths', ['Completed the practice session'])
            feedback.setdefault('improvements', ['Keep practicing regularly'])

            # Clamp scores to 0-100
            for key in ('confidence_score', 'content_score', 'structure_score'):
                feedback[key] = max(0, min(100, int(feedback[key])))

            # Attach analyzer scores (these come from TextAnalyzer, not the LLM)
            feedback['pace_score'] = metrics['pace_score']
            feedback['clarity_score'] = metrics['clarity_score']

            # Calculate overall as average of all 5 dimensions
            feedback['overall_score'] = round(
                (
                    feedback['pace_score']
                    + feedback['clarity_score']
                    + feedback['confidence_score']
                    + feedback['content_score']
                    + feedback['structure_score']
                )
                / 5,
                2,
            )

            return feedback

        except Exception as e:
            logger.error(f"Error parsing Groq feedback response: {str(e)}")
            logger.debug(f"Raw response was: {response_text}")
            return self._get_default_feedback(metrics)

    def _get_default_feedback(self, metrics):
        """Fallback feedback when Groq call or parsing fails"""
        return {
            'overall_score': 70,
            'pace_score': metrics.get('pace_score', 70),
            'clarity_score': metrics.get('clarity_score', 70),
            'confidence_score': 70,
            'content_score': 70,
            'structure_score': 70,
            'feedback': (
                'Thank you for practicing your pitch. '
                'Keep working on your delivery and timing.'
            ),
            'strengths': [
                'Completed the practice session',
                'Demonstrated commitment to improvement',
            ],
            'improvements': [
                'Focus on reducing filler words',
                'Work on maintaining consistent pacing',
                'Practice more frequently for better results',
            ],
        }