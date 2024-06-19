
from django.test import TestCase
from user_management.models import User
from rest_framework.test import APIClient
from user_management.serializers import UserSerializer
from organization_management.views import OrganizationsView,SearchUser,SwitchUserAccountStatus,DeleteUserAccount
from rest_framework import status
from django.urls import reverse
from rest_framework.exceptions import PermissionDenied
from unittest.mock import patch, MagicMock
from .permissions import Admin




class OrganizationsViewTestCase(TestCase):



    def setUp(self):
        self.admin = User.objects.create_user(
            username='testadmin', password='testpassword', email='testadmin1@gmail.com', user_type=0, is_register=1)
       
        
        self.client = APIClient()
        self.view = OrganizationsView.as_view()
        self.url = reverse('organizations')

    def test_organizations_view(self):
         user1 = User.objects.create_user(
            username='user1',
            password='user1password',
            is_register=1,
            email='user1@gmail.com',
            user_type=1
        )

         user2 = User.objects.create_user(
            username='user2',
            password='user2password',
            email='user2@gmail.com',
            is_register=1,
            user_type=1
        )
         self.client.force_authenticate(user=self.admin)
         response = self.client.get(self.url, {'sort_by': 'username', 'ascending': 'true'})
         self.assertEqual(response.status_code, status.HTTP_200_OK)

        
    def test_organizations_view_page_out_of_rage(self):
         
        user1 = User.objects.create_user(
            username='user1',
            password='user1password',
            is_register=1,
            email='user1@gmail.com',
            user_type=1
        )

        user2 = User.objects.create_user(
            username='user2',
            password='user2password',
            email='user2@gmail.com',
            is_register=1,
            user_type=1
        )
       
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {'page':999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], "Page out of range")

    def test_organizations_view_with_invalid_sortby_field(self):
           user1 = User.objects.create_user(
                   username='user1',
                   password='user1password',
                   is_register=1,
                   email='user1@gmail.com',
                   user_type=1
             )

           user2 = User.objects.create_user(
                username='user2',
                password='user2password',
                email='user2@gmail.com',
                is_register=1,
                user_type=1
             )
           self.client.force_authenticate(user=self.admin)
           response = self.client.get(self.url, {'sort_by': 'invalidfield', 'ascending': 'true'})
           self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
           self.assertEqual(response.data, {'errorCode': 'E20001', 'message': 'Invalid sort field'})
     

  

    @patch('organization_management.views.Admin.has_permission')
    def test_permission_denied(self,mock_has_permission):
        mock_has_permission.return_value = False
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_organizations_view_no_permission(self):
       user1 =  User.objects.create_user(
            username='nouser',
            password='nouserpassword',
            email='nouser@gmail.com',
            is_register=0,
            user_type=1
        )
   
       response = self.client.get(self.url, {'sort_by': 'username', 'ascending': 'true'})
       self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_organizations_view_permission_denied(self):
       user1 =  User.objects.create_user(
            username='nouser',
            password='nouserpassword',
            email='nouser@gmail.com',
            is_register=0,
            user_type=1
        )
       self.client.force_authenticate(user=user1)
       response = self.client.get(self.url, {'sort_by': 'username', 'ascending': 'true'})
       self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
       self.assertEqual(response.data['message'], "You do not have permission access this View")
    
     
     

    
       
        


    

class SearchUserViewTestCase(TestCase):
    
    def setUp(self):
        self.admin = User.objects.create_user(
            username='testadmin', password='testpassword', email='testadmin2@gmail.com', user_type=0, is_register=1)
       
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
        self.view = SearchUser.as_view()
        self.url = reverse('search_user')

    def test_search_user_view(self):
      
        user1 = User.objects.create_user(
            username='testuser1',
            password='user1password',
            email='testuser1@gmail.com',
            user_type=1,
            is_register=1
        )

        user2 = User.objects.create_user(
            username='testuser2',
            password='user2password',
            email='testuser2@gmail.com',
            user_type=1,
            is_register=1
        )

        response = self.client.get(self.url, {'search': 'testuser1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serialized_data = UserSerializer([user1], many=True).data
        self.assertEqual(response.data['results'], serialized_data)

   


class SwitchUserAccountStatusTestCase(TestCase):

    def setUp(self):
       
        self.admin = User.objects.create_user(
            username='testadmin',
            password='testpassword',
            email='testadmin3@gmail.com',
            user_type=0,
            is_register=1
        )

 
    

        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
       
        self.view = SwitchUserAccountStatus.as_view()

    def test_switch_user_account_status(self):
        user = User.objects.create_user(
            username='testuser1',
            password='userpassword',
            email='testuser1@gmail.com',
            user_type=1,
            is_register=1,
            status=1 
        )
      
        url = reverse('switch_user_account_status', kwargs={'pk':user.id})
        self.assertEqual(user.status, 1)
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.status, 0)
        self.assertEqual(response.data["message"], "The user has been blocked")


    def test_switch_user_account_status_unblock(self):
        user = User.objects.create_user(
            username='testuser2',
            password='userpassword',
            email='testuser2@gmail.com',
            user_type=1,
            is_register=1,
            status=0 
        )
      
        url = reverse('switch_user_account_status', kwargs={'pk':user.id})
        self.assertEqual(user.status, 0)
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.status, 1)
        self.assertEqual(response.data["message"], "The user has been unblocked")


    def test_switch_user_account_status_nonexistent_user(self):

        url = reverse('switch_user_account_status', kwargs={'pk':999})
        response = self.client.put(url)  

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["message"], "No user found")

    def test_switch_user_account_status_invalid_user(self):
        
        user = User.objects.create_user(
            username='invaliduser',
            password='invalidpassword',
            email='invaliduser@gmail.com',
            user_type=2,
            is_register=1,
            status=1
        )

        url = reverse('switch_user_account_status', kwargs={'pk':user.id})
        response = self.client.put(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Invalid user")

class DeleteUserAccountTestCase(TestCase):

    def setUp(self):
       
        self.admin = User.objects.create_user(
            username='testadmin',
            password='testpassword',
            email='testadmin@gmail.com',
            user_type=0,
            is_register=1
        )

        
       

        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
        self.view = DeleteUserAccount.as_view()
        
      

    def test_delete_user_account(self):

        user = User.objects.create_user(
            username='testuser3',
            password='userpassword',
            email='testuser3@gmail.com',
            user_type=1,
            is_register=1
        )
        url = reverse('delete_user_account', kwargs={'pk':user.id})
        self.assertEqual(user.is_register, 1)
        response = self.client.put(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.is_register, 0)
        self.assertEqual(response.data["message"], "The user has been successfully deleted")

    def test_delete_user_account_nonexistent_user(self):

        url = reverse('delete_user_account', kwargs={'pk':999})
        response = self.client.put(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["message"], "No user found")

    def test_delete_user_account_invalid_user(self):
      
        user = User.objects.create_user(
            username='invaliduser',
            password='invalidpassword',
            email='invaliduser@gmail.com',
            user_type=2,  
            is_register=1
        )

        url = reverse('delete_user_account', kwargs={'pk':user.id})
        response = self.client.put(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Invalid user")








