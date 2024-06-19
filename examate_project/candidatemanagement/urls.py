from django.urls import path
from .views import ExamCandidateCreateView,ExamTokenDecodeView,SendResultEmailsView, ExamCandidateListView,SendExamLinkView,CheckTokenExpirationView,DeleteCandidateView,CandidateListByExamAPIView,AddCandidateNameView,EvaluateExamCandidateListView

urlpatterns = [
    path('candidateslist/<int:exam_id>/',  ExamCandidateListView.as_view(), name='candidates-by-subject'),
    path('<int:exam_id>/add-candidate/', ExamCandidateCreateView.as_view(), name='exam-candidate-add'),
    path('access-link/', SendExamLinkView.as_view(), name='access-link'),
    path('check-token-expiration/', CheckTokenExpirationView.as_view(), name='check-token-expiration'),
    path('exam-candidate-list/<int:exam_id>/',CandidateListByExamAPIView.as_view(),name='exam-candidate-list'),
    path('candidates/delete/<int:candidate_id>/', DeleteCandidateView.as_view(), name='delete_candidate'),
    path('add-name/',AddCandidateNameView.as_view(),name='add-candidate-name'),
    path('evaluated-candidate-list/<int:exam_id>/',EvaluateExamCandidateListView.as_view(),name='evaluated-candidate-list'),
    path('examtokendecode/',ExamTokenDecodeView.as_view(),name='token_decode'),
    path('send-result-emails/', SendResultEmailsView.as_view(), name='send_emails'),  
]