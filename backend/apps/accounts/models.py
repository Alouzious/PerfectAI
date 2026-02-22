from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


class UserProfile(models.Model):
    """Extended user profile for Pitch Perfect AI"""
    
    # Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # One-to-One with Django User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Subscription Info
    SUBSCRIPTION_TIERS = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]
    subscription_tier = models.CharField(
        max_length=20, 
        choices=SUBSCRIPTION_TIERS, 
        default='free',
        db_index=True
    )
    subscription_start_date = models.DateTimeField(null=True, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    
    # Usage Limits (based on tier)
    pitch_decks_limit = models.IntegerField(default=3)  # Free: 3, Pro: unlimited
    practice_sessions_limit = models.IntegerField(default=10)  # Per month
    
    # Usage Tracking
    pitch_decks_uploaded = models.IntegerField(default=0)
    practice_sessions_completed = models.IntegerField(default=0)
    total_practice_time_seconds = models.BigIntegerField(default=0)
    
    # Preferences
    preferred_pitch_type = models.CharField(max_length=50, blank=True)
    target_practice_duration = models.IntegerField(default=300)  # 5 minutes default
    notifications_enabled = models.BooleanField(default=True)
    
    # Analytics
    average_practice_score = models.FloatField(default=0)
    best_practice_score = models.FloatField(default=0)
    improvement_rate = models.FloatField(default=0)  # Score improvement over time
    
    # Onboarding
    onboarding_completed = models.BooleanField(default=False)
    onboarding_step = models.IntegerField(default=0)  # Track progress
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        indexes = [
            models.Index(fields=['subscription_tier', '-created_at']),
            models.Index(fields=['user', 'subscription_tier']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.subscription_tier}"
    
    @property
    def is_free_user(self):
        """Check if user is on free tier"""
        return self.subscription_tier == 'free'
    
    @property
    def is_pro_user(self):
        """Check if user is on pro tier"""
        return self.subscription_tier == 'pro'
    
    @property
    def is_enterprise_user(self):
        """Check if user is on enterprise tier"""
        return self.subscription_tier == 'enterprise'
    
    @property
    def can_upload_more_decks(self):
        """Check if user can upload more pitch decks"""
        if self.subscription_tier != 'free':
            return True  # Pro and enterprise have unlimited
        return self.pitch_decks_uploaded < self.pitch_decks_limit
    
    @property
    def remaining_pitch_decks(self):
        """How many more decks can user upload"""
        if self.subscription_tier != 'free':
            return float('inf')  # Unlimited
        return max(0, self.pitch_decks_limit - self.pitch_decks_uploaded)
    
    @property
    def can_practice_more(self):
        """Check if user can do more practice sessions this month"""
        if self.subscription_tier != 'free':
            return True
        # TODO: Add logic to count sessions this month
        return self.practice_sessions_completed < self.practice_sessions_limit
    
    def increment_pitch_deck_count(self):
        """Called when user uploads a new deck"""
        self.pitch_decks_uploaded += 1
        self.save(update_fields=['pitch_decks_uploaded'])
    
    def increment_practice_session_count(self):
        """Called when user completes a practice session"""
        self.practice_sessions_completed += 1
        self.save(update_fields=['practice_sessions_completed'])
    
    def update_average_score(self, new_score):
        """Update average practice score"""
        if self.practice_sessions_completed == 0:
            self.average_practice_score = new_score
        else:
            total = self.average_practice_score * (self.practice_sessions_completed - 1)
            self.average_practice_score = (total + new_score) / self.practice_sessions_completed
        
        if new_score > self.best_practice_score:
            self.best_practice_score = new_score
        
        self.save(update_fields=['average_practice_score', 'best_practice_score'])


# Auto-create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create UserProfile when new User is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()