from rest_framework import permissions
from examate_project import messages

class Consumer(permissions.BasePermission):
   message = {'message': messages.E00000,"errorCode":"E00000"}
   def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
       
        if request.user.user_type not in [1] or request.user.status not in [1] or request.user.is_register != 1:
            return False
        return True


class Admin(permissions.BasePermission):
   message = {'message': messages.E00000,"errorCode":"E00000"}
   def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
       
        if request.user.user_type not in [0]:
            return False
        return True
