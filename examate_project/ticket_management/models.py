from django.db import models
from django.utils import timezone
from exam_management.models import Exam
from user_management.models import User



class Ticket(models.Model):
    STATUS_CHOICES = (
        (0, 'Requested'),
        (1, 'Approved'),
        (2, 'Consumed'),
        (5,'Rejected')
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    organisation = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE,null=True)
    class Meta:
        db_table = "tickets"
    
    def get_status_display(self):
        for status_value, status_label in self.STATUS_CHOICES:
            if status_value == self.status:
                return status_label
        return None



class Notification(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(default=0)
    class Meta:
        db_table = "notifications"
    
    


class DeviceRegistration(models.Model):
    USER_CHOICES = ((0, "Admin"), (1, "Organisation"))
    device_token=models.CharField(max_length=255)
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    user_type = models.IntegerField(choices=USER_CHOICES, default=1)
    class Meta:
        db_table = "device_registrations"
