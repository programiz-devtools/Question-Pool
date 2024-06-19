from rest_framework import serializers
from .models import Payments



class PaymentConfirmationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payments
        fields = ["payment_id", "amount","ticket_id"]