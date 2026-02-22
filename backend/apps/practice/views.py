from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.pitches.models import PitchDeck
from .models import PracticeSession, PracticeProgress
from .serializers import (
    PracticeSessionSerializer,
    PracticeSessionListSerializer,
    PracticeSessionCreateSerializer,
    PracticeProgressSerializer,
)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_practice_session(request):
    """Create a new practice session"""
    
    # Check if user can practice more
    if not request.user.profile.can_practice_more:
        return Response({
            'error': 'Practice limit reached',
            'message': f'Free users can practice up to {request.user.profile.practice_sessions_limit} times per month. Upgrade to Pro for unlimited practice.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = PracticeSessionCreateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        session = serializer.save()
        
        # ✅ TRIGGER BACKGROUND TASK
        from .tasks import analyze_practice_session
        analyze_practice_session.delay(str(session.id))
        
        return Response({
            'message': 'Practice session submitted. Analysis in progress.',
            'session': PracticeSessionSerializer(session).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_practice_sessions(request):
    """List all practice sessions for current user"""
    sessions = PracticeSession.objects.filter(user=request.user)
    
    # Optional filters
    pitch_deck_id = request.query_params.get('pitch_deck')
    pitch_type = request.query_params.get('pitch_type')
    
    if pitch_deck_id:
        sessions = sessions.filter(pitch_deck_id=pitch_deck_id)
    if pitch_type:
        sessions = sessions.filter(pitch_type=pitch_type)
    
    serializer = PracticeSessionListSerializer(sessions, many=True)
    
    return Response({
        'count': sessions.count(),
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_practice_session(request, session_id):
    """Get single practice session with full details"""
    session = get_object_or_404(PracticeSession, id=session_id, user=request.user)
    serializer = PracticeSessionSerializer(session)
    
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_practice_feedback(request, session_id):
    """Get feedback for a practice session"""
    session = get_object_or_404(PracticeSession, id=session_id, user=request.user)
    
    if session.status != 'completed':
        return Response({
            'message': 'Feedback not ready yet. Analysis in progress.',
            'status': session.status
        }, status=status.HTTP_202_ACCEPTED)
    
    return Response({
        'session_id': session.id,
        'overall_score': session.overall_score,
        'scores': {
            'pace': session.pace_score,
            'clarity': session.clarity_score,
            'confidence': session.confidence_score,
            'content': session.content_score,
            'structure': session.structure_score,
        },
        'metrics': {
            'duration_seconds': session.duration_seconds,
            'word_count': session.word_count,
            'speaking_pace_wpm': session.speaking_pace_wpm,
            'filler_words_count': session.filler_words_count,
            'filler_words_detail': session.filler_words_detail,
        },
        'feedback': session.feedback,
        'strengths': session.strengths,
        'improvements': session.improvements,
        'improvement_from_last': session.improvement_from_last,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_practice_progress(request):
    """Get practice progress for current user"""
    pitch_deck_id = request.query_params.get('pitch_deck')
    
    if pitch_deck_id:
        progress = get_object_or_404(
            PracticeProgress,
            user=request.user,
            pitch_deck_id=pitch_deck_id
        )
        serializer = PracticeProgressSerializer(progress)
        return Response(serializer.data)
    
    # Return all progress
    progress = PracticeProgress.objects.filter(user=request.user)
    serializer = PracticeProgressSerializer(progress, many=True)
    
    return Response({
        'count': progress.count(),
        'results': serializer.data
    })