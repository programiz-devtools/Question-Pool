from django.shortcuts import render
from rest_framework.response import Response
from user_management.models import User
from .models import Ticket
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from .serializers import TicketSerializer,TicketRequestSerializer,TicketDetailSerializer,NotificationSerializer
from examate_project.pagination import CustomSetPagination
from rest_framework import generics, status
from rest_framework.response import Response
from ticket_management.models import Ticket
from itertools import groupby
from rest_framework import filters
from rest_framework.filters import OrderingFilter
from django.core.exceptions import ObjectDoesNotExist
from examate_project import messages
import logging
from .models import DeviceRegistration  
from django.conf import settings
from pyfcm import FCMNotification
from .models import Notification,DeviceRegistration
from django.utils import timezone
from django.db.models import Count


logger = logging.getLogger(__name__)

push_service = FCMNotification(api_key=settings.FCM_SERVER_KEY)

MONTHS = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December',
}


class DeviceRegistrationView(APIView):
    def post(self, request, format=None):      
        user = self.request.user
        device_token = request.data
        user_type=self.request.user.user_type
        if device_token:
            exists = DeviceRegistration.objects.filter(user=user, device_token=device_token,user_type=user_type).exists()


            if exists:
                return Response({
                    "message": "Device token already registered"
                }, status=status.HTTP_200_OK)  

            DeviceRegistration.objects.create(device_token=device_token,user=user,user_type=user_type)
            return Response({'message': 'Device token registered successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response( {"message": messages.E83003,"errorCode":"E83003"}, status=status.HTTP_400_BAD_REQUEST)

class BuyTicketView(APIView):
     pagination_class = CustomSetPagination
     def post(self, request):

       
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be authenticated to access this resource.")
        
        ticket_count = request.data.get('ticket_count')

        if ticket_count is None:
            return Response( {"message": messages.E83001,"errorCode":"E83001"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            ticket_count = int(ticket_count)
            if ticket_count <= 0:
             raise ValueError
        except ValueError:
           return Response(
        {"message": messages.E83002, "errorCode": "E83002"},
        status=status.HTTP_400_BAD_REQUEST
    )
       
        user = self.request.user
        ticket_ids = [] 
        for _ in range(ticket_count):
         
            ticket=Ticket.objects.create(organisation=user)
            ticket_ids.append(ticket.id) 
        admin_user = User.objects.get(user_type=0)
        logger.info(f"Admin user: {admin_user}")

        admin_device_registration = None
        try:
            admin_device_registration = DeviceRegistration.objects.filter(user=admin_user)
        except DeviceRegistration.DoesNotExist:
                pass 
        print("admin registration",admin_device_registration)
        title="Ticket Request"
        body=f"{ticket_count} tickets requested by {user.username}!"

        device_ids = [registration.device_token for registration in admin_device_registration]      
        if device_ids:
            try:
                result = push_service.notify_multiple_devices(
                registration_ids=device_ids,
                data_message={
                    "title": title,
                    "body": body,
                    "type":"ticket_notification"
                }
                )
                print('Notification sent successfully:', result)
            except Exception as e:
                     logger.error(f'Error sending notification: {e}')
        Notification.objects.create(
                        title=title,
                        body=body,
                        user=admin_user, 
                    )
        return Response({"message":f"{ticket_count} tickets purchased successfully","ticket_id":ticket_ids})

        
     def get(self, request):
        if self.request.user.is_authenticated:
              organization = self.request.user
              tickets = Ticket.objects.filter(organisation=organization).order_by('-created_at')
              paginator = CustomSetPagination()
              paginated_tickets = paginator.paginate_queryset(tickets, request)
              serializer = TicketSerializer(paginated_tickets, many=True)
              return paginator.get_paginated_response(serializer.data)
        else:
            return Response(
                {"detail": "Authentication credentials were not provided."},status=status.HTTP_401_UNAUTHORIZED
            )


class TicketStatusCountAPIView(generics.RetrieveAPIView):

    def get(self, request):
        try:
            requested_count = Ticket.objects.filter(status=0, organisation=request.user).count()
            approved_count = Ticket.objects.filter(status=1, organisation=request.user).count()
            consumed_count = Ticket.objects.filter(status=2, organisation=request.user).count()

            data = {
                'requested_count': requested_count,
                'approved_count': approved_count,
                'consumed_count': consumed_count
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e :
            logger(f"something went wrong in retriving the ticket status count {str(e)}")
            return Response({"message": "An error occurred","errorDetails":e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TicketRequestListView(generics.ListAPIView):
    pagination_class=CustomSetPagination
    def list(self, request, *args, **kwargs):
        try:
            tickets = Ticket.objects.filter(status=0).order_by('organisation_id')
            print("tickets : ",tickets)
            grouped_tickets = []
            for company, tickets_group in groupby(tickets, key=lambda ticket: ticket.organisation):
                tickets_list = list(tickets_group)
                ticket_count = len(tickets_list)
                ticket_ids = [ticket.id for ticket in tickets_list] 
                grouped_tickets.append({
                    'organisation': company.username,
                    'count': ticket_count,
                    'tickets': ticket_ids  
                })
            
            paginated_grouped_tickets= self.paginate_queryset(grouped_tickets)
            serializer = TicketRequestSerializer(paginated_grouped_tickets, many=True)
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class TicketStatusUpdateView(generics.UpdateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        print(partial)
        print("request : ",request.data['ticket_ids'])
        ticket_ids = request.data['ticket_ids']
        updated_status = request.data['updatedStatus'] 
        try:
            tickets = Ticket.objects.filter(id__in=ticket_ids)
            tickets.update(status=updated_status)  
            unique_organizations = set(ticket.organisation for ticket in tickets)

          
            for organization in unique_organizations:
                try:
                    organization_device_registrations = DeviceRegistration.objects.filter(user=organization)
                    device_tokens = [registration.device_token for registration in organization_device_registrations]
                    title = "Tickets Approved" if updated_status == 1 else "Tickets Rejected"
                    body = "Your ticket request has been approved!" if updated_status == 1 else "Your ticket request has been rejected."

                    if device_tokens:
                        push_service.notify_multiple_devices(
                            registration_ids=device_tokens,
                            data_message={
                                "title": title,
                                "body": body,
                                "type":"ticket_notification"
                            }
                        )
                except ObjectDoesNotExist:
                    continue
                except Exception as e:
                    print('Error sending notification:', e)

                Notification.objects.create(
                        title=title,
                        body=body,
                        user=organization, 
                    )

            return Response({'message': 'Ticket status updated successfully'}, status=status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            return Response({'errorCode':'E83005','message': messages.E83005}, status=status.HTTP_404_NOT_FOUND)
class TicketDetailSearchFilter(filters.SearchFilter):
    search_param = 'searchparam' 


class TicketDetailHistoryView(generics.ListAPIView):
    pagination_class = CustomSetPagination
    serializer_class = TicketDetailSerializer
    filter_backends = [TicketDetailSearchFilter]
    search_fields = ['organisation__username']

    def get_queryset(self):
        try:
            return Ticket.objects.all()
        except Exception :
            return None 

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset is None:
            return Response({"message": "An error occurred while fetching ticket details"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            response = super().list(request, *args, **kwargs)
            return response
        except Exception:
            return Response({"detail": "An error occurred while processing the request"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteDeviceRegistrationTokenView(APIView):
    
    def delete(self,request,device_token,format=None,):
            try:

               

                user = self.request.user
                device_registration = DeviceRegistration.objects.filter(device_token=device_token,user=user)

                device_registration.delete()
                return Response({'message': 'Device registration deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
            except DeviceRegistration.DoesNotExist:
               return Response({'errorCode':'E83004','message': messages.E83004}, status=status.HTTP_404_NOT_FOUND)



class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    pagination_class = CustomSetPagination

    def get_queryset(self):
        user = self.request.user
        # Get notifications for the logged-in user
        queryset = Notification.objects.filter(user=user).order_by('-created_at')
        return queryset

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            updatedqueryset = queryset
            
            # Change status of data in queryset to 1
            for notification in updatedqueryset:
                notification.status = 1
                notification.save()

            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            print("data : ",serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CountNotificationsView(APIView):
    def get(self, request, format=None):
        try:
            user = self.request.user
            count = Notification.objects.filter(status=0,user=user).count()
            return Response({"count": count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ApprovedTicketRevenueList(APIView):
  def get(self, request, format=None):
                   
        six_months_ago = timezone.now() - timezone.timedelta(days=365 // 2)
        current_month = timezone.now().month
        total_approved_tickets = Ticket.objects.filter().count()
        desired_months = [(current_month-i-1) % 12 + 1 for i in range(6)]
        approved_tickets_by_month = Ticket.objects.filter(
             
            created_at__gte=six_months_ago
        ).annotate(count=Count('id')) \
        .order_by('created_at')  

        data = []
        for month_number in desired_months:
            month_data = approved_tickets_by_month.filter(created_at__month=month_number)
            count = month_data.count() 

            data.append(f"{MONTHS[month_number]}: {count}")
        response_data = {
        "revenue": total_approved_tickets,
        "data": data,
    }

        return Response(response_data,status=status.HTTP_200_OK)
