from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile"""
    
    can_upload_more_decks = serializers.ReadOnlyField()
    remaining_pitch_decks = serializers.ReadOnlyField()
    can_practice_more = serializers.ReadOnlyField()
    is_free_user = serializers.ReadOnlyField()
    is_pro_user = serializers.ReadOnlyField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id',
            'subscription_tier',
            'subscription_start_date',
            'subscription_end_date',
            'pitch_decks_limit',
            'practice_sessions_limit',
            'pitch_decks_uploaded',
            'practice_sessions_completed',
            'total_practice_time_seconds',
            'average_practice_score',
            'best_practice_score',
            'improvement_rate',
            'preferred_pitch_type',
            'target_practice_duration',
            'notifications_enabled',
            'onboarding_completed',
            'onboarding_step',
            'can_upload_more_decks',
            'remaining_pitch_decks',
            'can_practice_more',
            'is_free_user',
            'is_pro_user',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'pitch_decks_uploaded',
            'practice_sessions_completed',
            'total_practice_time_seconds',
            'average_practice_score',
            'best_practice_score',
            'improvement_rate',
            'created_at',
        ]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User with embedded profile"""
    
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'date_joined',
            'profile',
        ]
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, data):
        """Validate passwords match"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        """Create user with hashed password"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)