from celery import shared_task
from django.utils import timezone
from .models import Question, Answer
from apps.pitches.models import PitchDeck
from .services.question_generator import QuestionGenerator
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def generate_questions_for_deck(self, pitch_deck_id):
    """
    Background task to generate questions with real AI service
    """
    try:
        # Get pitch deck
        pitch_deck = PitchDeck.objects.get(id=pitch_deck_id)
        
        logger.info(f"Generating questions for pitch deck: {pitch_deck.title}")
        
        # Generate questions with AI
        generator = QuestionGenerator()
        questions_data = generator.generate(pitch_deck)
        
        # Create questions in database
        created_count = 0
        for q_data in questions_data:
            Question.objects.get_or_create(
                pitch_deck=pitch_deck,
                question_text=q_data['question_text'],
                defaults={
                    'category': q_data['category'],
                    'difficulty': q_data['difficulty'],
                    'related_slide_number': q_data.get('related_slide_number'),
                    'key_points_to_cover': q_data['key_points_to_cover'],
                }
            )
            created_count += 1
        
        logger.info(f"✅ Generated {created_count} questions for: {pitch_deck.title}")
        
        return {
            'status': 'success',
            'pitch_deck_id': str(pitch_deck_id),
            'questions_generated': created_count
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating questions: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task(bind=True)
def analyze_answer(self, answer_id):
    """
    Background task to analyze an answer (placeholder for now)
    """
    try:
        answer = Answer.objects.get(id=answer_id)
        
        logger.info(f"Analyzing answer: {answer.id}")
        
        # TODO: Build answer analyzer service
        # For now, simple scoring
        word_count = len(answer.answer_text.split())
        
        answer.quality_score = 75
        answer.completeness_score = 70
        answer.clarity_score = 80
        answer.confidence_score = 72
        answer.relevance_score = 85
        answer.feedback = "Good answer. Keep practicing!"
        answer.status = 'completed'
        answer.analyzed_at = timezone.now()
        answer.save()
        
        logger.info(f"✅ Analyzed answer: {answer.id}")
        
        return {'status': 'success', 'answer_id': str(answer_id)}
        
    except Exception as e:
        logger.error(f"❌ Error analyzing answer: {str(e)}")
        return {'status': 'error', 'message': str(e)}