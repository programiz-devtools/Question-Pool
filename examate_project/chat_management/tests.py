from django.test import TestCase
import unittest
from unittest import mock
from unittest.mock import patch,Mock,MagicMock
from django.test import RequestFactory
from rest_framework.test import APIRequestFactory,APITestCase,force_authenticate,APIClient
from rest_framework.response import Response
from rest_framework import status
from .views import GetMessages,UpdateIsRead,GetUnreadMessagesCount
from .serializers import GetMessageSerializer
from user_management.models import User
from .consumer import ChatConsumer
from django.urls import reverse
import json
from datetime import datetime
class GetMessagesTestCase(unittest.TestCase):
    def setUp(self):
        self.factory = APIRequestFactory() 
        self.user=MagicMock(username='chatuser',user_type=0)
        

    @patch('chat_management.views.ChatMessage.objects.filter')
    @patch('chat_management.views.GetMessageSerializer')
    def test_get_queryset(self,mock_serializer,mock_filter):
       
     
        url = f'chat/get-messages/?client_id={1}&&flag={1}'
        request = self.factory.get(url)
        force_authenticate(request,user=self.user)
        mock_queryset = MagicMock()
      
        mock_filter.return_value = mock_queryset
        response = GetMessages.as_view()(request)
      
        self.assertEqual(response.status_code, status.HTTP_200_OK)
       

    @patch('chat_management.views.ChatMessage.objects.filter')
    @patch('chat_management.views.GetMessageSerializer')
    def test_get_queryset_for_consumer(self,mock_serializer,mock_filter):
        self.user=MagicMock(username='chatuser',user_type=1)
        client_id=1
        flag=1
        url = f'chat/get-messages/?client_id={client_id}&&flag={flag}'
        request = self.factory.get(url,format='json')
        force_authenticate(request,user=self.user)
        mock_queryset = MagicMock()
      
        mock_filter.return_value = mock_queryset
        response = GetMessages.as_view()(request)
      
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('chat_management.views.ChatMessage.objects.filter')
    @patch('chat_management.views.GetMessageSerializer')
    def test_get_all_queryset(self,mock_serializer,mock_filter):
       
     
        url = f'chat/get-messages/?client_id={1}&&flag={10}'
        request = self.factory.get(url)
        force_authenticate(request,user=self.user)
        mock_queryset = MagicMock()
      
        mock_filter.return_value = mock_queryset
        response = GetMessages.as_view()(request)
      
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class UpdateIsReadTestCase(unittest.TestCase):
    def setUp(self):
        self.factory=APIRequestFactory()
        self.user=MagicMock(username='chatuser',user_type=0)

    @patch('chat_management.views.ChatMessage.objects.filter')
    def test_update_is_read(self,mock_filter):
       
        mock_queryset=MagicMock(client_id=1,flag=1)
        mock_filter.return_value=mock_queryset
        url='chat/mark-messages-read/'
        request_data = {'latest_message_id': 1, 'client_id': 1}
        request = self.factory.patch(url, data=json.dumps(request_data), content_type='application/json')
        force_authenticate(request,user=self.user)
        response=UpdateIsRead.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('chat_management.views.ChatMessage.objects.filter')
    def test_update_is_read_of_consumer(self,mock_filter):
        self.user=MagicMock(username='chatuser',user_type=1)
        mock_queryset=MagicMock(client_id=1,flag=0)
        mock_filter.return_value=mock_queryset
        url='chat/mark-messages-read/'
        request_data = {'latest_message_id': 1, 'client_id': 1}
        request = self.factory.patch(url, data=json.dumps(request_data), content_type='application/json')
        force_authenticate(request,user=self.user)
        response=UpdateIsRead.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('chat_management.views.ChatMessage.objects.filter')
    def test_update_is_read_latest_message_required(self,mock_filter):
        self.user=MagicMock(username='chatuser',user_type=1)
        mock_queryset=MagicMock(client_id=1,flag=0)
        mock_filter.return_value=mock_queryset
        url='chat/mark-messages-read/'
        request_data = {'client_id': 1}
        request = self.factory.patch(url, data=json.dumps(request_data), content_type='application/json')
        force_authenticate(request,user=self.user)
        response=UpdateIsRead.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'latest_message_id is required')

    @patch('chat_management.views.ChatMessage.objects.filter')
    def test_update_is_read_exception(self,mock_filter):
        self.user=MagicMock(username='chatuser',user_type=1)
        mock_queryset=MagicMock(client_id=1,flag=0)
        mock_filter.return_value=mock_queryset
        url='chat/mark-messages-read/'
        request_data = {'client_id': 1}
        request = self.factory.patch(url, data=request_data, content_type='application/json')
        force_authenticate(request,user=self.user)
        response=UpdateIsRead.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetUnreadMessagesCountTestCase(unittest.TestCase):
    def setUp(self):
        self.factory=APIRequestFactory()
        self.client=APIClient()
        self.user=MagicMock(username='chatuser',user_type=0)

    @patch('chat_management.views.ChatMessage.objects.filter')
    def test_get_unread_messages_count(self,mock_filter):
       
        mock_queryset=[MagicMock(client_id=1,flag=0,is_read=0),MagicMock(client_id=1,flag=0,is_read=0)]
        mock_filter.return_value.count.return_value = len(mock_queryset)
        url=reverse('unread-messages-count')
        data = {'client_id': 1}
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    @patch('chat_management.views.ChatMessage.objects.filter')
    def test_get_unread_messages_count_for_consumer(self,mock_filter):
        self.user=MagicMock(username='chatuser',user_type=1)
        mock_queryset=[MagicMock(client_id=1,flag=0,is_read=0),MagicMock(client_id=1,flag=0,is_read=0)]
        mock_filter.return_value.count.return_value = len(mock_queryset)
        url=reverse('unread-messages-count')
        data = {'client_id': 1}
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('chat_management.views.ChatMessage.objects.filter')
    def test_get_unread_messages_count_without_client_id(self,mock_filter):
        self.user=MagicMock(username='chatuser',user_type=0)
        mock_queryset=[MagicMock(client_id=1,flag=0,is_read=0),MagicMock(client_id=1,flag=0,is_read=0)]
        mock_filter.return_value.count.return_value = len(mock_queryset)
        url=reverse('unread-messages-count')
      
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    @patch('chat_management.views.ChatMessage.objects.filter')
    def test_get_unread_messages_count_exception(self,mock_filter):
        self.user=MagicMock(username='chatuser',user_type=0)
        mock_queryset=[MagicMock(client_id=1,flag=0,is_read=0),MagicMock(client_id=1,flag=0,is_read=0)]
       
        url=reverse('unread-messages-count')
        mock_filter.side_effect = Exception("Something went wrong")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConnectTestCase(unittest.TestCase):

    def setUp(self):
        pass

   
    def test_connect_success(self):
       
        mock_object=ChatConsumer()
        mock_object.scope = {
            'query_string': b'client_id=123'
        } 
        mock_object.channel_layer = mock.AsyncMock()
        mock_object.channel_name = "test_channel_name"
        mock_object.base_send=Mock()

        ChatConsumer.connect(mock_object)
        mock_object.channel_layer.group_add.assert_called_once_with(
            f"chat_123", "test_channel_name"
        )
        
       
        
        
        
       
      
class DisconnectTestCase(unittest.TestCase):

    def setUp(self):
        pass


    def test_disconnect_success(self):
        mock_object=ChatConsumer()
       
        mock_object.channel_layer = mock.AsyncMock()
        mock_object.channel_name = "test_channel_name"
        mock_object.base_send=Mock()
        mock_object.room_group_name="chat_123"

        ChatConsumer.disconnect(mock_object,None)
        mock_object.channel_layer.group_discard.assert_called_once_with(
            f"chat_123", "test_channel_name"
        )
class ReceiveTestCase(unittest.TestCase):

    @patch('chat_management.consumer.ChatConsumer.save_message')
    @patch('chat_management.consumer.datetime')
    def test_receive(self,mock_datetime,mock_save_message):
            mock_object=ChatConsumer()
            mock_object.room_group_name='test_room_group'
            mock_save_message.return_value=True,None
            mock_now = datetime(2024, 5, 10, 12, 0, 0)
            mock_datetime.now.return_value = mock_now
            mock_object.close=MagicMock()
            mock_object.channel_layer = mock.AsyncMock()
           
            mock_object.push_notification=MagicMock()

            message_data={
                "message":"Test message",
                "flag":0,
                "client":123
            }
            text_data=json.dumps(message_data)
            mock_object.receive(text_data)
            mock_object.save_message.assert_called_once_with({'message': 'Test message', 'flag': 0, 'client': 123, 'date': '2024-05-10 12:00:00Z'})
            mock_object.channel_layer.group_send.assert_called_once_with(
                mock_object.room_group_name, 
                {"type": "chat.message", "message":{'message': 'Test message', 'flag': 0, 'client': 123, 'date': '2024-05-10 12:00:00Z'}}
            )
            mock_object.close.assert_not_called()

    @patch('chat_management.consumer.ChatConsumer.save_message')
    @patch('chat_management.consumer.datetime')
    def test_receive_save_message_error(self,mock_datetime,mock_save_message):
           
            mock_object=ChatConsumer()
            mock_object.base_send=Mock()
            mock_object.room_group_name='test_room_group'
            mock_save_message.return_value=False,"Error"
            mock_now = datetime(2024, 5, 10, 12, 0, 0)
            mock_datetime.now.return_value = mock_now
            mock_object.close=MagicMock()
            mock_object.channel_layer = mock.AsyncMock()
           
            mock_object.push_notification=MagicMock()

            message_data={
                "message":"Test message",
                "flag":0,
                "client":123
            }
            text_data=json.dumps(message_data)
            mock_object.receive(text_data)
            mock_object.channel_layer.group_send.assert_not_called()
           


class ChatMessageTestCase(unittest.TestCase):
    def test_chat_message(self):
        mock_event = {"message": {"text": "Test message"}}
        mock_object = ChatConsumer()
        mock_object.send = MagicMock()
        mock_object.chat_message(mock_event)
        expected_message = {"text": "Test message", "type": "chat_message"}
        mock_object.send.assert_called_once_with(text_data=json.dumps(expected_message))

class SaveMessageTestCase(unittest.TestCase):

    @patch('chat_management.consumer.User.objects.get')
    @patch('chat_management.consumer.ChatMessage.objects.create')
    def test_save_message_success(self,mock_create,mock_get):
        mock_user=MagicMock()
        mock_get.return_value=mock_user
        mock_object=ChatConsumer()
        message_data = {
            'client': 123,
            'message': 'Test message',
            'flag': 0
        }
        result=mock_object.save_message(message_data)
        mock_create.assert_called_once_with(
            client=mock_user,
            message='Test message',
            flag=0
        )
        self.assertTrue(result)

    @patch('chat_management.consumer.User.objects.get')
    @patch('chat_management.consumer.ChatMessage.objects.create')
    def test_save_message_failure(self,mock_create,mock_get):
        mock_user=MagicMock()
        mock_get.side_effect = Exception('User not found')
        mock_object=ChatConsumer()
        message_data = {
            'client': 123,
            'message': 'Test message',
            'flag': 0
        }
        result,error=mock_object.save_message(message_data)
        mock_create.assert_not_called()
        self.assertFalse(result)

class PushNotificationTestCase(unittest.TestCase):

    @patch('chat_management.consumer.User.objects.get')
    @patch('chat_management.consumer.DeviceRegistration.objects.filter')
    @patch('chat_management.consumer.push_service.notify_multiple_devices')
    def test_push_notification_with_flag_receiver(self, mock_notify_devices, mock_filter, mock_get):
        mock_receiver=MagicMock()
        mock_receiver.username="Receiver username"
        mock_get.return_value = mock_receiver
        mock_filter.return_value=[mock_receiver]
        mock_object = ChatConsumer()
        message_data={
            'message': 'Test message',
            'flag': 0,
            'client': 123
        }
        mock_object.push_notification(message_data)
        mock_filter.assert_called_once_with(user=mock_receiver)
        mock_notify_devices.assert_called_once_with(
            registration_ids=[mock_receiver.device_token],
            data_message={
                'title': 'Examate',
                'body': 'Test message',
                'client_id': 123,
                'type': 'chatMessage'
            }
        )
        
    @patch('chat_management.consumer.User.objects.get')
    @patch('chat_management.consumer.DeviceRegistration.objects.filter')
    @patch('chat_management.consumer.push_service.notify_multiple_devices')
    def test_push_notification_with_flag_sender(self, mock_notify_devices, mock_filter, mock_get):
        mock_sender=MagicMock()
        mock_sender.username="Sender username"
        mock_get.return_value = mock_sender
        mock_filter.return_value=[mock_sender]
        mock_object = ChatConsumer()
        message_data={
            'message': 'Test message',
            'flag': 1,
            'client': 123
        }
        mock_object.push_notification(message_data)
        mock_filter.assert_called_once_with(user_type=0)
        mock_notify_devices.assert_called_once_with(
            registration_ids=[mock_sender.device_token],
            data_message={
                'title':"Sender username",
                'body': 'Test message',
                'client_id': 123,
                'type': 'chatMessage'
            }
        )
        










  





       
        

    
    




