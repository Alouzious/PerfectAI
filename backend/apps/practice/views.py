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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_practice_audio(request, session_id):
    """
    Receive an audio recording, transcribe it, then trigger analysis.

    Expected request: multipart/form-data with:
        - audio:            The audio file (required)
        - duration_seconds: How long the recording is in seconds (optional)

    Flow:
        1. Validate the session belongs to this user and is in 'pending' state
        2. Validate and save the audio file
        3. Transcribe audio → text via Whisper
        4. Save transcript + duration to session
        5. Trigger the existing background analysis task
        6. Return session data immediately (analysis happens in background)
    """
    # ── 1. Get session ────────────────────────────────────────────────────────
    session = get_object_or_404(PracticeSession, id=session_id, user=request.user)

    if session.status not in ('pending', 'failed'):
        return Response(
            {
                'error': 'Cannot submit audio',
                'detail': (
                    f"Session is already '{session.status}'. "
                    "Only pending or failed sessions can receive audio."
                ),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ── 2. Validate audio file ────────────────────────────────────────────────
    audio_file = request.FILES.get('audio')
    if not audio_file:
        return Response(
            {'error': 'No audio file provided. Send the file as "audio" in form-data.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ── 3. Transcribe ─────────────────────────────────────────────────────────
    try:
        from .services.speech_to_text import SpeechToTextService
        stt = SpeechToTextService()
        result = stt.transcribe(audio_file)
    except ValueError as e:
        # Validation errors (wrong format, too large)
        return Response(
            {'error': 'Invalid audio file', 'detail': str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except RuntimeError as e:
        # Whisper API errors
        return Response(
            {'error': 'Transcription failed', 'detail': str(e)},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    if not result['success']:
        return Response(
            {'error': 'No speech detected', 'detail': result.get('error', '')},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    # ── 4. Update session with transcript ─────────────────────────────────────
    transcript = result['transcript']

    # Use whisper duration if frontend didn't send one
    duration = int(request.data.get('duration_seconds', 0))
    if duration == 0 and result.get('duration'):
        duration = int(result['duration'])

    session.transcript = transcript
    session.duration_seconds = duration
    session.status = 'pending'          # reset so task picks it up cleanly
    session.save(update_fields=['transcript', 'duration_seconds', 'status'])

    # ── 5. Trigger existing Celery analysis task ───────────────────────────────
    from .tasks import analyze_practice_session
    analyze_practice_session.delay(str(session.id))

    # ── 6. Return immediately — analysis runs in background ───────────────────
    return Response(
        {
            'message': 'Audio received and transcribed. Analysis in progress.',
            'session_id': str(session.id),
            'transcript_preview': transcript[:200] + ('...' if len(transcript) > 200 else ''),
            'word_count': len(transcript.split()),
            'status': 'processing',
        },
        status=status.HTTP_202_ACCEPTED,
    )