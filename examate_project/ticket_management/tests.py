from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from user_management.models import User
from django.urls import reverse
from datetime import datetime
from .models import Ticket
from exam_management.models import Exam
from examate_project.pagination import CustomSetPagination
from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Ticket,Notification,DeviceRegistration
from user_management.models import User
from django.test import TestCase, RequestFactory
from rest_framework.test import APIRequestFactory
from .views import NotificationListView,BuyTicketView
from unittest.mock import patch,MagicMock

from examate_project.pagination import CustomSetPagination

MONTHS = {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December',
}

class BuyTicketViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser@gmail.com', password='testpassword')
        self.exam=Exam.objects.create(name='Exam 2', scheduled_time='2024-02-16T10:00:00Z', organization=self.user, status=1)
        self.ticket_1 = Ticket.objects.create(organisation=self.user,created_at=timezone.now(),status=0,exam=self.exam)
        self.ticket_2 = Ticket.objects.create(organisation=self.user,created_at=timezone.now(),status=0,exam=self.exam)
        self.ticket_3 = Ticket.objects.create(organisation=self.user,created_at=timezone.now(),status=0,exam=self.exam)
        self.admin = User.objects.create_user(username='testadmin', password='testpassword', email='testadmin1@gmail.com', user_type=0, is_register=1) 
        self.device_registration = DeviceRegistration.objects.create(device_token='test_device_token', user=self.user)
    def test_buy_tickets(self):
        self.client.force_authenticate(user=self.user)
        payload = {'ticket_count': 3}
        response = self.client.post(reverse('buy-ticket'), data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_unauthenticated_access(self):
        response = self.client.get(reverse('buy-ticket'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_missing_ticket_count(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('buy-ticket'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_invalid_ticket_count(self):
        self.client.force_authenticate(user=self.user)
        payload = {'ticket_count': 'abc'}
        response = self.client.post(reverse('buy-ticket'), data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_negative_ticket_count(self):
        self.client.force_authenticate(user=self.user)
        payload = {'ticket_count': -3}
        response = self.client.post(reverse('buy-ticket'), data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_ticket_creation_failure(self):
        self.client.force_authenticate(user=self.user)
        invalid_payload = {"ticket_count":' ' }
        response = self.client.post(reverse('buy-ticket'), data=invalid_payload) 
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
   
    def test_retrieve_purchased_tickets(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('ticket-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']),  3) 
    def test_pagination(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('ticket-list'))  
        self.assertEqual(response.status_code, 200)
        self.assertIn('count', response.data)
        self.assertIn('total_pages', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        self.assertIn('current_page_size', response.data)
        self.assertIn('page_size', response.data)
        self.assertEqual(len(response.data['results']), 3)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
    @patch('ticket_management.views.push_service.notify_single_device')
    def test_successful_ticket_purchase(self, mock_notify_single_device):
        self.client.force_authenticate(user=self.user)
        payload = {'ticket_count': 3}
        response = self.client.post(reverse('buy-ticket'), data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], '3 tickets purchased successfully')
   
class TicketStatusCountAPITest(TestCase):
    def setUp(self):
       
       self.user = User.objects.create_user(
            username='testuser', password='testuser', email='testuser@gmail.com', user_type=1, is_register=1)
       self.client = APIClient()
       self.client.force_authenticate(user=self.user)
      
       Ticket.objects.create(status=0, organisation=self.user)
       Ticket.objects.create(status=0, organisation=self.user)
       Ticket.objects.create(status=1, organisation=self.user)
       Ticket.objects.create(status=2, organisation=self.user)
       Ticket.objects.create(status=2, organisation=self.user)

    def test_ticket_status_count_api(self):
        url = reverse('ticket-status-count')  
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['requested_count'], 2)
        self.assertEqual(response.data['approved_count'], 1)
        self.assertEqual(response.data['consumed_count'], 2)

    def test_ticket_status_count_api_with_no_tickets(self):
      
        Ticket.objects.filter(organisation=self.user).delete()

        url = reverse('ticket-status-count') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['requested_count'], 0)
        self.assertEqual(response.data['approved_count'], 0)
        self.assertEqual(response.data['consumed_count'], 0)

        
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from user_management.models import User
from .models import Ticket
from django.urls import reverse

class TicketRequestListViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password='testpassword',
            email="testuser@gmail.com",
            user_type=1,
            is_register=1,
        )
        self.client = APIClient()
        self.client.login( email="testuser@gmail.com", password='testpassword')

    

    def test_list_ticket_requests(self):
        # Create some test tickets
        tickets = [
            Ticket.objects.create(organisation=self.user, status=0),
            Ticket.objects.create(organisation=self.user, status=0),
            Ticket.objects.create(organisation=self.user, status=0),
        ]
        # Make a GET request to the view
        url = reverse('ticket-request-list') 
        response = self.client.get(url)  # Replace with your actual API endpoint

        # Assert that the request was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the tickets are listed correctly in the response
        self.assertEqual(len(response.data['results']), 1)  # Assuming pagination is not applied
        # Add more assertions as needed to ensure the response matches the expected format

class TicketHidtoryListViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password='testpassword',
            email="testuser@gmail.com",
            user_type=1,
            is_register=1,
        )
        self.client = APIClient()
        self.client.login( email="testuser@gmail.com", password='testpassword')




    def test_history_list_ticket(self):
        # Create some test tickets
        tickets = [
            Ticket.objects.create(organisation=self.user, status=0),
            Ticket.objects.create(organisation=self.user, status=1),
            Ticket.objects.create(organisation=self.user, status=2),
        ]
        # Make a GET request to the view
        url = reverse('ticket-history') 
        response = self.client.get(url)  # Replace with your actual API endpoint

        # Assert that the request was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the tickets are listed correctly in the response
        self.assertEqual(len(response.data['results']), 3)  # Assuming pagination is not applied
        # Add more assertions as needed to ensure the response matches the expected format


        # Assert that the tickets are listed correctly in the response
 



class TicketStatusUpdateViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password='testpassword',
            email="testuser@gmail.com",
            user_type=1,
            is_register=1,
        )
        self.client = APIClient()
        self.client.login( email="testuser@gmail.com", password='testpassword') 

    def test_update_ticket_status(self):
        tickets = [
            Ticket.objects.create(organisation=self.user, status=0),
            Ticket.objects.create(organisation=self.user, status=0),
            Ticket.objects.create(organisation=self.user, status=0),
        ]
        data = {
            'ticket_ids': [tickets[0].id],
            'updatedStatus': 1,  # Set status to 1 (Approved)
        }

        # Make a PATCH request to the view
        url = reverse('ticket-status-update')  # Replace with your actual API endpoint
        response = self.client.patch(url, data, format='json')

        # Assert that the request was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

  # Expecting status to be updated to 1 (Approved)


class NotificationListViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test_user@gmail.com', password='test_password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_notification_list_view(self):
        # Create some notifications for the test user
        Notification.objects.create(title='Test Notification 1', body='Notification body 1', user=self.user)
        Notification.objects.create(title='Test Notification 2', body='Notification body 2', user=self.user)
        url = reverse('notifications-list') 
        # Make a GET request to the view
        response = self.client.get(url)

        # Check that the response status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("reponse ;",response.data)
        # Check that the response contains the notifications
        self.assertEqual(len(response.data), 7)

class DeviceRegistrationViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test_user@gmail.com', password='test_password')
        self.client.force_authenticate(user=self.user)       

    def test_device_registration_success(self):
        url = reverse('register_device')
        data={'kdjshfjshdf'}
        
        response = self.client.post(url,data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['message'], 'Device token registered successfully')

    def test_device_registration_failure(self):
        url = reverse('register_device')
        
        response = self.client.post(url)
      
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
     
        self.assertEqual(response.data['errorCode'], 'E83003')

class DeleteDeviceRegistrationTokenViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test_user@gmail.com', password='test_password')
        self.device_registration = DeviceRegistration.objects.create(device_token='test_device_token', user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_delete_device_registration_success(self):
        url=reverse("delete-register_device", kwargs={'device_token': self.device_registration.device_token})
        
        response = self.client.delete(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)     
        self.assertEqual(response.data['message'], 'Device registration deleted successfully')

 

    


class CountNotificationsViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test_user@gmail.com', password='test_password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        Notification.objects.create(title='Notification 1', body='Body 1', status=0,user=self.user)
        Notification.objects.create(title='Notification 2', body='Body 2', status=1,user=self.user)
        Notification.objects.create(title='Notification 3', body='Body 3', status=0,user=self.user)

    def test_count_notifications(self):
        url = reverse('count_notifications')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)  # Expecting 2 notifications with status 0

    def test_count_notifications_no_notifications(self):
        # Delete all notifications
        Notification.objects.all().delete()

        url = reverse('count_notifications')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)  


class ApprovedTicketRevenueListTest(APITestCase):
    def setUp(self):
            self.user = User.objects.create_user(email='testuser@gmail.com', password='testpassword')
            self.exam=Exam.objects.create(name='Exam 2', scheduled_time='2024-02-16T10:00:00Z', organization=self.user, status=1)      
            Ticket.objects.create(created_at=timezone.now() - timezone.timedelta(days=30),organisation=self.user,exam=self.exam),
            Ticket.objects.create(created_at=timezone.now() - timezone.timedelta(days=60),organisation=self.user,exam=self.exam),
            Ticket.objects.create(created_at=timezone.now() - timezone.timedelta(days=45),organisation=self.user,exam=self.exam),
            Ticket.objects.create(created_at=timezone.now() - timezone.timedelta(days=90),organisation=self.user,exam=self.exam),
            Ticket.objects.create(created_at=timezone.now() - timezone.timedelta(days=120),organisation=self.user,exam=self.exam),
           
        

    def test_get_with_tickets(self):
        url=reverse('revenue')   
        response = self.client.get(url)  
        self.assertEqual(response.status_code, status.HTTP_200_OK)
       