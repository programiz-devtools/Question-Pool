from rest_framework import serializers
from .models import Ticket,Notification

class TicketSerializer(serializers.ModelSerializer):
    exam_name = serializers.SerializerMethodField()
    

    class Meta:
        model = Ticket
        fields = "__all__"

    def get_exam_name(self, obj):
        if obj.exam:
            return obj.exam.name
        else:
            return None


class TicketRequestSerializer(serializers.Serializer):
    organisation = serializers.CharField()
    count = serializers.IntegerField()
    tickets = serializers.ListField(child=serializers.IntegerField())

class TicketDetailSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display', read_only=True)
    organisation = serializers.CharField(source='organisation.username', read_only=True)
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = '__all__'  # Include all fields from the Ticket model
    
    def get_created_at(self, obj):
        return obj.created_at.strftime('%d-%m-%Y %H:%M:%S') 


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'body', 'created_at', 'status']
    
