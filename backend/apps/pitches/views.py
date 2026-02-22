from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import PitchDeck, Slide
from .serializers import (
    PitchDeckSerializer,
    PitchDeckListSerializer,
    PitchDeckUploadSerializer,
    SlideSerializer,
    SlideListSerializer,
)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_pitch_deck(request):
    """Upload a new pitch deck"""
    
    # Check if user can upload more decks
    if not request.user.profile.can_upload_more_decks:
        return Response({
            'error': 'Upload limit reached',
            'message': f'Free users can upload up to {request.user.profile.pitch_decks_limit} pitch decks. Upgrade to Pro for unlimited uploads.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = PitchDeckUploadSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        pitch_deck = serializer.save()
        
        # Increment user's pitch deck count
        request.user.profile.increment_pitch_deck_count()
        
        # Trigger background task
        from .tasks import analyze_pitch_deck
        analyze_pitch_deck.delay(str(pitch_deck.id))
        
        return Response({
            'message': 'Pitch deck uploaded successfully. Analysis will begin shortly.',
            'pitch_deck': PitchDeckSerializer(pitch_deck).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pitch_decks(request):
    """List all pitch decks for current user"""
    pitch_decks = PitchDeck.objects.filter(owner=request.user)
    serializer = PitchDeckListSerializer(pitch_decks, many=True)
    
    return Response({
        'count': pitch_decks.count(),
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pitch_deck(request, deck_id):
    """Get single pitch deck with all slides"""
    pitch_deck = get_object_or_404(PitchDeck, id=deck_id, owner=request.user)
    serializer = PitchDeckSerializer(pitch_deck)
    
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_pitch_deck(request, deck_id):
    """Delete a pitch deck"""
    pitch_deck = get_object_or_404(PitchDeck, id=deck_id, owner=request.user)
    pitch_deck.delete()
    
    # Decrement user's pitch deck count
    if request.user.profile.pitch_decks_uploaded > 0:
        request.user.profile.pitch_decks_uploaded -= 1
        request.user.profile.save()
    
    return Response({
        'message': 'Pitch deck deleted successfully'
    }, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_slides(request, deck_id):
    """List all slides for a pitch deck"""
    pitch_deck = get_object_or_404(PitchDeck, id=deck_id, owner=request.user)
    slides = pitch_deck.slides.all()
    serializer = SlideListSerializer(slides, many=True)
    
    return Response({
        'pitch_deck_id': deck_id,
        'total_slides': slides.count(),
        'slides': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_slide(request, deck_id, slide_number):
    """Get single slide with full details"""
    pitch_deck = get_object_or_404(PitchDeck, id=deck_id, owner=request.user)
    slide = get_object_or_404(Slide, pitch_deck=pitch_deck, slide_number=slide_number)
    serializer = SlideSerializer(slide)
    
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_slide_coaching(request, deck_id, slide_number):
    """Get coaching/script for a specific slide"""
    pitch_deck = get_object_or_404(PitchDeck, id=deck_id, owner=request.user)
    slide = get_object_or_404(Slide, pitch_deck=pitch_deck, slide_number=slide_number)
    
    return Response({
        'slide_number': slide.slide_number,
        'slide_type': slide.slide_type,
        'suggested_script': slide.suggested_script,
        'key_points': slide.key_points,
        'estimated_speaking_time': slide.estimated_speaking_time,
        'suggestions': slide.suggestions,
    })


# ===== NEW: CHECK ANALYSIS STATUS =====
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_analysis_status(request, deck_id):
    """Check if pitch deck analysis is complete"""
    pitch_deck = get_object_or_404(PitchDeck, id=deck_id, owner=request.user)
    
    status_messages = {
        'pending': 'Analysis not started yet',
        'processing': 'Analysis in progress...',
        'completed': 'Analysis complete!',
        'failed': 'Analysis failed. Please try again.'
    }
    
    return Response({
        'pitch_deck_id': str(deck_id),
        'status': pitch_deck.status,
        'analyzed': pitch_deck.analyzed,
        'total_slides': pitch_deck.total_slides,
        'message': status_messages.get(pitch_deck.status, 'Unknown status'),
        'progress_percentage': 100 if pitch_deck.status == 'completed' else (50 if pitch_deck.status == 'processing' else 0)
    })