
from django.db import models
from user_management.models import User





class ChatMessage(models.Model):
    SENDER_CHOICES = (
        (0,'sent_by_admin'),
        (1,'sent_by_consumer')
    )
    client = models.ForeignKey(User,related_name='user',on_delete=models.CASCADE) 
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    flag = models.SmallIntegerField(choices=SENDER_CHOICES)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']
        verbose_name_plural="Message"

    def __str__(self):
        return f"{self.client} - {self.message}"
       

   
    
   


