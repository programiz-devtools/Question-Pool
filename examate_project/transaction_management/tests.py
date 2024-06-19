from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from user_management.models import User
from ticket_management.models import Ticket

class StripePaymentCheckoutTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url=reverse('payment-checkout')

    def test_stripe_payment_checkout(self):
        ticket_count = 2     
        response = self.client.post(self.url, ticket_count, format='json')      
        self.assertEqual(response.status_code, status.HTTP_200_OK)      
        self.assertIn('clientSecret', response.data)

class PaymentConfirmationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url=reverse('payment-confirmation')

    def test_payment_confirmation(self):
        
        user = User.objects.create_user(email='testuser@gmail.com', password='testpassword')
        ticket = Ticket.objects.create(organisation=user,status=0)
        payment_id = 'test_payment_id'
        amount = 100  
        data = {
            'ticket_id': [ticket.id], 
            'payment_id': payment_id,
            'amount': amount
        }
        self.client.force_authenticate(user=user) 
       
        response = self.client.post(self.url, data, format='json')        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

       
        

    