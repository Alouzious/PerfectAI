from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.pitches.models import PitchDeck
from .models import Question, Answer
from .serializers import (
    QuestionSerializer,
    QuestionListSerializer,
    AnswerSerializer,
    AnswerCreateSerializer,
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_questions(request, deck_id):
    """Generate or retrieve questions for a pitch deck"""
    pitch_deck = get_object_or_404(PitchDeck, id=deck_id, owner=request.user)
    
    # Check if questions already exist
    existing_questions = Question.objects.filter(pitch_deck=pitch_deck)
    
    if existing_questions.exists():
        serializer = QuestionListSerializer(existing_questions, many=True)
        return Response({
            'pitch_deck_id': deck_id,
            'total_questions': existing_questions.count(),
            'questions': serializer.data
        })
    
    # ✅ TRIGGER BACKGROUND TASK
    from .tasks import generate_questions_for_deck
    generate_questions_for_deck.delay(str(deck_id))
    
    return Response({
        'message': 'Questions are being generated. Please check back in a moment.',
        'pitch_deck_id': deck_id,
    }, status=status.HTTP_202_ACCEPTED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_question(request, question_id):
    """Get single question with details"""
    question = get_object_or_404(Question, id=question_id)
    
    # Verify user owns the pitch deck
    if question.pitch_deck.owner != request.user:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = QuestionSerializer(question)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answer(request):
    """Submit answer to a question"""
    serializer = AnswerCreateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        answer = serializer.save()
        
        # ✅ TRIGGER BACKGROUND TASK
        from .tasks import analyze_answer
        analyze_answer.delay(str(answer.id))
        
        return Response({
            'message': 'Answer submitted. Analysis in progress.',
            'answer': AnswerSerializer(answer).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_answer(request, answer_id):
    """Get answer with feedback"""
    answer = get_object_or_404(Answer, id=answer_id, user=request.user)
    serializer = AnswerSerializer(answer)
    
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_answers(request):
    """List all answers by current user"""
    answers = Answer.objects.filter(user=request.user)
    
    # Optional filters
    question_id = request.query_params.get('question')
    category = request.query_params.get('category')
    
    if question_id:
        answers = answers.filter(question_id=question_id)
    if category:
        answers = answers.filter(question__category=category)
    
    serializer = AnswerSerializer(answers, many=True)
    
    return Response({
        'count': answers.count(),
        'results': serializer.data
    })