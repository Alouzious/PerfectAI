from django.db import models
from django.contrib.auth.models import User
from apps.pitches.models import PitchDeck
from apps.practice.models import PracticeSession
import uuid


class Question(models.Model):
    """AI-generated investor question"""
    
    # Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    pitch_deck = models.ForeignKey(
        PitchDeck, 
        on_delete=models.CASCADE, 
        related_name='questions',
        db_index=True
    )
    
    # Question Details
    question_text = models.TextField()
    
    CATEGORIES = [
        ('market', 'Market Size & Opportunity'),
        ('competition', 'Competition & Differentiation'),
        ('business_model', 'Business Model & Revenue'),
        ('team', 'Team & Execution'),
        ('traction', 'Traction & Metrics'),
        ('financials', 'Financials & Projections'),
        ('product', 'Product & Technology'),
        ('risks', 'Risks & Challenges'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORIES, db_index=True)
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium', db_index=True)
    
    # Context (what slide prompted this question)
    related_slide_number = models.IntegerField(null=True, blank=True)
    
    # Suggested talking points for answer
    key_points_to_cover = models.JSONField(default=list, blank=True)
    
    # Usage stats
    times_asked = models.IntegerField(default=0)
    average_answer_score = models.FloatField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['category', 'difficulty', 'created_at']
        verbose_name = 'Investor Question'
        verbose_name_plural = 'Investor Questions'
        indexes = [
            models.Index(fields=['pitch_deck', 'category']),
            models.Index(fields=['difficulty', 'times_asked']),
        ]
    
    def __str__(self):
        return f"[{self.category}] {self.question_text[:50]}..."


class Answer(models.Model):
    """User's answer to an investor question"""
    
    # Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE, 
        related_name='answers',
        db_index=True
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='qa_answers',
        db_index=True
    )
    practice_session = models.ForeignKey(
        PracticeSession, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='qa_answers'
    )
    
    # User's answer
    answer_text = models.TextField()
    answer_duration_seconds = models.IntegerField(default=0)
    word_count = models.IntegerField(default=0)
    
    # AI Evaluation (0-100)
    quality_score = models.FloatField(default=0, db_index=True)
    completeness_score = models.FloatField(default=0)  # Covered all key points?
    clarity_score = models.FloatField(default=0)
    confidence_score = models.FloatField(default=0)
    relevance_score = models.FloatField(default=0)  # Stayed on topic?
    
    # Detailed analysis
    key_points_covered = models.JSONField(default=list, blank=True)
    key_points_missed = models.JSONField(default=list, blank=True)
    
    # Feedback
    feedback = models.TextField(blank=True)
    strong_points = models.JSONField(default=list, blank=True)
    improvements = models.JSONField(default=list, blank=True)
    suggested_answer = models.TextField(blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending Analysis'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Q&A Answer'
        verbose_name_plural = 'Q&A Answers'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['question', '-quality_score']),
        ]
    
    def __str__(self):
        return f"{self.user.username} answered: {self.question.question_text[:30]}..."
    
    def save(self, *args, **kwargs):
        """Update question statistics on save"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new and self.status == 'completed':
            # Update question stats
            self.question.times_asked += 1
            
            # Recalculate average score
            all_answers = Answer.objects.filter(question=self.question, status='completed')
            avg_score = sum(a.quality_score for a in all_answers) / all_answers.count()
            self.question.average_answer_score = avg_score
            
            self.question.save()