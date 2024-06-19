from django.db import models


from user_management.models import User
from ticket_management.models import Ticket

 

class Payments(models.Model):
    STATUS_CHOICES = (
        (0, 'pending'),
        (1, 'paid'),
       
    )
    payment_id = models.CharField(max_length=200, verbose_name="Payment ID")
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE,null=True)
    amount = models.IntegerField(verbose_name="Amount")
    organisation = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    class Meta:
        db_table = "payments"

    def __str__(self):
        return str(self.id)