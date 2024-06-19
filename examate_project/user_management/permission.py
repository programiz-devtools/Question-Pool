from rest_framework import permissions
from .models import User, OTP
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

class IsUserHaveOtp(permissions.BasePermission):
    def has_permission(self, request, view):
        email = request.data.get('email')
        otp_value = request.data.get('otp')
        otp_type = request.data.get('otp_type')

        try:
            user = User.objects.get(email=email)
            OTP.objects.get(user=user, otp=otp_value, otp_type=otp_type)
            return True   

        except (User.DoesNotExist, OTP.DoesNotExist):
            return False

        
 

