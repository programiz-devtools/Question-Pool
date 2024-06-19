from rest_framework import serializers
from .models import CandidateAnswers
from question_management.models import FreeAnswers

class CandidateAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateAnswers
        fields = '__all__'


class FreeAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreeAnswers
        fields = ('answer',)

class CandidateAnswerSerializers(serializers.ModelSerializer):
    question_description = serializers.CharField(source='question.question_description', read_only=True)
    question_mark = serializers.IntegerField(source='question.marks', read_only=True)
    answer_key = serializers.SerializerMethodField(source='question.free_answers.first.answer', read_only=True)
    candidate_name = serializers.SerializerMethodField()

    class Meta:
        model = CandidateAnswers
        fields = ('id','question_description','question_mark', 'free_answer', 'answer_key','candidate_name')

    def get_answer_key(self, obj):
     if obj.question.answer_type == 3 and obj.question.free_answers.exists():
        return obj.question.free_answers.first().answer
     return None

    
    def get_candidate_name(self, obj):
        return obj.exam_candidate.candidate.name



