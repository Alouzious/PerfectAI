from django.contrib import admin
from .models import Question, Answer


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin for Question"""
    list_display = (
        'question_text_short',
        'pitch_deck',
        'category',
        'difficulty',
        'times_asked',
        'average_answer_score',
        'created_at',
    )
    list_filter = ('category', 'difficulty', 'created_at')
    search_fields = ('question_text', 'pitch_deck__title')
    readonly_fields = (
        'id',
        'times_asked',
        'average_answer_score',
        'created_at',
    )
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'pitch_deck', 'question_text')
        }),
        ('Classification', {
            'fields': ('category', 'difficulty', 'related_slide_number')
        }),
        ('Guidance', {
            'fields': ('key_points_to_cover',)
        }),
        ('Stats', {
            'fields': ('times_asked', 'average_answer_score')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    def question_text_short(self, obj):
        return obj.question_text[:60] + '...' if len(obj.question_text) > 60 else obj.question_text
    question_text_short.short_description = 'Question'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Admin for Answer"""
    list_display = (
        'user',
        'question_short',
        'quality_score',
        'completeness_score',
        'status',
        'created_at',
    )
    list_filter = ('status', 'created_at', 'question__category')
    search_fields = ('user__username', 'question__question_text', 'answer_text')
    readonly_fields = (
        'id',
        'word_count',
        'created_at',
        'analyzed_at',
    )
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'question', 'user', 'practice_session')
        }),
        ('Answer', {
            'fields': ('answer_text', 'answer_duration_seconds', 'word_count')
        }),
        ('Scores', {
            'fields': (
                'quality_score',
                'completeness_score',
                'clarity_score',
                'confidence_score',
                'relevance_score',
            )
        }),
        ('Analysis', {
            'fields': (
                'key_points_covered',
                'key_points_missed',
                'feedback',
                'strong_points',
                'improvements',
                'suggested_answer',
            )
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'analyzed_at')
        }),
    )
    
    def question_short(self, obj):
        return obj.question.question_text[:40] + '...'
    question_short.short_description = 'Question'