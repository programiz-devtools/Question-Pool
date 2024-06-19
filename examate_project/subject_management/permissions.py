from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class Admin(permissions.BasePermission):
   def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
       
        if request.user.user_type not in [0]:
            raise PermissionDenied("You do not have permission to this.") 
        return True
