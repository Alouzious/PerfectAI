from django.urls import path
from . import views

app_name = 'practice'

urlpatterns = [
    # Practice Sessions
    path('sessions/', views.create_practice_session, name='create-session'),
    path('sessions/list/', views.list_practice_sessions, name='list-sessions'),
    path('sessions/<uuid:session_id>/', views.get_practice_session, name='session-detail'),
    path('sessions/<uuid:session_id>/feedback/', views.get_practice_feedback, name='session-feedback'),
    
    # Progress
    path('progress/', views.get_practice_progress, name='progress'),
]