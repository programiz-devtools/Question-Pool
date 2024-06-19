from django.shortcuts import render
from rest_framework import generics
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Candidate, ExamCandidate
from exam_management.models import ExamSubjects, Exam,ExamQuestions
from exam_management.models import ExamSubjects, Exam,ExamQuestions
from .serializers import (
    ExamCandidateSerializer,
    CandidateSerializer,
    ExamCandidateCreateSerializer,
)
import jwt
from subject_management.models import Subject
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils import timezone
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.filters import SearchFilter
from rest_framework.filters import OrderingFilter
from examate_project.pagination import CustomSetPagination
from rest_framework.filters import OrderingFilter
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO
from django.db.models import Sum
from django.core.mail import EmailMessage
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from .messages import E60010,E60011,E60013,E70001,E70002,E70003,E70004,E70005,E70006,E70008,E60014
from examate_project import messages

logger = logging.getLogger(__name__)

from rest_framework.exceptions import ValidationError

class ExamCandidateListView(ListAPIView):
    pagination_class = CustomSetPagination
    serializer_class = CandidateSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["id", "email", "status"]

    def get_queryset(self):
        page_size=5
        self.pagination_class.page_size=page_size
        exam_id = self.kwargs["exam_id"]
        queryset = Candidate.objects.filter(exam=exam_id)
        if not queryset.exists():
            raise ObjectDoesNotExist("No candidates found for the exam")

        search_param = self.request.query_params.get("searchparam", None)
        if search_param is not None:
            queryset = queryset.filter(email__contains=search_param)
        return queryset.order_by("-id")
    
    def handle_exception(self, exc):
        if isinstance(exc, ObjectDoesNotExist):
            return Response(E70001,
                status=status.HTTP_404_NOT_FOUND
            )
        return super().handle_exception(exc)

class ExamCandidateCreateView(generics.CreateAPIView):
    serializer_class = ExamCandidateSerializer

    def create(self, request, *args, **kwargs):
        exam_id = kwargs.get("exam_id")

        try:
            exam = Exam.objects.get(id=exam_id, status__lt=2)
            exam_subjects = ExamSubjects.objects.filter(exam=exam)

        except Exam.DoesNotExist:
            return Response(
                E70002,
                status=status.HTTP_404_NOT_FOUND,
            )

        
        candidate_data = {"email": request.data.get("email"), "exam": exam.id}
        existing_candidates = Candidate.objects.filter(
            exam=exam, email=candidate_data.get("email")
        )
        if existing_candidates.exists():
            return Response(
                E70003,
                status=status.HTTP_400_BAD_REQUEST,
            )

        candidate_serializer = CandidateSerializer(data=candidate_data)

        if candidate_serializer.is_valid():
            candidate = candidate_serializer.save()
            exam_candidate_data_list = []
            for exam_subject in exam_subjects:
                exam_candidate_data = {
                    "candidate": candidate.id,
                    "exam_subject": exam_subject.id,
                }

                exam_candidate_serializer = ExamCandidateCreateSerializer(
                    data=exam_candidate_data
                )

                if exam_candidate_serializer.is_valid():
                    exam_candidate_serializer.save()
                    print("inside valid check")
                    exam_candidate_data_list.append(exam_candidate_serializer.data)
                    exam_subject.exam.candidate_count += 1
                    exam_subject.exam.save()

            return Response({"message":"candidate added successfully"}, status=status.HTTP_201_CREATED)

        return Response(candidate_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CandidateListByExamAPIView(generics.ListAPIView):
    serializer_class = CandidateSerializer

    def get_queryset(self):
        exam_id = self.kwargs.get("exam_id")
        if exam_id:
            return Candidate.objects.filter(exam_id=exam_id, status=0)
        else:
            return Response(
                {"errorCode":"215425","message": "No candidates found for the exam"},
                status=status.HTTP_404_NOT_FOUND
            )


class SendExamLinkView(APIView):
    def post(self, request):
        candidate_ids = request.data.get("candidateId", [])
        exam_id = request.data.get("examid")
        responses = []
        candidates_with_errors = []
        exam_not_found_error = False

        try:
            exam = Exam.objects.get(id=exam_id)
            scheduled_time = exam.scheduled_time
            expired_time = scheduled_time + timedelta(minutes=30)
            active = scheduled_time - timedelta(minutes=15)
            exp = int(expired_time.timestamp())
            active_time = int(active.timestamp())
        except Exam.DoesNotExist:
            exam_not_found_error = True

        for candidate_id in candidate_ids:
            try:
                candidate = Candidate.objects.get(id=candidate_id, exam_id=exam_id)
                email = candidate.email
                payload = {
                    "candidateId": candidate_id,
                    "exam_id": exam_id,
                    "exp": exp,
                    "active_time": active_time,
                }
                jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
                exam_access_link = f"{settings.EXAM_ACCESS_LINK_URL}{jwt_token}"

                subject = "Assessment"
                html_message = render_to_string(
                    "candidatemanagement/acesslink_email.html",
                    {"exam_access_link": exam_access_link},
                )
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [email]
                send_mail(
                    subject, "", from_email, recipient_list, html_message=html_message
                )
                candidate.status = 1
                candidate.save()
                response = {
                    "candidateId": candidate_id,
                    "message": "Email sent successfully to all candidates",
                }
            except Candidate.DoesNotExist:
                candidates_with_errors.append(candidate_id)
                response = {
                    "candidateId": candidate_id,
                    "message": E60011.format(candidate_id),
                    "errorCode": "E60011"
                }
            except Exception:
                candidates_with_errors.append(candidate_id)
                response = {
                    "candidateId": candidate_id,
                }

            responses.append(response)

        if exam_not_found_error:
            return Response(
                {"message": E60010.format(exam_id), "errorCode": "E60010"},
                status=status.HTTP_404_NOT_FOUND,
            )
        elif candidates_with_errors:
            return Response(
                {
                    "message":E60011.format(candidates_with_errors),
                    "errorCode": "E60014"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif not responses:
            return Response(
                {"message": E60013, "errorCode": "E60013"},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                {"message": "Emails sent successfully to all Candidate"},
                status=status.HTTP_200_OK
            )


class CheckTokenExpirationView(APIView):
    def post(self, request):
        token = request.data

        try:

            decoded_token = jwt.decode(
                token["token"], settings.SECRET_KEY, algorithms="HS256"
            )
            activation_time = decoded_token.get("active_time")

            exp = decoded_token.get("exp")
            current = datetime.now().timestamp()
            current_time = int(current)

            if activation_time <= current_time <= exp:
                return Response({"expired": False}, status=status.HTTP_200_OK)
            else:
                return Response({"expired": True}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as e:
            print("ExpiredSignatureError: ", str(e))
            return Response({"expired": True}, status=status.HTTP_200_OK)
        except jwt.InvalidTokenError as e:
            print("InvalidTokenError: ", str(e))
            return Response(
                {"message":E60014,"errorCode":"E60014"}, status=status.HTTP_400_BAD_REQUEST
            )

class DeleteCandidateView(APIView):
    def delete(self, request, candidate_id):
        try:
            candidate = get_object_or_404(Candidate, id=candidate_id)

            if candidate.status == 1:
                return Response(
                    {"errorCode":"E70004","message": E70004},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            candidate.delete()
            return Response(
                {"message": "Candidate deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Http404:
            return Response(
                {"errorCode":"E70005","message": E70005},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AddCandidateNameView(APIView):
    def post(self, request, *args, **kwargs):

        try:
            token = request.data.get("token")
            request_name = request.data.get("name", "")
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
            candidate_id_from_token = decoded_token.get("candidateId")
            candidate = get_object_or_404(Candidate, id=candidate_id_from_token)
            if candidate.name and request_name:

                candidate.name = request.data.get("name", "")
                candidate.save()
                return Response(
                    {"message": "Name Updated successfully"}, status=status.HTTP_200_OK
                )
            else:
                if not request.data.get("name"):
                    return Response(
                        {"name": candidate.name}, status=status.HTTP_202_ACCEPTED
                    )

                candidate.name = request.data.get("name")
                candidate.save()
                return Response(
                    {"message": "Name Added successfully"}, status=status.HTTP_200_OK
                )

        except jwt.ExpiredSignatureError as e:
            print("ExpiredSignatureError: ", str(e))
            return Response({"expired": True}, status=status.HTTP_200_OK)
        except jwt.InvalidTokenError as e:
            print("InvalidTokenError: ", str(e))
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )



class EvaluateExamCandidateListView(ListAPIView):
    serializer_class = ExamCandidateSerializer
    pagination_class = CustomSetPagination

    def get_queryset(self):
        exam_id = self.kwargs.get("exam_id")
        try:
            exam = get_object_or_404(Exam, id=exam_id)
            return ExamCandidate.objects.filter(candidate__exam=exam)
        except Http404:
            return None

    def list(self, request, *args, **kwargs):
        page_size=5
        self.pagination_class.page_size=page_size
        queryset = self.get_queryset()
        if queryset is None:
            return Response({'message':messages.E40028,"errorCode":"E40028" }, status=status.HTTP_404_NOT_FOUND)

        submitted_candidates = queryset.filter(candidate__status=3)
        print(submitted_candidates)

        search_query = request.query_params.get("search", None)
        if search_query:
            queryset = queryset.filter(candidate__name__icontains=search_query)
            if not queryset.exists():
                return Response({'message': messages.E63002,"errorCode":"E63002"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)
        # Group the results by candidate ID
        candidates_data = {}
        submitted_candidates_count = 0
        for item in serializer.data:
            candidate_id = item["candidate_id"]
            candidate_email= item["candidate_email"]
            candidate_name = item["candidate_name"]
            candidate_status = item["candidate_status"]
            exam_subject_name = item["exam_subject_name"]
            exam_subject_mark = item["exam_subject_mark"]

            if candidate_id not in candidates_data:
                candidates_data[candidate_id] = {
                    "candidate_id": candidate_id,
                    "candidate_name": candidate_name,
                    "candidate_status": candidate_status,
                    "candidate_email": candidate_email,
                    "exams": {exam_subject_name: exam_subject_mark},
                }
            else:
                candidates_data[candidate_id]["exams"][
                    exam_subject_name
                ] = exam_subject_mark

        submitted_candidates_count = sum(
            1
            for candidate_data in candidates_data.values()
            if candidate_data["candidate_status"] == 3
        )
        logger.info("Submitted candidates count: %d", submitted_candidates_count)

        page = self.paginate_queryset(list(candidates_data.values()))
        if page is not None:
            return self.get_paginated_response(page)


class ExamTokenDecodeView(APIView):
    def post(self, request):
        exam_token = request.data.get(
            "exam_token"
        )  # Assuming the token is passed as a query parameter
        if not exam_token:
            return Response(
                {"error": "Exam token is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            decoded_token = jwt.decode(
                exam_token, settings.SECRET_KEY, algorithms=["HS256"]
            )
            candidate_id = decoded_token.get("candidateId")
            exam_id = decoded_token.get("exam_id")
            if not candidate_id:
                return Response(
                    {"error": "Candidate ID not found in token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            candidate = Candidate.objects.get(pk=candidate_id)
            if candidate.status > 1:
                return Response(
                    {"error": "candidate already attended"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            exam = Exam.objects.get(pk=exam_id)
            serialized_candidate = {
                "candidate_id": candidate.id,
                "candidate_name": candidate.name,
                "exam_id": exam.id,
                "exam_name": exam.name,
                "status": candidate.status,
                # Add other fields as needed
            }
            candidate.status = 2
            candidate.save()

            return Response(serialized_candidate, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response(
                {"error": "Exam token has expired"}, status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.InvalidTokenError:
            return Response(
                {"error": "Invalid exam token"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Candidate.DoesNotExist:
            return Response(
                {"error": "Candidate does not exist"}, status=status.HTTP_404_NOT_FOUND
            )


def generate_candidate_result_pdf(candidate_id):

    try:

        
        # Retrieve candidate details
        candidate = Candidate.objects.get(id=candidate_id)
        
        # Fetch exam results for the candidate
        exam_results = ExamCandidate.objects.filter(candidate=candidate.id)
        candidate_marks = {}
        all_subjects_passed = True
        for exam_candidate in exam_results:
            exam_subject_name = exam_candidate.exam_subject.subject.subject_name
            exam_subject_mark = exam_candidate.exam_subject_mark
            exam_subject_outcome_status =exam_candidate.exam_subject_outcome_status
            pass_percentage = exam_candidate.exam_subject.pass_percentage
            total_marks_for_subject = ExamQuestions.objects.filter(
                exam=exam_candidate.exam_subject
            ).aggregate(total_marks=Sum("question__marks"))["total_marks"]

            if total_marks_for_subject == 0:
                percentage_scored=0
            else:
                percentage_scored= (exam_subject_mark / total_marks_for_subject) * 100

            if not exam_subject_outcome_status or percentage_scored < pass_percentage:
                all_subjects_passed = False

            if exam_subject_name not in candidate_marks:
                candidate_marks[exam_subject_name] = []
            candidate_marks[exam_subject_name].append(
                {
                    "mark": exam_subject_mark,
                    "outcome_status": exam_subject_outcome_status,
                    "total":total_marks_for_subject,
                    "percentage":pass_percentage,
                    "percentage_scored":percentage_scored
                   
                }
            )
        overall_result = "Pass" if all_subjects_passed else "Fail"
        # Render the exam result PDF template
        html_template = render_to_string(
            "candidatemanagement/result.html",
            {
                "candidate": candidate,
                "exam_results": candidate_marks,  # Pass the dictionary items instead of serializer data
                "overall_result": overall_result 
            },
        )
        pdf_file = BytesIO()
        pisa_status = pisa.CreatePDF(html_template, dest=pdf_file)

        if pisa_status.err:
            return None  # Return None if PDF generation fails

        # Reset the pointer of the BytesIO object
        pdf_file.seek(0)

        print("pdf fle created", pdf_file)
        return pdf_file

    except Candidate.DoesNotExist:
        # Handle candidate not found error
        raise ValueError("Candidate not found")

    except Exception as e:
        
        raise ValueError(f'There was an error: {str(e)}')
    
class SendResultEmailsView(APIView):
    def post(self, request):
        send_email_list=[]
        try:
            data = request.data
            if not data:
                return Response({'errorCode': 'E70008',"message":E70008}, status=500) 
            from_email = settings.EMAIL_HOST_USER
            for candidate_id in data:
                try:
                    candidate = Candidate.objects.get(id=candidate_id, status=4)
                    exam = Exam.objects.get(id=candidate.exam_id)
                except Candidate.DoesNotExist:
                    continue

                resultpdf = generate_candidate_result_pdf(candidate_id)
                email = EmailMessage(
                    subject=f"Result of {exam.name}",
                    body="Please find attached your exam result PDF\nThank you for attending the exam.\nBest regards,",
                    from_email=from_email,
                    to=[candidate.email],
                )
                filename = f"{candidate.id}_result.pdf"
                email.attach(filename, resultpdf.getvalue(), "application/pdf")
                email.send()
                send_email_list.append(candidate.email)
                candidate.status = 5
                candidate.save()
            if send_email_list:
                return Response({"message": f"Emails sent successfully to {send_email_list}"})
            else:
                return Response({"errorCode":"E70006","message": E70006},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.info(e, f"Emails sent successfully to {send_email_list}")
            return Response({"error": str(e)}, status=500)
