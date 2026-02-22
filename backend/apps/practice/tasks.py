from celery import shared_task
from django.utils import timezone
from .models import PracticeSession
from .services.text_analyzer import TextAnalyzer
from .services.feedback_generator import FeedbackGenerator
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def analyze_practice_session(self, session_id):
    """
    Background task to analyze a practice session with real services
    """
    try:
        # Get session
        session = PracticeSession.objects.get(id=session_id)
        
        # Update status
        session.status = 'processing'
        session.save()
        
        logger.info(f"Starting analysis of practice session: {session.id}")
        
        # STEP 1: Analyze transcript
        text_analyzer = TextAnalyzer()
        metrics = text_analyzer.analyze(
            transcript=session.transcript,
            duration_seconds=session.duration_seconds
        )
        
        logger.info(f"Text analysis complete: {metrics['word_count']} words")
        
        # STEP 2: Generate feedback with AI
        feedback_gen = FeedbackGenerator()
        feedback_data = feedback_gen.generate(
            session=session,
            metrics=metrics,
            pitch_deck=session.pitch_deck
        )
        
        logger.info(f"Feedback generated, overall score: {feedback_data['overall_score']}")
        
        # Update session with all data
        session.word_count = metrics['word_count']
        session.unique_words_count = metrics['unique_words_count']
        session.speaking_pace_wpm = metrics['speaking_pace_wpm']
        session.filler_words_count = metrics['filler_words_count']
        session.filler_words_detail = metrics['filler_words_detail']
        
        session.pace_score = feedback_data['pace_score']
        session.clarity_score = feedback_data['clarity_score']
        session.confidence_score = feedback_data['confidence_score']
        session.content_score = feedback_data['content_score']
        session.structure_score = feedback_data['structure_score']
        session.overall_score = feedback_data['overall_score']
        
        session.feedback = feedback_data['feedback']
        session.strengths = feedback_data['strengths']
        session.improvements = feedback_data['improvements']
        
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.save()
        
        # Update user profile stats
        session.user.profile.increment_practice_session_count()
        session.user.profile.update_average_score(session.overall_score)
        
        logger.info(f"✅ Completed analysis of practice session: {session.id}")
        
        return {
            'status': 'success',
            'session_id': str(session_id),
            'overall_score': session.overall_score
        }
        
    except Exception as e:
        logger.error(f"❌ Error analyzing practice session: {str(e)}")
        
        try:
            session = PracticeSession.objects.get(id=session_id)
            session.status = 'failed'
            session.save()
        except:
            pass
        
        return {'status': 'error', 'message': str(e)}