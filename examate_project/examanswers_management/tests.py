from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from candidatemanagement.models import Candidate,ExamCandidate
from exam_management.models import Exam,ExamSubjects,ExamQuestions
from question_management.models import Questions,QuestionOptions,FreeAnswers
from examanswers_management.models import CandidateAnswers
from user_management.models import User
from subject_management.models import Subject
from examanswers_management.views import EvaluateFreeAnswerView
from examanswers_management.serializers import CandidateAnswerSerializers
from unittest.mock import patch, MagicMock,Mock
from examanswers_management.views import candidate_answer_evalaution,evaluate_sa_and_ma_questions
import unittest

# class EvaluateSAandMATestCase(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username='testuser', password='testuser', email='testuser@gmail.com', user_type=1, is_register=1)
#         self.client = APIClient()
#         self.url=reverse('evaluate_sa_and_ma_answers')
#         self.subject = Subject.objects.create(subject_name="Springboot")
#         self.subject2 = Subject.objects.create(subject_name="Computer")
#         self.exam=Exam.objects.create(name="sample exam", scheduled_time= "2026-01-18T12:00:00Z",organization_id=self.user.id)
#         self.exam_subject = ExamSubjects.objects.create(exam=self.exam,subject=self.subject,time_duration=30,difficulty_level=2,question_count=5,pass_percentage=50)
#         self.exam_subject2 = ExamSubjects.objects.create(exam=self.exam,subject=self.subject2,time_duration=30,difficulty_level=2,question_count=5,pass_percentage=50)
#         self.candidate = Candidate.objects.create(name="Hermoine",email="hermoine@gmail.com",exam=self.exam)
#         self.exam_candidate = ExamCandidate.objects.create(candidate=self.candidate, exam_subject=self.exam_subject)

#         self.single_answer_question = Questions.objects.create( question_description="What is 2 + 2 in sprinboot?",
#             difficulty_level=1,
#             answer_type=1,
#             subject_id=self.subject,
#             marks=5,
#             is_drafted=False,)
        
#         self.single_answer_question2 = Questions.objects.create( question_description="What is Computer?",
#             difficulty_level=1,
#             answer_type=1,
#             subject_id=self.subject2,
#             marks=5,
#             is_drafted=False,)
        
#         self.single_answer_option1 = QuestionOptions.objects.create(
#             question=self.single_answer_question,
#             options="3",
#             is_answer=False,
#         )
#         self.single_answer_option2 = QuestionOptions.objects.create(
#             question=self.single_answer_question,
#             options="4",
#             is_answer=True,
#         )

#         self.single_answer_option2_1 = QuestionOptions.objects.create(
#             question=self.single_answer_question2,
#             options="3",
#             is_answer=False,
#         )
#         self.single_answer_option2_2 = QuestionOptions.objects.create(
#             question=self.single_answer_question2,
#             options="4",
#             is_answer=True,
#         )
#         self.multiple_answer_question = Questions.objects.create(
#             question_description="Which of the following are colors?",
#             difficulty_level=1,
#             answer_type=2,
#             subject_id=self.subject,
#             marks=5,
#             is_drafted=False,
#         )
#         self.multiple_answer_option1 = QuestionOptions.objects.create(
#             question=self.multiple_answer_question,
#             options="Red",
#             is_answer=True,
#         )
#         self.multiple_answer_option2 = QuestionOptions.objects.create(
#             question=self.multiple_answer_question,
#             options="Green",
#             is_answer=True,
#         )
#         self.multiple_answer_option3 = QuestionOptions.objects.create(
#             question=self.multiple_answer_question,
#             options="Blue",
#             is_answer=False,
#         )

#         self.multiple_answer_option4 = QuestionOptions.objects.create(
#             question=self.multiple_answer_question,
#             options="Grey",
#             is_answer=False,
#         )


#     def test_evaluate_single_answer(self):
#         self.client.force_authenticate(user=self.user)
#         candidate_answer = CandidateAnswers.objects.create(
#             question=self.single_answer_question,
#             exam_candidate=self.exam_candidate,
#             Selective_answer=self.single_answer_option2,
#             marks_scored=0,
#             is_correct=None
#         )
#         data={'candidate_id':self.candidate.id}
#         response = self.client.post(self.url,data,format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['message'], "Marks calculated successfully")
#         candidate_answer.refresh_from_db()
#         self.assertEqual(candidate_answer.marks_scored, 5)
#         self.assertTrue(candidate_answer.is_correct)

#     def test_evaluate_multiple_answer(self):
#         self.client.force_authenticate(user=self.user)
#         candidate_answer = CandidateAnswers.objects.create(
#             question=self.multiple_answer_question,
#             exam_candidate=self.exam_candidate,
#             Selective_answer=self.multiple_answer_option1,
#             marks_scored=0,
#             is_correct=None
#         )
#         candidate_answer2 = CandidateAnswers.objects.create(
#             question=self.multiple_answer_question,
#             exam_candidate=self.exam_candidate,
#             Selective_answer=self.multiple_answer_option2,
#             marks_scored=0,
#             is_correct=None,
#         )
   
#         data = {'candidate_id': self.candidate.id}
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['message'], "Marks calculated successfully")
#         candidate_answer.refresh_from_db()
#         candidate_answer2.refresh_from_db()
#         self.assertEqual(candidate_answer.marks_scored, 5)
#         self.assertTrue(candidate_answer.is_correct)
    
#         self.assertEqual(candidate_answer2.marks_scored, 5)
#         self.assertTrue(candidate_answer2.is_correct)
       


#     def test_evaluate_wrong_single_answer_choice(self):
#         self.client.force_authenticate(user=self.user)
#         candidate_answer = CandidateAnswers.objects.create(
#             question=self.single_answer_question,
#             exam_candidate=self.exam_candidate,
#             Selective_answer=self.single_answer_option1,
#             marks_scored=0,
#             is_correct=None
#         )
#         data={'candidate_id':self.candidate.id}
#         response = self.client.post(self.url,data,format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['message'], "Marks calculated successfully")
#         candidate_answer.refresh_from_db()
#         self.assertEqual(candidate_answer.marks_scored, 0)
#         self.assertTrue(candidate_answer.is_correct==False)


#     def test_evaluate_multiple_answer_wrong_choice(self):
#         self.client.force_authenticate(user=self.user)
#         candidate_answer = CandidateAnswers.objects.create(
#             question=self.multiple_answer_question,
#             exam_candidate=self.exam_candidate,
#             Selective_answer=self.multiple_answer_option3,
#             marks_scored=0,
#             is_correct=None
#         )
#         candidate_answer2 = CandidateAnswers.objects.create(
#             question=self.multiple_answer_question,
#             exam_candidate=self.exam_candidate,
#             Selective_answer=self.multiple_answer_option4,
#             marks_scored=0,
#             is_correct=None,
#         )
   
#         data = {'candidate_id': self.candidate.id}
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['message'], "Marks calculated successfully")




#     def test_candidate_or_exam_not_exist(self):
#         self.client.force_authenticate(user=self.user)
    
    
#         invalid_candidate_id = 999999  
    
#         data = {'candidate_id': invalid_candidate_id}
#         response = self.client.post(self.url, data, format='json')
    
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['error'], "Candidate or Exam does not exist")
        
  

class EvaluateFreeAnswerViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url=reverse('evaluate_free_answers')
        self.user = User.objects.create_user(
            username='testuser', password='testuser', email='testuser@gmail.com', user_type=1, is_register=1)
        self.exam=Exam.objects.create(name="sample exam", scheduled_time= "2026-01-18T12:00:00Z",organization_id=self.user.id)
        self.subject = Subject.objects.create(subject_name="Sample Subject")
        self.exam_subject = ExamSubjects.objects.create(exam=self.exam,subject=self.subject,time_duration=30,difficulty_level=2,question_count=5,pass_percentage=50)
        self.candidate = Candidate.objects.create(name="Hermoine",email="hermoine@gmail.com",exam=self.exam)
        self.exam_candidate = ExamCandidate.objects.create(candidate=self.candidate, exam_subject=self.exam_subject)

        self.question = Questions.objects.create(
            question_description="What is your favorite color?",
            difficulty_level=1,
            answer_type=3,
            subject_id=self.subject,
            marks=10,
            is_drafted=False
        )

        self.question1 = Questions.objects.create(
            question_description="What is your favorite movie?",
            difficulty_level=1,
            answer_type=3,
            subject_id=self.subject,
            marks=10,
            is_drafted=False
        )
        self.question2 = Questions.objects.create(
            question_description="Who is your favourite actress?",
            difficulty_level=1,
            answer_type=3,
            subject_id=self.subject,
            marks=10,
            is_drafted=False
        )

        self.free_answer1 = FreeAnswers.objects.create(answer="Captain America:Winter Soldier",question=self.question1)
        self.free_answer2 = FreeAnswers.objects.create(answer="Emma Watson",question=self.question2)

        self.exam_question = ExamQuestions.objects.create(exam=self.exam_subject, question=self.question)

    def test_evaluate_free_answer_correct(self):
        self.client.force_authenticate(user=self.user)
        candidate_answer=CandidateAnswers.objects.create(
            exam_candidate = self.exam_candidate,
            question = self.question,
            free_answer="Blue",
            marks_scored = 0,
            is_correct=None
        )
        response = self.client.put(self.url,[{'candidate_answer_id':candidate_answer.id,
                                              "correct":True}],format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Free answers evaluated successfully")

        candidate_answer.refresh_from_db()
        self.assertTrue(candidate_answer.is_correct)
        self.assertEqual(candidate_answer.marks_scored, 10)

    def test_evaluate_free_answer_incorrect(self):
        self.client.force_authenticate(user=self.user)
        candidate_answer =  CandidateAnswers.objects.create(
            exam_candidate=self.exam_candidate,
            question=self.question,
            free_answer="Red",
            marks_scored=0,
            is_correct=None
        )
        response = self.client.put(self.url,[{
            'candidate_answer_id':candidate_answer.id,
            'correct':False
        }],format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Free answers evaluated successfully")

        candidate_answer.refresh_from_db()
        self.assertFalse(candidate_answer.is_correct)
        self.assertEqual(candidate_answer.marks_scored, 0)


    def test_candidate_answer_not_exist(self):
        self.client.force_authenticate(user=self.user)
        
        invalid_candidate_answer_id=10000
        response = self.client.put(self.url,[{
            'candidate_answer_id': invalid_candidate_answer_id,
            'correct':False
        }],format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'],f"Candidate did not answer the question with id {invalid_candidate_answer_id}")

    # def test_calculate_percentage_with_zero_total_marks(self):
    #     self.client.force_authenticate(user=self.user)
       
    #     total_marks = 0
    #     marks_scored = 50  
    #     expected_percentage = 0

    #     view_instance = EvaluateFreeAnswerView()
    #     percentage = view_instance.calculate_percentage(total_marks, marks_scored)
    #     self.assertEqual(percentage, expected_percentage)


    def test_get_queryset(self):
        self.client.force_authenticate(user=self.user)

        candidate_answer1 =  CandidateAnswers.objects.create(
            exam_candidate=self.exam_candidate,
            question=self.question1,
            free_answer="Captain America:Winter Soldier",
            marks_scored=0,
            is_correct=None
        )
        candidate_answer2 =  CandidateAnswers.objects.create(
            exam_candidate=self.exam_candidate,
            question=self.question2,
            free_answer="Emma Watson",
            marks_scored=0,
            is_correct=None
        )
        self.url=reverse('candidate_free_answers',args=[self.candidate.id])
        response = self.client.get(self.url)
        serialized_data = CandidateAnswerSerializers([candidate_answer1, candidate_answer2], many=True).data

        print("Response Data:", response.data['results'])
        print("Serialized Data:", serialized_data[0])
        self.assertEqual(response.data["results"][0], serialized_data[0])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

   
       
       
        


    def test_no_queryset_available(self):
        self.client.force_authenticate(user=self.user)

       
        self.url=reverse('candidate_free_answers',args=[self.candidate.id])
        response = self.client.get(self.url)
      
        self.assertEqual(response.data["message"], "No free answers found")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
class TestCandidateAnswerEvaluation(unittest.TestCase):
  
    def test_evaluate_single_answer_correct(self):
    
        total_marks_scored = 0
        evaluated_questions=set()
        candidate_answer=Mock()
        question=Mock()
        question.id=1
        question.answer_type=1
        candidate_answer.question=question
        candidate_answer.Selective_answer.is_answer=True
        candidate_answer.is_correct=None
        candidate_answer.marks_scored=0
        question.marks=5
       
        total_marks_scored = candidate_answer_evalaution(total_marks_scored, evaluated_questions, candidate_answer)
        self.assertEqual(total_marks_scored, 5)
        self.assertIn(question.id, evaluated_questions)

    def test_evaluate_single_answer_incorrect(self):
    
        total_marks_scored = 0
        evaluated_questions=set()
        candidate_answer=Mock()
        question=Mock()
        question.id=1
        question.answer_type=1
        candidate_answer.question=question
        candidate_answer.Selective_answer.is_answer=False
        candidate_answer.is_correct=None
        candidate_answer.marks_scored=0
        question.marks=5
       
        total_marks_scored = candidate_answer_evalaution(total_marks_scored, evaluated_questions, candidate_answer)
        self.assertEqual(total_marks_scored, 0)
        self.assertIn(question.id, evaluated_questions)

        
    @patch('examanswers_management.views.CandidateAnswers.objects.filter')
    def test_evaluate_multiple_answer_correct(self,mock_filter):
        total_marks_scored=0
        evaluated_questions = set()
        candidate_answer = Mock()
        question = Mock()
        question.id=3
        question.answer_type=2
        option1=Mock()
        option2=Mock()
        option1.id=Mock()
        option2.id=Mock()
        option1.is_answer=True
        option2.is_answer=True
        candidate_answer.question=question
        candidate_answer.is_correct=None
        candidate_answer.marks_scored=0
        mock_filter.return_value.values_list.return_value = [1,2]

       
        mock_filter.return_value.exclude.return_value = [Mock(is_correct=None,marks_scored=0), Mock(is_correct=None,marks_scored=0)]
        question.options.filter.return_value.values_list.return_value = [1, 2]
        question.marks = 10

        total_marks_scored = candidate_answer_evalaution(total_marks_scored, evaluated_questions, candidate_answer)

        self.assertEqual(total_marks_scored, 10)
        self.assertIn(question.id, evaluated_questions)
        for other_candidate_answer in mock_filter.return_value.exclude.return_value:
           other_candidate_answer.is_correct=None
           other_candidate_answer.save.assert_called_once_with()


    @patch('examanswers_management.views.CandidateAnswers.objects.filter')
    def test_evaluate_multiple_answer_incorrect(self,mock_filter):
        total_marks_scored=0
        evaluated_questions = set()
        candidate_answer = Mock()
        question = Mock()
        question.id=3
        question.answer_type=2
        option1=Mock()
        option2=Mock()
        option1.id=Mock()
        option2.id=Mock()
        option1.is_answer=True
        option2.is_answer=True
        candidate_answer.question=question
        candidate_answer.is_correct=None
        candidate_answer.marks_scored=0
       
        

        mock_filter.return_value = Mock()
        mock_filter.return_value.values_list.return_value = [1,2]


        question.options.filter.return_value.values_list.return_value = [1, 3]

        question.marks = 10

        total_marks_scored = candidate_answer_evalaution(total_marks_scored, evaluated_questions, candidate_answer)

        self.assertEqual(total_marks_scored, 0)
        self.assertIn(question.id, evaluated_questions)
        mock_filter.return_value.update.assert_called_once_with(is_correct=False)
       


    

 



class CandidateAnswerCreateAPIViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testuser', email='testuser@gmail.com', user_type=1, is_register=1)
        self.exam=Exam.objects.create(name="sample exam", scheduled_time= "2026-01-18T12:00:00Z",organization_id=self.user.id)
        self.subject = Subject.objects.create(subject_name="Sample Subject")
        self.exam_subject = ExamSubjects.objects.create(exam=self.exam,subject=self.subject,time_duration=30,difficulty_level=2,question_count=5,pass_percentage=50)
        self.candidate = Candidate.objects.create(name="Hermoine",email="hermoine@gmail.com",exam=self.exam)
        self.exam_candidate = ExamCandidate.objects.create(candidate=self.candidate, exam_subject=self.exam_subject)

        self.question = Questions.objects.create(
            question_description="What is your favorite color?",
            difficulty_level=1,
            answer_type=3,
            subject_id=self.subject,
            marks=10,
            is_drafted=False
        )

        self.question1 = Questions.objects.create(
            question_description="What is your favorite movie?",
            difficulty_level=1,
            answer_type=2,
            subject_id=self.subject,
            marks=10,
            is_drafted=False
        )
        self.question2 = Questions.objects.create(
            question_description="Who is your favourite actress?",
            difficulty_level=1,
            answer_type=3,
            subject_id=self.subject,
            marks=10,
            is_drafted=False
        )

    def test_create_candidate_answer(self):
        url = reverse('candidateanswers-create', kwargs={'exam_subject_id': self.exam_subject.id, 'exam_candidate_id': self.candidate.id})
        data = {
            "answers": [
                {
                    "answertype": 3,
                    "answer": "Free text answer",
                    "questionid": 2
                }
                # Add more answers as needed
            ]
        }
        response = self.client.post(url, data, format='json')
        print('response : ',response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



       




        



        

        