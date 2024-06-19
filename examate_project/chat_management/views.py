


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
from rest_framework import generics
from .serializers import ChatMessageSerializer,GetMessageSerializer
from .models import ChatMessage
from django.db.models import Subquery,OuterRef,Q,Max
from user_management.models import User
from rest_framework.response import Response
from rest_framework import status


    
class GetMessages(generics.ListAPIView):
    serializer_class = GetMessageSerializer

    def get_queryset(self):
        user = self.request.user
        user_type = user.user_type
        flag=int(self.request.query_params.get("flag"))
        if user_type == 0:
           client_id=int(self.request.query_params.get("client_id"))
        else:
            client_id = self.request.user.id
        
        if flag in [0,1]:
            
             messages =ChatMessage.objects.filter(
                is_read=0,client=client_id,flag=flag
            )
             
        else:
             messages = ChatMessage.objects.filter(
            client=client_id
        ).order_by('date')
           
        return messages
    
  
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


    

        

class UpdateIsRead(generics.UpdateAPIView):
    def patch(self,request,*args,**kwargs):
      
      
     
      
        try:
            latest_message_id = request.data.get('latest_message_id')
            user_type=request.user.user_type


            if latest_message_id is not None:
                if user_type==0:
                    client_id=request.data.get('client_id')
                    messages = ChatMessage.objects.filter(id__lte=latest_message_id,client=client_id,flag=1)
                    messages.update(is_read=True)
                else:
                    client_id=request.user.id
                    messages = ChatMessage.objects.filter(id__lte=latest_message_id,client=client_id,flag=0)
                    messages.update(is_read=True)
                return Response({'message':"is_read updated for messages"},status=status.HTTP_200_OK)
            else:
                return Response({'message':"latest_message_id is required"},status=status.HTTP_200_OK)
        except Exception as e:
          
            return Response({'message':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        
class GetUnreadMessagesCount(generics.RetrieveAPIView):

    def get(self, request, *args, **kwargs):
       
       
        user_type = request.user.user_type
        try:

            if user_type==0:
                client_id_str=request.GET.get("client_id")
                client_id = int(client_id_str) if client_id_str is not None else 0
                count=ChatMessage.objects.filter(client=client_id,flag=1,is_read=0).count()
                return Response({'count':count},status=status.HTTP_200_OK)
            else:
                client_id=request.user.id
                count = ChatMessage.objects.filter(client=client_id,flag=0,is_read=0).count()
                return Response({'count':count},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

      
            
