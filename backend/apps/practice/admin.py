from django.contrib import admin
from .models import PracticeSession, PracticeProgress


@admin.register(PracticeSession)
class PracticeSessionAdmin(admin.ModelAdmin):
    """Admin for PracticeSession"""
    list_display = (
        'user',
        'pitch_deck',
        'pitch_type',
        'session_number',
        'overall_score',
        'duration_seconds',
        'status',
        'created_at',
    )
    list_filter = ('status', 'pitch_type', 'created_at')
    search_fields = ('user__username', 'pitch_deck__title', 'transcript')
    readonly_fields = (
        'id',
        'session_number',
        'word_count',
        'created_at',
        'completed_at',
    )
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'user', 'pitch_deck', 'pitch_type', 'session_number')
        }),
        ('Timing', {
            'fields': ('duration_seconds', 'target_duration_seconds')
        }),
        ('Transcript', {
            'fields': ('transcript', 'word_count')
        }),
        ('Scores', {
            'fields': (
                'overall_score',
                'pace_score',
                'clarity_score',
                'confidence_score',
                'content_score',
                'structure_score',
            )
        }),
        ('Metrics', {
            'fields': (
                'speaking_pace_wpm',
                'filler_words_count',
                'filler_words_detail',
                'unique_words_count',
            )
        }),
        ('Feedback', {
            'fields': ('feedback', 'strengths', 'improvements')
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'completed_at')
        }),
    )


@admin.register(PracticeProgress)
class PracticeProgressAdmin(admin.ModelAdmin):
    """Admin for PracticeProgress"""
    list_display = (
        'user',
        'pitch_deck',
        'total_sessions',
        'average_score',
        'best_score',
        'last_session_date',
    )
    list_filter = ('user', 'pitch_deck')
    search_fields = ('user__username', 'pitch_deck__title')
    readonly_fields = ('updated_at',)