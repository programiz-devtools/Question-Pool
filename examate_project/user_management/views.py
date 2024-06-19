from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from rest_framework import serializers
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from .models import User, OTP
from .serializers import UserSerializer, CustomTokenObtainPairSerializer,OrganizationSerializer,ViewProfileSerializer
import random
from examate_project.permissions import Consumer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.shortcuts import render
from rest_framework import generics
from rest_framework import status
from .serializers import UserSerializer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .permission import IsUserHaveOtp
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.conf import settings
from rest_framework.authtoken.models import Token
from examate_project import messages
import re
from examate_project import messages
import json
from django.db import IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken
import logging
import os


logger = logging.getLogger(__name__)

EMAIL_IS_REQUIRED="Email is required"
LOGIN_SUCCESSFUL='Login Successful'

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


def otp_generate(user, otp_type):
    otp = get_random_string(length=4, allowed_chars="1234567890")
    existing_otp = OTP.objects.filter(user=user, otp_type=otp_type).first()
    if existing_otp:
        existing_otp.otp = otp
        existing_otp.otp_type = otp_type
        existing_otp.otp_created_at = timezone.now()
        existing_otp.save()
    else:
       
        new_otp = OTP.objects.create(user=user, otp=otp, otp_type=otp_type)
        new_otp.otp_created_at = timezone.now()
        new_otp.save()
    subject = "Password Reset OTP" if otp_type == 0 else "Your OTP for Registration"
    message = f"Your OTP is: {otp}"

    from_email = settings.DEFAULT_FROM_EMAIL
    
    to_email = [user.email]
    send_mail(subject, message, from_email, to_email, fail_silently=False)



class RegisterView(generics.CreateAPIView):
   
    def post(self, request):
      
        serializer = UserSerializer(data=request.data)
      

       
        if not serializer.is_valid():
            return self.handle_invalid_serializer(serializer)
        
       

        validated_data = serializer.validated_data
        username = validated_data.get("username")
        email = validated_data.get("email")
        contact_number = validated_data.get("contact_number")
        address = validated_data.get("address")

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            return self.handle_existing_user(existing_user)

        return self.handle_new_user(username, email, contact_number, address, serializer)
    
    def handle_invalid_serializer(self, serializer):
        
        # Check if the username field has errors
        username_errors = serializer.errors.get("username")
        if username_errors:
                error_data = username_errors[0]
                error_message=getattr(messages,error_data)

                return Response({"message": error_message,"errorCode":error_data}, status=status.HTTP_400_BAD_REQUEST,)
        
        email_errors = serializer.errors.get("email")

        if email_errors:
            error_data = email_errors[0]
            error_message=getattr(messages,error_data)

            return Response({"message": error_message,"errorCode":error_data}, status=status.HTTP_400_BAD_REQUEST,)
        
        contact_errors = serializer.errors.get("contact_number")
        if contact_errors:
            error_data = contact_errors[0]
            error_message=getattr(messages,error_data)

            return Response({"message": error_message,"errorCode":error_data}, status=status.HTTP_400_BAD_REQUEST,)
            
        password_errors = serializer.errors.get("password")
        if password_errors:
            error_data = password_errors[0]
            error_message=getattr(messages,error_data)

            return Response({"message": error_message,"errorCode":error_data}, status=status.HTTP_400_BAD_REQUEST,)
        
        # Handle other validation errors if needed
        return Response(
            {"message": messages.E13016,"errorCode":"E13016"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    def handle_existing_user(self, existing_user):
        if existing_user.is_register == 1:
            return Response(
                {"message": messages.E13008,"errorCode":"E13008"},
                status=status.HTTP_409_CONFLICT,
            )
        else:
            OTP.objects.filter(user=existing_user, otp_type=1).delete()
            otp_generate(existing_user, 1)
            expiration_time = timezone.now() + timezone.timedelta(minutes=1)
            token,created = Token.objects.get_or_create(user=existing_user)
            return Response(
                {
                    "message": "Registered Successfully. You received an OTP for verification.",
                    "expiration_time": expiration_time,
                    "token": token.key if not created else None,
                },
                status=status.HTTP_201_CREATED,
            )

    def handle_new_user(self, username, email, contact_number, address, serializer):
        if User.objects.filter(username=username).exists():
            return Response(
                {"message": messages.E13004,"errorCode":"E13004"},
                status=status.HTTP_409_CONFLICT,
            )
        if User.objects.filter(contact_number=contact_number).exists():
            return Response(
                {"message": messages.E13012,"errorCode":"E13012"},
                status=status.HTTP_409_CONFLICT,
            )

        try:
            hashed_password = make_password(serializer.validated_data.get("password"))
            user = User.objects.create(
                username=username,
                email=email,
                contact_number=contact_number,
                password=hashed_password,
                address=address,
            )
            otp_generate(user, 1)
            expiration_time = timezone.now() + timezone.timedelta(minutes=1)
            token,created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "message": "Registered Successfully. You received an OTP for verification.",
                    "expiration_time": expiration_time,
                    "token": token.key if not created else None
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"message": f"Error occurred during user creation: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        

class ForgetPasswordView(generics.CreateAPIView):
    def post(self, request):
        
        email = request.data.get("email")
        response={}

        if not email:
            response["errorCode"]="E10100"
            response["message"]=messages.E10100
            return Response(
               response, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            if user.is_register == 0:
                response["errorCode"]="E10107"
                response["message"]=messages.E10107
                return Response(
                  response,
                    status=status.HTTP_404_NOT_FOUND,
                )
            if user.external_login_provider== True:
                response["errorCode"]="E10112"
                response["message"]=messages.E10112
                return Response(response, status=status.HTTP_403_FORBIDDEN)
            
        except User.DoesNotExist:
            response["errorCode"]="E10103"
            response["message"]=messages.E10103
            return Response(
               response,
                status=status.HTTP_404_NOT_FOUND,
            )

        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        otp_generate(user, 0)
        expiration_time = timezone.now() + timezone.timedelta(minutes=1)
        return Response(
            {
                "message": "Password reset OTP sent successfully",
                "expiration_time": expiration_time,
                "token": token,
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyOTPView(generics.UpdateAPIView):
    def patch(self, request):
       
        
        email = request.data.get("email")
        otp_value = request.data.get("otp")
        otp_type = request.data.get("otp_type")
      
        response={}

        if not email:
            response["errorCode"]="E10100"
            response["message"]=messages.E10100
            return Response(
               response, status=status.HTTP_400_BAD_REQUEST
            )

        if otp_type==None:
            response["errorCode"]="E10101"
            response["message"]=messages.E10101
            return Response(
               response, status=status.HTTP_400_BAD_REQUEST
            )

        if otp_type!=1 and otp_type!=0:
            response["errorCode"]="E10102"
            response["message"]=messages.E10102
            return Response(
               response, status=status.HTTP_400_BAD_REQUEST
            )


        
       
        
        if not otp_value:
            response["errorCode"]="E10104"
            response["message"]=messages.E10104
            return Response(
               response, status=status.HTTP_400_BAD_REQUEST
            )
       
       
        try:
            user = User.objects.get(email=email)
            otp = OTP.objects.get(user=user, otp=otp_value, otp_type=otp_type)

        except User.DoesNotExist:
            response["errorCode"]="E10103"
            response["message"]=messages.E10103
            return Response(
               response,
                status=status.HTTP_404_NOT_FOUND,
            )
        except OTP.DoesNotExist:
            response["errorCode"]="E10105"
            response["message"]=messages.E10105
            return Response(
              response, status=status.HTTP_403_FORBIDDEN
            )

        expiration_time = otp.otp_created_at + timezone.timedelta(minutes=1)

        if timezone.now() > expiration_time:
            response["errorCode"]="E10106"
            response["message"]=messages.E10106
            return Response(
               response,
                status=status.HTTP_400_BAD_REQUEST,
            )
        if otp.otp_type == 1:
            user.is_register = 1
            user.save()
            return Response(
                {"message": "OTP verification successful"}, status=status.HTTP_200_OK
            )
        elif otp.otp_type == 0:
            return Response(
                {"message": "OTP verification successful"}, status=status.HTTP_200_OK
            )


class ResendOTPView(generics.CreateAPIView):
    
    def post(self, request):
      
        
        email = request.data.get("email")
        otp_type = request.data.get("otp_type")
        response={}

        if otp_type==None:
            response["errorCode"]="E10101"
            response["message"]=messages.E10101
            return Response(
               response, status=status.HTTP_400_BAD_REQUEST
            )

        
        if otp_type!=1 and otp_type!=0:
            response["errorCode"]="E10102"
            response["message"]=messages.E10102
            return Response(
               response, status=status.HTTP_400_BAD_REQUEST
            )

        if not email:
            response["errorCode"]="E10100"
            response["message"]=messages.E10100
            return Response(
               response, status=status.HTTP_400_BAD_REQUEST
            )
        
       

    

        try:
            user = User.objects.get(email=email)
            otp_generate(user, otp_type)
            expiration_time = timezone.now() + timezone.timedelta(minutes=1)
            return Response(
                {
                    "message": "New OTP sent successfully",
                    "expiration_time": expiration_time,
                },
                status=status.HTTP_201_CREATED,
            )

        except User.DoesNotExist:
            response["errorCode"]="E10103"
            response["message"]=messages.E10103
            return Response(
               response,
                status=status.HTTP_404_NOT_FOUND,
            )


class ResetPasswordView(generics.UpdateAPIView):
    permission_classes = [IsUserHaveOtp]

    def patch(self, request):
        email = request.data.get("email")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")
        otp_type = request.data.get("otp_type")

        response={}

        
       

        if new_password != confirm_password:
            response["errorCode"]="E010108"
            response["message"]=messages.E10108
            return Response(
              response,
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
            if not password_pattern.match(new_password):
               raise serializers.ValidationError()
        except serializers.ValidationError :
            error_message = messages.E10111
            response["errorCode"]="E10111"
            response["message"]=error_message
            return Response(response,status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            otp = OTP.objects.filter(user=user.id, otp_type=otp_type)

            otp.delete()
        except User.DoesNotExist:
            response["errorCode"]="E010110"
            response["message"]=messages.E10110
            return Response(
               response, status=status.HTTP_400_BAD_REQUEST
            )

        if user:
            user.password = make_password(new_password)
            user.save()
            return Response(
                {"message": "Password reset successfully"}, status=status.HTTP_200_OK
            )

class CurrentOrganizationProfileAPIView(generics.RetrieveAPIView):
    serializer_class = ViewProfileSerializer
   
    def get_object(self):
        user_id = self.request.user.id
        organization = User.objects.get(id=user_id)
        return organization
        

    def retrieve(self, request, *args, **kwargs):
        # Get the organization object
        try:
            organization = self.get_object()

        # Serialize the organization object
            serializer = self.get_serializer(organization)

            return Response(serializer.data)
        
        except User.DoesNotExist:
            return Response(
                {"errorCode": "E10001","message":messages.E10001},
                status=status.HTTP_404_NOT_FOUND
            )


class UpdateProfileFieldAPIView(APIView):
    
     def save_profile_image(self, user_id, profile, profile_image, image_folder,request):
        try:

    
            if not os.path.exists(image_folder):
                os.makedirs(image_folder)
            _,file_extension=os.path.splitext(profile_image.name)
                
            file_name=f"{user_id}{file_extension}"
            file_path=os.path.join(image_folder,file_name)
           
            if profile.profile_image and os.path.exists(file_path):
                os.remove(file_path)
          
       
            with open(file_path,'wb+') as destination:
                for chunk in profile_image.chunks():
                    destination.write(chunk)

            profile.profile_image=f"{file_name}"
            profile.save()

            request_data=request.data.copy()
            request_data.pop("profile_image",None)
            if not any(request_data.values()) and profile_image:
                return Response({"message": "Profile image updated successfully"}, status=status.HTTP_200_OK)

        except OSError as e:
            logger.error(str(e))
            return Response({"message":"Something went wrong in OS"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            logger.error(str(e))
            return Response({"message":"Something went wrong"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
                

     def put(self, request):
            response = {}
          
            try:
            
                user_id = self.request.user.id
                profile = User.objects.get(id=user_id)
                profile_image=request.FILES.get("profile_image")
                remove_profile_image=request.data.get("remove_profile_image",False)
                if remove_profile_image==True and profile.profile_image:
                   
                    file_extension = os.path.splitext(profile.profile_image)[1]
                    file_name=f"{user_id}{file_extension}"
                    image_folder=os.path.join(settings.MEDIA_ROOT,'profiles')
                    existing_file_path=os.path.join(image_folder,file_name)
                    if profile.profile_image and os.path.exists(existing_file_path):
                           profile.profile_image=None
                           profile.save()
                           os.remove(existing_file_path)
                           return Response({"message":"Profile Image removed successfully"},status=status.HTTP_200_OK)
                elif remove_profile_image==True:
                      response["message"]=messages.E10114
                      response["errorCode"]="E10114"
                      return Response(response,status=status.HTTP_404_NOT_FOUND)        
            
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            except OSError as e:
                logger.error(str(e))
                return Response({"message": "Error removing profile image"}, status=status.HTTP_400_BAD_REQUEST)
            
            except Exception as e:
                logger.error(str(e))
                return Response({"message":"Something went wrong"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            
           
            if profile_image:
                    max_size_mb = 10
                    if profile_image.size > max_size_mb * 1024 * 1024:
                        response["message"]=messages.E10113
                        response["errorCode"]="E10113"
                        return Response(response,status=status.HTTP_400_BAD_REQUEST)
                    image_folder=os.path.join(settings.MEDIA_ROOT,'profiles')
                    return self.save_profile_image(user_id, profile, profile_image, image_folder,request)
                    
                    
 
            request_data=request.data.copy()
            request_data.pop("profile_image",None)
            serializer = OrganizationSerializer(profile, data=request_data)
            
            if serializer.is_valid():
            

                serializer.save()
                return Response({"message":"Profile details updated successfully"}, status=status.HTTP_200_OK)
            else:
                return self.handle_invalid_serializer(serializer)

    
        
     def handle_invalid_serializer(self, serializer):

            updateusername_errors = serializer.errors.get("username")
            if  updateusername_errors:
                    error_data =  updateusername_errors[0]
                    error_message=getattr(messages,error_data)

                    return Response({"message": error_message,"errorCode":error_data}, status=status.HTTP_400_BAD_REQUEST,)
            

            updatecontact_errors = serializer.errors.get("contact_number")
            if updatecontact_errors:
                error_data = updatecontact_errors[0]
                error_message=getattr(messages,error_data)

                return Response({"message": error_message,"errorCode":error_data}, status=status.HTTP_400_BAD_REQUEST,)
                
            # Handle other validation errors if needed
            return Response(
                {"message": messages.E13016,"errorCode":"E13016"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
class LoginWithGoogle(generics.CreateAPIView):

    def post(self, request):
        try:
            email = request.data.get('email','')
            user = User.objects.get(email=email)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            return Response({
                'message': LOGIN_SUCCESSFUL,
                'role': user.user_type,
                'access': access_token,
                'refresh': refresh_token,
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            name = request.data.get('name')
            try:
                user = User.objects.create_google_user(email=email, username=name)
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)
                return Response({
                    'message': LOGIN_SUCCESSFUL,
                    'role': user.user_type,
                    'access': access_token,
                    'refresh': refresh_token,
                }, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"message": "Integrity error"}, status=status.HTTP_400_BAD_REQUEST)

class GetAdminProfileAPIView(generics.RetrieveAPIView):
    serializer_class = ViewProfileSerializer
   
    def get_object(self):
        user_id = self.request.user.id
        organization = User.objects.get(id=user_id)
        if organization.user_type != 0:
            raise User.DoesNotExist
        return organization
        

    def retrieve(self, request, *args, **kwargs):
        # Get the organization object
        try:
            organization = self.get_object()

        # Serialize the organization object
            serializer = self.get_serializer(organization)

            return Response(serializer.data)
        
        except User.DoesNotExist:
            return Response(
                {"errorCode": "E10001","message":messages.E10001},
                status=status.HTTP_404_NOT_FOUND
            )
    
    


