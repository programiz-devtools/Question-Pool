from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory,APIClient
from django.utils import timezone
from user_management.models import OTP, User
from .views import ForgetPasswordView, VerifyOTPView, ResendOTPView, ResetPasswordView, RegisterView
from django.utils.crypto import get_random_string
from django.core.mail import outbox
from django.core import mail
from rest_framework import permissions
from .permission import IsUserHaveOtp
from rest_framework.test import force_authenticate
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from django.core.exceptions import ValidationError
from .models import CustomUserManager
from .serializers import CustomTokenObtainPairSerializer
from unittest.mock import patch
from django.conf import settings
import os
import json
from rest_framework.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import response
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from rest_framework.response import Response
from .views import LoginWithGoogle
import unittest
from google.auth.exceptions import InvalidValue, MalformedError




from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import response
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from rest_framework.response import Response
from .views import LoginWithGoogle
import unittest
from google.auth.exceptions import InvalidValue, MalformedError



class RegisterViewTestCase(APITestCase):

    def setUp(self):
        self.factory = APIClient()
        self.register_url = reverse('sign-up')

    def test_user_registration_success(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Testpassword@123",
            "contact_number": "9234567890",
            "address": "TestAddress",
        }
        response = self.client.post(self.register_url, data, format='json')
        print(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    
    def test_user_registration_success_is_not_register(self):
        User.objects.create(email='test1@example.com')
        data = {
            'username': 'test user',
            'email': 'tests@example.com',
            'address': 'tests address',
            'contact_number': '9089786756',
            'password': 'Passwords@123'
            }

        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_invalid_registration(self):
        data = {
            
            'email': 'invalid email',
            'address': 'test address',
            'contact_number': 'no',
            'password': 'shot',
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_existing_email_conflict(self):
        existing_user = User.objects.create(email='test@example.com')
        existing_user.is_register = 1
        existing_user.save()

        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'address':'test address',
            'contact_number': '9089786756',
            'password': 'Password@123'
        }

        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['message'], 'Email already exists')
        self.assertEqual(response.data['errorCode'], 'E13008')

    def test_existing_username_conflict(self):
        existing_user = User.objects.create(username='testuser')
        existing_user.is_register = 1
        existing_user.save()

        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'address':'test address',
            'contact_number': '9089786756',
            'password': 'Password@123'
        }

        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['message'],'Please use a different username. It  already exists.')
   
    def test_invalid_username_format(self):
        data = {
            "username": "1",
            "email": "test@gmail.com",
            "address": "test password",
            "contact_number": "9987786790",
            "password": "Test@123"
        }

        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'username must be greater than 4')
        self.assertEqual(response.data['errorCode'], 'E13001')

    def test_username_required(self):
        data = {
            
            "email": "test@gmail.com",
            "address": "test password",
            "contact_number": "9987786790",
            "password": "Test@123"
        }

        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Username required')
        self.assertEqual(response.data['errorCode'], 'E13003')

    def test_long_username_format(self):
        data = {
            "username": "abcdefghijklmnopqrstuvwxyz",
            "email": "test@gmail.com",
            "address": "test password",
            "contact_number": "9987786790",
            "password": "Test@123"
        }

        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'username must be less than 20')
        self.assertEqual(response.data['errorCode'], 'E13002')

    def test_short_contact_number(self):
        data = {
            "username": "abcde",
            "email": "test@gmail.com",
            "address": "test password",
            "contact_number": "8679333222222220",
            "password": "Test@123"
        }

        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Contact number should be less than 10')
        self.assertEqual(response.data['errorCode'], 'E13009')

    def test_required_contact_number(self):
        data = {
            "username": "abcde",
            "email": "test@gmail.com",
            "address": "test password",
             "contact_number": "867933abcc",
            "password": "Test@123"
        }

        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'The contact field format is invalid')
        self.assertEqual(response.data['errorCode'], 'E13011')

    def test_required_contact(self):
        data = {
            "username": "abcde",
            "email": "test@gmail.com",
            "address": "test password",
            "password": "Test@123"
        }

        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Contact number required')
        self.assertEqual(response.data['errorCode'], 'E13010')

    def test_existing_contact_number_conflict(self):
        existing_user = User.objects.create(contact_number='9999999999')
        existing_user.is_register = 1
        existing_user.save()

        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'address':'test address',
            'contact_number': '9999999999',
            'password': 'Password@123'
        }

        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['message'], 'Contact number already exists.')
        self.assertEqual(response.data['errorCode'], 'E13012')

    def test_length_password(self):
        data = {
            "username": "abcde",
            "email": "test@gmail.com",
            "contact_number": "9987786790",
            "address": "test password",
            "password": "123"
        }

        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'password should contains minimum 8 length')
        self.assertEqual(response.data['errorCode'], 'E13013')
        
    def test_invalid_password(self):
        data = {
            "username": "abcde",
            "email": "test@gmail.com",
            "contact_number": "9987786790",
            "address": "test password",
            
        }

        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'password required')
        self.assertEqual(response.data['errorCode'], 'E13014')

    def test_required_email(self):
        data = {
            "username": "abcde",
            "address": "test password",
            "contact_number": "8679337867",
            "password": "Test@123"
        }

        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Email required')
        self.assertEqual(response.data['errorCode'], 'E13006')

    def test_email_invalid(self):
        data = {
            "username": "abcde",
            "email": "test@gmailcom",
            "address": "test password",
            "contact_number": "9987786790",
            "password": "Test@123"
        }

        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'The email field format is invalid')
        self.assertEqual(response.data['errorCode'], 'E13007')


    @patch('user_management.views.make_password')  # Mocking make_password function
    @patch('user_management.views.otp_generate')  # Mocking otp_generate function
    @patch('user_management.views.Token.objects.get_or_create')  # Mocking Token creation
    
    def test_error_during_user_creation(self, mock_token_get_or_create, mock_otp_generate, mock_make_password):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'address':'test address',
            'contact_number': '9988998877',
            'password': 'Password@123'
        }

        # Mocking an exception occurring during user creation
        mock_make_password.side_effect = Exception('Some error occurred')

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['message'], 'Error occurred during user creation: Some error occurred')
        # Verify that the functions were not called
        mock_otp_generate.assert_not_called()
        mock_token_get_or_create.assert_not_called()

class ForgetPasswordViewTestCase(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.reset_password_url = reverse('forgot-password')

    def test_forget_password_view_invalid_email(self):
        data = {'email': 'invalid@email.com'}
        request = self.factory.post(self.reset_password_url, data)
        response = ForgetPasswordView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'],
                         'User not found with this email')

    def test_forget_password_view_missing_email(self):
        data = {}
        request = self.factory.post(self.reset_password_url, data)
        response = ForgetPasswordView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], "Email is required")

    def test_forget_password_view_success(self):
        user = User.objects.create_user(
            username='testuser', password='testpassword', email='testuser@gmail.com',is_register=1)
        
        data = {'email': 'testuser@gmail.com'}
        request = self.factory.post(self.reset_password_url, data)
        response = ForgetPasswordView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'],
                         'Password reset OTP sent successfully')
        self.assertIn('expiration_time', response.data)

        expiration_time_from_response = response.data['expiration_time']
        expiration_time_from_db = OTP.objects.get(
            user=user).otp_created_at + timezone.timedelta(minutes=1)

        self.assertAlmostEqual(expiration_time_from_response,
                               expiration_time_from_db, delta=timezone.timedelta(seconds=1))
        self.assertEqual(OTP.objects.filter(user=user).count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Password Reset OTP')
        self.assertIn('Your OTP is:', mail.outbox[0].body)

  
    def test_forget_password_view_failed_for_google_user(self):
        user = User.objects.create_google_user(
            username='test1user', email='test1user@gmail.com',is_register=1)
        
      
        
        data = {'email': 'test1user@gmail.com'}
        request = self.factory.post(self.reset_password_url, data)
        response = ForgetPasswordView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
       
    def test_forget_password_view(self):
        user = User.objects.create_user(
            username='testuser', password='testpassword', email='testuser@gmail.com')
        
        data = {'email': 'testuser@gmail.com'}
        request = self.factory.post(self.reset_password_url, data)
        response = ForgetPasswordView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'],
                         'User is not registered')
    def test_forget_password_view_failed_for_google_user(self):
        user = User.objects.create_google_user(
            username='test1user', email='test1user@gmail.com',is_register=1)
        
        data = {'email': 'test1user@gmail.com'}
        request = self.factory.post(self.reset_password_url, data)
        response = ForgetPasswordView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class VerifyOTPViewTestCase(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.verify_otp_url = reverse('verify-otp')

    def test_verify_otp_view_success(self):
        user = User.objects.create_user(
            username='testuser', password='testpassword', email='testuser@gmail.com')
        otp = OTP.objects.create(
            user=user, otp='1234', otp_type=0, otp_created_at=timezone.now())
        data = {'email': 'testuser@gmail.com', 'otp': '1234', 'otp_type': 0}
        json_data = json.dumps(data)
        request = self.factory.patch(self.verify_otp_url, json_data,content_type='application/json')
        response = VerifyOTPView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'],
                         'OTP verification successful')
        


    def test_verify_otp_view_without_otp(self):
        user = User.objects.create_user(
            username='testuser', password='testpassword', email='testuser@gmail.com')
        otp = OTP.objects.create(
            user=user, otp='1234', otp_type=0, otp_created_at=timezone.now())
        data = {'email': 'testuser@gmail.com', 'otp_type': 0}
        json_data = json.dumps(data)
        request = self.factory.patch(self.verify_otp_url, json_data,content_type='application/json')
        response = VerifyOTPView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'],
                         'OTP is required')
        

    def test_verify_otp_view_invalid_otp_type(self):
        user = User.objects.create_user(
            username='testuser', password='testpassword', email='testuser@gmail.com')
        otp = OTP.objects.create(
            user=user, otp='1234', otp_type=0, otp_created_at=timezone.now())
        data = {'email': 'testuser@gmail.com', 'otp': '1234', 'otp_type': 10}
        json_data = json.dumps(data)
        request = self.factory.patch(self.verify_otp_url, json_data,content_type='application/json')
        response = VerifyOTPView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'],
                         'OTP type must be 0 or 1')
        

    def test_verify_otp_view_none_otp_type(self):
        user = User.objects.create_user(
            username='testuser', password='testpassword', email='testuser@gmail.com')
        otp = OTP.objects.create(
            user=user, otp='1234', otp_type=0, otp_created_at=timezone.now())
        data = {'email': 'testuser@gmail.com'}
        json_data = json.dumps(data)
        request = self.factory.patch(self.verify_otp_url, json_data,content_type='application/json')
        response = VerifyOTPView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'],
                         'OTP type is required')

       

    def test_verify_otp_view_expired_otp(self):
        user = User.objects.create_user(
            username='testuser', password="testpassword", email="testuser@gmail.com")
        otp = OTP.objects.create(user=user, otp='1234', otp_type=0,
                                 otp_created_at=timezone.now() - timezone.timedelta(minutes=2))
        data = {'email': 'testuser@gmail.com', 'otp': '1234', 'otp_type': 0}
        json_data = json.dumps(data)
        request = self.factory.patch(self.verify_otp_url, json_data,content_type='application/json')
        response = VerifyOTPView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'],
                         'OTP has expired. Click on resend')

    def test_verify_otp_view_missing_email(self):
        data = {'otp': '1234', 'otp_type': 0}
        json_data = json.dumps(data)
        request = self.factory.patch(self.verify_otp_url, json_data,content_type='application/json')
        response = VerifyOTPView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], "Email is required")

    def test_verify_otp_view_missing_email_and_otp(self):
        data = {}
        json_data = json.dumps(data)
        request = self.factory.patch(self.verify_otp_url,  json_data,content_type='application/json')
        response = VerifyOTPView.as_view()(request)
       
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'],
                         'Email is required')

    def test_verify_otp_view_invalid_otp(self):
        user = User.objects.create_user(
            username='testuser', password='testpassword', email='testuser@gmail.com')
        data = {'email': 'testuser@gmail.com', 'otp': '1234', 'otp_type':0}
        json_data = json.dumps(data)
        request = self.factory.patch(self.verify_otp_url, json_data,content_type='application/json')
        response = VerifyOTPView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Invalid OTP')

    def test_verify_otp_view_invalid_otp_value(self):
        user = User.objects.create_user(
            username='testuser', password='testpassword', email='testuser@gmail.com')
        otp = OTP.objects.create(
            user=user, otp='1234', otp_type=0, otp_created_at=timezone.now())

        data = {'email': 'testuser@gmail.com', 'otp': '5678', 'otp_type': 0}
        json_data = json.dumps(data)
        request = self.factory.patch(self.verify_otp_url,  json_data ,content_type='application/json')
        response = VerifyOTPView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Invalid OTP')

    def test_verify_otp_view_invalid_otp_type(self):
        user = User.objects.create_user(
            username='testuser', password='testpassword', email='testuser@gmail.com')
        otp = OTP.objects.create(
            user=user, otp='1234', otp_type=0, otp_created_at=timezone.now())
        data = {'email': 'testuser@gmail.com', 'otp': '1234', 'otp_type': 10}
        json_data = json.dumps(data)
        request = self.factory.patch(self.verify_otp_url, json_data,content_type='application/json')
        response = VerifyOTPView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'],
                         'OTP type must be 0 or 1')
        

    def test_verify_otp_view_none_otp_type(self):
        user = User.objects.create_user(
            username='testuser', password='testpassword', email='testuser@gmail.com')
        otp = OTP.objects.create(
            user=user, otp='1234', otp_type=0, otp_created_at=timezone.now())
        data = {'email': 'testuser@gmail.com'}
        json_data = json.dumps(data)
        request = self.factory.patch(self.verify_otp_url, json_data,content_type='application/json')
        response = VerifyOTPView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'],
                         'OTP type is required')


    @patch('user_management.views.User.objects.get')
    def test_verify_otp_view_user_not_found(self,mock_no_user):
      
        mock_no_user.side_effect=User.DoesNotExist
        data = {"email": "nonexistentuser@gmail.com",
                "otp": "1234", 'otp_type': 0}
        json_data = json.dumps(data)
        request = self.factory.patch(self.verify_otp_url, json_data,content_type='application/json')
        response = VerifyOTPView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'User not found with this email')

    def test_verify_otp_view_success_register_user(self):
        user = User.objects.create_user(
            username='testuser', password='testpassword', email='testuser@gmail.com')
        otp = OTP.objects.create(
            user=user, otp='1234', otp_type=1, otp_created_at=timezone.now())
        data = {'email': 'testuser@gmail.com', 'otp': '1234', 'otp_type': 1}
        json_data = json.dumps(data)
        request = self.factory.patch(self.verify_otp_url,  json_data,content_type='application/json')
        response = VerifyOTPView.as_view()(request)

        updated_user = User.objects.get(id=user.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'],
                         'OTP verification successful')
        self.assertEqual(updated_user.is_register, 1)

    def test_verify_otp_view_without_otp(self):
        user = User.objects.create_user(
            username='testuser', password='testpassword', email='testuser@gmail.com')
        otp = OTP.objects.create(
            user=user, otp='1234', otp_type=0, otp_created_at=timezone.now())
        data = {'email': 'testuser@gmail.com', 'otp_type': 0}
        json_data = json.dumps(data)
        request = self.factory.patch(self.verify_otp_url, json_data,content_type='application/json')
        response = VerifyOTPView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'],
                         'OTP is required')


class ResendOTPViewTestCase(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.resend_otp_url = reverse('resend-otp')

    def test_resend_otp_view_invalid_email(self):
        data = {'email': 'nonexistent@example.com', 'otp_type': 0}
        json_data = json.dumps(data)
        request = self.factory.post(self.resend_otp_url, json_data,content_type='application/json')
        response = ResendOTPView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'],
                         'User not found with this email')
        

    def test_resend_otp_view_none_otp_type(self):
        data = {'email': 'nonexistent@example.com'}
        json_data = json.dumps(data)
        request = self.factory.post(self.resend_otp_url, json_data,content_type='application/json')
        response = ResendOTPView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'],
                         'OTP type is required')


    def test_resend_otp_view_missing_email(self):
        data = {'otp_type':0}
        json_data = json.dumps(data)
        request = self.factory.post(self.resend_otp_url, json_data,content_type='application/json')
        response = ResendOTPView.as_view()(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], "Email is required")

    def test_resend_otp_view_success(self):

        user = User.objects.create_user(
            username='testuser', password='testpassword', email='testuser@gmail.com')
        initial_otp = OTP.objects.create(
            user=user, otp='1234', otp_type=0, otp_created_at=timezone.now())
        data = {'email': 'testuser@gmail.com', 'otp_type': 0}
        json_data = json.dumps(data)
        request = self.factory.post(self.resend_otp_url, json_data,content_type='application/json')
        response = ResendOTPView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'New OTP sent successfully')
        self.assertEqual(OTP.objects.filter(user=user).count(), 1)

    def test_resend_otp_view_none_otp_type(self):
        data = {'email': 'nonexistent@example.com'}
        json_data = json.dumps(data)
        request = self.factory.post(self.resend_otp_url, json_data,content_type='application/json')
        response = ResendOTPView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'],
                         'OTP type is required')
       
        

    def test_resend_otp_type(self):

        user = User.objects.create_user(
            username='testuser', password='testpassword', email='testuser@gmail.com')
        initial_otp = OTP.objects.create(
            user=user, otp='1234', otp_type=0, otp_created_at=timezone.now())
        data = {"email": "testuser@gmail.com", "otp_type": 10}
        json_data = json.dumps(data)

        request = self.factory.post(self.resend_otp_url, json_data,content_type='application/json')

        response = ResendOTPView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], 'OTP type must be 0 or 1')

       

    def test_resend_otp_view_without_existing_otp(self):
        user = User.objects.create_user(
            username='testuser', password='testpassword', email='testuser@gmail.com')
        OTP.objects.filter(user=user).delete()

        data = {'email': 'testuser@gmail.com', 'otp_type': 1}
        json_data = json.dumps(data)
        request = self.factory.post(self.resend_otp_url, json_data,content_type='application/json')
        response = ResendOTPView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'New OTP sent successfully')
        self.assertEqual(OTP.objects.filter(user=user).count(), 1)

        new_otp = OTP.objects.get(user=user)
       
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Your OTP for Registration')


class ResetPasswordViewTestCase(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.url = 'reset-password'

    def test_reset_password_valid_data(self):

        user = User.objects.create_user(
            username='testuser', password='testpassword', email='test@example.com')
        otp = OTP.objects.create(user=user, otp=get_random_string(
            length=4, allowed_chars='1234567890'), otp_type=0, otp_created_at=timezone.now())
        request_data = {
            'email': user.email,
            'new_password': 'Newpassword@12345',
            'confirm_password': 'Newpassword@12345',
            'otp': otp.otp,
            'otp_type': 0
        }

        request = self.factory.patch(self.url, data=request_data)
        response = ResetPasswordView.as_view()(request)
        update_user = User.objects.get(email=user.email)
       
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'],
                         'Password reset successfully')
        

  

    def test_reset_password_mismatched_confirm_password(self):
        user = User.objects.create_user(
            username='testuser', password='testpassword', email='test@example.com')
        otp = OTP.objects.create(user=user, otp=get_random_string(
            length=4, allowed_chars='1234567890'), otp_type=0, otp_created_at=timezone.now())
        request_data = {
            'email': user.email,
            'new_password': 'newpassword@12345',
            'confirm_password': 'mismatchedpassword',
            'otp': otp.otp,
            'otp_type': 0
        }

        request = self.factory.patch(self.url, data=request_data)
        response = ResetPasswordView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Password does not match', response.data['message'])

    def test_reset_password_weak_password(self):
        user = User.objects.create_user(
            username='testuser', password='testpassword', email='test@example.com')
        otp = OTP.objects.create(user=user, otp=get_random_string(
            length=4, allowed_chars='1234567890'), otp_type=0, otp_created_at=timezone.now())
        request_data = {
            'email': user.email,
            'new_password': 'weak',
            'confirm_password': 'weak',
            'otp': otp.otp,
            'otp_type': 0
        }
        request = self.factory.patch(self.url, data=request_data)
        response = ResetPasswordView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)

    def test_reset_password_invalid_otp(self):
        user = User.objects.create_user(
            username='testuser', password='testpassword', email='test@example.com')
        request_data = {
            'email': user.email,
            'new_password': 'newpassword@12345',
            'confirm_password': 'newpassword@12345',
            'otp': 'invalidotp',
            'otp_type': 0
        }

        request = self.factory.patch(self.url, data=request_data)
        response = ResetPasswordView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn(
            'Authentication credentials were not provided.', response.data['detail'])

    @patch('user_management.permission.IsUserHaveOtp.has_permission')
    def test_reset_password_invalid_user_or_otp(self, mock_has_permission):

        mock_has_permission.return_value = True

        user = User.objects.create_user(
            username='testuser', password='testpassword', email='test@example.com')
        otp = OTP.objects.create(user=user, otp=get_random_string(
            length=4, allowed_chars='1234567890'), otp_type=0, otp_created_at=timezone.now())

        request_data = {
            'email': 'testuser@gmail.com',
            'new_password': 'Newpassword@12345',
            'confirm_password': 'Newpassword@12345',
            'otp': otp.otp,
        }

        request = self.factory.patch(self.url, data=request_data)
        response = ResetPasswordView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Invalid email or OTP')



User = get_user_model()

class TestLoginWithGoogle(unittest.TestCase):

    def setUp(self):
        self.factory=RequestFactory()
        self.view=LoginWithGoogle.as_view()
        self.user_data={
            'email':"testemail@gmail.com",
            'name':"testuser"
        }
        self.error_message="Mocked error message"

   
    @patch("user_management.views.User")
    def test_successful_login_existing_user(self,mock_user):
       
        user_instance = mock_user.objects.get.return_value
        user_instance.email='testemail@gmail.com'
        user_instance.username='testuser'
        user_instance.user_type=1
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        url = reverse('login-with-google')
        request = self.factory.post(url, self.user_data)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Login Successful')
        self.assertEqual(response.data['role'], user_instance.user_type)
       
  
    
   
  
  
    @patch("user_management.views.User.objects.get")
    @patch("user_management.views.User.objects.create_google_user")
    def test_integrity_error(self,mock_create_google_user,mock_user):
      
        mock_user.side_effect=User.DoesNotExist
        mock_create_google_user.side_effect = IntegrityError("Integrity error occurred")
        url = reverse('login-with-google')
        request = self.factory.post(url, self.user_data)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    @patch("user_management.views.User.objects.get")
    @patch("user_management.views.User.objects.create_google_user")
    def test_login_with_google_for_new_user(self,mock_create_google_user,mock_user):
      
        mock_user.side_effect=User.DoesNotExist
        user_instance=mock_create_google_user.return_value
        user_instance.email='testemail@gmail.com'
        user_instance.username='testuser'
        user_instance.user_type=1
        refresh = RefreshToken.for_user(user_instance)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)


      
        url = reverse('login-with-google')
        request = self.factory.post(url, self.user_data)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  
        return super().setUp()



class CurrentOrganizationProfileAPIViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@gmail.com', username='test_username',password='password', user_type=1,status=1,is_register=1)
        self.client = APIClient()
        self.client.login(email='testuser@gmail.com', password='password')

    def test_get_organization_profile(self):
      
        self.client.force_authenticate(user=self.user)
        url = reverse('view-profile') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    @patch('user_management.views.User.objects.get')
    def test_get_organization_exception_profile(self,mock_get_user):
        mock_get_user.side_effect = User.DoesNotExist
        self.user = User.objects.create_user(email='testuser1@gmail.com', username='test1_username',password='password', user_type=0,status=1,is_register=1)
        self.client.force_authenticate(user=self.user)
        url = reverse('view-profile') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        

class UpdateProfileFieldAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', email='test@example.com')
        self.url = reverse('update_profile_field') 
        
    def test_valid_update(self):
        data = {
            'username': 'newusername',
            'contact_number': '8189114417',
            'address': 'New Address,kannur'
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, data, format='json')

    # def test_invalid_user_id(self):
    #     self.client.force_authenticate(user=self.user)
    #     invalid_user_id = 9999
    #     response = self.client.put(f'/api/update-profile/{invalid_user_id}/', {}, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # def test_invalid_data(self):
    #     invalid_data = {
    #         'username': 'sdegf',  # Empty username
    #         'contact_number': '6756',  # Invalid contact number format
    #         'address': 'sdfgs',  # Empty address
    #     }
    #     self.client.force_authenticate(user=self.user)
    #     response = self.client.put(self.url, invalid_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

   
    def test_profile_image_upload(self):
       
        self.client.force_authenticate(user=self.user)
        file_content = b'mock_image_data'
        file_size_mb=8
        profile_image =SimpleUploadedFile('test_image.jpg', file_content, content_type='image/jpeg')

        with patch('user_management.views.User.objects.get') as mock_get_user:
             mock_profile = MagicMock()
             mock_profile.id = self.user.id
             mock_profile.profile_image = 'existing_profile_image_url' 
             mock_get_user.return_value = mock_profile
            
               
           
             response = self.client.put(self.url, {'profile_image': profile_image}, format='multipart')
             self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('os.path.exists', return_value=True)
    @patch('os.remove')
    @patch('user_management.views.User.objects.get')
    def test_remove_profile_image_success(self,mock_get_user,mock_os_remove,mock_os_path):
        self.client.force_authenticate(user=self.user)
       
        mock_os_path.return_value=True
        mock_os_remove.return_value=MagicMock()
        mock_profile = MagicMock()
        mock_profile.id = self.user.id
        mock_profile.profile_image = 'existing_profile_image_url.jpg' 
        mock_get_user.return_value = mock_profile

        response = self.client.put(self.url, {'remove_profile_image': True}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Profile Image removed successfully')


    @patch('os.path.exists', return_value=True)
    @patch('user_management.views.User.objects.get')
    def test_remove_profile_image_failed(self,mock_get_user,mock_os_path):
        self.client.force_authenticate(user=self.user)
       
        mock_os_path.return_value=True
       
        mock_profile = MagicMock()
        mock_profile.id = self.user.id
        mock_profile.profile_image=None
        mock_get_user.return_value = mock_profile

        response = self.client.put(self.url, {'remove_profile_image': True}, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Profile Image not found')


   

    def test_profile_image_size_limit_exceeded(self):
        self.client.force_authenticate(user=self.user)

      
        oversized_image_content = b'A' * (12 * 1024 * 1024) 
        oversized_profile_image = SimpleUploadedFile(
        'large_test_image.jpg', 
        oversized_image_content, 
        content_type='image/jpeg'
    )
        response = self.client.put(self.url, {'profile_image': oversized_profile_image}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'The maximum allowed file size is 10MB')
           
            


   
    



 