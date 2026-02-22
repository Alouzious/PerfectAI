from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify
import uuid


class PitchDeck(models.Model):
    """Main pitch deck uploaded by user"""
    
    # Primary Key (Better than default auto-increment)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='pitch_decks',
        db_index=True  # INDEX for faster queries
    )
    
    # Basic Info
    title = models.CharField(max_length=200, db_index=True)  # INDEX for search
    slug = models.SlugField(max_length=250, unique=True, blank=True)  # SEO-friendly URLs
    
    # File Storage
    uploaded_file = models.FileField(
        upload_to='pitch_decks/%Y/%m/%d/',  # Organized by date
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'pptx', 'ppt'])],
        max_length=500
    )
    file_type = models.CharField(max_length=10)
    file_size = models.BigIntegerField(default=0)  # Store file size in bytes
    
    # Status & Metadata
    STATUS_CHOICES = [
        ('pending', 'Pending Analysis'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    total_slides = models.IntegerField(default=0)
    analyzed = models.BooleanField(default=False, db_index=True)  # INDEX for filtering
    
    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)  # INDEX for sorting
    updated_at = models.DateTimeField(auto_now=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Pitch Deck'
        verbose_name_plural = 'Pitch Decks'
        indexes = [
            models.Index(fields=['-uploaded_at', 'owner']),  # Composite index
            models.Index(fields=['status', 'analyzed']),  # Composite index
        ]
    
    def __str__(self):
        return f"{self.title} by {self.owner.username}"
    
    def save(self, *args, **kwargs):
        """Auto-generate slug on save"""
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while PitchDeck.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    @property
    def file_size_mb(self):
        """Return file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)
    
    @property
    def is_processed(self):
        """Check if deck has been fully processed"""
        return self.status == 'completed' and self.analyzed


class Slide(models.Model):
    """Individual slide from a pitch deck"""
    
    # Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    pitch_deck = models.ForeignKey(
        PitchDeck, 
        on_delete=models.CASCADE, 
        related_name='slides',
        db_index=True
    )
    slide_number = models.IntegerField(db_index=True)  # INDEX for ordering
    
    # Extracted content
    text_content = models.TextField(blank=True)
    has_images = models.BooleanField(default=False)
    has_charts = models.BooleanField(default=False)
    
    # AI Analysis
    SLIDE_TYPES = [
        ('title', 'Title/Cover'),
        ('problem', 'Problem Statement'),
        ('solution', 'Solution'),
        ('product', 'Product Demo'),
        ('market', 'Market Size'),
        ('business_model', 'Business Model'),
        ('traction', 'Traction/Metrics'),
        ('competition', 'Competition'),
        ('team', 'Team'),
        ('financials', 'Financials'),
        ('ask', 'The Ask'),
        ('other', 'Other'),
    ]
    slide_type = models.CharField(max_length=50, choices=SLIDE_TYPES, blank=True, db_index=True)
    
    # JSON Fields for flexibility
    strengths = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
    suggestions = models.TextField(blank=True)
    
    # Coaching
    suggested_script = models.TextField(blank=True)
    key_points = models.JSONField(default=list, blank=True)
    estimated_speaking_time = models.IntegerField(default=0)  # seconds
    
    # Quality Score
    quality_score = models.FloatField(default=0, db_index=True)  # 0-100
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['slide_number']
        verbose_name = 'Slide'
        verbose_name_plural = 'Slides'
        unique_together = [['pitch_deck', 'slide_number']]  # Prevent duplicate slide numbers
        indexes = [
            models.Index(fields=['pitch_deck', 'slide_number']),  # Composite index
            models.Index(fields=['slide_type', 'quality_score']),  # For filtering
        ]
    
    def __str__(self):
        return f"Slide {self.slide_number} - {self.pitch_deck.title}"
    
    @property
    def is_key_slide(self):
        """Identify critical slides"""
        return self.slide_type in ['problem', 'solution', 'market', 'ask']