from django.urls import path
from .views import CreateQuestionView,QuestionlistAPIView,QuestionDetailView,QuestionDeleteAPIView,ChangeDraftStatusAPIView,UpdateQuestionView,ExamSubjectsQuestionsAPIView,CountView
urlpatterns = [
    path('create-question/',CreateQuestionView.as_view(), name= "create-question"),
    path('question-list/',QuestionlistAPIView.as_view(), name= "question-list"),
    path('update-question/<int:question_id>/',UpdateQuestionView.as_view(), name= "create-question"),
    path('question-details/<int:question_id>/',QuestionDetailView.as_view(), name= "question-detail"),
    path('question-delete/<int:pk>/', QuestionDeleteAPIView.as_view(), name='question-delete'),
    path('approve-question/<int:question_id>/', ChangeDraftStatusAPIView.as_view(), name='change_draft_status'),
    path('exam-questions/<int:exam_subject_id>/', ExamSubjectsQuestionsAPIView.as_view(), name='exam-subject-questions'),
    path('count/', CountView.as_view(), name='count'),
]