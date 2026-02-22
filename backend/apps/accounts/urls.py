from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # User
    path('me/', views.current_user_view, name='current-user'),
    path('profile/', views.profile_view, name='profile'),
    
    # ===== NEW ENDPOINTS =====
    path('health/', views.health_check, name='health-check'),
    path('password-reset/', views.request_password_reset, name='password-reset'),

    path('csrf/', views.csrf_token_view, name='csrf-token'),
]