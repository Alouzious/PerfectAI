from celery import shared_task
from django.utils import timezone
from .models import PitchDeck, Slide
from .services.file_processor import FileProcessor
from .services.ai_analyzer import AIAnalyzer
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def analyze_pitch_deck(self, pitch_deck_id):
    """
    Background task to analyze a pitch deck with real services
    """
    try:
        # Get pitch deck
        pitch_deck = PitchDeck.objects.get(id=pitch_deck_id)
        
        # Update status
        pitch_deck.status = 'processing'
        pitch_deck.save()
        
        logger.info(f"Starting analysis of pitch deck: {pitch_deck.title}")
        
        # STEP 1: Extract slides
        processor = FileProcessor()
        slides_data = processor.extract_slides(pitch_deck.uploaded_file.path)
        
        logger.info(f"Extracted {len(slides_data)} slides")
        
        # STEP 2: Analyze each slide with AI
        analyzer = AIAnalyzer()
        
        for slide_data in slides_data:
            try:
                # Analyze with AI
                analysis = analyzer.analyze_slide(
                    slide_number=slide_data['number'],
                    text_content=slide_data['text'],
                    has_images=slide_data['has_images'],
                    has_charts=slide_data.get('has_charts', False)
                )
                
                # Create slide in database
                Slide.objects.create(
                    pitch_deck=pitch_deck,
                    slide_number=slide_data['number'],
                    text_content=slide_data['text'],
                    has_images=slide_data['has_images'],
                    has_charts=slide_data.get('has_charts', False),
                    slide_type=analysis['slide_type'],
                    quality_score=analysis['quality_score'],
                    strengths=analysis['strengths'],
                    weaknesses=analysis['weaknesses'],
                    suggestions=analysis['suggestions'],
                    suggested_script=analysis['coaching_script'],
                    key_points=analysis['key_points'],
                    estimated_speaking_time=analysis['estimated_speaking_time'],
                )
                
                logger.info(f"Analyzed slide {slide_data['number']}")
                
            except Exception as e:
                logger.error(f"Error analyzing slide {slide_data['number']}: {str(e)}")
                continue
        
        # Update pitch deck
        pitch_deck.total_slides = len(slides_data)
        pitch_deck.analyzed = True
        pitch_deck.status = 'completed'
        pitch_deck.analyzed_at = timezone.now()
        pitch_deck.save()
        
        logger.info(f"✅ Completed analysis of pitch deck: {pitch_deck.title}")
        
        return {
            'status': 'success',
            'pitch_deck_id': str(pitch_deck_id),
            'total_slides': len(slides_data)
        }
        
    except Exception as e:
        logger.error(f"❌ Error analyzing pitch deck: {str(e)}")
        
        try:
            pitch_deck = PitchDeck.objects.get(id=pitch_deck_id)
            pitch_deck.status = 'failed'
            pitch_deck.save()
        except:
            pass
        
        return {'status': 'error', 'message': str(e)}