from django.urls import path
from .views import BuyTicketView,TicketStatusCountAPIView,TicketRequestListView,TicketStatusUpdateView,TicketDetailHistoryView,DeviceRegistrationView,DeleteDeviceRegistrationTokenView,NotificationListView,CountNotificationsView,ApprovedTicketRevenueList

urlpatterns = [
    path('buy-ticket/', BuyTicketView.as_view(), name="buy-ticket"),
    path('ticket-list/', BuyTicketView.as_view(), name="ticket-list"),
    path('ticket-status-count/', TicketStatusCountAPIView.as_view(), name='ticket-status-count'),
    path('ticket-request/', TicketRequestListView.as_view(), name='ticket-request-list'),
    path('ticket-status-update/',TicketStatusUpdateView.as_view(),name='ticket-status-update'),
    path('ticket-history/', TicketDetailHistoryView.as_view(), name='ticket-history'),
    path('register-device/', DeviceRegistrationView.as_view(), name='register_device'),
    path('delete-register-device/<str:device_token>/', DeleteDeviceRegistrationTokenView.as_view(), name='delete-register_device'),
    path('notifications-list/',NotificationListView.as_view(),name='notifications-list'),
    path('notifications/count/', CountNotificationsView.as_view(), name='count_notifications'),
    path('revenue/', ApprovedTicketRevenueList.as_view(), name='revenue'),
]
