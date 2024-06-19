# serializers.py in your exam_management app
# serializers.py in your exam_management app

from rest_framework import serializers
from .models import Candidate,ExamCandidate
from  exam_management.models import ExamQuestions
from django.db.models import Sum

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'email', 'status','exam']

class ExamCandidateSerializer(serializers.ModelSerializer):
    candidate_id = serializers.ReadOnlyField(source='candidate.id')
    candidate_name = serializers.ReadOnlyField(source='candidate.name')
    candidate_status=serializers.ReadOnlyField(source='candidate.status')
    candidate_email=serializers.ReadOnlyField(source='candidate.email')
    exam_subject_mark = serializers.IntegerField()
    exam_subject_name = serializers.SerializerMethodField()
    exam_subject_outcome_status=serializers.SerializerMethodField()
   

    
    class Meta:
        model = ExamCandidate
        fields = ['candidate_id', 'candidate_name','candidate_email','exam_subject_mark', 'exam_subject_name','candidate_status','exam_subject_outcome_status']

    def get_exam_subject_name(self, obj):
        return obj.exam_subject.subject.subject_name
    
    def get_exam_subject_outcome_status(self, obj):
        return obj.exam_subject_outcome_status
    
    
class ExamCandidateCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExamCandidate
        fields = ['id', 'candidate', 'exam_subject']

   
