from django.contrib import admin
from .models import PitchDeck, Slide


@admin.register(PitchDeck)
class PitchDeckAdmin(admin.ModelAdmin):
    """Admin for PitchDeck"""
    list_display = (
        'title',
        'owner',
        'status',
        'total_slides',
        'analyzed',
        'file_size_mb',
        'uploaded_at',
    )
    list_filter = ('status', 'analyzed', 'file_type', 'uploaded_at')
    search_fields = ('title', 'owner__username', 'slug')
    readonly_fields = (
        'id',
        'slug',
        'file_size',
        'uploaded_at',
        'updated_at',
        'analyzed_at',
    )
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'owner', 'title', 'slug')
        }),
        ('File Info', {
            'fields': ('uploaded_file', 'file_type', 'file_size')
        }),
        ('Status', {
            'fields': ('status', 'total_slides', 'analyzed', 'analyzed_at')
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'updated_at')
        }),
    )
    
    def file_size_mb(self, obj):
        return f"{obj.file_size_mb} MB"
    file_size_mb.short_description = 'File Size'


@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    """Admin for Slide"""
    list_display = (
        'slide_number',
        'pitch_deck',
        'slide_type',
        'quality_score',
        'has_images',
        'estimated_speaking_time',
    )
    list_filter = ('slide_type', 'has_images', 'has_charts', 'pitch_deck__owner')
    search_fields = ('pitch_deck__title', 'text_content')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'pitch_deck', 'slide_number')
        }),
        ('Content', {
            'fields': ('text_content', 'has_images', 'has_charts')
        }),
        ('Analysis', {
            'fields': (
                'slide_type',
                'quality_score',
                'strengths',
                'weaknesses',
                'suggestions',
            )
        }),
        ('Coaching', {
            'fields': (
                'suggested_script',
                'key_points',
                'estimated_speaking_time',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )