from rest_framework import serializers
from .models import Question, Answer


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question"""
    
    pitch_deck_title = serializers.CharField(source='pitch_deck.title', read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id',
            'pitch_deck',
            'pitch_deck_title',
            'question_text',
            'category',
            'difficulty',
            'related_slide_number',
            'key_points_to_cover',
            'times_asked',
            'average_answer_score',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'times_asked',
            'average_answer_score',
            'created_at',
        ]


class QuestionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing questions"""
    
    class Meta:
        model = Question
        fields = [
            'id',
            'question_text',
            'category',
            'difficulty',
            'times_asked',
        ]


class AnswerSerializer(serializers.ModelSerializer):
    """Serializer for Answer"""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    question_category = serializers.CharField(source='question.category', read_only=True)
    
    class Meta:
        model = Answer
        fields = [
            'id',
            'question',
            'question_text',
            'question_category',
            'user',
            'user_username',
            'practice_session',
            'answer_text',
            'answer_duration_seconds',
            'word_count',
            'quality_score',
            'completeness_score',
            'clarity_score',
            'confidence_score',
            'relevance_score',
            'key_points_covered',
            'key_points_missed',
            'feedback',
            'strong_points',
            'improvements',
            'suggested_answer',
            'status',
            'created_at',
            'analyzed_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'word_count',
            'quality_score',
            'completeness_score',
            'clarity_score',
            'confidence_score',
            'relevance_score',
            'key_points_covered',
            'key_points_missed',
            'feedback',
            'strong_points',
            'improvements',
            'suggested_answer',
            'status',
            'created_at',
            'analyzed_at',
        ]


class AnswerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating answers"""
    
    class Meta:
        model = Answer
        fields = [
            'question',
            'practice_session',
            'answer_text',
            'answer_duration_seconds',
        ]
    
    def validate_answer_text(self, value):
        """Validate answer is not empty"""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Answer must be at least 10 characters")
        return value
    
    def create(self, validated_data):
        """Create answer"""
        answer = Answer.objects.create(
            user=self.context['request'].user,
            question=validated_data['question'],
            practice_session=validated_data.get('practice_session'),
            answer_text=validated_data['answer_text'],
            answer_duration_seconds=validated_data.get('answer_duration_seconds', 0),
            word_count=len(validated_data['answer_text'].split()),
            status='pending',
        )
        
        return answer