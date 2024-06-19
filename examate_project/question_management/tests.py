from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from user_management.models import User
from .models import Questions
from subject_management.models import Subject
from .views import QuestionlistAPIView
from rest_framework.test import APIClient
from .serializers import QuestionOptionsDetailSerializer,FreeAnswerQuestionDetailSerializer
from .models import Questions,QuestionOptions,FreeAnswers
from exam_management.models import ExamQuestions
from subject_management.models import Subject
from rest_framework import serializers
from unittest.mock import patch, MagicMock
from rest_framework import serializers
from .messages import E30026,E30027,E30028,E30029,E30050

class CreateQuestionViewTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@gmail.com", password="testpassword", user_type=0, is_register=1
        )
        self.subject = Subject.objects.create(subject_name="c")
        self.create_url = reverse("create-question")

    def test_create_question_with_free_answer_success(self):
        data = {
            "question_description": "Who is the father of Bulb?",
            "difficulty_level": 2,
            "answer_type": 3,
            "marks": 2,
            "answer": "Edison",
            "subject_id": self.subject.id,
            "is_drafted": True,
        }
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(
            response.data["message"], "Free answer question created successfully"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_question_success(self):
        data = {
            "question_description": "What is java?",
            "difficulty_level": 2,
            "answer_type": 3,
            "marks": 2,
            "subject_id": 1,
            "is_drafted": False,
        }
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_question_with_options_success(self):
        data = {
            "question_description": "Who is the father of C languag",
            "difficulty_level": 2,
            "answer_type": 2,
            "marks": 2,
            "subject_id": self.subject.id,
            "is_drafted": True,
            "options": [
                {"options": "Steve Jobs", "is_answer": False},
                {"options": "Dennis ", "is_answer": True},
                 {"options": "Dennis ", "is_answer": True},
                 
            ],
        }
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch("question_management.views.settings")
    def test_update_question_with_mocked_option_limit(self, mock_option_limit):
        mock_option_limit.OPTION_LIMIT = 1

        data = {
            "question_description": "Who is the father of C languag  question",
            "difficulty_level": 2,
            "answer_type": 1,
            "subject_id": self.subject.id,
            "marks": 15,
            "is_drafted": True,
            "options": [
                {"options": " Option 1", "is_answer": True},
                {"options": " Option 2", "is_answer": False},
                {"options": " Option 3", "is_answer": False},
                {"options": " Option 4", "is_answer": False},
            ],
        }
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Options are out of limit")


class QuestionDetailViewTest(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="testadmin",
            password="testpassword",
            email="testadmin1@gmail.com",
            user_type=0,
            is_register=1,
        )
        self.subject = Subject.objects.create(subject_name="java1")
        self.question = Questions.objects.create(
            question_description="easy,single answer,sub1",
            difficulty_level=1,
            answer_type=1,
            marks=2,
            subject_id=self.subject,
            is_drafted=True,
        )
        self.question3 = Questions.objects.create(
            question_description="free answer question",
            difficulty_level=1,
            answer_type=3,
            marks=2,
            subject_id=self.subject,
            is_drafted=False,
        )

    def test_get_question_detail(self):
        self.create_url = reverse("question-detail", args=[self.question.id])
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.create_url)
       
        if self.question.answer_type == 1 or self.question.answer_type == 2:
            expected_serializer = QuestionOptionsDetailSerializer(self.question)
        elif self.question.answer_type == 3:
            expected_serializer = FreeAnswerQuestionDetailSerializer(self.question)

        self.assertEqual(response.data, expected_serializer.data)

    def test_get_free_answer_question_detail(self):
        self.create_url = reverse("question-detail", args=[self.question3.id])
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.create_url)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the correct serializer is used based on answer_type
        if self.question3.answer_type == 1 or self.question3.answer_type == 2:
            expected_serializer = QuestionOptionsDetailSerializer(self.question)
        elif self.question3.answer_type == 3:
            expected_serializer = FreeAnswerQuestionDetailSerializer(self.question3)
        self.assertEqual(response.data, expected_serializer.data)

    def test_get_nonexistent_question_detail(self):
        self.create_url = reverse("question-detail", args=[999])
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data,  {'error_code': 'E30050', 'message':E30050 })


class QuestionDeleteViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="testadmin",
            password="testpassword",
            email="testadmin1@gmail.com",
            user_type=0,
            is_register=1,
        )
        self.subject = Subject.objects.create(subject_name="java12")
        self.question = Questions.objects.create(
            question_description="test question for deletion",
            difficulty_level=1,
            answer_type=1,
            marks=2,
            subject_id=self.subject,
            is_drafted=True,
        )

    def test_delete_question(self):
        self.create_url = reverse("question-detail", args=[self.question.id])
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)

    def test_delete_non_exist_question(self):
        self.create_url = reverse("question-detail", args=[99])
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.create_url)
        self.assertEqual({"error_code":"E30050","message": E30050}, response.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        

class ChangeDraftStatusAPIViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()     
        self.subject = Subject.objects.create(subject_name="golang")   
        self.admin = User.objects.create_user(username='testadmin', password='testpassword', email='testadmin1@gmail.com', user_type=0, is_register=1)
        self.question = Questions.objects.create(
            question_description="test question for draft status change",
            difficulty_level=1,
            answer_type=1,
            marks=2,
            subject_id=self.subject,
            is_drafted=True,
        )
        self.url = reverse('change_draft_status', args=[self.question.id])

    def test_change_draft_status(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_question = Questions.objects.get(id=self.question.id)
        self.assertFalse(updated_question.is_drafted)

    def test_change_draft_status_nonexistent_question(self):
        nonexistent_url = reverse('change_draft_status', args=[999])
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(nonexistent_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        
class UpdateQuestionViewTest(APITestCase):

    def setUp(self):
          self.admin = User.objects.create_user(
            username='testadmin', password='testpassword', email='testadmin1@gmail.com', user_type=0, is_register=1)
          
          self.client.force_authenticate(user = self.admin)
          self.subject = Subject.objects.create(subject_name='Test Subject')
          self.single_answer_question = Questions.objects.create(
            question_description='Test Single answer question',
            difficulty_level=1,
            answer_type=1,
            subject_id=self.subject,
            marks=10,
            is_drafted=False

        )
          self.multiple_answer_question = Questions.objects.create(
            question_description='Test Multiple answer question',
            difficulty_level=1,
            answer_type=2,
            subject_id=self.subject,
            marks=10,
            is_drafted=False

        )
          
          self.free_answer_question = Questions.objects.create(
            question_description='Test Free answer question',
            difficulty_level=1,
            answer_type=3,
            subject_id=self.subject,
            marks=10,
            is_drafted=False

        )
        
          self.free_answer = FreeAnswers.objects.create(question=self.single_answer_question, answer='Free answer')
          self.option1 = QuestionOptions.objects.create(question=self.single_answer_question, options='Option 1', is_answer=True)
          self.option2 = QuestionOptions.objects.create(question=self.single_answer_question, options='Option 2', is_answer=False)

          self.option3 = QuestionOptions.objects.create(question=self.multiple_answer_question, options='Option 3', is_answer=True)
          self.option4 = QuestionOptions.objects.create(question=self.multiple_answer_question, options='Option 4', is_answer=False)


    def test_update_question_single_answer(self):
           data = {
            'question_description': 'Updated question',
            'difficulty_level': 2,
            'answer_type': 1,
            'subject_id': self.subject.id,
            'marks': 15,
            'is_drafted': True,
            'options': [{'options': 'Updated Option 1', 'is_answer':True}]
        }
           single_answer_question = Questions.objects.create(
            question_description='Test Single answer question',
            difficulty_level=1,
            answer_type=1,
            subject_id=self.subject,
            marks=10,
            is_drafted=True

        )
           
           response = self.client.put(f'/question/update-question/{single_answer_question.id}/',data,format='json')
           self.assertEqual(response.status_code, status.HTTP_200_OK)
           self.assertEqual(response.data['message'], 'Single answer question updated successfully')

    
    def test_update_question_single_answer_option_validation(self):
           data = {
            'question_description': 'Updated question',
            'difficulty_level': 2,
            'answer_type': 1,
            'subject_id': self.subject.id,
            'marks': 15,
            'is_drafted': True,
            'options': [{'options': 'Updated Option 1', 'is_answer':True},
                        {'options': 'Updated Option 1', 'is_answer':True}]
        }
           single_answer_question = Questions.objects.create(
            question_description='Test Single answer question',
            difficulty_level=1,
            answer_type=1,
            subject_id=self.subject,
            marks=10,
            is_drafted=True

        )
           
           response = self.client.put(f'/question/update-question/{single_answer_question.id}/',data,format='json')
           self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
           self.assertEqual(response.data['message'], 'Only one option should be marked as answer for single answer question')


      
    def test_update_question_single_answer_option_validation_no_selection(self):
           data = {
            'question_description': 'Updated question',
            'difficulty_level': 2,
            'answer_type': 1,
            'subject_id': self.subject.id,
            'marks': 15,
            'is_drafted': True,
            'options': [{'options': 'Updated Option 1', 'is_answer':False},
                        {'options': 'Updated Option 1', 'is_answer':False}]
        }
           single_answer_question = Questions.objects.create(
            question_description='Test Single answer question',
            difficulty_level=1,
            answer_type=1,
            subject_id=self.subject,
            marks=10,
            is_drafted=True

        )
           
           response = self.client.put(f'/question/update-question/{single_answer_question.id}/',data,format='json')
           self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
           self.assertEqual(response.data['message'], 'At least one option must be marked as answer for single answer question')


          
       
    


    def test_update_question_multiple_answer(self):
           data = {
            'question_description': 'Updated question',
            'difficulty_level': 2,
            'answer_type': 2,
            'subject_id': self.subject.id,
            'marks': 15,
            'is_drafted': True,
            'options': [{'options': 'Updated Option 1', 'is_answer':True},
                        {'options': 'Updated Option 2', 'is_answer': False},
                        {'options': 'Updated Option 3', 'is_answer': True},
                        {'options': 'Updated Option 4', 'is_answer': False}]
        }
           
           multiple_answer_question = Questions.objects.create(
            question_description='Test Multiple answer question',
            difficulty_level=1,
            answer_type=2,
            subject_id=self.subject,
            marks=10,
            is_drafted=True

        )
           
           response = self.client.put(f'/question/update-question/{multiple_answer_question.id}/',data,format='json')
           self.assertEqual(response.status_code, status.HTTP_200_OK)
           self.assertEqual(response.data['message'], 'Multiple answer question updated successfully')


   
    def test_update_question_multiple_answer_option_validation_no_selection(self):
           data = {
            'question_description': 'Updated question',
            'difficulty_level': 2,
            'answer_type': 2,
            'subject_id': self.subject.id,
            'marks': 15,
            'is_drafted': True,
            'options': [{'options': 'Updated Option 1', 'is_answer':False},
                        {'options': 'Updated Option 2', 'is_answer': False},
                        {'options': 'Updated Option 3', 'is_answer': False},
                        {'options': 'Updated Option 4', 'is_answer': False}]
        }
           
           multiple_answer_question = Questions.objects.create(
            question_description='Test Multiple answer question',
            difficulty_level=1,
            answer_type=2,
            subject_id=self.subject,
            marks=10,
            is_drafted=True

        )
           
           response = self.client.put(f'/question/update-question/{multiple_answer_question.id}/',data,format='json')
           self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
           self.assertEqual(response.data['message'], 'At least two options must be marked as answer for multiple answers question')





   


    def test_update_question_free_answer(self):
           data = {
            'question_description': 'Updated question',
            'difficulty_level': 2,
            'answer_type': 3,
            'subject_id': self.subject.id,
            'marks': 15,
            'is_drafted': True,
            'answer':"Updated answer"
        }
           free_answer_question = Questions.objects.create(
            question_description='Test Free answer question',
            difficulty_level=1,
            answer_type=3,
            subject_id=self.subject,
            marks=10,
            is_drafted=True

        )
           
           response = self.client.put(f'/question/update-question/{free_answer_question.id}/',data,format='json')
           self.assertEqual(response.status_code, status.HTTP_200_OK)
           self.assertEqual(response.data['message'], 'Free answer question updated successfully')


    def test_update_question_free_answer_answer_type_error(self):
           data = {
            'question_description': 'Updated question',
            'difficulty_level': 2,
            'answer_type': 34,
            'subject_id': self.subject.id,
            'marks': 15,
            'is_drafted': True,
            'answer':"Updated answer"
        }
           free_answer_question = Questions.objects.create(
            question_description='Test Free answer question',
            difficulty_level=1,
            answer_type=3,
            subject_id=self.subject,
            marks=10,
            is_drafted=True

        )
           
           response = self.client.put(f'/question/update-question/{free_answer_question.id}/',data,format='json')
           self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
           self.assertEqual(response.data['message'],"Invalid answer_type")

          

    def test_no_question_available(self):
           data = {
            'question_description': 'Updated question',
            'difficulty_level': 2,
            'answer_type': 3,
            'subject_id': self.subject.id,
            'marks': 15,
            'is_drafted': True,
            'answer':"Updated answer"
        }
           
           response = self.client.put(f'/question/update-question/21/',data,format='json')
           self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
           self.assertEqual(response.data['message'], 'question not found')

    @patch('question_management.views.settings')
    def test_update_question_with_mocked_option_limit(self, mock_option_limit):
           mock_option_limit.OPTION_LIMIT = 1

           single_answer_question = Questions.objects.create(
            question_description='Test Single answer question',
            difficulty_level=1,
            answer_type=1,
            subject_id=self.subject,
            marks=10,
            is_drafted=True

        )

           data = {
          'question_description': 'Updated question',
        'difficulty_level': 2,
        'answer_type': 1,
        'subject_id': self.subject.id,
        'marks': 15,
        'is_drafted': True,
        'options': [{'options': 'Updated Option 1', 'is_answer': False},
                        {'options': 'Updated Option 2', 'is_answer': False},
                        {'options': 'Updated Option 3', 'is_answer': True},
                        {'options': 'Updated Option 4', 'is_answer': False}]
    }      
             
           response = self.client.put(f'/question/update-question/{single_answer_question.id}/',data,format='json')
           self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
           self.assertEqual(response.data['message'], 'Options are out of limit')

  
    def test_free_answer_validation_error(self):
          data={
               
              
                "answer_type":3 ,
                "is_drafted":True,
                "marks":10,
                "answer":"A" * 5010 
                


          } 

          free_answer_question = Questions.objects.create(
            question_description='Test Free answer question',
            difficulty_level=1,
            answer_type=3,
            subject_id=self.subject,
            marks=10,
            is_drafted=True

        )

         
          response = self.client.put(f'/question/update-question/{free_answer_question.id}/',data,format='json')
          self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
          self.assertEqual(response.data['message'], 'Answer must be at most 500 characters long')

   
    def test_question_validation_error(self):
          data = {
            'question_description': 'Updated question',
            'difficulty_level': 2,
            'answer_type': 3,
            'subject_id': self.subject.id,
            'marks': 15,
            'is_drafted': "drafted",
            'answer':"Updated answer"
        }
          
          free_answer_question = Questions.objects.create(
            question_description='Test Free answer question',
            difficulty_level=1,
            answer_type=3,
            subject_id=self.subject,
            marks=10,
            is_drafted=True

        )

        
          response = self.client.put(f'/question/update-question/{free_answer_question.id}/',data,format='json')
          self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
          self.assertEqual(response.data['message'], 'Invalid value for is_drafted')


    @patch('question_management.views.QuestionOptionSerializer')
    def test_options_validation_error(self,mock_option_serializer):
          data = {
            'question_description': 'Updated question',
            'difficulty_level': 2,
            'answer_type': 1,
            'subject_id': self.subject.id,
            'marks': 15,
            'is_drafted': True,
            'options': [{'id': self.option1.id, 'options': 'Updated Option 1', 'is_answer': True}]
        }

          mock_option_instance = mock_option_serializer.return_value
          mock_option_instance.is_valid.side_effect = serializers.ValidationError({
            'field_name': ['This field is required.'],
        })
          response = self.client.put(f'/question/update-question/{self.single_answer_question.id}/',data,format='json')
          self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
         
class QuestionlistAPIViewTests(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_user(username='testadmin', password='testpassword', email='testadmin1@gmail.com', user_type=0, is_register=1) # Log in admin for authorization
        self.create_url = reverse('question-list')
        self.client = APIClient()
        self.view = QuestionlistAPIView.as_view()
        # Create test questions
        self.subject1 = Subject.objects.create(subject_name="subject1")
        self.subject2 = Subject.objects.create(subject_name="subject2")
        self.subject3 = Subject.objects.create(subject_name="subject3")

        self.question1 = Questions.objects.create(
            question_description="easy,single answer,sub1",
            difficulty_level=1,
            answer_type=1,
            marks=2,
            subject_id=self.subject1,
            is_drafted = True  
        )

        self.question2 = Questions.objects.create(
            question_description="medium,multiple answer,sub2?",
            difficulty_level=2,
            answer_type=2,
            marks=2,
            subject_id=self.subject2,
            is_drafted = True   
        )
        self.question3 = Questions.objects.create(
            question_description="hard,free answer,sub3?",
            difficulty_level=3,
            answer_type=3,
            marks=2,
            subject_id=self.subject3,
            is_drafted = True   
        )
        



    def test_filtering_by_is_drafted(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.create_url, {'is_drafted': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3) 
        self.assertEqual(response.data['results'][0]['id'], self.question1.id) 
    
    def test_filtering_by_difficulty_level(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.create_url, {'difficulty_level':'1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.question1.id) 
    
    def test_filtering_by_difficulty_level2(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.create_url, {'difficulty_level':'2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.question2.id) 
    
    def test_filtering_by_answer_type2(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.create_url, {'answer_type':'2'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.question2.id) 
    
    def test_filtering_by_subject_id3(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.create_url, {'subject_id':self.subject3.id})
        print("subject id3 :",self.subject3.id)
        print("response id3 :",response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.question3.id) 
    
    def test_search_question(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.create_url, {'search_param':'hard,free answer,sub3?'})
        print("response search:",response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)


class CountViewTestCase(APITestCase):
    def setUp(self):
      
        self.subject1 = Subject.objects.create(subject_name="subject1")
        self.question1 = Questions.objects.create(
            question_description="easy,single answer,sub1",
            difficulty_level=1,
            answer_type=1,
            marks=2,
            subject_id=self.subject1,
            is_drafted = False 
        )
       
        self.user1 = User.objects.create_user(
            username="nouser",
            password="nouserpassword",
            email="nouser@gmail.com",
            is_register=1,
            user_type=1,
        )
        self.url = reverse('count')

    def test_count_view(self):
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        
        self.assertEqual(response.data['total_question_count'], 1)
        self.assertEqual(response.data['total_subject_count'], 1)
        self.assertEqual(response.data['total_organisation_count'], 1)

