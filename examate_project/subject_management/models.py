from django.db import models
from django.utils import timezone

class Subject(models.Model): 
    subject_name = models.CharField(max_length=20, unique=True)
    question_count = models.PositiveIntegerField(default=0)
    exam_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "subjects"
