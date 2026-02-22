from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Display UserProfile inline with User in admin"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    
    fields = (
        'subscription_tier',
        'subscription_start_date',
        'subscription_end_date',
        'pitch_decks_uploaded',
        'practice_sessions_completed',
        'average_practice_score',
        'best_practice_score',
        'onboarding_completed',
    )
    readonly_fields = (
        'pitch_decks_uploaded',
        'practice_sessions_completed',
        'average_practice_score',
        'best_practice_score',
    )


class UserAdmin(BaseUserAdmin):
    """Extended User admin with profile"""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_subscription_tier', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__subscription_tier')
    
    def get_subscription_tier(self, obj):
        return obj.profile.subscription_tier if hasattr(obj, 'profile') else 'N/A'
    get_subscription_tier.short_description = 'Subscription'


# Unregister the default User admin
admin.site.unregister(User)

# Register with our custom admin
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile"""
    list_display = (
        'user',
        'subscription_tier',
        'pitch_decks_uploaded',
        'practice_sessions_completed',
        'average_practice_score',
        'created_at',
    )
    list_filter = ('subscription_tier', 'onboarding_completed', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = (
        'id',
        'pitch_decks_uploaded',
        'practice_sessions_completed',
        'total_practice_time_seconds',
        'created_at',
        'updated_at',
    )
    
    fieldsets = (
        ('User', {
            'fields': ('id', 'user')
        }),
        ('Subscription', {
            'fields': (
                'subscription_tier',
                'subscription_start_date',
                'subscription_end_date',
                'pitch_decks_limit',
                'practice_sessions_limit',
            )
        }),
        ('Usage Stats', {
            'fields': (
                'pitch_decks_uploaded',
                'practice_sessions_completed',
                'total_practice_time_seconds',
            )
        }),
        ('Performance', {
            'fields': (
                'average_practice_score',
                'best_practice_score',
                'improvement_rate',
            )
        }),
        ('Preferences', {
            'fields': (
                'preferred_pitch_type',
                'target_practice_duration',
                'notifications_enabled',
            )
        }),
        ('Onboarding', {
            'fields': (
                'onboarding_completed',
                'onboarding_step',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_login_at')
        }),
    )