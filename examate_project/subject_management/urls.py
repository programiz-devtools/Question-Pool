from django.urls import path
from . import views

urlpatterns = [

    path('subjects/create/', views.SubjectCreateAPIView.as_view(), name='subject-create'),
    path('subjects/list/', views.SubjectListAPIView.as_view(), name='subject-list'),
    path('subjects/delete/<int:id>/',views.SubjectDeleteView.as_view(),name='subject-delete'),
    path('subjects/dropdownlist/', views.subjectdropdownlist.as_view(), name='subject-list'),
    path('subjects/search/',views.SubjectSearchView.as_view(),name='subject-search'),
   
]