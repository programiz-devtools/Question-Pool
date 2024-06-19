from django.shortcuts import render
from django.db.models import Q
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import CandidateAnswers
from candidatemanagement.models import Candidate, ExamCandidate
from .models import QuestionOptions, Questions
from .serializers import CandidateAnswerSerializer, CandidateAnswerSerializers
from candidatemanagement.models import Candidate, ExamCandidate
from exam_management.models import ExamSubjects, ExamQuestions, Exam
from examate_project.pagination import CustomSetPagination
from django.db.models import Sum, F
from examate_project.permissions import Consumer
from django.utils import timezone
import logging
from examate_project import messages
from examanswers_management.exceptions import CandidateNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404


logger = logging.getLogger(__name__)

class CandidateAnswerCreateAPIView(generics.CreateAPIView):
    serializer_class = CandidateAnswerSerializer

    def post(self, request, *args, **kwargs):
        try:
            answers = request.data
            exam_subject_id = self.kwargs["exam_subject_id"]
            candidate_id = self.kwargs["exam_candidate_id"]

            exam_candidate = ExamCandidate.objects.get(
                candidate_id=candidate_id, exam_subject_id=exam_subject_id
            )
            exam_candidate.end_time = timezone.now()

            exam_candidate_id = exam_candidate.id
            exam_candidate.save()

            for answer in answers:
                if "answertype" in answer:
                    answer_type = answer["answertype"]
                    if answer_type == 2 or answer_type == 1:
                        for option in answer["answer"]:
                            CandidateAnswers.objects.create(
                                Selective_answer=QuestionOptions.objects.get(id=option),
                                exam_candidate_id=exam_candidate_id,
                                question=Questions.objects.get(id=answer["questionid"]),
                            )
                    elif answer_type == 3:
                        CandidateAnswers.objects.create(
                            free_answer=answer["answer"],
                            exam_candidate_id=exam_candidate_id,
                            question=Questions.objects.get(id=answer["questionid"]),
                        )
            candidate = Candidate.objects.get(id=candidate_id)
            candidate.status = 3
            candidate.save()

            return Response(
                {"message": "Answers inserted successfully"},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def calculate_percentage(total_marks_for_subject, marks_scored_for_subject):

    if total_marks_for_subject == 0:
        return 0
    return (marks_scored_for_subject / total_marks_for_subject) * 100


def set_examsubject_outcome_status(exam_candidate, pass_percentage, percentage_scored):

    if percentage_scored >= pass_percentage:
        exam_candidate.exam_subject_outcome_status = True
    else:
        exam_candidate.exam_subject_outcome_status = False
    exam_candidate.save()


def set_exam_as_evaluated(exam_id):
   
  
    try:
        
        exam_candidates = ExamCandidate.objects.filter(exam_subject__exam_id=exam_id)

        for exam_candidate in exam_candidates:
            candidate = exam_candidate.candidate
            unchecked_questions = CandidateAnswers.objects.filter(
                exam_candidate__candidate=candidate, is_correct=None
            )

            if not unchecked_questions.exists():
                candidate.status = 4
                candidate.save()

                exam_subject = exam_candidate.exam_subject
                total_marks_for_subject = ExamQuestions.objects.filter(
                    exam=exam_subject
                ).aggregate(total_marks=Sum("question__marks"))["total_marks"]
                marks_scored_for_subject = exam_candidate.exam_subject_mark
                pass_percentage = exam_subject.pass_percentage

                percentage_scored = calculate_percentage(
                    total_marks_for_subject, marks_scored_for_subject
                )
                set_examsubject_outcome_status(
                    exam_candidate, pass_percentage, percentage_scored
                )

        exam = Exam.objects.get(id=exam_id)
        candidates_for_exam = Candidate.objects.filter(exam=exam)
        all_candidates_evaluated = all(
            candidate.status == 4 for candidate in candidates_for_exam
        )

        if all_candidates_evaluated:
            exam.status = 3
            exam.save()

    except Exception as e:
        logger.error(str(e))
        raise e


#evaluate single answer questions attended by a candidate
def evaluate_single_answer(total_marks_scored, candidate_answer, question):
        
        try:

            selected_option = candidate_answer.Selective_answer
            if selected_option.is_answer:
                if candidate_answer.is_correct is None:
                    candidate_answer.marks_scored += question.marks
                    total_marks_scored += question.marks
                    candidate_answer.is_correct = True
            else:
                candidate_answer.is_correct = False
            candidate_answer.save()
            return total_marks_scored
        
        except Exception as e:
              logger.error(f"An error occured in evaluation of single answer {str(e)}")
              raise e


def evaluate_multiple_answer(total_marks_scored, candidate_answer, question):

    try:

        selected_options = set(
            CandidateAnswers.objects.filter(
                exam_candidate=candidate_answer.exam_candidate, question=question
            ).values_list("Selective_answer__id", flat=True)
        )

        correct_options = set(
            question.options.filter(is_answer=True).values_list("id", flat=True)
        )

        if selected_options == correct_options:
            if candidate_answer.is_correct is None:
                candidate_answer.marks_scored += question.marks
                total_marks_scored += question.marks
                candidate_answer.is_correct = True
                candidate_answer.save()

                other_candidate_answers = CandidateAnswers.objects.filter(
                    exam_candidate=candidate_answer.exam_candidate,
                    question=question,
                    is_correct=None,
                ).exclude(id=candidate_answer.id)
                for other_candidate_answer in other_candidate_answers:
                    if other_candidate_answer.is_correct is None:
                        other_candidate_answer.marks_scored += question.marks
                        other_candidate_answer.is_correct = True
                        other_candidate_answer.save()
        else:
            candidate_answers_to_update = CandidateAnswers.objects.filter(
                Q(exam_candidate=candidate_answer.exam_candidate) & Q(question=question)
            )

            candidate_answers_to_update.update(is_correct=False)
        return total_marks_scored
    
    except Exception as e:
        logger.error(f"An error occured in evaluation of smultiple answer {str(e)}")
        raise e



def candidate_answer_evalaution(
    total_marks_scored, evaluated_questions, candidate_answer
):
    try:

        question = candidate_answer.question
        if question.id not in evaluated_questions:
            if question.answer_type == 1:
                total_marks_scored = evaluate_single_answer(
                    total_marks_scored, candidate_answer, question
                )

            elif question.answer_type == 2:
                total_marks_scored = evaluate_multiple_answer(
                    total_marks_scored, candidate_answer, question
                )
            evaluated_questions.add(question.id)
        return total_marks_scored
    
    except Exception as e:
        logger.error(f"Something went wrong in evaluation SA and MA{str(e)}")
        raise e


def evaluate_sa_and_ma_questions(candidate_id):
   
   
    try:
        candidate = Candidate.objects.get(id=candidate_id)
        exam = candidate.exam
        exam_subjects = exam.exam_subjects.all()
    except ObjectDoesNotExist as e:
        logger.error(f"An error occured in finding instance in evaluate SA amd MA{str(e)}")
        raise e
    
    for exam_subject in exam_subjects:
        candidate_answers = CandidateAnswers.objects.filter(
            exam_candidate__candidate=candidate,
            exam_candidate__exam_subject=exam_subject,
            is_correct=None,
        )
        total_marks_scored = 0
        evaluated_questions = set()

        for candidate_answer in candidate_answers:
            total_marks_scored = candidate_answer_evalaution(
                total_marks_scored, evaluated_questions, candidate_answer
            )

        try:
            exam_candidate = ExamCandidate.objects.get(
                candidate=candidate, exam_subject=exam_subject
            )
            if exam_candidate:
                exam_candidate.exam_subject_mark = (
                    exam_candidate.exam_subject_mark or 0
                ) + total_marks_scored
                exam_candidate.save()
        except ExamCandidate.DoesNotExist:
            pass
    try:

     set_exam_as_evaluated(exam.id)

    except Exception as e:
        logger.error(f"An error occured in evaluation of single and multiple answers {str(e)}")
        raise e

    return "Marks calculated successfully"


class CandidateFreeAnswerListView(generics.ListAPIView):
    permission_classes = [Consumer]
    serializer_class = CandidateAnswerSerializers
    pagination_class = CustomSetPagination

    def get_queryset(self):
        try:
            candidate_id = self.kwargs.get("candidate_id")
            evaluate_sa_and_ma_questions(candidate_id)
            try:
                candidate = Candidate.objects.get(id=candidate_id)
                return CandidateAnswers.objects.filter(
                    exam_candidate__candidate=candidate,
                    question__answer_type=3,
                    is_correct=None,
                )
            except Candidate.DoesNotExist:
              raise CandidateNotFound("E50002")
        except Exception as e:
            logger.error(f"An error occured in evaluation of listing free answers {str(e)}")
            return Response({"message":"An error occured in Free answer list view","error":str(e)})
            

    def list(self, request, *args, **kwargs):
        try:
            self.pagination_class.page_size=1
            queryset = self.get_queryset()
            free_answer_details = self.paginate_queryset(queryset)
            if not queryset.exists():
                return Response(
                    {"message": messages.E50001, "errorCode": "E50001"},
                    status=status.HTTP_204_NO_CONTENT
                )
            serializer = self.get_serializer(free_answer_details, many=True)
            return self.get_paginated_response(serializer.data)
        except CandidateNotFound as e:
             return Response({"message": e.message, "errorCode": e.error_code}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"message": "An error occurred", "error_details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



class EvaluateFreeAnswerView(generics.UpdateAPIView):
    permission_classes=[Consumer]

    def put(self, request, *args, **kwargs):
        try:
      
     
            data = request.data
            for entry in data:
                candidate_answer_id = entry.get("candidate_answer_id")
                correct = entry.get("correct", False)

                try:
                    candidate_answer = CandidateAnswers.objects.get(id=candidate_answer_id)
                except CandidateAnswers.DoesNotExist:
                    return Response(
                        {
                            "message": messages.E50005.format(candidate_answer_id),"errorCode":"E50005"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                exam_id = candidate_answer.exam_candidate.exam_subject.exam_id

                question = candidate_answer.question

                if question.answer_type == 3 and candidate_answer.is_correct is None:
                    if correct:
                        candidate_answer.marks_scored = question.marks
                        exam_candidate = candidate_answer.exam_candidate
                        exam_candidate.exam_subject_mark += question.marks
                        exam_candidate.save()
                    candidate_answer.is_correct = correct
                    candidate_answer.save()
            set_exam_as_evaluated(exam_id)

            return Response(
                {"message": "Free answers evaluated successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"An error occured in evaluation of free answers {str(e)}")
            return Response(
                {"message": "An error occurred", "error_details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
