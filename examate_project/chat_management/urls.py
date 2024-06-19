from django.urls import path
from .views import GetMessages,UpdateIsRead,GetUnreadMessagesCount



urlpatterns = [
 
   path("get-messages/<sender_id>/<receiver_id>/",GetMessages.as_view(),name="get-messages"),
   path("get-messages/",GetMessages.as_view(),name="get-messages"),
   path("mark-messages-read/",UpdateIsRead.as_view(),name="update-messages"),
   path("unread-messages-count/",GetUnreadMessagesCount.as_view(),name="unread-messages-count")


]
