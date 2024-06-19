from rest_framework import serializers
from decimal import Decimal
from .models import Exam, ExamQuestions, ExamSubjects, Feedback
from django.utils import timezone
from subject_management.serializers import SubjectdropdownlistSerializer
from user_management.models import User


class ExamSerializer(serializers.ModelSerializer):
   
    name = serializers.CharField(
        max_length=255,
        error_messages={
            "required": "E40001",
            "blank": "E40002",
            "max_length": "E40003",
        },
    )

   
    exam_duration = serializers.IntegerField(allow_null=True, required=False)
    scheduled_time = serializers.DateTimeField(allow_null=True, required=False)
    status = serializers.ChoiceField(choices=Exam.EXAM_STATUS_CHOICES,
                                     error_messages={
                                         "invalid_choice":"E40026"
                                     })
    candidate_count = serializers.IntegerField(default=0, required=False)
    instructions = serializers.CharField(max_length=1000, allow_blank=True, required=False)

    class Meta:
        model = Exam
        fields = [
            "id",
            "name",
            "scheduled_time",
            "instructions",
            "status",
            "exam_duration",
            "candidate_count",    
        ]
   
   
    def validate(self, data):
        if 'status' in data and data['status'] == 1:
            if 'scheduled_time' not in data or data['scheduled_time'] is None:
                raise serializers.ValidationError({'E40027'})
        return data

    def validate_scheduled_time(self, value):
        status=self.context.get("status",None)
        if status==1 and value==None:
            raise serializers.ValidationError("E40004")
        if value is not None and value <= timezone.now():
            raise serializers.ValidationError("E40004")
        return value

  

    def validate(self, data):
        status = data.get('status')
        
        if status == 1:
            if 'name' not in data or data.get('name')=="" :
                raise serializers.ValidationError("E40001")
            if 'scheduled_time' not in data:
                raise serializers.ValidationError("E40027")
        elif status == 0 and ('name' not in data or data.get('name')==""):
        
                raise serializers.ValidationError("E40001")
        return data



class ExamSubjectsSerializer(serializers.ModelSerializer):

    time_duration=serializers.IntegerField(
       
        error_messages={
            "required":"E40011"
        }
    )
    pass_percentage=serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
       
        error_messages={
            "required":"E40012"
        }
    )
    difficulty_level = serializers.IntegerField(
    allow_null=True,
    error_messages={
        "required": "E40014"
    }
)
    question_count=serializers.IntegerField(
       
        error_messages={
            "required":"E40013"
        }
    )
   
    class Meta:
        model = ExamSubjects
        fields = [
            "subject",
            "time_duration",
            "pass_percentage",
            "difficulty_level",
            "question_count",
        ]
    

    def validate_time_duration(self, value):
        
        if value < 0:
            raise serializers.ValidationError("E40005")
        return value

    def validate_pass_percentage(self, value):
     
        if value < 0 or value > 100:
            raise serializers.ValidationError("E40006")
        return value

    def validate_difficulty_level(self, value):
      
       
        if self.context.get("status") != 0 and value not in [1, 2, 3]:
            raise serializers.ValidationError("E40007")
        return value

    def validate_question_count(self, value):
        
       
        if value < 0:
            raise serializers.ValidationError("E40008")
        return value

class ExamSubjectsSerializerWithSubjectName(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name")

    class Meta:
        model = ExamSubjects
        fields = [
            "subject",
            "subject_name",
            "time_duration",
            "pass_percentage",
            "difficulty_level",
            "question_count",
        ]


class ExamQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamQuestions
        fields = "__all__"



class FeedbackSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.name')
    candidate_email = serializers.EmailField(source='candidate.email')
    class Meta:
        model = Feedback
        fields = ['id','candidate_name', 'candidate_email', 'rating', 'feedback']


class ExamSubjectsListSerializer(serializers.ModelSerializer):
    subject = SubjectdropdownlistSerializer()

    class Meta:
        model = ExamSubjects
        fields = ["id", "subject", "question_count", "time_duration"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["subject"] = instance.subject.subject_name
        return representation

class DashboardExamListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'name', 'scheduled_time', 'status','organization'] 
