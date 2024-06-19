from rest_framework import serializers
from user_management.models import User
from chat_management.models import ChatMessage

class UserWithChatMessageSerializer(serializers.ModelSerializer):
    unread_messages_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields =  fields = ['id', 'user_type', 'status', 'address', 'username', 'email','contact_number','date_joined','is_register','password','profile_image','unread_messages_count']

    def get_unread_messages_count(self, user):
        return ChatMessage.objects.filter(client=user, is_read=0,flag=1).count()