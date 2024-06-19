from rest_framework import response
from ticket_management.models import Ticket
from django.http import HttpResponse
import stripe
from rest_framework.views import APIView,status
from django.conf import settings
from django.shortcuts import render,redirect
from .models import Payments
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from .serializers import PaymentConfirmationSerializer
from django.db import transaction
from rest_framework.response import Response




stripe.api_key=settings.STRIPE_SECRET_KEY


class StripePaymentCheckout(APIView):
    def post(self, request, *args, **kwargs):
        try:
            
            ticket_count = request.data
            total_payment=ticket_count*100
            intent = stripe.PaymentIntent.create(
                amount=total_payment * 100, 
                currency='inr', 
                description='Payment for ticket',
                payment_method_types=['card'] ,
            )
            return Response({'clientSecret': intent.client_secret})
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class PaymentConfirmation(APIView):
    def post(self, request, format=None):
        try:
            with transaction.atomic():            
                organisation = request.user
                serializer = PaymentConfirmationSerializer(data=request.data)
                
                if not serializer.is_valid():
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                ticket_ids = request.data.get('ticket_id', [])
                payment_id = request.data.get('payment_id')
                amount = request.data.get('amount')

                if not ticket_ids:
                 
                    payment = Payments.objects.create(payment_id=payment_id,
                        organisation=organisation,
                        amount=amount,
                        status=0
                    )
                    
                else:
                    ticket_count = len(ticket_ids)

                    for ticket_id in ticket_ids:
                        try:
                            ticket = Ticket.objects.get(id=ticket_id, organisation=organisation)
                            
                            payment,_ = Payments.objects.get_or_create(ticket=ticket, organisation=ticket.organisation, amount=amount)
                            
                            if payment.status == 0:
                                payment.payment_id = payment_id
                                payment.amount = amount / ticket_count
                                payment.status = 1
                                payment.save()
                        except Ticket.DoesNotExist:
                            return Response({"message":"ticket is not fount{ticket_id}"},status=status.HTTP_400_BAD_REQUEST)
                return Response({'message': 'Ticket purchases confirmed successfully'}, status=status.HTTP_200_OK)       
        except Exception:
            return Response({'message': 'Error occurred during the process'}, status=status.HTTP_400_BAD_REQUEST)
