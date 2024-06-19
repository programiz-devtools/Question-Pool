from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from subject_management.models import Subject
from exam_management.models import Exam,ExamSubjects
from subject_management.models import Subject
from exam_management.models import Exam, ExamSubjects
from user_management.models import User
from candidatemanagement.models import Candidate,ExamCandidate
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.conf import settings
import jwt
from django.http import HttpResponse
import unittest
from unittest.mock import patch
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpRequest
from .views import CheckTokenExpirationView
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from django.core import mail
from .messages import E60010,E60011,E60013,E70001,E70002,E70003,E70004,E70005,E70006,E70008



class SendExamLinkViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="testuser",
            password="testuser",
            email="testuser1@gmail.com",
            user_type=1,
            is_register=1,
        )
        
        self.exam = Exam.objects.create(
            scheduled_time=timezone.now() + timedelta(days=1),
            organization=self.user,
        )
        self.candidate = Candidate.objects.create(id=1, email="example@gmail.com",exam=self.exam)
        self.url = reverse("access-link")
    def test_send_exam_link(self):
        data = {
            "candidateId": [self.candidate.id],
            "examid": self.exam.id,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_send_exam_link_invalid_exam_id(self):
        data = {
            "candidateId": [self.candidate.id],
            "examid": 2,
        }

        response = self.client.post(self.url, data, format="json")

        expected_response = {'message': E60010, 'errorCode': 'E60010'}
        
        self.assertEqual(response.data, expected_response)

    def test_send_exam_link(self):
        data = {
            "candidateId": [self.candidate.id],
            "examid": self.exam.id,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_send_exam_link_invalid_candidate_id(self):
        data = {
            "candidateId": [99],
            "examid": self.exam.id,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class CheckTokenExpirationViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse("check-token-expiration")

    def test_token_not_expired(self):
        exp_time = datetime.utcnow() + timedelta(hours=1)
        token = jwt.encode(
            {
                "active_time": int(datetime.utcnow().timestamp()),
                "exp": int(exp_time.timestamp()),
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )

        response = self.client.post(self.url, {"token": token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["expired"], False)

    @patch("candidatemanagement.views.jwt.decode")
    def test_expired_signature_error_response(self, mock_jwt_decode):
        mock_jwt_decode.side_effect = jwt.ExpiredSignatureError("Token has expired")

        client = APIClient()
        response = client.post(self.url, data={"token": "expired_token"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"expired": True})

    @patch("candidatemanagement.views.jwt.decode")
    def test_invalid_token_error(self, mock_jwt_decode):
        mock_jwt_decode.side_effect = jwt.InvalidTokenError("Invalid token")

        client = APIClient()
        response = client.post(self.url, data={"token": "invalid_token"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import (
    Candidate,
) 


class ExamCandidateListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testuser",
            email="testuser@gmail.com",
            user_type=1,
            is_register=1,
        )

        self.subject = Subject.objects.create(
            subject_name="testsubject", question_count=20
        )

        self.exam = Exam.objects.create(
            name="Test Exam",
            scheduled_time="2026-01-18T12:00:00Z",
            organization=self.user,
        )
        self.exam2 = Exam.objects.create(
            name="Test Exam2",
            scheduled_time="2026-02-18T12:00:00Z",
            organization=self.user,
        )


        Candidate.objects.create(exam_id=self.exam.id, email="test@example.com")
        Candidate.objects.create(exam_id=self.exam.id, email="another@example.com")
        self.client = APIClient()

    def test_get_candidate_list(self):
        url = reverse("candidates-by-subject", kwargs={"exam_id": self.exam.id})
        print("url :", url)
        response = self.client.get(url)
        

        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

    def test_get_exam_with_no_candidates(self):
        url = reverse("candidates-by-subject", kwargs={"exam_id": self.exam2.id})
        print("url :", url)
        response = self.client.get(url)
        print("response for no candidate----------:", response)
        expected_response=E70001

        # Assert that the response status code is 200 OK
        self.assertEqual(response.data,expected_response)



    def test_search_candidates(self):

        # Define the URL for your view, replace 'your_exam_id' with the actual exam ID
        url = reverse("candidates-by-subject", kwargs={"exam_id": self.exam.id})

        # Add a query parameter for search
        response = self.client.get(url, {"searchparam": "test@example.com"})
        print("response", response)
        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response contains only the candidate matching the search parameter
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["email"], "test@example.com")


class ExamCandidateCreateViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testuser",
            email="testuser@gmail.com",
            user_type=1,
            is_register=1,
        )
        self.subject = Subject.objects.create(
            subject_name="testsubject", question_count=20
        )
        self.exam = Exam.objects.create(
            name="Test Exam",
            scheduled_time="2026-01-18T12:00:00Z",
            organization=self.user,
        )
        self.exam_subject = ExamSubjects.objects.create(
            exam=self.exam,
            subject=self.subject,
            time_duration=120,  # Set the time duration as needed
            pass_percentage=70.0,  # Set the pass percentage as needed
            difficulty_level=2,  # Choose the difficulty level (1: easy, 2: medium, 3: difficult)
            question_count=50,  # Set the initial question count as needed
        )

    def test_create_exam_candidate(self):
        url = reverse("exam-candidate-add", kwargs={"exam_id": self.exam.id})
        data = {"email": "test@example.com"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if the candidate and exam candidate were created
        # candidate = Candidate.objects.get(email=data["email"], exam=self.exam)

    def test_create_exam_candidate_existing_email(self):
        # Create a candidate with the same email
        existing_candidate = Candidate.objects.create(
            email="test@example.com", exam=self.exam
        )

        url = reverse("exam-candidate-add", kwargs={"exam_id": self.exam.id})
        data = {"email": existing_candidate.email}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Candidate with the given email already exists for this exam",
            response.data["message"],
        )

class AddCandidateNameViewTestCase(TestCase):
    def setUp(self):
        self.client=APIClient()
        

    @patch("candidatemanagement.views.jwt.decode")
    def test_update_cabdidate_name(self,mock_decode):
        candidate = Candidate.objects.create(name="Candidate name")
        mock_decode.return_value = {"candidateId":candidate.id}
        url=reverse("add-candidate-name")
        new_name = 'Updated name'
        data = {"token":"dummy_token","name":new_name}
        response = self.client.post(url,data,format="json")
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Name Updated successfully")
        updated_candidate = Candidate.objects.get(id=candidate.id)
        self.assertEqual(updated_candidate.name, new_name)

    @patch("candidatemanagement.views.jwt.decode")
    def test_add_candidate_name(self, mock_decode):
        candidate = Candidate.objects.create(name=None)
        mock_decode.return_value = {"candidateId":candidate.id}
        url = reverse("add-candidate-name")  
        new_name = "New Name"
        data = {"token": "dummy_token", "name": new_name}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Name Added successfully")
        added_candidate = Candidate.objects.get(id=candidate.id)
        self.assertEqual(added_candidate.name, new_name)


    @patch("candidatemanagement.views.jwt.decode")
    def test_empty_name_field(self, mock_decode):
        candidate = Candidate.objects.create(name="Candidate name")
        mock_decode.return_value = {"candidateId": candidate.id}
        url = reverse("add-candidate-name") 
        data = {"token": "dummy_token"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        unchanged_candidate = Candidate.objects.get(id=candidate.id)
        self.assertEqual(unchanged_candidate.name, "Candidate name")


class SendResultEmailsViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testuser', email='testuser@gmail.com', user_type=1, is_register=1)
        self.exam=Exam.objects.create(name="sample exam", scheduled_time= "2026-01-18T12:00:00Z",organization_id=self.user.id)
        self.candidate = Candidate.objects.create(id=1, name="Test Candidate", email="test@example.com", exam_id=self.exam.id,status=4)

        

    def test_send_result_emails_view(self):

        data = [self.candidate.id]

        url = reverse('send_emails')
        response = self.client.post(url, data, format='json')
        print("test send email reponse : ",response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.subject, f"Result of {self.exam.name}")
        self.assertIn('Please find attached your exam result PDF', sent_email.body)
        self.assertEqual(sent_email.from_email, 'aexamate@gmail.com')
        self.assertEqual(sent_email.to, ['test@example.com'])
        self.assertEqual(sent_email.attachments[0][0], f'{self.candidate.id}_result.pdf')
        self.assertEqual(sent_email.attachments[0][2], 'application/pdf')


class ExamTokenDecodeViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testuser', email='testuser@gmail.com', user_type=1, is_register=1)
        self.candidate = Candidate.objects.create(id=1, name="Test Candidate", status=1)  # Assuming status 1 means registered
        self.exam=Exam.objects.create(name="sample exam", scheduled_time= "2026-01-18T12:00:00Z",organization_id=self.user.id)
        self.token_payload = {
            'candidateId': self.candidate.id,
            'exam_id': self.exam.id
        }
        self.token = jwt.encode(self.token_payload, settings.SECRET_KEY, algorithm='HS256')

    def test_exam_token_decode_view(self):
        # Mock the jwt.decode function to return the token payload


        # Send the POST request to the view
        url = reverse('token_decode')
        response = self.client.post(url, {'exam_token': self.token}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert response data
        expected_data = {
            'candidate_id': self.candidate.id,
            'candidate_name': self.candidate.name,
            'exam_id': self.exam.id,
            'exam_name': self.exam.name,
            'status': 1 
        }
        self.assertEqual(response.data, expected_data)

        # Assert that the candidate's status is updated to 2
        self.candidate.refresh_from_db()
        self.assertEqual(self.candidate.status, 2)

class EvaluateExamCandidateListViewTest(APITestCase):

    def setUp(self):
          # Create user
        self.user = User.objects.create_user(
            username="testuser",
            password="testuser",
            email="testuser@gmail.com",
            user_type=1,
            is_register=1,
        )
        # Create an exam
        self.exam = Exam.objects.create(
            name="Test Exam",
            scheduled_time="2026-01-18T12:00:00Z",
            organization=self.user,
        )

        # Create some subjects
        self.subject1 = Subject.objects.create(subject_name="Math", question_count=10, exam_count=1)
        self.subject2 = Subject.objects.create(subject_name="Science", question_count=20, exam_count=1)
 # Create exam subjects with different difficulty levels
        self.exam_subject1 = ExamSubjects.objects.create(
            exam=self.exam,
            subject=self.subject1,
            time_duration=60,
            pass_percentage=0.5,
            difficulty_level=1,  # Easy
            question_count=10,
        )
        self.exam_subject2 = ExamSubjects.objects.create(
            exam=self.exam,
            subject=self.subject2,
            time_duration=90,
            pass_percentage=0.7,
            difficulty_level=2,  # Medium
            question_count=20,
        )

        # Create exam candidates with different statuses and start/end times
        self.candidate1 = ExamCandidate.objects.create(
            candidate=Candidate.objects.create(name="John Doe", email="john.doe@example.com", exam=self.exam, status=1),
            exam_subject=self.exam_subject1,
            start_time="2024-02-26T10:00:00",
            end_time="2024-02-26T11:00:00",
        )
        self.candidate2 = ExamCandidate.objects.create(
            candidate=Candidate.objects.create(name="Jane Doe", email="jane.doe@example.com", exam=self.exam, status=2),
            exam_subject=self.exam_subject2,
            start_time="2024-02-26T12:00:00",
            end_time=None,  # Incomplete exam
        )
        self.candidate3 = ExamCandidate.objects.create(
            candidate=Candidate.objects.create(name="Mary Smith", email="mary.smith@example.com", exam=self.exam, status=3),
            exam_subject=self.exam_subject1,
            exam_subject_mark=80,
            start_time="2024-02-26T09:00:00",
            end_time="2024-02-26T09:45:00",
        )
        self.candidate4 = ExamCandidate.objects.create(
            candidate=Candidate.objects.create(name="Peter Johnson", email="peter.johnson@example.com", exam=self.exam, status=3),
            exam_subject=self.exam_subject2,
            exam_subject_mark=90,
            start_time="2024-02-26T11:30:00",
            end_time="2024-02-26T12:30:00",
        )

    def test_get_list_all_candidates(self):
        url = reverse("evaluated-candidate-list", kwargs={"exam_id": self.exam.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
    def test_get_list_filter_by_search_query(self):
        url = reverse("evaluated-candidate-list", kwargs={"exam_id": self.exam.id})
        response = self.client.get(url+"?search=ma")
        self.assertEqual(response.status_code, 200)
        
