from django.urls import path
from . import views

app_name = 'qa'

urlpatterns = [
    # Questions
    path('questions/<uuid:deck_id>/', views.generate_questions, name='generate-questions'),
    path('questions/detail/<uuid:question_id>/', views.get_question, name='question-detail'),
    
    # Answers
    path('answers/', views.submit_answer, name='submit-answer'),
    path('answers/<uuid:answer_id>/', views.get_answer, name='answer-detail'),
    path('answers/list/', views.list_user_answers, name='list-answers'),
]