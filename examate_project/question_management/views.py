from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from django.db import transaction
from .serializers import (
    QuestionSerializer,
    FreeAnswerSerializer,
    QuestionOptionSerializer,
    QuestionListSerializer,
    FreeAnswers,
    QuestionOptions,
    QuestionOptionsDetailSerializer,
    FreeAnswerQuestionDetailSerializer,
    ExamSubjectsQuestionsSerializer,
)
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework import generics
from question_management.models import Questions
from examate_project.pagination import CustomSetPagination ,PaginationforExam
from examate_project.permissions import Admin
from subject_management.models import Subject
from user_management.models import User
from exam_management.models import ExamQuestions
import random
from django.db.models.functions import Random
from question_management import messages
from .messages import E30026, E30027, E30028, E30029,E30013,E30050
from examate_project.exceptions import QuestionValidationError,OptionValidationError,NonUpdateable,OptionLimitException,MaxStringLength
from exam_management.views import handle_validation_error

import logging
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

logger = logging.getLogger(__name__)

def  check_answer_type(question,answer_type):
   
     if answer_type is None:
         raise QuestionValidationError("E30109")
     if answer_type not in [1,2,3]:
         raise QuestionValidationError("E30110")
     if question.answer_type != answer_type:
        raise QuestionValidationError("E30103")
     else:
         return
     
def validate_options(options_data,answer_type):

  
    if options_data is None or options_data == []:
        return
    
  
    if answer_type ==1 or answer_type=='1':
        has_answer=any(option.get('is_answer',False)==True for option in options_data)
        if not has_answer:
            raise OptionValidationError("E30104")
        
        num_answers=sum(1 for option in options_data if option.get('is_answer',False)==True)
        if num_answers>1:
            raise OptionValidationError("E30105")
    elif answer_type ==2 or answer_type=='2':
        num_answers=sum(1 for option in options_data if option.get("is_answer",False)==True)
        if num_answers <2:
            raise OptionValidationError("E30106")
        



def check_required_fields(question,request_data):
    
    
   
    required_fields=[]
    field_error_codes={}
 

    if question.answer_type==3:
        required_fields = ['marks', 'question_description', 'subject_id', 'answer','difficulty_level']
        field_error_codes = {'marks': 'E30101', 'question_description': 'E30010', 'subject_id': 'E30102', "difficulty_level":"E40014",'answer': 'E30029',}
    elif question.answer_type in [1, 2]:  
            required_fields = ['marks', 'question_description', 'subject_id', 'options']
            field_error_codes = {'marks': 'E30101', 'question_description': 'E30010', 'subject_id': 'E30102',"difficulty_level":"E40014",  'options': 'E30026'}
    for field in required_fields:
            if field not in request_data or request_data.get(field) in [None, ""]:
                error_code = field_error_codes.get(field, 'E31000') 
                raise QuestionValidationError(error_code)
            
def option_limit_validity(options_data):
    if len(options_data) > settings.OPTION_LIMIT:
             
               raise OptionLimitException("E30027")
         

class CreateQuestionView(APIView):
    permission_classes = [Admin]
    def post(self, request):
        with transaction.atomic():        
            try:
                question_serializer = QuestionSerializer(data=request.data)
                
                if not question_serializer.is_valid():
                    return self.handle_invalid_question(question_serializer.errors)
                
                options_data = request.data.get("options", [])
                question = question_serializer.save()
                logger.info("question created successfully:%s", question.id)
                self.update_subject_question_count(request)
                
                if not question.is_drafted:
                
                    response= self.handle_non_drafted_question(request, question)
                    if response is not False:
                        return response
                
                if question.answer_type == 3:
                 
                    return self.save_free_answer_question(question, request)
                    
                if ((question.answer_type == 1 or question.answer_type == 2) and (question.is_drafted == False)
                    and not request.data.get("options",[])
):
                    return self.handle_missing_options()
                    
                                
                if ((question.answer_type == 1 or question.answer_type == 2) and question.is_drafted == False
                    ):
                    validate_options(options_data,question.answer_type)
                
                if question.answer_type == 1 or question.answer_type == 2:
                    return self.handle_options(question, options_data)
                    
                return Response({"message": "question created successfully"}, status=status.HTTP_201_CREATED)
            
            except (QuestionValidationError, OptionValidationError) as e:
                
                transaction.set_rollback(True)
                return Response({"message": e.message, "errorCode": e.error_code}, status=status.HTTP_400_BAD_REQUEST)
            
            except Exception:
                return Response({"message": E30028, "errorCode": "E30028"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def handle_free_answer_question(self, question, request):
        
            response= self.save_free_answer_question(question, request)
            if response is not False:
                            return response

    def handle_non_drafted_question(self, request, question):

        try:

            check_required_fields(question, request.data)
        except QuestionValidationError as e:
            transaction.set_rollback(True)
            return Response({"message": e.message, "errorCode": e.error_code}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return False

   
        

    def handle_missing_options(self):
        transaction.set_rollback(True)
        return Response({"message": E30026, "errorCode": "E30026"}, status=status.HTTP_400_BAD_REQUEST)

    def handle_options(self, question, options_data):
        if self.is_options_out_of_limit(options_data):
            return Response({"message": E30027, "errorCode": "E30027"}, status=status.HTTP_400_BAD_REQUEST)
        return self.save_question_options(question, options_data)
        


    def update_subject_question_count(self, request):
        subject_id = int(request.data["subject_id"])
        subject = Subject.objects.get(id=subject_id)
        subject.question_count += 1
        subject.save()

    def is_options_out_of_limit(self, options_data):
        return len(options_data) > settings.OPTION_LIMIT
        

    def save_question_options(self, question, options_data):
     
       

        for item in options_data:
            item["question"] = question.id
        option_serializer = QuestionOptionSerializer(data=options_data, many=True)
        if option_serializer.is_valid():
            option_serializer.save()
            response_message = (
                "Multiple answer question created successfully"
                if question.answer_type == 2
                else "Single answer Question created successfully"
            )
            return Response(
                {"message": response_message}, status=status.HTTP_201_CREATED
            )
        else:
            first_error = option_serializer.errors[0] 
            _, error_detail = next(iter(first_error.items()))
            error_code = error_detail[0]  
            error_message = getattr(messages, error_code) 
            return Response(
                {"message": f"{error_message}is required", "errorCode": error_code},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
    def handle_invalid_question(self, errors):
        logger.warning(
            "Received invalid data for question creation: %s",
            errors,
        )

        first_value = next(iter(errors.values()))
        error_data = first_value[0]
        error_message = getattr(messages, error_data)
        transaction.set_rollback(True)
        return Response(
            {"message": error_message, "errorCode": error_data},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def save_free_answer_question(self, question, request):
        free_answer_data = request.data
        free_answer_data["question"] = question.id
        free_answer_data.update(request.data)
        free_answer_serializer = FreeAnswerSerializer(data=free_answer_data)
        answer = request.data.get("answer")

        if free_answer_serializer.is_valid() and answer != "" :
            
            if answer is not None and len(answer) > 500:
                return Response(
                    {"message": "Answer length cannot exceed 500 characters"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            free_answer_serializer.save()
            logger.info("Free answer question created successfully:%s", question.id)
            return Response(
                {"message": "Free answer question created successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"message": "Free answer question created successfully"},
                status=status.HTTP_201_CREATED,
            ) 
            

class UpdateQuestionView(APIView):
    permission_classes = [Admin]
    
    #check question is already published or not
    def check_question_is_updatable(self,question):
         if not question.is_drafted:
             raise NonUpdateable("E30200")
         


    #return free answer serializer for validation and updation
    def update_free_answer(self, request, question):

        free_answer_instance = FreeAnswers.objects.filter(
            question=question).first()
        free_answer_data = {
            "answer": request.data.get("answer", ""),
            "question": question.id,
        }
        free_answer_serializer = FreeAnswerSerializer(
            instance=free_answer_instance, data=free_answer_data
        )
        return free_answer_serializer
    
    #check free answer fields validation
    def check_free_answer_validation(self,free_answer_serializer, request):
        
         
        
          answer = request.data.get("answer", None)
          MAX_ANSWER_LENGTH=500

    
          if answer is not None:
                if len(answer) > MAX_ANSWER_LENGTH: 
                    raise serializers.ValidationError("E30023")
                
              
                free_answer_serializer.is_valid(raise_exception=True)
                free_answer_serializer.save()

            
            
       
           
    #delete unwanted existing options   
    def delete_unwanted_options(self, options_data, existing_options):
        new_option_ids = set(option.get("id") for option in options_data)
        options_to_delete = existing_options.exclude(id__in=new_option_ids)
        options_to_delete.delete()


    #create new options or update existing options
    def create_or_update_option(self, question, options_data):
      
        for new_option_data in options_data:
            new_option_data['question'] = question.id
            option_id = new_option_data.get('id', None)
            
            if option_id is not None:
                try:
                    existing_option = QuestionOptions.objects.get(id=option_id, question=question)
                    option_serializer = QuestionOptionSerializer(instance=existing_option, data=new_option_data)
                    option_serializer.is_valid(raise_exception=True)
                    option_serializer.save()

                except QuestionOptions.DoesNotExist:
                    pass
            else:
               
                option_serializer = QuestionOptionSerializer(
                  data=new_option_data)
                option_serializer.is_valid(raise_exception=True)
                option_serializer.save()
            
               
                  
   

    #return new options data and existing options
    def update_sa_and_ma(self, request, question):
      

        options_data = request.data.get("options", [])
        existing_options = QuestionOptions.objects.filter(question=question)
        return options_data, existing_options
    
    #return appropriate success response
    def update_question_response(self, updated_question, message):
        if updated_question.answer_type == 1:
            return Response(
                {"message": f"Single answer question {message}"},
                status=status.HTTP_200_OK,
            )
        elif updated_question.answer_type == 2:
            return Response(
                {"message": f"Multiple answer question {message}"},
                status=status.HTTP_200_OK,
            )
        elif updated_question.answer_type == 3:
            return Response(
                {"message": f"Free answer question {message}"},
                status=status.HTTP_200_OK,
            )
        
    #handle all type of serializer validation error   
    def serializer_validation_error(self, e):
       
        if isinstance(e, str):
           
            error_code = e
        elif hasattr(e, 'detail') and isinstance(e.detail, list):
           
            error_code = e.detail[0] if e.detail else ''
        elif hasattr(e, 'detail') and isinstance(e.detail, dict):
            
            error_code = str(next(iter(e.detail.values()))[0])
        elif hasattr(e, 'detail') and hasattr(e.detail, '__iter__'):
           
            error_code = str(next(iter(e))[0])
        else:
           
            error_code = str(e)

        error_message = getattr(messages, error_code, "Unknown error")
        logger.error(f"Serializer field error:{str(e)}")

        return error_code, error_message



    def put(self, request, question_id):
       
        response = {}
       
       
        with transaction.atomic():
          
            try:
                question = Questions.objects.get(id=question_id)
                self.check_question_is_updatable(question)
            
            
                
            except NonUpdateable as e:
                    transaction.set_rollback(True)
                    return Response({"message": e.message, "errorCode": e.error_code}, status=status.HTTP_400_BAD_REQUEST)
            
            except Questions.DoesNotExist:
                response["errorCode"] = "E30100"
                response["message"] = messages.E30100
                transaction.set_rollback(True)
                return Response(response, status=status.HTTP_404_NOT_FOUND)
        
            request_data = request.data.copy()
            answer_type=request_data.get('answer_type',None)
            is_drafted=request.data.get('is_drafted',True)
            try:
                check_answer_type(question, answer_type)
                validate_options(request_data.get('options',None), answer_type)

            except (QuestionValidationError, OptionValidationError) as e:
                transaction.set_rollback(True)
                logger.error(f"Question serializer or option validation error-{str(e)}")
                return Response({"message": e.message, "errorCode": e.error_code}, status=status.HTTP_400_BAD_REQUEST)
            
            request_data.pop('answer_type', None)
            if is_drafted is False:
                try:
                 check_required_fields(question,request_data)
                except QuestionValidationError as e:
                    transaction.set_rollback(True)
                    logger.error(f"Question serializer validation error-{str(e)}")
                    return Response({"message": e.message, "errorCode": e.error_code}, status=status.HTTP_400_BAD_REQUEST)
            question_serializer = QuestionSerializer(
            instance=question, data=request_data, partial=True)

            try:
                question_serializer.is_valid(raise_exception=True)
                updated_question = question_serializer.save()
            except serializers.ValidationError as e:
                error_code, error_message = self.serializer_validation_error(e)
                transaction.set_rollback(True)
                logger.error(f"Question serializer validation error-{str(e)}")
                return Response({"message":error_message,"errorCode":error_code},status=status.HTTP_400_BAD_REQUEST)


            if updated_question.answer_type == 3:
                free_answer_serializer = self.update_free_answer(request, question)
                try:
                    self.check_free_answer_validation(free_answer_serializer,request)
                   
                    return Response({"message":"Free answer question updated successfully"},status=status.HTTP_200_OK)
                
                

                except serializers.ValidationError as e:
                
                  error_code, error_message = self.serializer_validation_error(e)
                  transaction.set_rollback(True)
                  logger.error(f"Free answer serializer validation error-{str(e)}")
                  return Response({"message":error_message,"errorCode":error_code},status=status.HTTP_400_BAD_REQUEST)
            

            
            elif updated_question.answer_type in [1, 2]:
                options_data, existing_options = self.update_sa_and_ma(
                request, question)
                try:

                 option_limit_validity(options_data)

                except (OptionLimitException,MaxStringLength) as e:
                    transaction.set_rollback(True)
                    return Response({"message": e.message, "errorCode": e.error_code}, status=status.HTTP_400_BAD_REQUEST)
            
                self.delete_unwanted_options(options_data, existing_options)    
            

                try:

                    self.create_or_update_option(question, options_data)
             
                except serializers.ValidationError as e:
                
                  error_message = next(iter(e.detail.values()))[0]
                  field_name = next(iter(e.detail))
                  transaction.set_rollback(True)
                  logger.error(f"Option serializer validation error-{str(e)}")
                  return Response({"message": f"{field_name}: {error_message}"}, status=status.HTTP_400_BAD_REQUEST)
            
          
           
            return self.update_question_response(updated_question, "updated successfully")


   


class QuestionlistAPIView(generics.ListAPIView):
    permission_classes = [Admin]
    serializer_class = QuestionListSerializer
    pagination_class = CustomSetPagination

    def get_queryset(self):
        try:
            page_size=5
            self.pagination_class.page_size=page_size
            queryset = Questions.objects.all().order_by("created_at")
            is_drafted = self.request.query_params.get("is_drafted")
            answer_type = self.request.query_params.get("answer_type")
            difficulty_level = self.request.query_params.get("difficulty_level")
            subject = self.request.query_params.get("subject_id")
            search_param = self.request.query_params.get("searchparam", None)

            # Apply filters if provided
            if bool(is_drafted)==True:
                queryset = queryset.filter(is_drafted=bool(is_drafted))

            if answer_type:
                queryset = queryset.filter(answer_type=answer_type)

            if difficulty_level is not None:
                queryset = queryset.filter(difficulty_level=difficulty_level)

            if subject:
                queryset = queryset.filter(subject_id=subject)

            if search_param is not None:
                queryset = queryset.filter(question_description__icontains=search_param)

            return queryset
        except ValidationError as e:
            print("in validation : ",e)
            return Response({"error": "Validation Error", "code": "VALIDATION_ERROR"}, status=400) 
        except Exception as e:
            print("in exception :",e)
            return Response({"error": "Validation Error", "code": "VALIDATION_ERROR"}, status=400) 
       



class QuestionDetailView(APIView):
    permission_classes = [Admin]

    def get(self, request, question_id):
        try:
            question = Questions.objects.get(id=question_id)
            if question.answer_type == 2 or question.answer_type == 1:
                serializer = QuestionOptionsDetailSerializer(question)
            elif question.answer_type == 3:
                serializer = FreeAnswerQuestionDetailSerializer(question)
        except Questions.DoesNotExist:
            return Response(
                {"error_code":"E30050","message": E30050}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(serializer.data, status=status.HTTP_200_OK)


class QuestionDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [Admin]
    queryset = Questions.objects.all()
    serializer_class = QuestionListSerializer

    def destroy(self, request, *args, **kwargs):
        try:

           
            instance = self.get_object()           
            instance.delete()
            return Response({"message":"question deleted successfully"},status=status.HTTP_204_NO_CONTENT)

        except Exception :
            return Response(
                {"error_code":"E30050","message": E30050}, status=status.HTTP_404_NOT_FOUND
            )

class ChangeDraftStatusAPIView(APIView):
    permission_classes = [Admin]

    def post(self, request, question_id):
        try:
            # Get the question by ID
            question = Questions.objects.get(id=question_id)
            if question.is_drafted== False:
                return Response(
                    {"error_code":"1234234","message": "Question is already approved"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            question.is_drafted = False
            question.save()

            return Response(
                {"message": "Question status updated successfully"},
                status=status.HTTP_200_OK,
            )
        except Questions.DoesNotExist:
            return Response(
                {"error": "Question not found" ,"error_code":"1234"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TotalQuestionCountView(APIView):
    def get(self, request):
        total_question_count = Questions.objects.filter(
            is_drafted=False).count()
        return Response(
            {"total_question_count": total_question_count}, status=status.HTTP_200_OK
        )


class ExamSubjectsQuestionsAPIView(generics.ListAPIView):
    serializer_class = ExamSubjectsQuestionsSerializer

    def get_queryset(self):
        try:
            exam_subject_id = self.kwargs.get("exam_subject_id")
            queryset = ExamQuestions.objects.filter(exam_id=exam_subject_id)
            randomized_queryset = queryset.order_by("?")
            return randomized_queryset
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"error_code":"1234234","message":"Exam id does not exist"},status=status.HTTP_404_NOT_FOUND)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)



class CountView(APIView):
    def get(self, request):
        total_question_count = Questions.objects.filter(is_drafted=False).count()
        total_subject_count = Subject.objects.count()
        total_organisation_count = User.objects.filter(user_type=1, status=1,is_register=1).count()
        response={"total_question_count":total_question_count,"total_subject_count":total_subject_count,"total_organisation_count":total_organisation_count}
        return Response(
            response, status=status.HTTP_200_OK
        )
