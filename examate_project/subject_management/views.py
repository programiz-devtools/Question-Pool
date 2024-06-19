from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from subject_management.models import Subject
from examate_project.pagination import CustomSetPagination
from rest_framework import filters
from .serializers import SubjectSerializer, SubjectdropdownlistSerializer
from examate_project.permissions import Admin
from question_management.models import Questions

from django.core.exceptions import ObjectDoesNotExist


from examate_project import messages


class SubjectCreateAPIView(APIView):
    permission_classes = [Admin]
    def post(self, request, format=None):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            sub_name = serializer.validated_data.get("subject_name")
            if Subject.objects.filter(subject_name__iexact=sub_name).exists():
                return Response(
                    {"message": messages.E33005,"errorCode":"E33005"},
                    status=status.HTTP_409_CONFLICT,
                )
    
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subject_errors = serializer.errors.get("subject_name")

        if subject_errors:
                error_data = subject_errors[0]
                error_message=getattr(messages,error_data)

                return Response({"message": error_message,"errorCode":error_data}, status=status.HTTP_400_BAD_REQUEST,)
        

class SubjectListAPIView(generics.ListAPIView):
    permission_classes = [Admin]
    queryset = Subject.objects.order_by("-created_at")
    serializer_class = SubjectSerializer
    pagination_class = CustomSetPagination

    def list(self, request, *args, **kwargs):
        page_size=5
        self.pagination_class.page_size=page_size
        subjects = self.paginate_queryset(self.queryset)

        if not subjects:
                return Response(
                    {"message": messages.E33006,"errorCode":"E33006"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        serialized_data = self.get_serializer(subjects, many=True).data

        # Adding question count to each subject in the serialized data
        for subject_data in serialized_data:
            subject_id = subject_data["id"]
            question_count = Questions.objects.filter(subject_id=subject_id).count()
            subject_data["question_count"] = question_count

        return self.get_paginated_response(serialized_data)


class SubjectSearchView(generics.ListAPIView):
    permission_classes = [Admin]
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    pagination_class=CustomSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['subject_name']  
    
    def list(self, request, *args, **kwargs):
        page_size=5
        self.pagination_class.page_size=page_size
        queryset = self.filter_queryset(self.get_queryset())
        subjects = self.paginate_queryset(queryset)

        if not subjects:
            return Response(
                {"message": messages.E33007,"errorCode":"E33007"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(subjects, many=True)
        return self.get_paginated_response(serializer.data)


class SubjectDeleteView(APIView):
    permission_classes = [Admin]

    def delete(self, request, id):
        try:
            subject = Subject.objects.get(id=id)
            if Questions.objects.filter(
                subject_id=subject.id
            ).exists():  # It is used for preventing th deletion of subject that already have questions.
                return Response(
                    {"message": messages.E33008,"errorCode":"E33008"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            subject.delete()
            return Response(
                {"message": "Subject Deleted Successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Subject.DoesNotExist:
            return Response(
                {"message": messages.E33009,"errorCode":"E33009"}, status=status.HTTP_404_NOT_FOUND
            )


class subjectdropdownlist(generics.ListAPIView):
    queryset = Subject.objects.all().order_by("subject_name")
    serializer_class = SubjectdropdownlistSerializer


    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            return response
        except ObjectDoesNotExist:
            return Response({"errorCode":"E33010","message": messages.E33010}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"errorCode":"E33011","message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class TotalSubjectCountView(APIView):
    def get(self, request):
        total_subject_count = Subject.objects.count()
        return Response(
            {"total_subject_count": total_subject_count}, status=status.HTTP_200_OK
        )




