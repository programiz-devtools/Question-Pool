from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from rest_framework import serializers
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from rest_framework import generics
from rest_framework import status, pagination
from django.core.exceptions import ValidationError
from user_management.models import User
from user_management.serializers import UserSerializer
from examate_project.pagination import CustomSetPagination 
from rest_framework import filters
from rest_framework import generics, filters, status
from rest_framework.response import Response
from examate_project.permissions import Admin
from django.core.paginator import EmptyPage
from examate_project import messages
import logging
from rest_framework.exceptions import NotFound,ValidationError
from .serializers import UserWithChatMessageSerializer


logger = logging.getLogger(__name__)


class OrganizationsView(generics.ListAPIView):
    permission_classes = [Admin]
    serializer_class = UserWithChatMessageSerializer
    pagination_class = CustomSetPagination
   

    def get_queryset(self):
        sort_by = self.request.query_params.get("sort_by", "username")
        ascending = self.request.query_params.get("ascending", "true").lower() == "true"
        sort_fields = ["username", "email", "address"]

        if sort_by not in sort_fields:
            raise ValidationError("Invalid sort field")
        order_by = f"{'' if ascending else '-'}{sort_by}"
        return User.objects.filter(is_register=1, user_type=1).order_by(order_by)

    def list(self, request, *args, **kwargs):
      
     
        page_size=5
        self.pagination_class.page_size=page_size
        response = {}
        try:
            queryset = self.filter_queryset(self.get_queryset())
            users = self.paginate_queryset(queryset)
            serializer = self.get_serializer(users, many=True)
        except ValidationError as e:
            response["errorCode"]="E20001"
            response["message"] = str(e.args[0]) if e.args else "Unknown error"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

       

        try:
            users = self.paginate_queryset(queryset)
            serializer = self.get_serializer(users, many=True)
            return self.get_paginated_response(serializer.data)
        
        except NotFound as e:
            response["errorCode"]="P10001"
            response["message"]=messages.P1001
            return Response(
               response, status=status.HTTP_404_NOT_FOUND
            )


        except EmptyPage as e:
            response["errorCode"]="E20003"
            response["message"]=messages.E20003
            logger.error("Page Error occured")
            return Response(
               response, status=status.HTTP_404_NOT_FOUND
            )


class SearchUser(generics.ListAPIView):
    permission_classes = [Admin]
    pagination_class = CustomSetPagination
    queryset = User.objects.filter(is_register=1, user_type=1)
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["username"]
    

    def list(self, request, *args, **kwargs):
        response={}
       
        try:

            queryset = self.filter_queryset(self.get_queryset())
            users = self.paginate_queryset(queryset)
            serializer = self.get_serializer(users, many=True)
            return self.get_paginated_response(serializer.data)
        
        except Exception:
            logger.error("An error occured in Search user")
            response["message"]=messages.E00500
            response["errorCode"]="E00500"
            return Response(response,status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SwitchUserAccountStatus(generics.UpdateAPIView):
    permission_classes = [Admin]
    serializer_class = UserSerializer

    def get_object(self):
        user_id = self.kwargs["pk"]
        return User.objects.get(id=user_id)

    def update(self, request, *args, **kwargs):
        response={}
        try:
            user = self.get_object()
        except User.DoesNotExist:
            response["errorCode"]="E20004"
            response["message"]=messages.E20004
            
            return Response(
                response, status=status.HTTP_404_NOT_FOUND
            )

        if user.user_type == 1 and user.is_register == 1:
            user.status = 1 - user.status
            user.save()

            if user.status == 0:
                return Response(
                    {"message": "The user has been blocked"}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"message": "The user has been unblocked"},
                    status=status.HTTP_200_OK,
                )
        else:
            response["errorCode"]="E20005"
            response["message"]=messages.E20005
            return Response(response, status.HTTP_400_BAD_REQUEST)


class DeleteUserAccount(generics.UpdateAPIView):
    permission_classes = [Admin]

    def get_object(self):
        user_id = self.kwargs["pk"]
        return User.objects.get(id=user_id)

    def update(self, request, *args, **kwargs):
        response={}
        try:
            user = self.get_object()
        except User.DoesNotExist:
            response["errorCode"]="E20004"
            response["message"]=messages.E20004
            
            return Response(
                response, status=status.HTTP_404_NOT_FOUND
            )

        if user.user_type == 1:
            user.is_register = 0
            user.save()
            return Response(
                {"message": "The user has been successfully deleted"},
                status=status.HTTP_200_OK,
            )
        else:
            response["errorCode"]="E20005"
            response["message"]=messages.E20005
            return Response(response, status.HTTP_400_BAD_REQUEST)

