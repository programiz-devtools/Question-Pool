from django.db import models
from subject_management.models import Subject
from django.core.validators import MinLengthValidator,MinValueValidator,MaxValueValidator


class Questions(models.Model):
    DIFFICULTY_LEVEL_CHOICE = ((1, "easy"), (2, "medium"), (3, "difficult"))
    ANSWER_TYPE_CHOICE = (
        (1, "single answer"),
        (2, "multiple answer"),
        (3, "free answer"),
    )
    question_description = models.CharField(max_length=250,validators=[MinLengthValidator(10)])
    difficulty_level = models.PositiveSmallIntegerField(
        choices=DIFFICULTY_LEVEL_CHOICE, null=True
    )
    answer_type = models.PositiveSmallIntegerField(choices=ANSWER_TYPE_CHOICE)
    subject_id = models.ForeignKey(
        Subject, on_delete=models.CASCADE, db_column="subject_id"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    marks = models.IntegerField(null=True,validators=[MinValueValidator(0),MaxValueValidator(100)])
    is_drafted = models.BooleanField()
    class Meta:
        db_table = "questions"
       


class FreeAnswers(models.Model):
    answer = models.CharField(max_length=500)
    question = models.ForeignKey(
        Questions, on_delete=models.CASCADE, related_name="free_answers"
    )
    class Meta:
        db_table = "free_answers"

class QuestionOptions(models.Model):
    question = models.ForeignKey(Questions, on_delete=models.CASCADE,related_name='options')
    options = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_answer = models.BooleanField()
    class Meta:
        db_table = "question_options"
