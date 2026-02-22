from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from apps.pitches.models import PitchDeck
import uuid


class PracticeSession(models.Model):
    """Practice session where user practices their pitch"""
    
    # Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    pitch_deck = models.ForeignKey(
        PitchDeck, 
        on_delete=models.CASCADE, 
        related_name='practice_sessions',
        db_index=True
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='practice_sessions',
        db_index=True
    )
    
    # Session Info
    PITCH_TYPES = [
        ('elevator', 'Elevator Pitch (30 seconds)'),
        ('demo_day', 'Demo Day (3 minutes)'),
        ('investor', 'Investor Pitch (10 minutes)'),
        ('competition', 'Competition Pitch (5 minutes)'),
    ]
    pitch_type = models.CharField(max_length=50, choices=PITCH_TYPES, db_index=True)
    session_number = models.IntegerField(default=1)  # Track attempt number
    
    # Timing
    duration_seconds = models.IntegerField(default=0)
    target_duration_seconds = models.IntegerField(default=0)  # Expected duration
    
    # Transcript (from browser voice recognition)
    transcript = models.TextField(blank=True)
    word_count = models.IntegerField(default=0, db_index=True)
    
    # Analysis scores (0-100) with indexes for performance tracking
    overall_score = models.FloatField(default=0, db_index=True)
    pace_score = models.FloatField(default=0)
    clarity_score = models.FloatField(default=0)
    confidence_score = models.FloatField(default=0)
    content_score = models.FloatField(default=0)
    structure_score = models.FloatField(default=0)
    
    # Detailed metrics
    speaking_pace_wpm = models.FloatField(default=0)  # words per minute
    filler_words_count = models.IntegerField(default=0)
    unique_words_count = models.IntegerField(default=0)  # Vocabulary richness
    
    # Filler word details (JSON for flexibility)
    filler_words_detail = models.JSONField(default=dict, blank=True)  # {"um": 5, "uh": 3}
    
    # AI Feedback
    feedback = models.TextField(blank=True)
    strengths = models.JSONField(default=list, blank=True)
    improvements = models.JSONField(default=list, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending Analysis'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Practice Session'
        verbose_name_plural = 'Practice Sessions'
        indexes = [
            models.Index(fields=['user', '-created_at']),  # User's recent sessions
            models.Index(fields=['pitch_deck', '-overall_score']),  # Best sessions
            models.Index(fields=['pitch_type', '-created_at']),  # By type
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.pitch_type} - {self.created_at.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate session number"""
        if not self.session_number:
            last_session = PracticeSession.objects.filter(
                user=self.user,
                pitch_deck=self.pitch_deck,
                pitch_type=self.pitch_type
            ).order_by('-session_number').first()
            
            self.session_number = (last_session.session_number + 1) if last_session else 1
        
        super().save(*args, **kwargs)
    
    @property
    def is_within_time_limit(self):
        """Check if practice was within expected duration"""
        if self.target_duration_seconds == 0:
            return True
        tolerance = 30  # 30 seconds tolerance
        return abs(self.duration_seconds - self.target_duration_seconds) <= tolerance
    
    @property
    def improvement_from_last(self):
        """Calculate improvement from previous session"""
        previous = PracticeSession.objects.filter(
            user=self.user,
            pitch_deck=self.pitch_deck,
            pitch_type=self.pitch_type,
            session_number=self.session_number - 1
        ).first()
        
        if previous:
            return round(self.overall_score - previous.overall_score, 2)
        return 0
    
    @classmethod
    def get_user_average_score(cls, user):
        """Get user's average score across all sessions"""
        return cls.objects.filter(user=user, status='completed').aggregate(
            avg_score=Avg('overall_score')
        )['avg_score'] or 0


class PracticeProgress(models.Model):
    """Track user's overall progress"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='practice_progress')
    pitch_deck = models.ForeignKey(PitchDeck, on_delete=models.CASCADE, related_name='progress_tracking')
    
    # Aggregate stats
    total_sessions = models.IntegerField(default=0)
    best_score = models.FloatField(default=0)
    average_score = models.FloatField(default=0)
    
    # Milestones
    first_session_date = models.DateTimeField(null=True, blank=True)
    last_session_date = models.DateTimeField(null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Practice Progress'
        verbose_name_plural = 'Practice Progress'
        unique_together = [['user', 'pitch_deck']]
    
    def __str__(self):
        return f"{self.user.username} - Progress"