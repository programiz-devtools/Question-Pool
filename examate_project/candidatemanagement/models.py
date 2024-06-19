from django.db import models
from subject_management.models import Subject 
from exam_management.models import Exam,ExamSubjects

# Create your models here.
class Candidate(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50,null=True)
    email = models.EmailField(max_length=50)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='candidates', null=True)
    status = models.SmallIntegerField(default=0)
    class Meta:
        db_table = "candidates"


class ExamCandidate(models.Model):
    id = models.BigAutoField(primary_key=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    exam_subject = models.ForeignKey(ExamSubjects, on_delete=models.CASCADE) 
    exam_subject_mark = models.IntegerField(default=0)
    exam_subject_outcome_status = models.BooleanField(default=None,null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    class Meta:
        db_table = "exam_candidates"


