from .models import Questions, FreeAnswers, QuestionOptions
from rest_framework import serializers
from exam_management.models import ExamQuestions
import re
from subject_management.models import Subject



class QuestionSerializer(serializers.ModelSerializer):
    question_description = serializers.CharField(
        max_length=250, 
        min_length=10,    
        error_messages={
            "required": "E30010",
            "max_length": "E30011",
            "min_length": "E30012",
        }
    )
    difficulty_level = serializers.ChoiceField(
        allow_null=True,
        choices=Questions.DIFFICULTY_LEVEL_CHOICE,
        required=False,
        error_messages={
            "invalid_choice": "E30014",
        }
    )
    answer_type = serializers.ChoiceField(
        choices=Questions.ANSWER_TYPE_CHOICE,
        error_messages={
            "invalid_choice": "E30015",
            "required":"E30013"
        }
    )
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        error_messages={
            "does_not_exist": "E30016",
            "incorrect_type": "E30017",
            "required":"E30030"
        }
    )
    marks = serializers.IntegerField(
        allow_null=True,
        min_value=0,
        max_value=100,
          required=False,
        error_messages={
            "min_value": "E30018",
            "max_value": "E30019",
            "invalid":"E30108"
        }
    )
    is_drafted = serializers.BooleanField(
        error_messages={"invalid": "E30020"}
    )

    class Meta:
        model = Questions
        fields = '__all__'


class FreeAnswerSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(
        queryset=Questions.objects.all(),
        error_messages={
            "does_not_exist": "E30021",
            "incorrect_type": "E30022",
            "blank":"E30111"
        }
    )
    answer = serializers.CharField(
        required=False,
        max_length=500,
        allow_blank=True, 
        error_messages={"max_length": "E30023","blank":"E30029"}
    )
    class Meta:
        model = FreeAnswers
        fields = ["question", "answer"]

    


class QuestionOptionSerializer(serializers.ModelSerializer):
   
    options = serializers.CharField(
        max_length=50,
        error_messages={
            "max_length": "E30024",
        }
    )
    is_answer = serializers.BooleanField(
        error_messages={"invalid": "E30025"}
    )
    class Meta:
        model = QuestionOptions
        fields = ["question", "options", "is_answer", "created_at", "updated_at"]

class QuestionOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOptions
        fields = ["id","options", "is_answer"]


class QuestionListSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = Questions
        fields = ["id", "question_description", "answer_type", "options"]

    def get_options(self, instance):
        # Check if the question has options
        if hasattr(instance, 'options'):
            return QuestionOptionsSerializer(instance.options.all(), many=True).data
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation


class GetFreeAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreeAnswers
        fields = ["answer"]




class QuestionOptionsDetailSerializer(serializers.ModelSerializer):
    options = QuestionOptionsSerializer(many=True, read_only=True, max_length=50)
    difficulty_level_display = serializers.SerializerMethodField()

    class Meta:
        model = Questions
        fields = [
            "id",
            "question_description",
            "options",
            "is_drafted",
            "marks",
            "difficulty_level",
            "subject_id",
            "answer_type",
            "difficulty_level_display",
        ]

    def get_difficulty_level_display(self, obj):
        return dict(Questions.DIFFICULTY_LEVEL_CHOICE).get(
            obj.difficulty_level, "Unknown"
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        options_data = QuestionOptionsSerializer(
            instance.options.all(), many=True
        ).data
        representation["options"] = options_data
        return representation

    def validate_options(self, value):
        if len(value) > 50:
            raise serializers.ValidationError(
                {"message": "option should not exceed 50 characters."}
            )
        return value


class FreeAnswerQuestionDetailSerializer(serializers.ModelSerializer):
    answer = GetFreeAnswerSerializer(many=True, read_only=True)
    difficulty_level_display = serializers.SerializerMethodField()

    class Meta:
        model = Questions
        fields = [
            "id",
            "question_description",
            "answer",
            "is_drafted",
            "marks",
            "difficulty_level",
            "difficulty_level_display",
            "subject_id",
            "answer_type",
        ]

    def get_difficulty_level_display(self, obj):
        return dict(Questions.DIFFICULTY_LEVEL_CHOICE).get(
            obj.difficulty_level, "Unknown"
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Access the related FreeAnswers data using the 'free_answers' attribute
        free_answer_data = GetFreeAnswerSerializer(
            instance.free_answers.all(), many=True
        ).data
        representation["answer"] = free_answer_data

        return representation

class ExamSubjectsQuestionsSerializer(serializers.ModelSerializer):
    question = QuestionListSerializer()

    class Meta:
        model = ExamQuestions
        fields = ['id', 'exam', 'question']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation['question']