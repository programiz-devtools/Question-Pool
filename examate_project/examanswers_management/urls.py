from django.urls import path
from .views import CandidateAnswerCreateAPIView,CandidateFreeAnswerListView,EvaluateFreeAnswerView

urlpatterns = [
    path('candidateanswers/<int:exam_subject_id>/<int:exam_candidate_id>/', CandidateAnswerCreateAPIView.as_view(), name='candidateanswers-create'),
    path('evaluate-free-answer/', EvaluateFreeAnswerView.as_view(), name='evaluate_free_answers'),
    path('candidate-free-answers/<int:candidate_id>/', CandidateFreeAnswerListView.as_view(), name='candidate_free_answers'),
]