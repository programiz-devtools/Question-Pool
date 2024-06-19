
from django.urls import path
from .views import StripePaymentCheckout,PaymentConfirmation

urlpatterns = [
    path('payment-checkout/', StripePaymentCheckout.as_view(), name="payment-checkout"),
    path('payment-confirmation/',PaymentConfirmation.as_view(), name='payment-confirmation')
]
