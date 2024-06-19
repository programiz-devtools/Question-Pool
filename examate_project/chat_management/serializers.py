


from rest_framework import serializers
from .models import ChatMessage
from user_management.serializers import UserSerializer

class ChatMessageSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = ChatMessage
        fields = ['client','flag','message','is_read','date']
        

class GetMessageSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = ChatMessage
        fields = ['id','client','flag','message','is_read','date']