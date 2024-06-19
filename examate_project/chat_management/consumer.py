
import json
import jwt
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.conf import settings
from django.contrib.auth import get_user_model
from datetime import datetime
from chat_management.models import ChatMessage
from user_management.models import User
from ticket_management.models import DeviceRegistration
from pyfcm import FCMNotification
from urllib.parse import parse_qs



push_service = FCMNotification(api_key=settings.FCM_SERVER_KEY)



class ChatConsumer(WebsocketConsumer):

    def save_message(self,message_data):
      
        print("savve",message_data)
        try:
            user=User.objects.get(id=message_data['client'])
           
            ChatMessage.objects.create(
            client=user,
            message=message_data['message'],
            flag=message_data['flag']
        )
            return True,None
        except Exception as e:
            print("Error in saving message",e)
            return False, str(e)
           


    def connect(self):
        
        try:

            query_params = parse_qs(self.scope['query_string'].decode())
            self.client_id = query_params.get('client_id', [None])[0]
            self.room_group_name = f"chat_{self.client_id}"
           
        
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name, self.channel_name
            )

            self.accept()
        except Exception as e:
           print(e)
           self.send_error(str(e))

            

    def disconnect(self, close_code):
        
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

   
    def receive(self, text_data):
       
        data= json.loads(text_data)
        print("text_data",text_data)
        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")+'Z'
        data["date"]= formatted_time
        print("data",data)
        message = data
        status, error_message = self.save_message(message)

        if status:
             
             async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat.message", "message":message}
        )    
            
             try:
                 
              self.push_notification(message)  
             except Exception as e:
              error_message = str(e)
        if error_message:
            print(error_message)
            self.send_error(error_message,'push_notification')


    def push_notification(self, message):
        
        organization_device_registrations = None
        device_tokens = []
        title = ""
        message_type = "chatMessage"
        body = message['message']
        client_id=message["client"]
        
        if message['flag'] == 0:
            receiver = User.objects.get(id=message['client'])
            organization_device_registrations = DeviceRegistration.objects.filter(user=receiver)
            title = "Examate"
        elif message['flag'] == 1:
            organization_device_registrations = DeviceRegistration.objects.filter(user_type=0)
            sender = User.objects.get(id=message['client'])
            title = sender.username
        
        device_tokens = [registration.device_token for registration in organization_device_registrations if organization_device_registrations]
        
        if device_tokens:
            push_service.notify_multiple_devices(
                registration_ids=device_tokens,
                data_message={
                    "title": title,
                    "body": body,
                    "client_id":client_id,
                    "type": message_type
                }
            )
   

    def chat_message(self, event):
        print("Chat Message",event)
        message = event["message"]
        message["type"]="chat_message"
        self.send(text_data=json.dumps(message))

    def send_error(self, message,error_type="connection_error"):
        error_data = {
            'error_type': error_type,
            'message': message
        }
        self.send(text_data=json.dumps(error_data))



