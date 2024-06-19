from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Feedback
from .serializers import FeedbackSerializer
from user_management.models import User
from .serializers import ExamSerializer
from subject_management.models import Subject
from .views import ExamCreationView, generate_questions_for_subject,get_difficulty_level_value
from .models import Exam, ExamQuestions, ExamSubjects
from unittest import mock
from rest_framework.exceptions import PermissionDenied
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import Exam
from user_management.models import User
from subject_management.models import Subject
from question_management.models import Questions, QuestionOptions, FreeAnswers
from candidatemanagement.models import Candidate,ExamCandidate
from ticket_management.models import Ticket
import jwt
from django.utils import timezone
import unittest



class ExamCreationViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testuser', email='testuser@gmail.com', user_type=1, is_register=1)

        self.subject = Subject.objects.create(
            subject_name='testsubject',
            question_count=20
        )

        self.subject2 = Subject.objects.create(
            subject_name='testsubject2',
            question_count=20
        )

        self.subject3 = Subject.objects.create(
            subject_name='testsubject3',
            question_count=20
        )

        self.subject4 = Subject.objects.create(
            subject_name='testsubject4',
            question_count=20
        )

        self.client = APIClient()
        self.view = ExamCreationView.as_view()
        self.url = reverse('create-exam')

    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_create_exam_success(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        mock_questions_filter.return_value = MagicMock()
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Test Exam1",
            "scheduled_time": "2026-01-18T12:00:00Z",
            "instructions": "Read carefully and write more",
            "status":0,
            "subjects": [
                {
                    "subject": self.subject.id,
                    "question_count": 5,
                    "time_duration": 30,
                    "pass_percentage": 70,
                    "difficulty_level": 2
                },{
                    "subject":self.subject2.id,
                    "question_count": 5,
                    "time_duration": 30,
                    "pass_percentage": 70,
                    "difficulty_level": 2
                },

            ]
        }
        response = self.client.post(self.url, data, format='json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Exam Created Successfully')

    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_create_exam_success_with_status_0_and_no_subjects_data(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        mock_questions_filter.return_value = MagicMock()
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Test Exam1",
            "scheduled_time": "2026-01-18T12:00:00Z",
            "instructions": "Read carefully and write more",
            "status":0,
            "subjects": [
               
            ]
        }
        response = self.client.post(self.url, data, format='json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Exam Created Successfully')

    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_empty_field_on_publish(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        mock_questions_filter.return_value = MagicMock()
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Test Exam1",
            "scheduled_time": "2026-01-18T12:00:00Z",
            "instructions": "Read carefully and write more",
            "status":1,
             "subjects": [
        {
            "subject": self.subject.id,
            "time_duration":10,
            "pass_percentage":10,
            "difficulty_level": 2,
            "question_count": 1
        },
         {
            "subject": "",
            "time_duration":10,
            "pass_percentage":10,
            "difficulty_level": 2,
            "question_count": 1
        }
       
    ]
        }
        response = self.client.post(self.url, data, format='json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Please provide a subject')

  



    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_publish_exam(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        mock_questions_filter.return_value = MagicMock()
        self.client.force_authenticate(user=self.user)
        user_ticket = Ticket.objects.create(status=1,organisation=self.user)
        data = {
            "name": "Test Exam1",
            "scheduled_time": "2026-01-18T12:00:00Z",
            "instructions": "Read carefully and write more",
            "status":1,
            "subjects": [
                {
                    "subject": self.subject.id,
                    "question_count": 5,
                    "time_duration": 30,
                    "pass_percentage": 70,
                    "difficulty_level": 2
                },

            ]
        }
        response = self.client.post(self.url, data, format='json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Exam Published Successfully')

    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_publish_exam_ticket_validation_error(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        mock_questions_filter.return_value = MagicMock()
        self.client.force_authenticate(user=self.user)
      
        data = {
            "name": "Test Exam1",
            "scheduled_time": "2026-01-18T12:00:00Z",
            "instructions": "Read carefully and write more",
            "status":1,
            "subjects": [
                {
                    "subject": self.subject.id,
                    "question_count": 5,
                    "time_duration": 30,
                    "pass_percentage": 70,
                    "difficulty_level": 2
                },

            ]
        }
        response = self.client.post(self.url, data, format='json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Insufficient ticket:Please purchase 1 ticket')

    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_publish_exam_ticket_validation_errors(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        mock_questions_filter.return_value = MagicMock()
        self.client.force_authenticate(user=self.user)
      
        data = {
            "name": "Test Exam1",
            "scheduled_time": "2026-01-18T12:00:00Z",
            "instructions": "Read carefully and write more",
            "status":1,
            "subjects": [
                {
                    "subject": self.subject.id,
                    "question_count": 15,
                    "time_duration": 30,
                    "pass_percentage": 70,
                    "difficulty_level": 2
                },

            ]
        }
        response = self.client.post(self.url, data, format='json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Insufficient tickets:Please purchase 2 more additional tickets')


    @patch('exam_management.views.Questions.objects.filter')
    def test_create_exam_invalid_data(self, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        self.client.force_authenticate(user=self.user)
        invalid_data = {
            'name': 'Test Exam',
            'scheduled_time': '2026-01-18T12:00:00Z',
            "instructions": "Read carefully",
            "status":0,
            'subjects': [
                    {
                        'subject': self.subject.id,
                        'question_count': 30,
                        'time_duration': 60,
                        'pass_percentage': 90,
                        'difficulty_level': 1,
                    },
            ]
        }

        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['message'], f"Question count for subject {self.subject.subject_name} exceeds the available questions")

    @patch('exam_management.views.Questions.objects.filter')
    def test_create_exam_invalid_name(self, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        self.client.force_authenticate(user=self.user)
        invalid_data = {
            'name': '',
            'scheduled_time': '2025-01-18T12:00:00Z',
            'instructions': "xxxx",
            "status":0,
            'subjects': [
                {
                    'subject': self.subject.id,
                    'question_count': 3,
                    'time_duration': 60,
                    'pass_percentage': 90,
                    'difficulty_level': 1,
                },
            ]
        }

        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'],
                         "Name field cannot be blank")

    @patch('exam_management.views.Questions.objects.filter')
    def test_create_exam_with_past_scheduled_time(self, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        self.client.force_authenticate(user=self.user)
        invalid_data = {
            'name': 'TestExam',
            'scheduled_time': '2023-01-18T12:00:00Z',
            'instructions': "Instruction 1",
            "status":0,
            'subjects': [
                {
                    'subject': self.subject.id,
                    'question_count': 30,
                    'time_duration': 60,
                    'pass_percentage': 90,
                    'difficulty_level': 1,
                },
            ]
        }

        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['message'], "Scheduled time must be in the future")

    @patch('exam_management.views.Questions.objects.filter')
    def test_create_exam_with_more_than_100_pass_percentage(self, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        self.client.force_authenticate(user=self.user)
        invalid_data = {
            'name': 'ExamateExam',
            'scheduled_time': '2025-01-18T12:00:00Z',
            'instructions': "Read Carefully",
            "status":0,
            'subjects': [
                {
                    'subject': self.subject.id,
                    'question_count': 20,
                    'time_duration': 60,
                    'pass_percentage': 101,
                    'difficulty_level': 1,
                },
            ]
        }

        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['message'], "Pass percentage must be between 0 and 100")

    @patch('exam_management.views.Questions.objects.filter')
    def test_create_exam_with_negative_time_duration(self, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        self.client.force_authenticate(user=self.user)
        invalid_data = {
            'name': 'ExamateExam',
            'scheduled_time': '2025-01-18T12:00:00Z',
            'instructions': "Read Carefully",
            "status":0,
            'subjects': [
                {
                    'subject': self.subject.id,
                    'question_count': 30,
                    'time_duration': -60,
                    'pass_percentage': 101,
                    'difficulty_level': 1,
                },
            ]
        }

        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['message'], "Time duration cannot be negative")

    @patch('exam_management.views.Questions.objects.filter')
    def test_create_exam_no_questions_for_difficulty_level(self, mock_questions_filter):
        mock_questions_filter.return_value.exists.side_effect = [True, False]

        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Test Exam",
            "scheduled_time": "2025-01-18T12:00:00Z",
            "instructions": "Read carefully",
            "status":0,
            "subjects": [
                {
                    "subject": self.subject.id,
                    "question_count": 5,
                    "time_duration": 30,
                    "pass_percentage": 70,
                    "difficulty_level": 2
                },
            ]
        }

        response = self.client.post(self.url, data, format='json')
        difficulty_level_value = get_difficulty_level_value(2)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['message'], f"No questions available for {difficulty_level_value} level for subject {self.subject.subject_name}")
        
    @patch('exam_management.views.Questions.objects.filter')
    def test_create_exam_no_questions_for_none_difficulty_level(self, mock_questions_filter):
        mock_questions_filter.return_value.exists.side_effect = [True, False]

        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Test Exam",
            "scheduled_time": "2025-01-18T12:00:00Z",
            "instructions": "Read carefully",
            "status":0,
            "subjects": [
                {
                    "subject": self.subject.id,
                    "question_count": 5,
                    "time_duration": 30,
                    "pass_percentage": 70,
                    "difficulty_level": ""
                },
            ]
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['message'], f"No questions available for None level for subject {self.subject.subject_name}")

    @patch('exam_management.views.Questions.objects.filter')
    def test_create_exam_no_questions_for_subject(self, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = False

        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Test Exam",
            "scheduled_time": "2025-01-18T12:00:00Z",
            "instructions": "Read carefully",
            "status":0,
            "subjects": [
                {
                    "subject": self.subject.id,
                    "question_count": 5,
                    "time_duration": 30,
                    "pass_percentage": 70,
                    "difficulty_level": 2
                },
            ]
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['message'], f"No questions available for subject {self.subject.subject_name}")

    def test_organizations_view_permission_denied(self):
        user1 = User.objects.create_user(
            username='nouser',
            password='nouserpassword',
            email='nouser@gmail.com',
            is_register=0,
            user_type=0
        )
        data = {
            "name": "Test Exam",
            "scheduled_time": "2025-01-18T12:00:00Z",
            "instructions": "Read carefully",
            "organization_id": user1.id,
            "status":0,
            "subjects": [
                {
                    "subject": self.subject.id,
                    "question_count": 5,
                    "time_duration": 30,
                    "pass_percentage": 70,
                    "difficulty_level": 2
                },
            ]
        }
        self.client.force_authenticate(user=user1)
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['message'], "You do not have permission access this View")

    def test_organizations_view_no_permission(self):

        data = {
            "name": "Test Exam",
            "scheduled_time": "2025-01-18T12:00:00Z",
            "instructions": "Read carefully",
            "organization_id": 4,
            "status":0,
            "subjects": [
                {
                    "subject": self.subject.id,
                    "question_count": 5,
                    "time_duration": 30,
                    "pass_percentage": 70,
                    "difficulty_level": 2
                },
            ]
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_create_exam_with_no_subject(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        mock_questions_filter.return_value = MagicMock()
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Test Exam",
            "scheduled_time": "2026-01-18T12:00:00Z",
            "instructions": "Read carefully and write more",
            "status":1,
            "subjects": []
        }
        response = self.client.post(self.url, data, format='json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['message'], 'At least one subject is required for exam')

    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_create_exam_with_repeat_subject(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        mock_questions_filter.return_value = MagicMock()
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Test Exam1",
            "scheduled_time": "2026-01-18T12:00:00Z",
            "instructions": "Read carefully and write more",
            "status":0,
            "subjects": [
                {
                    "subject": self.subject.id,
                    "question_count": 5,
                    "time_duration": 30,
                    "pass_percentage": 70,
                    "difficulty_level": 2
                },
                {
                    "subject": self.subject.id,
                    "question_count": 5,
                    "time_duration": 30,
                    "pass_percentage": 70,
                    "difficulty_level": 2
                }

            ]
        }
        response = self.client.post(self.url, data, format='json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['message'], f"Duplicate subject {self.subject.subject_name} found in the request")

    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_create_exam_with_more_than_three_subjects(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        mock_questions_filter.return_value = MagicMock()
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Test Exam1",
            "scheduled_time": "2026-01-18T12:00:00Z",
            "instructions": "Read carefully and write more",
            "status":0,
            "subjects": [
                {
                    "subject": self.subject.id,
                    "question_count": 5,
                    "time_duration": 30,
                    "pass_percentage": 70,
                    "difficulty_level": 2
                },
                {
                    "subject": self.subject2.id,
                    "question_count": 5,
                    "time_duration": 30,
                    "pass_percentage": 70,
                    "difficulty_level": 2
                },
                {
                    "subject": self.subject3.id,
                    "question_count": 5,
                    "time_duration": 30,
                    "pass_percentage": 70,
                    "difficulty_level": 2
                },
                {
                    "subject": self.subject4.id,
                    "question_count": 5,
                    "time_duration": 30,
                    "pass_percentage": 70,
                    "difficulty_level": 2
                }

            ]
        }
        response = self.client.post(self.url, data, format='json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['message'], "Cannot create more than 3 subjects for a exam")


class ExamUpdationViewTestCases(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testuser', email='testuser@gmail.com', user_type=1, is_register=1)
        self.exam = Exam.objects.create(name='Test Exam', scheduled_time='2024-02-01T12:00:00Z',status=0,
                                        instructions='Instruction 1,Instruction 2', organization_id=self.user.id)
        self.subject1 = Subject.objects.create(
            subject_name='Subject 1', question_count=21)
        self.subject2 = Subject.objects.create(
            subject_name='Subject 2', question_count=20)
        self.subject3 = Subject.objects.create(
            subject_name='Subject 3', question_count=20)
        self.subject4 = Subject.objects.create(
            subject_name='Subject 4', question_count=20)
        self.exam_subject1 = ExamSubjects.objects.create(
            exam=self.exam, subject=self.subject1, time_duration=60, pass_percentage=70, difficulty_level=1, question_count=20)
        self.exam_subject2 = ExamSubjects.objects.create(
            exam=self.exam, subject=self.subject2, time_duration=45, pass_percentage=80, difficulty_level=1, question_count=20)
        self.client = APIClient()

    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_exam_updation_successful_response(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        data = {
            "name": "Updated Exam name",
            "scheduled_time": '2025-02-01T14:00:00Z',
            "instructions": 'Updated Instruction 1,Updated Instruction 2',
            "status":0,
            "subjects": [
                {"subject": self.subject1.id, "time_duration": 75,
                    "pass_percentage": 65, "difficulty_level": 1, "question_count": 20},
                {"subject": self.subject3.id, "time_duration": 50,
                    "pass_percentage": 75, "difficulty_level": 1, "question_count": 20}
            ]
        }
        self.client.force_authenticate(user=self.user)
        url = reverse('update-exam', args=[self.exam.id])
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, {"message": "Exam Updated Successfully"})
    
    @patch('exam_management.views.Questions.objects.filter')
    def test_update_exam_no_questions_for_none_difficulty_level(self, mock_questions_filter):
        mock_questions_filter.return_value.exists.side_effect = [True, False]

        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Test Exam",
            "scheduled_time": "2025-01-18T12:00:00Z",
            "instructions": "Read carefully",
            "status":0,
            "subjects": [
                {
                    "subject": self.subject1.id,
                    "question_count": 5,
                    "time_duration": 30,
                    "pass_percentage": 70,
                    "difficulty_level": ""
                },
            ]
        }
        url = reverse('update-exam', args=[self.exam.id])
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['message'], f"No questions available for None level for subject {self.subject1.subject_name}")

        

    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_exam_updation_no_questions(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = False
        data = {
            "name": "Updated Exam name",
            "scheduled_time": '2025-02-01T14:00:00Z',
            "instructions": 'Updated Instruction 1,Updated Instruction 2',
            "status":0,
            "subjects": [
                {"subject": self.subject1.id, "time_duration": 75,
                    "pass_percentage": 65, "difficulty_level": 1, "question_count": 20},
                {"subject": self.subject3.id, "time_duration": 50,
                    "pass_percentage": 75, "difficulty_level": 1, "question_count": 20},
                {"subject": "", "time_duration": 50,
                    "pass_percentage": 75, "difficulty_level": 1, "question_count": 20}
            ]
        }
        self.client.force_authenticate(user=self.user)
        url = reverse('update-exam', args=[self.exam.id])
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['message'], f"No questions available for subject {self.subject1.subject_name}")

    # @patch('exam_management.views.Questions.objects.filter')
    # @patch('exam_management.views.ExamQuestions.objects.create')
    # def test_exam_updation_successful_response_on_publish_with_different_question_count(self, mock_create_exam_questions, mock_questions_filter):
    #     mock_questions_filter.return_value.exists.return_value = True
    #     data = {
    #         "name": "Updated Exam name",
    #         "scheduled_time": '2025-02-01T14:00:00Z',
    #         "instruction": 'Updated Instruction 1,Updated Instruction 2',
    #         "status":1,
    #         "subjects": [
    #             {"subject": self.subject1.id, "time_duration": 75,
    #                 "pass_percentage": 65, "difficulty_level": 1, "question_count": 21},
    #             {"subject": self.subject3.id, "time_duration": 50,
    #                 "pass_percentage": 75, "difficulty_level": 1, "question_count": 20}
    #         ]
    #     }
    #     self.client.force_authenticate(user=self.user)
    #     url = reverse('update-exam', args=[self.exam.id])
    #     response = self.client.put(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(
    #         response.data, {"message": "Exam Updated and Published Successfully"})
        
    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_exam_updation_successful_response_status_publish(self, mock_create_exam_questions, mock_questions_filter):
        for _ in range(5):
              user_ticket = Ticket.objects.create(status=1, organisation=self.user)

        mock_questions_filter.return_value.exists.return_value = True
        data = {
            "name": "Updated Exam name",
            "scheduled_time": '2025-02-01T14:00:00Z',
            "instructions": 'Updated Instruction 1,Updated Instruction 2',
            "status":1,
            "subjects": [
                {"subject": self.subject1.id, "time_duration": 75,
                    "pass_percentage": 65, "difficulty_level": 1, "question_count": 20},
                {"subject": self.subject3.id, "time_duration": 50,
                    "pass_percentage": 75, "difficulty_level": 1, "question_count": 20}
            ]
        }
        self.client.force_authenticate(user=self.user)
        url = reverse('update-exam', args=[self.exam.id])
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, {"message": "Exam Updated and Published Successfully"})
        

    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_exam_updation_with_subject_with_question_count_0_response_status_publish(self, mock_create_exam_questions, mock_questions_filter):
        for _ in range(5):
              user_ticket = Ticket.objects.create(status=1, organisation=self.user)

        mock_questions_filter.return_value.exists.return_value = True
        data = {
            "name": "Updated Exam name",
            "scheduled_time": '2025-02-01T14:00:00Z',
            "instructions": 'Updated Instruction 1,Updated Instruction 2',
            "status":1,
            "subjects": [
                {"subject": self.subject1.id, "time_duration": 75,
                    "pass_percentage": 65, "difficulty_level": 1, "question_count": 0},
                {"subject": self.subject3.id, "time_duration": 50,
                    "pass_percentage": 75, "difficulty_level": 1, "question_count": 20}
            ]
        }
        self.client.force_authenticate(user=self.user)
        url = reverse('update-exam', args=[self.exam.id])
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'message': 'Question count is zero for Subject 1', 'errorCode': 'E40019'})
        
    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_exam_updation_failure_response_status_publish(self, mock_create_exam_questions, mock_questions_filter):
        for _ in range(5):
              user_ticket = Ticket.objects.create(status=1, organisation=self.user)

        mock_questions_filter.return_value.exists.return_value = True
        data = {
            "name": "Updated Exam name",
            "scheduled_time": '2025-02-01T14:00:00Z',
            "instructions": 'Updated Instruction 1,Updated Instruction 2',
            "status":1,
            "subjects": [
                {"subject": self.subject1.id, "time_duration": "",
                    "pass_percentage": 65, "difficulty_level": 1, "question_count": 20},
                {"subject": self.subject3.id, "time_duration": 50,
                    "pass_percentage": 75, "difficulty_level": 1, "question_count": 20}
            ]
        }
        self.client.force_authenticate(user=self.user)
        url = reverse('update-exam', args=[self.exam.id])
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'errorCode': 'E40011', 'message': 'Time duration is required'})
        
    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_exam_updation_publish_failed(self, mock_create_exam_questions, mock_questions_filter):
       
        mock_questions_filter.return_value.exists.return_value = True
        data = {
            "name": "Updated Exam name",
            "scheduled_time": '2025-02-01T14:00:00Z',
            "instructions": 'Updated Instruction 1,Updated Instruction 2',
            "status":1,
            "subjects": [
                {"subject": self.subject1.id, "time_duration": 75,
                    "pass_percentage": 65, "difficulty_level": 1, "question_count": 20},
                {"subject": self.subject3.id, "time_duration": 50,
                    "pass_percentage": 75, "difficulty_level": 1, "question_count": 20}
            ]
        }
        self.client.force_authenticate(user=self.user)
        url = reverse('update-exam', args=[self.exam.id])
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Insufficient tickets:Please purchase 4 more additional tickets')

    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_exam_updation_publish_failed_due_to_one_ticket(self, mock_create_exam_questions, mock_questions_filter):
       
        mock_questions_filter.return_value.exists.return_value = True
        data = {
            "name": "Updated Exam name",
            "scheduled_time": '2025-02-01T14:00:00Z',
            "instructions": 'Updated Instruction 1,Updated Instruction 2',
            "status":1,
            "subjects": [
                {"subject": self.subject1.id, "time_duration": 75,
                    "pass_percentage": 65, "difficulty_level": 1, "question_count": 5},
                {"subject": self.subject3.id, "time_duration": 50,
                    "pass_percentage": 75, "difficulty_level": 1, "question_count": 5}
            ]
        }
        self.client.force_authenticate(user=self.user)
        url = reverse('update-exam', args=[self.exam.id])
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Insufficient ticket:Please purchase 1 ticket')



    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_exam_updation_successful_response_with_no_subject_data(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        data = {
            "name": "Updated Exam name",
            "scheduled_time": '2025-02-01T14:00:00Z',
            "instructions": 'Updated Instruction 1,Updated Instruction 2',
            "status":0,
            "subjects": [
               
            ]
        }
        self.client.force_authenticate(user=self.user)
        url = reverse('update-exam', args=[self.exam.id])
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, {"message": "Exam Updated Successfully"})

    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_exam_updation_successful_response_by_adding_new_subject(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        data = {
            "name": "Updated Exam name",
            "scheduled_time": '2025-02-01T14:00:00Z',
            "instructions": 'Updated Instruction 1,Updated Instruction 2',
            "subjects": [
                {"subject": self.subject1.id, "time_duration": 75,
                    "pass_percentage": 65, "difficulty_level": 1, "question_count": 20},
                {"subject": self.subject3.id, "time_duration": 50,
                    "pass_percentage": 75, "difficulty_level": 1, "question_count": 20},
                {"subject": self.subject2.id, "time_duration": 50,
                    "pass_percentage": 75, "difficulty_level": 1, "question_count": 20}
            ]
        }
        self.client.force_authenticate(user=self.user)
        url = reverse('update-exam', args=[self.exam.id])
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, {"message": "Exam Updated Successfully"})

    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_exam_updation_successful_response_by_repeating_subject(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        data = {
            "name": "Updated Exam name",
            "scheduled_time": '2025-02-01T14:00:00Z',
            "instructions": 'Updated Instruction 1,Updated Instruction 2',
            "subjects": [
                {"subject": self.subject1.id, "time_duration": 75,
                    "pass_percentage": 65, "difficulty_level": 1, "question_count": 20},
                {"subject": self.subject3.id, "time_duration": 50,
                    "pass_percentage": 75, "difficulty_level": 1, "question_count": 20},
                {"subject": self.subject3.id, "time_duration": 50,
                    "pass_percentage": 75, "difficulty_level": 1, "question_count": 20},

            ]
        }
        self.client.force_authenticate(user=self.user)
        url = reverse('update-exam', args=[self.exam.id])
        response = self.client.put(url, data, format='json')
        print(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'errorCode': 'E40018','message': "Duplicate subject Subject 3 found in the request"})

    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_exam_updation_with_validation_message_exceed_question_count(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        data = {
            "name": "Updated Exam name",
            "scheduled_time": '2025-02-01T14:00:00Z',
            "instructions": 'Updated Instruction 1,Updated Instruction 2',
            "subjects": [
                {"subject": self.subject1.id, "time_duration": 75,
                    "pass_percentage": 65, "difficulty_level": 1, "question_count": 65},
                {"subject": self.subject3.id, "time_duration": 50,
                    "pass_percentage": 75, "difficulty_level": 1, "question_count": 20},
                {"subject": self.subject2.id, "time_duration": 50,
                    "pass_percentage": 75, "difficulty_level": 1, "question_count": 20},

            ]
        }
        self.client.force_authenticate(user=self.user)
        url = reverse('update-exam', args=[self.exam.id])
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], 
                         f"Question count for subject {self.subject1.subject_name} exceeds the available questions")

    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_exam_updation_with_validation_message(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.side_effect = [True, False]

        data = {
            "name": "Updated Exam name",
            "scheduled_time": '2025-02-01T14:00:00Z',
            "instructions": 'Updated Instruction 1,Updated Instruction 2',
            "subjects": [
                {"subject": self.subject1.id, "time_duration": 75, "pass_percentage": 65, "difficulty_level": 1,
                 "question_count": 20},
                {"subject": self.subject3.id, "time_duration": 50, "pass_percentage": 75, "difficulty_level": 1,
                 "question_count": 20},
                {"subject": self.subject2.id, "time_duration": 50, "pass_percentage": 75, "difficulty_level": 1,
                 "question_count": 20}
            ]
        }

        self.client.force_authenticate(user=self.user)
        url = reverse('update-exam', args=[self.exam.id])
        response = self.client.put(url, data, format='json')
        difficulty_level_value = get_difficulty_level_value(1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['message'], f"No questions available for {difficulty_level_value} level for subject {self.subject1.subject_name}")
        

    
    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_exam_updation_with_four_subject(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        data = {
            "name": "Updated Exam name",
            "scheduled_time": '2025-02-01T14:00:00Z',
            "instructions": 'Updated Instruction 1,Updated Instruction 2',
            "subjects": [
                {"subject": self.subject1.id, "time_duration": 75,
                    "pass_percentage": 65, "difficulty_level": 1, "question_count": 20},
                {"subject": self.subject3.id, "time_duration": 50,
                    "pass_percentage": 75, "difficulty_level": 1, "question_count": 20},
                 {"subject": self.subject2.id, "time_duration": 50,
                    "pass_percentage": 75, "difficulty_level": 1, "question_count": 20},
                 {"subject": self.subject4.id, "time_duration": 50,
                    "pass_percentage": 75, "difficulty_level": 1, "question_count": 20},
                    
                    

            ]
        }
        self.client.force_authenticate(user=self.user)
        url = reverse('update-exam', args=[self.exam.id])
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'errorCode': 'E40023','message': 'Cannot create more than 3 subjects for a exam'})
        


    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_exam_updation_with_new_subject(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        new_subject = Subject.objects.create(subject_name='New Subject', question_count=25)
        data = {
            "name": "Updated Exam name",
            "scheduled_time": '2025-02-01T14:00:00Z',
            "instructions": 'Updated Instruction 1,Updated Instruction 2',
            "subjects": [
                {"subject": self.subject1.id, "time_duration": 75,
                    "pass_percentage": 65, "difficulty_level": 1, "question_count": 20},
                {"subject": new_subject.id, "time_duration": 50,
                "pass_percentage": 75, "difficulty_level": 1, "question_count": 20},
                
                    

            ]
        }
        self.client.force_authenticate(user=self.user)
        url = reverse('update-exam', args=[self.exam.id])
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, {"message": "Exam Updated Successfully"})
        

    
    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_exam_updation_with_new_subject_and_invalid_passpercentage(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        new_subject = Subject.objects.create(subject_name='New Subject', question_count=25)
        data = {
            "name": "Updated Exam name",
            "scheduled_time": '2025-02-01T14:00:00Z',
            "instructions": 'Updated Instruction 1,Updated Instruction 2',
            "subjects": [
                {"subject": self.subject1.id, "time_duration": 75,
                    "pass_percentage": 65, "difficulty_level": 1, "question_count": 20},
                {"subject": new_subject.id, "time_duration": 50,
                "pass_percentage": 750, "difficulty_level": 1, "question_count": 20},
                
                    

            ]
        }
        self.client.force_authenticate(user=self.user)
        url = reverse('update-exam', args=[self.exam.id])
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'errorCode': 'E40006', 'message': 'Pass percentage must be between 0 and 100'})
        
        


        
    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_exam_updation_with_exam_subject_serializer_error(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        data = {
            "name": "Updated Exam name",
            "scheduled_time": '2026-02-01T14:00:00Z',
            "instructions": 'Updated Instruction 1,Updated Instruction 2',
            "subjects": [
                {"subject": self.subject1.id, "time_duration": 75,
                    "pass_percentage": 650, "difficulty_level": 1, "question_count": 20},
                {"subject": self.subject3.id, "time_duration": 50,
                    "pass_percentage": 75, "difficulty_level": 1, "question_count": 20},
                 {"subject": self.subject2.id, "time_duration": 50,
                    "pass_percentage": 75, "difficulty_level": 1, "question_count": 20},
                 
                    

            ]
        }
        self.client.force_authenticate(user=self.user)
        url = reverse('update-exam', args=[self.exam.id])
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'errorCode': 'E40006', 'message': 'Pass percentage must be between 0 and 100'})
        

    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_exam_updation_with_past_time(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        data = {
            "name": "Updated Exam name",
            "scheduled_time": '2023-02-01T14:00:00Z',
            "instructions": 'Updated Instruction 1,Updated Instruction 2',
            "subjects": [
                {"subject": self.subject1.id, "time_duration": 75,
                    "pass_percentage": 65, "difficulty_level": 1, "question_count": 20},
                {"subject": self.subject3.id, "time_duration": 50,
                    "pass_percentage": 75, "difficulty_level": 1, "question_count": 20},
                 {"subject": self.subject2.id, "time_duration": 50,
                    "pass_percentage": 75, "difficulty_level": 1, "question_count": 20},
                 
                    

            ]
        }
        self.client.force_authenticate(user=self.user)
        url = reverse('update-exam', args=[self.exam.id])
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'errorCode': 'E40004', 'message': 'Scheduled time must be in the future'})
        

    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_exam_updation_with_no_subjects(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        data = {
            "name": "Updated Exam name",
            "scheduled_time": '2028-02-01T14:00:00Z',
            "instructions": 'Updated Instruction 1,Updated Instruction 2',
            "status":1,
            "subjects": []

        }
        self.client.force_authenticate(user=self.user)
        url = reverse('update-exam', args=[self.exam.id])
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'message': 'At least one subject is required for exam', 'errorCode': 'E40015'})
        
    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_update_exam_subject_instance(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        exam1= Exam.objects.create(name='Test Exam', scheduled_time='2024-02-01T12:00:00Z',
                                        instructions='Instruction 1,Instruction 2', organization_id=self.user.id,status=1)
        exam_subject_instance = ExamSubjects.objects.create(
            exam=exam1, 
            subject=self.subject1, 
            time_duration=60, 
            pass_percentage=70, 
            difficulty_level=1, 
            question_count=5
        )
        
        
        data = {
            "name": "Updated Exam name",
            "scheduled_time": '2025-02-01T14:00:00Z',
            "instructions": 'Updated Instruction 1,Updated Instruction 2',
            "subjects": [
                {"subject": self.subject1.id, "time_duration": 60,
                    "pass_percentage": 70, "difficulty_level": 1, "question_count": 6},
            ]
        }
        self.client.force_authenticate(user=self.user)
        url = reverse('update-exam', args=[self.exam.id])
        response = self.client.put(url, data, format='json')
        
     
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    @patch('exam_management.views.Questions.objects.filter')
    @patch('exam_management.views.ExamQuestions.objects.create')
    def test_exam_not_updateble(self, mock_create_exam_questions, mock_questions_filter):
        mock_questions_filter.return_value.exists.return_value = True
        exam1= Exam.objects.create(name='Test Exam', scheduled_time='2024-02-01T12:00:00Z',
                                        instructions='Instruction 1,Instruction 2', organization_id=self.user.id,status=1)
        exam_subject_instance = ExamSubjects.objects.create(
            exam=exam1, 
            subject=self.subject1, 
            time_duration=60, 
            pass_percentage=70, 
            difficulty_level=1, 
            question_count=5
        )
        
        
        data = {
            "name": "Updated Exam name",
            "scheduled_time": '2025-02-01T14:00:00Z',
            "instructions": 'Updated Instruction 1,Updated Instruction 2',
            "subjects": [
                {"subject": self.subject1.id, "time_duration": 60,
                    "pass_percentage": 70, "difficulty_level": 1, "question_count": 6},
            ]
        }
        self.client.force_authenticate(user=self.user)
        url = reverse('update-exam', args=[exam1.id])
        response = self.client.put(url, data, format='json')
        
     
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'message': 'Exam cannot be updated', 'errorCode': 'E40009'})



class ExamListViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test_user@gmail.com', password='test_password')
        Exam.objects.create(name='Exams 1', scheduled_time='2024-02-15T10:00:00Z', organization=self.user, status=1)
        Exam.objects.create(name='Exam 2', scheduled_time='2024-02-16T10:00:00Z', organization=self.user, status=1)
        

    def test_list_exams_authenticated(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse('exam-list')
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    def test_list_exams_unauthenticated(self):
        client = APIClient()
        url = reverse('exam-list')
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    def test_ordering(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse('exam-list') + '?ordering=name'
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        exam_names = [exam['name'] for exam in response.data['results']]
        self.assertEqual(exam_names, ['Exam 2', 'Exams 1'])
    def test_search_exam_by_name(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse('exam-list')
        response = client.get(url, {'search': 'Exam 2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Exam 2')

class SoftDeleteViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1=User.objects.create(username= 'test user', email='test@example.com',address= 'test address',contact_number= '9089786756',password= 'Password@123')
        self.exam = Exam.objects.create(name='Test Exam', status=0, candidate_count=0,organization_id=self.user1.id)

    def test_soft_delete_success(self):
        url = reverse('delete-exam', kwargs={'pk': self.exam.id})
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.exam.refresh_from_db()
        self.assertEqual(self.exam.status, -1)

    def test_soft_delete_past_exam(self):
        self.exam.save()
        url = reverse('delete-exam', kwargs={'pk': self.exam.id})
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.exam.refresh_from_db()
        self.assertEqual(self.exam.status, 1)


class ExamViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testuser', email='testuser@gmail.com', user_type=1, is_register=1)
        
        self.exam = Exam.objects.create(name = 'Test Exam',scheduled_time = '2025-02-05T12:00:00Z',exam_duration = 120,instructions = 'Read Carefully',organization = self.user)
        self.subject = Subject.objects.create(
            subject_name='testsubject',
            question_count=20
        )


        ExamSubjects.objects.create(
            exam=self.exam,
            subject=self.subject,
            time_duration=60,
            pass_percentage=70,
            difficulty_level=2,
            question_count=20
        )

      
        self.client = APIClient()

    @patch('exam_management.views.get_object_or_404')
    def test_exam_detail_view(self, mock_get_object_or_404):
   
        mock_get_object_or_404.return_value = self.exam
        url = reverse('exam-details', args=[self.exam.id])

      
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Exam')


    @patch('exam_management.views.jwt.decode')
    @patch('exam_management.views.get_object_or_404')
    def test_end_user_exam_view(self, mock_get_object_or_404, mock_jwt_decode):
       
        mock_get_object_or_404.return_value = self.exam
        mock_jwt_decode.return_value = {'exam_id': self.exam.id}
        url = reverse('exam-details-token')
        data = {"token":"mock_token"}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Exam')

    @patch('exam_management.views.jwt.decode')
    def test_invalid_token(self, mock_decode):
       
        mock_decode.side_effect = jwt.InvalidTokenError("Invalid token")
        url = reverse('exam-details-token')
        data = {"token":"invalid_token"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'Invalid token', 'errorCode': 'E40029'})


    
    @patch('exam_management.views.jwt.decode')
    def test_expired_token(self, mock_decode):
       
        mock_decode.side_effect = jwt.ExpiredSignatureError("Expired token")
        url = reverse('exam-details-token')
        data = {"token":"expired_token"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"expired": True})

class SoftDeleteViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1=User.objects.create(username= 'test user', email='test@example.com',address= 'test address',contact_number= '9089786756',password= 'Password@123')
        self.exam = Exam.objects.create(name='Test Exam', status=0, candidate_count=30,organization_id=self.user1.id)

    def test_soft_delete_success(self):
        url = reverse('delete-exam', kwargs={'pk': self.exam.id})
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.exam.refresh_from_db()
        self.assertEqual(self.exam.status, -1)

    def test_soft_delete_past_exam(self):
        self.exam.status=1
        self.exam.save()
        url = reverse('delete-exam', kwargs={'pk': self.exam.id})
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.exam.refresh_from_db()
        self.assertEqual(self.exam.status, 1)



class ExamQuestionViewTestCase(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(
            subject_name="testsubject2", question_count=20
        )

        self.user1 = User.objects.create_user(
            username="nouser",
            password="nouserpassword",
            email="nouser@gmail.com",
            is_register=0,
            user_type=1,
        )

        self.exam = Exam.objects.create(
            name="Test Exam",
            scheduled_time="2024-02-08 10:00:00",
            organization_id=self.user1.id,
        )

        self.question1 = Questions.objects.create(
            question_description="Question 1",
            answer_type=3,
            subject_id=self.subject,
            is_drafted=True,
        )
        FreeAnswers.objects.create(
            question=self.question1, answer="Free answer 1"
        )
        QuestionOptions.objects.create(question=self.question1, options="Free answer 1",is_answer=True)
        QuestionOptions.objects.create(question=self.question1, options="Free answer ",is_answer=False)

        self.question2 = Questions.objects.create(
            question_description="Question 2",
            answer_type=1,
            subject_id=self.subject,
            is_drafted=True,
        )

        self.exam_subject = ExamSubjects.objects.create(
            exam=self.exam,
            subject=self.subject,
            time_duration=60,
            pass_percentage=70,
            difficulty_level=2,
            question_count=10,
        )

        self.exam_question1 = ExamQuestions.objects.create(
            exam=self.exam_subject, question=self.question1
        )

        self.exam_question2 = ExamQuestions.objects.create(
            exam=self.exam_subject, question=self.question2
        )

    def test_get_exam_questions_success(self):

        url = reverse("exam-questions", kwargs={"exam_subject_id": self.exam_subject.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_exam_questions_not_success(self):

        url = reverse("exam-questions", kwargs={"exam_subject_id": 2})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class RegenerateQuestionViewTestCase(TestCase):
    def setUp(self):
       
        self.subject = Subject.objects.create(
            subject_name="testsubject2", question_count=20
        )

        self.user1 = User.objects.create_user(
            username="nouser",
            password="nouserpassword",
            email="nouser@gmail.com",
            is_register=0,
            user_type=1,
        )

        self.exam = Exam.objects.create(
            name="Test Exam",
            scheduled_time="2040-02-08 10:00:00",
            organization_id=self.user1.id,
            status=1
        )
        self.exam1 = Exam.objects.create(
            name="Test Exam",
            scheduled_time="2023-02-08 10:00:00",
            organization_id=self.user1.id,
            status=1
            
        )

    def test_regeneration_success(self):

        exam_subject = ExamSubjects.objects.create(
            subject=self.subject,
            exam=self.exam,
            time_duration=60,
            pass_percentage=70,
            difficulty_level=2,
            question_count=10,
        )
        
        url = reverse(
            "regenarate-questions",
            kwargs={"exam_id": exam_subject.exam.id, "subject_id": exam_subject.subject.id},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["message"], "Question regenerated successfully")

    def test_regeneration_failure(self):
        exam_subject = ExamSubjects.objects.create(
            subject=self.subject,
            exam=self.exam,
            time_duration=60,
            pass_percentage=70,
            difficulty_level=2,
            question_count=10,
        )
        url = reverse(
            "regenarate-questions",
            kwargs={"exam_id": exam_subject.exam.id, "subject_id": 2,}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Question regeneration failed")
    
    
    def test_regeneration_failure_scheduledtime(self):
        exam_subject = ExamSubjects.objects.create(
            subject=self.subject,
            exam=self.exam1,
            time_duration=60,
            pass_percentage=70,
            difficulty_level=2,
            question_count=10,
        )
        url = reverse(
            "regenarate-questions",
            kwargs={"exam_id": exam_subject.exam.id, "subject_id": 2,}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Regeneration is not allowed after the scheduled time")



class ExamScheduledTimeViewTest(APITestCase):
    def setUp(self):
       self.user = User.objects.create_user(email='test_user@gmail.com', password='test_password')
       self.exam = Exam.objects.create(name='Exams 1', scheduled_time='2024-02-15T10:00:00Z', organization=self.user, status=1)
       self.subject = Subject.objects.create(subject_name='Sample Subject')
       self.exam_subject = ExamSubjects.objects.create(
            exam=self.exam,
            subject=self.subject,
            time_duration=60,
            pass_percentage=50.00,
            difficulty_level=1,
            question_count=20
        )
    def test_get_exam_scheduled_time_success(self):
        url = reverse('exam-schedule', kwargs={'exam_id': self.exam.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Exams 1')


class FeedbackAPIViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test_user@gmail.com', password='test_password')
        self.exam = Exam.objects.create(name='Exams 1', scheduled_time='2024-02-15T10:00:00Z', organization=self.user, status=2)
        self.candidate = Candidate.objects.create(name='Sample Candidate')

    def test_create_feedback(self):
        data = {
            'exam': self.exam.id,
            'candidate': self.candidate.id,
            'feedback': 'Sample feedback',
            'rating': 4.5
        }
        response = self.client.post(reverse('exam-feedback'), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Feedback.objects.filter(exam=self.exam, candidate=self.candidate).exists())

class PendingEvaluationListViewTestCase(TestCase):
    def setUp(self):
       
        self.user = User.objects.create_user(
            username="testuser",
            password="testuser",
            email="testuser@gmail.com",
            user_type=1,
            is_register=1,
        )
        Exam.objects.create(
            name="Exam 1",
            scheduled_time="2024-02-20T12:00:00Z",
            status=2,
            organization_id=self.user.id,
        )
        Exam.objects.create(
            name="Exam 2",
            scheduled_time="2024-02-21T12:00:00Z",
            status=2,
            organization_id=self.user.id,
        )
        Exam.objects.create(
            name="Exam 3",
            scheduled_time="2024-02-22T12:00:00Z",
            status=2,
            organization_id=self.user.id,
        )
        Exam.objects.create(
            name="Exam 4",
            scheduled_time="2025-02-05T12:00:00Z",
            status=2,
            organization_id=self.user.id,
            candidate_count=2
        )

    def test_get_queryset(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        url = reverse("pending-evaluation-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DownloadMarkListViewTestCase(TestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser",
            password="testuser",
            email="testuser@gmail.com",
            user_type=1,
            is_register=1,
        )
        self.subject1 = Subject.objects.create(
            subject_name="testsubject1", question_count=20
        )
        self.subject2 = Subject.objects.create(
            subject_name="testsubject2", question_count=20
        )
        self.question1 = Questions.objects.create(
            question_description="Question 1",
            answer_type=3,
            subject_id=self.subject1,
            is_drafted=True,
            marks=100,
        )
        FreeAnswers.objects.create(question=self.question1, answer="Free answer 1")
        QuestionOptions.objects.create(
            question=self.question1, options="Free answer 1", is_answer=True
        )
        QuestionOptions.objects.create(
            question=self.question1, options="Free answer ", is_answer=False
        )

        self.question2 = Questions.objects.create(
            question_description="Question 2",
            answer_type=1,
            subject_id=self.subject2,
            is_drafted=True,
            marks=100,
        )

        self.exam = Exam.objects.create(
            name="Exam 1",
            scheduled_time="2024-02-20T12:00:00Z",
            status=1,
            organization_id=self.user.id,
        )
        self.candidate = Candidate.objects.create(
            email="test@example.com", exam=self.exam,status=4
        )

        self.exam_subject1 = ExamSubjects.objects.create(
            subject=self.subject1,
            exam=self.exam,
            time_duration=60,
            pass_percentage=70,
            difficulty_level=2,
            question_count=10,
        )
        self.exam_subject2 = ExamSubjects.objects.create(
            subject=self.subject2,
            exam=self.exam,
            time_duration=60,
            pass_percentage=70,
            difficulty_level=2,
            question_count=10,
        )
        self.exam_question1 = ExamQuestions.objects.create(
            exam=self.exam_subject1, question=self.question1
        )

        self.exam_question2 = ExamQuestions.objects.create(
            exam=self.exam_subject2, question=self.question2
        )

        ExamCandidate.objects.create(
            candidate=self.candidate,
            exam_subject=self.exam_subject1,
            exam_subject_mark=80,
        )
        ExamCandidate.objects.create(
            candidate=self.candidate,
            exam_subject=self.exam_subject2,
            exam_subject_mark=90,
        )

    def test_download_success(self):

        response = self.client.get(
            reverse("download_mark_list", kwargs={"exam_id": self.exam.id})
        )
        self.assertTrue(response.content)
        
    def test_download_fail(self):

        response = self.client.get(
            reverse("download_mark_list", kwargs={"exam_id": 99})
        )
        self.assertEqual(response.status_code, 400)


class SubjectPopularityViewTestCase(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser",
            password="testuser",
            email="testuser@gmail.com",
            user_type=1,
            is_register=1,
        )
        self.subject1 = Subject.objects.create(
            subject_name="testsubject1", question_count=20
        )
        self.subject2 = Subject.objects.create(
            subject_name="testsubject2", question_count=20
        )
        self.exam1 = Exam.objects.create(
            name="Exam 1",
            scheduled_time="2024-02-20T12:00:00Z",
            status=1,
            organization_id=self.user.id,
        )
        self.exam2 = Exam.objects.create(
            name="Exam 2",
            scheduled_time="2024-02-20T12:00:00Z",
            status=1,
            organization_id=self.user.id,
        )
        self.exam_subject1 = ExamSubjects.objects.create(
            subject=self.subject1,
            exam=self.exam1,
            time_duration=60,
            pass_percentage=70,
            difficulty_level=2,
            question_count=10,
        )
        self.exam_subject2 = ExamSubjects.objects.create(
            subject=self.subject1,
            exam=self.exam2,
            time_duration=60,
            pass_percentage=70,
            difficulty_level=2,
            question_count=10,
        )

        self.url = reverse("subject-popularity")

    def test_get_subject_popularity(self):
        url = reverse("subject-popularity")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

# class TestGenerateQuestionsForSubject(unittest.TestCase):

#     @patch('exam_management.views.ExamQuestions.objects.filter')
#     @patch('exam_management.views.Questions.objects.filter')
#     @patch('exam_management.views.ExamQuestions.objects.create')
#     @patch('exam_management.views.random.shuffle')
#     def test_generate_questions_for_subject(self,mock_shuffle,mock_create,mock_question_filter,mock_exam_questions_filter):
#         mock_questions_queryset = [MagicMock() for _ in range(5)] 
#         mock_question_filter.return_value = mock_questions_queryset
#         mock_exam_questions_filter.return_value.delete.return_value=None

#         exam_subject = MagicMock(subject_id=1,difficulty_level=2,question_count=5)
#         generate_questions_for_subject(exam_subject)
      
#         mock_question_filter.assert_called_once_with(
#             subject_id_id=exam_subject.subject_id,
#             difficulty_level=exam_subject.difficulty_level,
#             is_drafted=False,
#         )
#         self.assertEqual(mock_create.call_count, 5)
       



class DashboardExamListAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testuser', email='testuser@gmail.com', user_type=1, is_register=1)
        self.invaliduser = User.objects.create_user(username='testuser2', password='testuser2', email='testuser2@gmail.com', user_type=0, is_register=1)
        self.client.force_authenticate(user=self.user)
        self.organization_id = self.user.id

    def test_get_exams_with_valid_status(self):
        Exam.objects.create(organization_id=self.organization_id, status=1,scheduled_time="2024-02-20T12:00:00Z", name='Exam 1')
        Exam.objects.create(organization_id=self.organization_id, status=0,scheduled_time="2024-02-20T12:00:00Z", name='Exam 2')
        url = reverse('dashboard-exam-list', kwargs={'status': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  

class ExamCancelAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='test_user@gmail.com', password='test_password')
        self.exam=Exam.objects.create(name='Exams 1', scheduled_time='2024-02-15T10:00:00Z', organization=self.user, status=1)
        self.ticket = Ticket.objects.create(exam=self.exam, status=2,organisation_id=self.user.id) 

    def test_cancel_exam_with_valid_data(self):
        url = reverse('exam-cancel', kwargs={'exam_id': self.exam.id})
        response = self.client.patch(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.exam=Exam.objects.get(id=self.exam.id) 
        self.assertEqual(self.exam.status, 5) 

    def test_cancel_exam_with_exam_status_not_1(self):
        self.exam.status = 2  # Set exam status to 2
        self.exam.save()
        url = reverse('exam-cancel', kwargs={'exam_id': self.exam.id})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.exam=Exam.objects.get(id=self.exam.id) 
        self.assertEqual(self.exam.status, 2)  
        self.assertEqual(Ticket.objects.filter(exam=self.exam).count(), 1) 
        self.assertEqual(response.data['message'], "Can't cancel this exam")
        self.assertEqual(response.data['errorCode'], 'E44011')

    def test_cancel_exam_with_not_found(self):
        url = reverse('exam-cancel', kwargs={'exam_id': 19999})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Exam not found')
        self.assertEqual(response.data['errorCode'], 'E40028')
        
    
   


