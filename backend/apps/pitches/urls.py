from django.urls import path
from . import views

app_name = 'pitches'

urlpatterns = [
    # Pitch Decks
    path('upload/', views.upload_pitch_deck, name='upload'),
    path('', views.list_pitch_decks, name='list'),
    path('<uuid:deck_id>/', views.get_pitch_deck, name='detail'),
    path('<uuid:deck_id>/delete/', views.delete_pitch_deck, name='delete'),
    
    # ===== NEW: STATUS CHECK =====
    path('<uuid:deck_id>/status/', views.check_analysis_status, name='analysis-status'),
    
    # Slides
    path('<uuid:deck_id>/slides/', views.list_slides, name='slides-list'),
    path('<uuid:deck_id>/slides/<int:slide_number>/', views.get_slide, name='slide-detail'),
    path('<uuid:deck_id>/slides/<int:slide_number>/coaching/', views.get_slide_coaching, name='slide-coaching'),
]