from rest_framework import serializers
from .models import PitchDeck, Slide


class SlideSerializer(serializers.ModelSerializer):
    """Serializer for Slide"""
    
    is_key_slide = serializers.ReadOnlyField()
    
    class Meta:
        model = Slide
        fields = [
            'id',
            'pitch_deck',
            'slide_number',
            'text_content',
            'has_images',
            'has_charts',
            'slide_type',
            'quality_score',
            'strengths',
            'weaknesses',
            'suggestions',
            'suggested_script',
            'key_points',
            'estimated_speaking_time',
            'is_key_slide',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]


class SlideListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing slides"""
    
    class Meta:
        model = Slide
        fields = [
            'id',
            'slide_number',
            'slide_type',
            'quality_score',
            'has_images',
        ]


class PitchDeckSerializer(serializers.ModelSerializer):
    """Serializer for PitchDeck"""
    
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    slides = SlideListSerializer(many=True, read_only=True)
    file_size_mb = serializers.ReadOnlyField()
    is_processed = serializers.ReadOnlyField()
    
    class Meta:
        model = PitchDeck
        fields = [
            'id',
            'owner',
            'owner_username',
            'title',
            'slug',
            'uploaded_file',
            'file_type',
            'file_size',
            'file_size_mb',
            'status',
            'total_slides',
            'analyzed',
            'is_processed',
            'slides',
            'uploaded_at',
            'updated_at',
            'analyzed_at',
        ]
        read_only_fields = [
            'id',
            'owner',
            'slug',
            'file_type',
            'file_size',
            'status',
            'total_slides',
            'analyzed',
            'uploaded_at',
            'updated_at',
            'analyzed_at',
        ]


class PitchDeckListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing pitch decks"""
    
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    file_size_mb = serializers.ReadOnlyField()
    
    class Meta:
        model = PitchDeck
        fields = [
            'id',
            'owner_username',
            'title',
            'slug',
            'status',
            'total_slides',
            'analyzed',
            'file_size_mb',
            'uploaded_at',
        ]


class PitchDeckUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading pitch decks"""
    
    class Meta:
        model = PitchDeck
        fields = ['title', 'uploaded_file']
    
    def validate_uploaded_file(self, value):
        """Validate file type and size"""
        # Check file extension
        file_extension = value.name.split('.')[-1].lower()
        allowed_extensions = ['pdf', 'pptx', 'ppt']
        
        if file_extension not in allowed_extensions:
            raise serializers.ValidationError(
                f"File type '{file_extension}' not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Check file size (50MB limit)
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size too large. Maximum allowed: 50MB. Your file: {round(value.size / (1024 * 1024), 2)}MB"
            )
        
        return value
    
    def create(self, validated_data):
        """Create PitchDeck with file metadata"""
        uploaded_file = validated_data['uploaded_file']
        
        # Extract file metadata
        file_extension = uploaded_file.name.split('.')[-1].lower()
        file_size = uploaded_file.size
        
        pitch_deck = PitchDeck.objects.create(
            owner=self.context['request'].user,
            title=validated_data['title'],
            uploaded_file=uploaded_file,
            file_type=file_extension,
            file_size=file_size,
            status='pending',
        )
        
        return pitch_deck