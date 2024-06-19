from rest_framework import serializers
from .models import Subject
import re


class SubjectSerializer(serializers.ModelSerializer):

    subject_name = serializers.CharField(max_length=20,min_length=2,error_messages={
    "min_length":"E33001",
    "max_length":"E33002",
    "required":"E33003",
    "invalid":"E33004",
    "blank":"E33000"
     })
    
    class Meta:
        model = Subject
        fields = "__all__"
        ordering = ["-created_at"]

    

    def validate_subject_name(self, value):
        if not re.match(r"^[a-zA-Z\s]+$", value):
            raise serializers.ValidationError(
                'E33004'
            )

        return value


class SubjectdropdownlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = (
            "id",
            "subject_name",
        )
