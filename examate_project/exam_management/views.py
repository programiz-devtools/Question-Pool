from django.shortcuts import render
from django.db import transaction
from rest_framework import generics, status
from rest_framework import serializers
from rest_framework.response import Response
from .models import Exam, ExamQuestions, ExamSubjects, Feedback
from examate_project.permissions import Consumer
from rest_framework.exceptions import PermissionDenied
from question_management.models import Questions
from subject_management.models import Subject
from ticket_management.models import Ticket
from .serializers import (
    ExamSerializer,
    ExamQuestionsSerializer,
    ExamSubjectsSerializer,
    FeedbackSerializer,
    ExamSubjectsListSerializer,
    ExamSubjectsSerializerWithSubjectName,
    DashboardExamListSerializer,
)
import random
from rest_framework.views import APIView
from unittest.mock import patch
from unittest import mock
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags
from examate_project.pagination import CustomSetPagination
from rest_framework import filters
from datetime import datetime, timedelta
from rest_framework.views import APIView
import jwt
from django.conf import settings
from rest_framework.generics import ListAPIView
from question_management.models import Questions
from question_management.serializers import QuestionSerializer
from django.db.models import Count
from rest_framework.views import APIView
from question_management.models import QuestionOptions, FreeAnswers
from question_management.serializers import (
    FreeAnswerSerializer,
    QuestionOptionSerializer,
)

from django.db.models import Count, F, FloatField
from datetime import date
from rest_framework.filters import OrderingFilter, SearchFilter
from django.http import HttpResponse
import csv
from candidatemanagement.models import Candidate, ExamCandidate
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
import io
from examate_project.exceptions import (
    ExamNotUpdatable,
    NoSubjectsProvidedException,
    DuplicateSubjectException,
    MaxSubjectsExceededException,
    SubjectValidationError,
    ValidationErrorMessage,
    InsufficientTicketsException,
    NoScheduleTime
    
)

from django.db.models import Sum
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import datetime as dt
from reportlab.pdfgen import canvas
from io import BytesIO
from .messages import E40300,E40301,E40302,E40303,E40304,E40305,E40307
from rest_framework.exceptions import ValidationError

from examate_project import messages
from django.http import Http404


buffer = BytesIO()
import logging


logger = logging.getLogger(__name__)


DIFFICULTY_LEVEL_CHOICE = ((1, "easy"), (2, "medium"), (3, "difficult"))

# Function to handle serializer validation errors and unexpected errors
def handle_validation_error(e):
    response={}
   
    try:
        error_code = str(e).split("ErrorDetail(string='")[1].split("'")[0]
        error_message=getattr(messages,error_code)
        transaction.set_rollback(True)

      
        return Response(
                {"message": error_message, "errorCode": error_code},
                status=status.HTTP_400_BAD_REQUEST,
            )
     
           
    except Exception as e:
        response["message"]=messages.E00500
        response["errorCode"]="E00500"
        logger.error(f"An error occured in handle validation error function at exam view - {str(e)}")
      
        return Response(
            
           response,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
 
        )
    

# Function to check if subject data is empty
def is_subject_data_empty(subject_data,status_field):
       

        if not subject_data and status_field == 1:
            raise NoSubjectsProvidedException(
                "E40015"
            )

# Function to validate subject data on publishing
def is_valid_subject(subject_id,other_data_values,status_field):
   
   
    msg = ""
    if status_field==0 and subject_id==0:
          if all(value[1] == 0 for value in other_data_values if value[1] is not None):
              return
    if subject_id==0:
        msg="E40016"
        raise SubjectValidationError(msg)
    for key, value in other_data_values:
        if value == 0 :
                msg = "E40017"
                raise SubjectValidationError(msg,key)
        



               
 # Function to validate subject data on publishing         
def validate_subject_data_on_publish(subjects_data):
   
    error_messages = {
        "time_duration": "E40011",
        "pass_percentage": "E40012",
        "question_count": "E40013",
        "difficulty_level": "E40014",
        "subject": "E40016"
    }

    for subject_data in subjects_data:
        for key, value in subject_data.items():
            if key in error_messages and value == "":
                raise SubjectValidationError(error_messages[key])


            
# Function to handle subject duplication validation
def validate_subject_duplication(subject_id, subject_name, encountered_subject_ids):

        if subject_id in encountered_subject_ids:

            raise DuplicateSubjectException(
                "E40018",params=subject_name
            )
        
# Function to convert empty strings to zero in subject data      
def from_empty_string_to_zero(subject_data):
       
       
        for key, value in subject_data.items():
             if value == '':
                 subject_data[key] = 0
                 if key=="difficulty_level" and value=='':
                     subject_data[key]=None
        return subject_data


# Function to generate questions for a subject of exam
def generate_questions_for_subject(exam_subjects_instances):
       
        try:

  
    
            for exam_subject in exam_subjects_instances:
                if exam_subject.question_count == 0:
                    raise SubjectValidationError("E40019",exam_subject.subject.subject_name)

                ExamQuestions.objects.filter(exam=exam_subject).delete()

                questions = Questions.objects.filter(
                    subject_id_id=exam_subject.subject_id,
                    difficulty_level=exam_subject.difficulty_level,
                    is_drafted=False,
                )


                questions = list(questions)
                random.shuffle(questions)
                selected_questions = questions[:exam_subject.question_count]
                for question in selected_questions:
                    ExamQuestions.objects.create(exam=exam_subject, question=question)
        except SubjectValidationError as e:
            raise e
        except Exception as e:
            logger.error(f"An error occured in question generation -  {str(e)}")


def get_difficulty_level_value(difficulty_level):
   
    for level, level_value in DIFFICULTY_LEVEL_CHOICE:
        if difficulty_level == level:
            return level_value


def validate_subject(subject_instance, difficulty_level, requested_question_count):

 
    if not Questions.objects.filter(
        subject_id=subject_instance.id, is_drafted=False
    ).exists():
        return "E40020",(subject_instance.subject_name,)

    if not Questions.objects.filter(subject_id=subject_instance.id,
        difficulty_level=difficulty_level, is_drafted=False
    ).exists():
        difficulty_level_value = get_difficulty_level_value(difficulty_level)
        return "E40021", (difficulty_level_value, subject_instance.subject_name)

    if requested_question_count > subject_instance.question_count:
        return "E40022",(subject_instance.subject_name,)
    
    return None, None
    
def validate_subject_count(existing_subjects_count):
    

        if existing_subjects_count >= 3:
            raise MaxSubjectsExceededException(
                "E40023"
            )
def validate_question_availabilty(validation_error_message,params):
      
        if validation_error_message:
            raise ValidationErrorMessage(validation_error_message,params)
        

 # Function to validate ticket availability       
def validate_ticket_availabilty(total_questions_count,user_tickets_count):
   
   
    additional_tickets_needed = ((total_questions_count+9)//10)-user_tickets_count
    if additional_tickets_needed > 0:
        if additional_tickets_needed == 1:
            error_code = "E40024"
        else:
            error_code = "E40025"

        raise InsufficientTicketsException(error_code,additional_tickets_needed)
    
    
 # Function to update ticket status   
def update_ticket_status(request, updated_tickets, exam, total_questions_count):
        
      
        try:

            user_tickets =request.user.ticket_set.filter(status=1)[:(total_questions_count+9)//10]
            for ticket in user_tickets:
                ticket.status = 2
                ticket.exam=exam
                updated_tickets.append(ticket)
            Ticket.objects.bulk_update(updated_tickets, ['status', 'exam'])
        except Exception as e:
            logger.error(f"An error occured in updation of ticket status - {str(e)}")
            raise e

        

 # Function to update subject exam count 

def update_subject_count(subjects_data):
    try:

        for subject_data in subjects_data:
            subject_id = subject_data.get("subject")
            if subject_id:
                subject=Subject.objects.get(id=subject_id)
                subject.exam_count+=1
                subject.save()
    except Exception as e:
        logger.error(f"An error occured in updation of subject count-{str(e)}")
        raise e



class ExamCreationView(generics.CreateAPIView):
    permission_classes = [Consumer]
    
    #return success response based on status
    def return_success_response(self,status_field):
        if status_field==0:
             return Response(
                        {"message": "Exam Created Successfully"},
                        status=status.HTTP_201_CREATED,
                    )
        else:

           return Response(
                        {"message": "Exam Published Successfully"},
                        status=status.HTTP_200_OK,
                    )
    
    #validate the time recieved from user   
    def schedule_time_required(self,request):
        if not request.data.get('scheduled_time') or request.data.get('scheduled_time')=="" :
                        raise NoScheduleTime("E40027")
                   



   

    def create(self, request):
       
        
        response={}
    

    
        subjects_data = request.data.get("subjects", [])
        status_field = request.data.get("status",0)
        exam_serializer = ExamSerializer(data=request.data, context={'status': status_field})
        encountered_subject_ids = set()
        exam_subjects_instances = [] 
        updated_tickets = []

        with transaction.atomic():
           
            try:
               
                is_subject_data_empty(subjects_data,status_field)
                exam_serializer.is_valid(raise_exception=True)
                if status_field==0 and not subjects_data:
                    exam = Exam.objects.create(
                    name=request.data["name"],
                    scheduled_time = exam_serializer.validated_data.get('scheduled_time', None),
                    organization_id=request.user.id,
                    instructions=request.data.get("instructions",None),
                    status = status_field
                )
                    return Response(
                        {"message": "Exam Created Successfully"},
                        status=status.HTTP_201_CREATED,
                    )
                elif status_field==1:
                    self.schedule_time_required(request)
                    
                    validate_subject_data_on_publish(subjects_data)
               
                
                total_time_duration = 0
                total_questions_count = 0
                exam = Exam.objects.create(
                    name=request.data["name"],
                    scheduled_time=exam_serializer.validated_data['scheduled_time'],
                    organization_id=request.user.id,
                    instructions=request.data["instructions"],
                    status = status_field
                )
                for subject_data in subjects_data:
                    subject_data=from_empty_string_to_zero(subject_data)

                    subject_id = int(subject_data.get("subject"))
                    other_subject_data_values=[(key,value) for key,value in subject_data.items() if key!='subject']

                    is_valid_subject(subject_id, other_subject_data_values,status_field)
    
                    if subject_id == 0:
                         continue
    
                    subject_name = Subject.objects.get(id=subject_id).subject_name

                    validate_subject_duplication(subject_id, subject_name, encountered_subject_ids)

                    encountered_subject_ids.add(subject_id)
                    exam_subject_serializer = ExamSubjectsSerializer(data=subject_data,context={"status":status_field})
                    try:
                       
                       
                        exam_subject_serializer.is_valid(raise_exception=True)
                        subject_instance = exam_subject_serializer.validated_data[
                            "subject"
                        ]
                        requested_question_count = int(subject_data["question_count"])

                        validation_error_message,params = validate_subject(
                            subject_instance,subject_data["difficulty_level"], requested_question_count
                        )
                        validate_question_availabilty(validation_error_message,params)

                        existing_subjects_count = ExamSubjects.objects.filter(
                            exam=exam
                        ).count()
                        validate_subject_count(existing_subjects_count)

                        exam_subject = ExamSubjects.objects.create(
                            exam=exam,
                            subject=subject_instance,
                            time_duration=subject_data["time_duration"],
                            pass_percentage=subject_data["pass_percentage"],
                            difficulty_level=subject_data["difficulty_level"],
                            question_count=requested_question_count,
                        )
                        total_time_duration += int(exam_subject.time_duration)
                        total_questions_count += int(exam_subject.question_count)
                        exam_subjects_instances.append(exam_subject)
                        

                    except serializers.ValidationError as e:
                       logger.error(f"Exam seriliazer validation error occured-{str(e)}")
                       return handle_validation_error(e)
                user_tickets_count = request.user.ticket_set.filter(status=1).count()
                if status_field==1:
                            
                            validate_ticket_availabilty(total_questions_count,user_tickets_count)
                            generate_questions_for_subject(exam_subjects_instances)
                            update_ticket_status(request, updated_tickets, exam, total_questions_count)
                            update_subject_count(subjects_data)
                            

                exam.exam_duration = total_time_duration
                exam.save()
                


                return self.return_success_response(status_field)  
            except ValueError as e:
                logger.error(f"Value error occcured-{str(e)}")
                error_message, error_code = str(e).split("+")
                
                return Response({"message": error_message, "errorCode": error_code}, status=status.HTTP_400_BAD_REQUEST)
            except (
            NoSubjectsProvidedException,
            DuplicateSubjectException,
            MaxSubjectsExceededException,
            SubjectValidationError,
            ValidationErrorMessage,
             NoScheduleTime
           ) as e:
                 transaction.set_rollback(True)
                 return Response({"message": e.message, "errorCode": e.error_code}, status=status.HTTP_400_BAD_REQUEST)
            except InsufficientTicketsException as e:
                transaction.set_rollback(True)
                return Response({"message": e.message, "errorCode": e.error_code}, status=status.HTTP_400_BAD_REQUEST)
            except serializers.ValidationError as e:
                 
                  return handle_validation_error(e)
            
            except Exception as e:
                response["errorCode"]="E00501"
                response["message"]=messages.E00501
                logger.error(f"An error occured in creation of exam - {str(e)}")
                return Response(response,status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

  


class ExamUpdationView(generics.UpdateAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [Consumer]

    #check if exam is published or not before update
    def is_exam_updatable(self, exam_instance,status_field):
      
        if exam_instance.status not in [0]:
            if status_field==0:
                  raise ExamNotUpdatable("E40009")
            elif status_field==1:
                 raise ExamNotUpdatable("E40010")


          
    #update the fields of exam
    def exam_details_update(self, request, exam_instance, status_field):
        exam_instance.name = request.data.get("name", exam_instance.name)
        exam_instance.scheduled_time = request.data.get("scheduled_time", exam_instance.scheduled_time)
        exam_instance.status = status_field
        exam_instance.instructions = request.data.get("instructions")
        exam_instance.save()

   
    #process the subjects of exam for updation
    def process_exam_subject(self, exam_instance, subject_data, status_field, encountered_subject_ids):
       
        subject_id = int(subject_data.get("subject"))
        if subject_id == 0:
            return
        
        subject_name = Subject.objects.get(id=subject_id).subject_name
        validate_subject_duplication(subject_id, subject_name, encountered_subject_ids)
        encountered_subject_ids.add(subject_id)

        try:
            exam_subject_instance = ExamSubjects.objects.get(exam=exam_instance, subject=subject_data["subject"])
            subject_duration,requested_question_count = self.update_existing_exam_subject(exam_subject_instance, subject_data, status_field)
            return subject_duration,requested_question_count
        
        except ExamSubjects.DoesNotExist:
            new_subject_time_duration,requested_question_count = self.create_new_exam_subject(exam_instance, subject_data, status_field)
            return new_subject_time_duration,requested_question_count

    #update the field of existing subjects
    def update_existing_exam_subject(self, exam_subject_instance, subject_data, status_field):
        exam_subject_serializer = ExamSubjectsSerializer(instance=exam_subject_instance, data=subject_data, context={"status": status_field})
        exam_subject_serializer.is_valid(raise_exception=True)

        difficulty_level = subject_data["difficulty_level"]
        requested_question_count = int(subject_data["question_count"])

        subject_instance = exam_subject_instance.subject
        validation_error_message,params = validate_subject(subject_instance, difficulty_level, requested_question_count)
        validate_question_availabilty(validation_error_message,params)

       

        exam_subject_instance.time_duration = subject_data["time_duration"]
        exam_subject_instance.pass_percentage = subject_data["pass_percentage"]
        exam_subject_instance.difficulty_level = difficulty_level
        exam_subject_instance.question_count = requested_question_count

        exam_subject_instance.save()
        return  subject_data["time_duration"],requested_question_count
    
    #create a new exam subject for a exam
    def create_new_exam_subject(self, exam_instance, subject_data, status_field):
        exam_subject_serializer = ExamSubjectsSerializer(data=subject_data, context={"status": status_field})
        exam_subject_serializer.is_valid(raise_exception=True)

        subject_instance = exam_subject_serializer.validated_data["subject"]
        existing_subjects_count = ExamSubjects.objects.filter(exam=exam_instance).count()
        validate_subject_count(existing_subjects_count)

        validation_error_message,params = validate_subject(subject_instance, subject_data["difficulty_level"], int(subject_data["question_count"]))
        validate_question_availabilty(validation_error_message,params)

        new_exam_subject_instance = exam_subject_serializer.save(exam=exam_instance)
       
        return new_exam_subject_instance.time_duration,new_exam_subject_instance.question_count
    
    #delete existing subjects of exam which is not in request 
    def delete_existing_subjects(self, subjects_data, existing_subjects):
        subjects_to_delete = existing_subjects.exclude(subject__in=[subject_data["subject"] for subject_data in subjects_data])
        for subject_to_delete in subjects_to_delete:
            ExamQuestions.objects.filter(exam=subject_to_delete).delete()
        subjects_to_delete.delete()

    def update(self, request, *args, **kwargs):
       

        response={}

        exam_instance = self.get_object()
        exam_serializer = self.get_serializer(exam_instance, data=request.data, partial=True)
        subjects_data = request.data.get("subjects", [])
        status_field = request.data.get('status', 0)
        encountered_subject_ids = set()
        updated_tickets=[]

        try:
            self.is_exam_updatable(exam_instance,status_field)
        except ExamNotUpdatable as e:
            return Response({"message": e.message, "errorCode": e.error_code}, status=status.HTTP_400_BAD_REQUEST)


        with transaction.atomic():
            try:
                is_subject_data_empty(subjects_data, status_field)
                exam_serializer.is_valid(raise_exception=True)
                total_time_duration = 0
                total_questions_count = 0
                self.exam_details_update(request, exam_instance, status_field)

                if status_field == 0 and not subjects_data:
                    return Response({"message": "Exam Updated Successfully"}, status=status.HTTP_200_OK)
                elif status_field == 1:
                    validate_subject_data_on_publish(subjects_data)

                for subject_data in subjects_data:
                
                    subject_data = from_empty_string_to_zero(subject_data)
                    subject_id = int(subject_data.get("subject"))
                  
                    if subject_id==0:
                        continue
                    subject_total_time_duration,subject_question_count=self.process_exam_subject(exam_instance, subject_data, status_field, encountered_subject_ids)
                    total_time_duration += int(subject_total_time_duration)
                    total_questions_count += int(subject_question_count)


                exam_instance.exam_duration =  total_time_duration
                exam_instance.save()
                if exam_instance.status == 1:
                    user_tickets_count = request.user.ticket_set.filter(status=1).count()
                    exam_subjects = ExamSubjects.objects.filter(exam=exam_instance)
                    validate_ticket_availabilty(total_questions_count,user_tickets_count)
                    generate_questions_for_subject(exam_subjects)
                    update_ticket_status(request, updated_tickets, exam_instance, total_questions_count)
                    update_subject_count(subjects_data)
                    

 
                existing_subjects = ExamSubjects.objects.filter(exam=exam_instance)
                self.delete_existing_subjects(subjects_data, existing_subjects)

            
                if exam_instance.status == 1:  
                    return Response({"message": "Exam Updated and Published Successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Exam Updated Successfully"}, status=status.HTTP_200_OK)
            except (NoSubjectsProvidedException, DuplicateSubjectException, MaxSubjectsExceededException, SubjectValidationError, ValidationErrorMessage,ValueError) as e:
                transaction.set_rollback(True)
                return Response({"message": e.message, "errorCode": e.error_code}, status=status.HTTP_400_BAD_REQUEST)
               
            except InsufficientTicketsException as e:
                transaction.set_rollback(True)
                return Response({"message": e.message, "errorCode": e.error_code}, status=status.HTTP_400_BAD_REQUEST)
            
            except serializers.ValidationError as e:
                   return handle_validation_error(e)
            
            except Exception as e:
                response["errorCode"]="E00502"
                response["message"]=messages.E00502
                logger.error(f"An error occured in exam updation view-{str(e)}")
                return Response(response,status=status.HTTP_500_INTERNAL_SERVER_ERROR)

   
class ExamListView(generics.ListAPIView):
    serializer_class = ExamSerializer
    pagination_class = CustomSetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = [
        "name",
        "scheduled_time",
        "exam_duration",
        "status",
        "candidate_count",
    ]
    search_fields = ["name"]

    def get_queryset(self):

        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be authenticated to access this resource.")
        
        queryset = Exam.objects.filter(organization=self.request.user, status__gt=-1).order_by('-scheduled_time')
        status_param = self.request.query_params.get("status")
        if status_param is not None:
            queryset = queryset.filter(status=status_param)
        # Apply search filter
        search_query = self.request.query_params.get("search", None)
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        
        return queryset

    def list(self, request, *args, **kwargs):
        try:
            page_size=5
            self.pagination_class.page_size=page_size
            ordering_param = request.query_params.get("ordering")
            if ordering_param and ordering_param.lstrip('-') not in self.ordering_fields:
                return Response({"messages":messages.E43001,"errorCode":"E43001"}, status=status.HTTP_400_BAD_REQUEST)
            
            queryset = self.filter_queryset(self.get_queryset())
            
            if not queryset.exists():
                return Response({"message": messages.E43002,"errorCode":"E43002"}, status=status.HTTP_404_NOT_FOUND)
            
            exams = self.paginate_queryset(queryset)
            serialized_data = self.get_serializer(exams, many=True).data
            return self.get_paginated_response(serialized_data)
        except Exception as e:
            return self.handle_exception(e)
                
class SoftDeleteView(generics.UpdateAPIView):
    serializer_class = ExamSerializer

    def get_object(self):
        instance_id = self.kwargs["pk"]
        return Exam.objects.get(id=instance_id)

    def update(self, request, *args, **kwargs):

        try:
            instance = self.get_object()

            if instance.status != 0:
                return Response(
                    {"message": messages.E43004,"errorCode":"E43004"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
                
            else:
                instance.status = -1  # Soft delete by updating the status
                instance.save()
                return Response(
                    {"message": messages.E43003,"errorCode":"E43003"},
                    status=status.HTTP_204_NO_CONTENT,
                )
                
        except Exam.DoesNotExist:
            return Response(
                {"message": messages.E40028,"errorCode":"E40028"},
                status=status.HTTP_404_NOT_FOUND,
            )

class ExamSubjectTimeDurationView(APIView):
    def get(self, request, exam_subject_id):
        try:
            exam_subject = ExamSubjects.objects.get(id=exam_subject_id)
            serializer = ExamSubjectsSerializer(exam_subject)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ExamSubjects.DoesNotExist:
            return Response(
                {"message": "Exam subject not found."}, status=status.HTTP_404_NOT_FOUND
            )


class ExamScheduledTimeView(APIView):
    def get(self, request, exam_id):
        try:
            exams = Exam.objects.get(id=exam_id)
            serializer = ExamSerializer(exams)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ExamSubjects.DoesNotExist:
            return Response(
                {"message": "Exam not found."}, status=status.HTTP_404_NOT_FOUND
            )


class FeedbackAPIView(APIView):
    pagination_class = CustomSetPagination

    def post(self, request):

        data = request.data
        exam_id = data.get("exam")
        candidate_id = data.get("candidate")
        feedback = data.get("feedback")
        rating = data.get("rating")
        if not exam_id:
            return Response(
                {"message": messages.E44001,"errorCode":"E44001"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate candidate_id
        if not candidate_id:
            return Response(
                {"message":messages.E44002,"errorCode":"E44002"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
             Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return Response(
                {"message": messages.E44009,"errorCode":"E44009"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate candidate_id exist
        try:
            Candidate.objects.get(id=candidate_id)
        except Candidate.DoesNotExist:
            return Response(
                {"message": messages.E44010,"errorCode":"E44010"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Validate feedback_text
        if not feedback:
            return Response(
                {"message": messages.E44003,"errorCode":"E44003"},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif len(feedback) < 2:
            return Response(
                {"message": messages.E44004,"errorCode":"E44004"},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif len(feedback) > 255:
            return Response(
                {"message": messages.E44005,"errorCode":"E44005"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not rating:
            return Response(
                {"message":messages.E44007,"errorCode":"E44007"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Validate rating
        rating = float(rating)
        valid_ratings = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
        if rating not in valid_ratings:
            return Response(
                {"message": messages.E44006,"errorCode":"E44006"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create and save Feedback object
        feedback = Feedback.objects.create(
            exam_id=exam_id, candidate_id=candidate_id, feedback=feedback, rating=rating
        )

        return Response(
            {"message": "Feedback saved successfully"}, status=status.HTTP_201_CREATED
        )

    def get(self, request, exam_id):
        # Retrieve feedback for candidates where the associated exam status is "completed"
        try:
            page_size=5
            self.pagination_class.page_size=page_size
            completed_exams = Exam.objects.filter(id=exam_id, status__gte=2)
            if not completed_exams.exists():
                return Response(
                    {"message": messages.E44008,"errorCode":"E44008"}, status=status.HTTP_404_NOT_FOUND
                )

            feedbacks = Feedback.objects.filter(candidate__exam__in=completed_exams)
            paginator = CustomSetPagination()
            paginated_feedbacks = paginator.paginate_queryset(feedbacks, request)
            serializer = FeedbackSerializer(paginated_feedbacks, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class ExamSubjectsListView(ListAPIView):
    serializer_class = ExamSubjectsListSerializer

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        print("token : ", auth_header)

    def get_queryset(self):
        exam_id = self.kwargs["exam_id"]
        return ExamSubjects.objects.filter(exam_id=exam_id)


class ExamDetailView(generics.RetrieveAPIView):
    def get(self, request, examid):
        exam = get_object_or_404(Exam, id=examid)
        exam_subjects = ExamSubjects.objects.filter(exam=exam)
        scheduled_time = exam.scheduled_time

        if scheduled_time:
            scheduled_time_only = scheduled_time.timestamp()
            scheduled_date_only = scheduled_time.date()

            current_date = datetime.today().date()
            if (current_date >= scheduled_date_only) and (
                datetime.now().timestamp() > scheduled_time_only
            ) and exam.status in [0,1]:
                
                exam.status = 2
                exam.save()

        response_data = {
            "name": exam.name,
            "scheduled_time": exam.scheduled_time,
            "status": exam.status,
            "candidate_count": exam.candidate_count,
            "subjects": [
                {
                    "id": subject.id,
                    "subject": subject.subject.id,
                    "time_duration": subject.time_duration,
                    "pass_percentage": subject.pass_percentage,
                    "difficulty_level": subject.difficulty_level,
                    "question_count": subject.question_count,
                    "subjectname": subject.subject.subject_name,
                }
                for subject in exam_subjects
            ],
        }

        return Response(response_data, status=status.HTTP_200_OK)

class BaseExamView(APIView):

    #function to return details of exam
    def get_exam_data(self, exam):
        exam_subjects = ExamSubjects.objects.filter(exam=exam)

        return {
            "exam_id": exam.id,
            "name": exam.name,
            "scheduled_time": exam.scheduled_time,
            "exam_duration": exam.exam_duration,
            "instructions": exam.instructions,
            "organization_name": exam.organization.username,
            "subjects": [
                {
                    "subject": subject.subject.id,
                    "subject_name": subject.subject.subject_name,
                    "time_duration": subject.time_duration,
                    "pass_percentage": subject.pass_percentage,
                    "difficulty_level": subject.difficulty_level,
                    "question_count": subject.question_count,
                }
                for subject in exam_subjects
            ],
        }


class ExamDetailViews(BaseExamView):
    def get(self, request, examid):
        try:
            exam = get_object_or_404(Exam, id=examid)
            response_data = self.get_exam_data(exam)
            return Response(response_data, status=status.HTTP_200_OK)
        except Http404:
            return Response({"message":messages.E40028,"errorCode":"E40028"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EndUserExamView(BaseExamView):
    def post(self, request, *args, **kwargs):

        try:
            token = request.data.get("token")
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
            exam_id_from_token = decoded_token.get("exam_id")
            exam = get_object_or_404(Exam, id=exam_id_from_token)
            response_data = self.get_exam_data(exam)
            return Response(response_data, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            return Response({"expired": True}, status=status.HTTP_200_OK)
        except jwt.InvalidTokenError:
            return Response(
                {"error":messages.E40029,"errorCode":"E40029"}, status=status.HTTP_400_BAD_REQUEST
            )


class ExamQuestionView(generics.ListAPIView):

    def get(self, request, exam_subject_id):
        try:

            exam_questions = ExamQuestions.objects.filter(exam=exam_subject_id).all()
            if not exam_questions:
                return Response(
                    {"message":E40300,"errorCode":"E40300"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            question_ids = [
                exam_question.question_id for exam_question in exam_questions
            ]
            questions = Questions.objects.filter(id__in=question_ids)
            question_serializer = QuestionSerializer(questions, many=True)
            response_data = {"questions": question_serializer.data}

            answers = []
            for question in questions:
                if question.answer_type == 3:
                    free_answer = FreeAnswers.objects.get(question=question)
                    free_answer_serializer = FreeAnswerSerializer(free_answer)
                    answers.append(free_answer_serializer.data)
                elif question.answer_type in [1,2]:
                    options = QuestionOptions.objects.filter(question=question)
                    option_serializer = QuestionOptionSerializer(options, many=True)
                    answers.append(option_serializer.data)
                else:
                    answers[question.id] = None

            response_data["answers"] = answers
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return Response(
                {"error": "An error occurred while processing the request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



class RegenarateQuestionView(generics.ListAPIView):
  def get(self, request, *args, **kwargs):
    try:
      subject_id = self.kwargs.get("subject_id")
      exam_id = self.kwargs.get("exam_id")
      exam = Exam.objects.get(id=exam_id)
     

      current_time = int(datetime.now().timestamp())
      exam_scheduled_time =exam.scheduled_time 
      scheduled_time= int(exam_scheduled_time.timestamp())

      if current_time > scheduled_time:
        return Response(
            {"message": E40307, "errorCode": "E40307"},
            status=status.HTTP_400_BAD_REQUEST,
        )
      else:
        exam_subject = ExamSubjects.objects.get(
        subject_id=subject_id, exam_id=exam_id
      )
        exam_subject_instances = []
        exam_subject_instances.append(exam_subject)
        generate_questions_for_subject(exam_subject_instances)
        return Response(
            {"message": "Question regenerated successfully"},
            status=status.HTTP_200_OK,
        )
    except Exception:
      return Response(
          {"message": E40301, "errorCode": "E40301"},
          status=status.HTTP_400_BAD_REQUEST,
      )


class SubjectPopularityView(APIView):
    def get(self, request, format=None):
        try:
            total_count = ExamSubjects.objects.count()
            subject_popularity = (
                ExamSubjects.objects.values("subject")
                .annotate(
                    popularity=Count("subject"),
                    percentage=100 * F("popularity") / total_count,
                )
                .order_by("-popularity")
            )

            subject_popularity_list = []
            for item in subject_popularity:
                subject_id = item["subject"]
                subject_name = Subject.objects.get(pk=subject_id).subject_name
                item["subject_name"] = subject_name
                subject_popularity_list.append(item)

            return Response(subject_popularity_list, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "An error occurred while processing the request.","errorDetails":e},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        


class PendingEvaluationListView(ListAPIView):
    serializer_class = ExamSerializer
    filter_backends = [OrderingFilter, SearchFilter]
    pagination_class = CustomSetPagination
    ordering_fields = [
        "name",
        "scheduled_time",
        "exam_duration",
        "status",
        "candidate_count",       
    ]
    search_fields = ["name"]

    def get_queryset(self):
       
        user_id = self.request.user
        current_time=int(datetime.now().timestamp())
        queryset = Exam.objects.filter(candidate_count__gt=0,
                                        scheduled_time__gte=current_time - F('exam_duration'), organization_id=user_id).exclude(status__in=[3, 4]) 

        search_param = self.request.query_params.get("searchparam", None)
        if search_param is not None:
            queryset = queryset.filter(name__contains=search_param)
            if not queryset.exists():
                raise ValidationError(
                    {"message": E40302,"errorCode":"E40302"}
                )
        ordering = self.request.query_params.get("ordering")
        if ordering is not None:
            if ordering or ordering.lstrip('-') not in self.ordering_fields:
                queryset = queryset.order_by(ordering)
            else:
                raise ValidationError(
                    {"message": E40303,"errorCode":"E40303"}
                )

        return queryset



class DownloadMarkListView(APIView):

    def get(self, request, exam_id):
        try:
            exam = Exam.objects.get(pk=exam_id)
            candidates = Candidate.objects.filter(status__in=[4, 5], exam=exam)
            if not candidates:
                return Response(
                    {"message":E40305,"errorCode":"E40305"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            subjects_queryset = ExamSubjects.objects.filter(exam=exam)
            subjects = list(subjects_queryset)
            bufferlist = io.BytesIO()
            c = canvas.Canvas(bufferlist, pagesize=letter)
            styles = getSampleStyleSheet()
            ParagraphStyle(
                name="ExamName",
                fontSize=14,
                alignment=0,
                spaceAfter=5,
            )
            exam_name_paragraph = Paragraph(f"{exam.name}", styles["Title"])
            exam_name_paragraph.wrapOn(c, 400, 100)
            exam_name_paragraph.drawOn(c, 50, 750)

            header_row = (
                ["Candidate Name"]
                + ["Candidate Email"]
                + [subject.subject.subject_name for subject in subjects]
                + ["Result"]
            )
            data = [header_row]

            for candidate in candidates:
                marks = [""] * len(subjects)
                exam_candidates = ExamCandidate.objects.filter(candidate=candidate)
                true_count = 0

                for exam_candidate in exam_candidates:
                    subject_index = header_row.index(
                        exam_candidate.exam_subject.subject.subject_name
                    )
                    total_marks_for_subject = ExamQuestions.objects.filter(
                        exam=exam_candidate.exam_subject
                    ).aggregate(total_marks=Sum("question__marks"))["total_marks"]

                    if total_marks_for_subject != 0:
                        percentage = (
                            exam_candidate.exam_subject_mark / total_marks_for_subject
                        ) * 100
                        marks[subject_index - 2] = f"{percentage:.2f}%"
                    else:
                        marks[subject_index - 2] = exam_candidate.exam_subject_mark

                    if exam_candidate.exam_subject_outcome_status:
                        true_count += 1
                result = "Qualified" if true_count == len(subjects) else "Disqualified"
                data.append([candidate.name] + [candidate.email] + marks + [result])

            table = Table(data)
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.ReportLabBluePCMYK),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            table.wrapOn(c, 400, 400)
            table.drawOn(c, 50, 650)
            c.showPage()
            c.save()
            pdf_data = bufferlist.getvalue()
            bufferlist.close()

            response = HttpResponse(pdf_data, content_type="application/pdf")
            response["Content-Disposition"] = (
                f'attachment; filename="mark_list_exam_{exam.name}.pdf"'
            )
            response.data = {
                "exam_name": exam.name,
            }

            return response



        except Exam.DoesNotExist:
            return Response(
                {"message":E40304,"errorCode":"E40304"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ExamCountAPIView(APIView):
    def get(self, request):
        try:
            # Get total count of exams        
            total_count = Exam.objects.filter(organization_id=self.request.user.id).count()
            upcoming_exams = Exam.objects.filter(organization_id=self.request.user.id, status=0).count()
            completed_exams = Exam.objects.filter(organization_id=self.request.user.id, status=1).count()
            evaluated_exams = Exam.objects.filter(organization_id=self.request.user.id, status=2).count()
            published_exams = Exam.objects.filter(organization_id=self.request.user.id, status=3).count()

            return Response(
                {
                    "total_count": total_count,
                    "upcoming_exams": upcoming_exams,
                    "completed_exams": completed_exams,
                    "evaluated_exams": evaluated_exams,
                    "published_exams": published_exams,
                }
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DashboardExamListAPIView(APIView):
    def get(self, request, status):
        try:
            exams = Exam.objects.filter(
                organization_id=self.request.user.id, status=status
            )[:5]
            serializer = DashboardExamListSerializer(exams, many=True)
            return Response(serializer.data)
        except Exam.DoesNotExist:
            return Response(
                {"errorCode":"1234234","message": "Exams not found for the given organization and status"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
class  ExamCancelAPIView(generics.UpdateAPIView):
    def patch(self,request,exam_id):   
     
        try:
            related_exams= Exam.objects.get(id=exam_id)
            
            if related_exams.status != 1:
                return Response(
                {"message": messages.E44011,"errorCode":"E44011"},
                status=status.HTTP_400_BAD_REQUEST
            )
            user_tickets =Ticket.objects.filter(exam=exam_id)
            updated_tickets=[]
            for ticket in user_tickets:
                ticket.status = 1
                ticket.exam=None
                updated_tickets.append(ticket)
            Ticket.objects.bulk_update(updated_tickets, ['status', 'exam'])
            related_exams.status=5
            related_exams.save()

            candidates_to_notify = Candidate.objects.filter(exam=related_exams, status=1)
            for candidate in candidates_to_notify:
                send_cancelation_email(candidate)
            return Response(
                {"message": "Tickets for this exam are canceled successfully."},
                status=status.HTTP_200_OK,
                )
        
        except Exam.DoesNotExist:
            return Response(
                {"message": messages.E40028,"errorCode":"E40028"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
def send_cancelation_email(candidate):
    subject = 'Exam Cancellation Notification'
    html_message = render_to_string('exammanagement/cancelation.html', {'candidate': candidate})
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER # Change this to your sender email
    to_email = candidate.email
    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)      
