"""
URL configuration for examate_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('examate/',include('user_management.urls')),
    path('examate/organization/',include('organization_management.urls')),
    path('question/',include('question_management.urls')),
    path('examate/',include('subject_management.urls')),
    path('examate/exam/',include('exam_management.urls')),
    path('examatecandidates/',include('candidatemanagement.urls')),
    path('examateanswers/',include('examanswers_management.urls')),
    path('examate/mark/',include('examanswers_management.urls')),
    path('tickets/',include('ticket_management.urls')),
    path('transaction/',include('transaction_management.urls')),
    path('chat/',include('chat_management.urls'))
    

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




