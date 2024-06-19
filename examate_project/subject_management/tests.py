from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Subject
from question_management.models import Questions
from user_management.models import User

class SubjectCreateAPIViewTest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(email='admin@gmail.com', password='admin_password', user_type=0)

    def test_create_subject(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('subject-create')
        data = {'subject_name': 'Test Subject'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subject.objects.count(), 1)
        self.assertEqual(Subject.objects.get().subject_name, 'Test Subject')
    def test_create_subject_unauthorized(self):
        url = reverse('subject-create')
        data = {'subject_name': 'Test Subject'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    def test_create_existing_subject(self):
        self.client.force_authenticate(user=self.admin_user)
        Subject.objects.create(subject_name='Existing Subject')
        url = reverse('subject-create')
        data = {'subject_name': 'Existing Subject'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
    def test_create_invalid_subject(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('subject-create')
        data = {'subject_name': '+ test'}  
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_create_subject_error(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('subject-create')
        data = {'subject_name':'' }  
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

   

class SubjectListAPIViewTest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(email='admin@gmail.com', password='admin_password', user_type=0)
        Subject.objects.create(subject_name='React')
        Subject.objects.create(subject_name='Python')
        Subject.objects.create(subject_name='Java')

    def test_list_all_subjects(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('subject-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  
    
    def test_list_subjects_pagination(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('subject-list')
        response = self.client.get(url, {'page': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('next' in response.data) 
        self.assertTrue('previous' in response.data)  
        self.assertEqual(len(response.data['results']), 3)


class SubjectSearchViewTest(APITestCase):
   
    def setUp(self):
        self.admin_user = User.objects.create_user(email='admin@gmail.com', password='admin_password', user_type=0)
        self.subject1 = Subject.objects.create(subject_name='React' )
        self.subject2 = Subject.objects.create(subject_name='Python')
        self.subject3 = Subject.objects.create(subject_name='Java')

    def test_search_existing_subject(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('subject-search') 
        data = {'search': 'Java'}
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['subject_name'], 'Java')
    def test_search_non_existing_subject(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('subject-search')
        data = {'search': 'CPP'}
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'No Matching Subject found')
    def test_no_search_query_provided(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('subject-search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3) 
class SubjectDeleteViewTest(APITestCase):
    def setUp(self):
        self.subject = Subject.objects.create(subject_name='Test Subject')
        self.admin_user = User.objects.create_user(email='admin@gmail.com', password='admin_password', user_type=0)

    def test_delete_existing_subject(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('subject-delete', kwargs={'id': self.subject.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Subject.objects.filter(id=self.subject.id).exists())

    def test_delete_existing_subject_unauthorized(self):
        url = reverse('subject-delete', kwargs={'id': self.subject.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_delete_nonexistent_subject(self):
        self.client.force_authenticate(user=self.admin_user)
        max_id = Subject.objects.all().order_by('-id').first().id
        nonexistent_id = max_id + 1 if max_id else 1
        url = reverse('subject-delete', kwargs={'id': nonexistent_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Subject not Found')
