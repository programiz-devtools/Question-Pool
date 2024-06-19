from django.db import models
from question_management.models import Questions,QuestionOptions
from candidatemanagement.models import ExamCandidate

    
class CandidateAnswers(models.Model):
    question = models.ForeignKey(Questions,on_delete=models.CASCADE)
    exam_candidate = models.ForeignKey(ExamCandidate,on_delete=models.CASCADE)
    free_answer = models.CharField(max_length=1025, blank=True,null=True)
    Selective_answer = models.ForeignKey(QuestionOptions,on_delete=models.CASCADE,blank=True,null=True)
    is_correct = models.BooleanField(blank=True,null=True)
    marks_scored = models.IntegerField(default=0)
    class Meta:
        db_table = "candidate_answers"