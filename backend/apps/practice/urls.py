from django.urls import path
from . import views

app_name = 'practice'

urlpatterns = [
    path('sessions/', views.create_practice_session, name='create-session'),
    path('sessions/list/', views.list_practice_sessions, name='list-sessions'),
    path('sessions/<uuid:session_id>/', views.get_practice_session, name='session-detail'),
    path('sessions/<uuid:session_id>/feedback/', views.get_practice_feedback, name='session-feedback'),
    path('sessions/<uuid:session_id>/submit-audio/', views.submit_practice_audio, name='submit-audio'),  # NEW
    path('progress/', views.get_practice_progress, name='progress'),
]