from rest_framework import serializers
from .models import PracticeSession, PracticeProgress


class PracticeSessionSerializer(serializers.ModelSerializer):
    """Serializer for PracticeSession"""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    pitch_deck_title = serializers.CharField(source='pitch_deck.title', read_only=True)
    is_within_time_limit = serializers.ReadOnlyField()
    improvement_from_last = serializers.ReadOnlyField()
    
    class Meta:
        model = PracticeSession
        fields = [
            'id',
            'user',
            'user_username',
            'pitch_deck',
            'pitch_deck_title',
            'pitch_type',
            'session_number',
            'duration_seconds',
            'target_duration_seconds',
            'transcript',
            'word_count',
            'overall_score',
            'pace_score',
            'clarity_score',
            'confidence_score',
            'content_score',
            'structure_score',
            'speaking_pace_wpm',
            'filler_words_count',
            'filler_words_detail',
            'unique_words_count',
            'feedback',
            'strengths',
            'improvements',
            'status',
            'is_within_time_limit',
            'improvement_from_last',
            'created_at',
            'completed_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'session_number',
            'word_count',
            'overall_score',
            'pace_score',
            'clarity_score',
            'confidence_score',
            'content_score',
            'structure_score',
            'speaking_pace_wpm',
            'filler_words_count',
            'filler_words_detail',
            'unique_words_count',
            'feedback',
            'strengths',
            'improvements',
            'status',
            'created_at',
            'completed_at',
        ]


class PracticeSessionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing practice sessions"""
    
    pitch_deck_title = serializers.CharField(source='pitch_deck.title', read_only=True)
    
    class Meta:
        model = PracticeSession
        fields = [
            'id',
            'pitch_deck_title',
            'pitch_type',
            'session_number',
            'overall_score',
            'duration_seconds',
            'status',
            'created_at',
        ]


class PracticeSessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating practice sessions"""
    
    class Meta:
        model = PracticeSession
        fields = [
            'pitch_deck',
            'pitch_type',
            'transcript',
            'duration_seconds',
            'target_duration_seconds',
        ]
    
    def validate_transcript(self, value):
        """Validate transcript is not empty"""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Transcript must be at least 10 characters")
        return value
    
    def create(self, validated_data):
        """Create practice session"""
        session = PracticeSession.objects.create(
            user=self.context['request'].user,
            pitch_deck=validated_data['pitch_deck'],
            pitch_type=validated_data['pitch_type'],
            transcript=validated_data['transcript'],
            duration_seconds=validated_data.get('duration_seconds', 0),
            target_duration_seconds=validated_data.get('target_duration_seconds', 0),
            status='pending',
        )
        
        return session


class PracticeProgressSerializer(serializers.ModelSerializer):
    """Serializer for PracticeProgress"""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    pitch_deck_title = serializers.CharField(source='pitch_deck.title', read_only=True)
    
    class Meta:
        model = PracticeProgress
        fields = [
            'user_username',
            'pitch_deck_title',
            'total_sessions',
            'best_score',
            'average_score',
            'first_session_date',
            'last_session_date',
            'updated_at',
        ]