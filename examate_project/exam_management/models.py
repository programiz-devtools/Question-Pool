from django.db import models
from user_management.models import User
from subject_management.models import Subject
from question_management.models import Questions

class Exam(models.Model):
    EXAM_STATUS_CHOICES = (
        (0,'drafted'),
        (1,'confirmed'),
        (2, 'completed'),
        (3, 'evaluated'),
        (4,'result_published'),
        (5,'cancelled'),
    )

    name = models.CharField(max_length=255)
    exam_duration = models.IntegerField(null=True)
    scheduled_time = models.DateTimeField(blank=True,null=True)
    status = models.SmallIntegerField(choices=EXAM_STATUS_CHOICES,default = 0)
    candidate_count = models.IntegerField(default = 0)
    organization = models.ForeignKey(User,on_delete=models.CASCADE)
    access_link = models.CharField(max_length=255,blank=True)
    instructions = models.CharField(max_length=1000, blank=True)
    class Meta:
        db_table = "exams"
   


    def __str__(self):
        return self.name


class ExamSubjects(models.Model):
    DIFFICULTY_LEVEL_CHOICE = (
        (1, "easy"),
        (2, "medium"),
        (3, "difficult")
    )
    
    exam = models.ForeignKey(Exam,on_delete=models.CASCADE,related_name='exam_subjects')
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE,blank=True)
    time_duration = models.IntegerField(blank=True)
    pass_percentage = models.DecimalField(max_digits=5,decimal_places=2,blank=True)
    difficulty_level = models.PositiveSmallIntegerField(choices=DIFFICULTY_LEVEL_CHOICE,blank=True,null=True)
    question_count = models.IntegerField(default = 0,blank=True) 
    class Meta:
        db_table = "exam_subjects"  


class ExamQuestions(models.Model):
     exam = models.ForeignKey(ExamSubjects,on_delete=models.CASCADE)
     question = models.ForeignKey(Questions,on_delete=models.CASCADE)
     class Meta:
        db_table = "exam_questions"


class Feedback(models.Model):
    exam = models.ForeignKey(Exam,on_delete=models.CASCADE)
    feedback=models.CharField(max_length=255, blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    candidate = models.ForeignKey('candidatemanagement.Candidate', on_delete=models.CASCADE)
    class Meta:
        db_table = "feedbacks"
