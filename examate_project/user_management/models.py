from django.db import models
import random

from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_google_user(self,**extra_field):

        user=self.model(**extra_field)
        user.external_login_provider=True
        user.set_unusable_password() 
        user.is_register=1
        user.user_type=1
        user.save()
        return user


class User(AbstractUser):
    USER_CHOICES = ((0, "Admin"), (1, "Organisation"))
    REGISTER_CHOICE = (
        (0, "inactive"),
        (1, "active"),
    )
    STATUS_CHOICES = (
        (0, "blocked"),
        (1, "unblock"),
    )

    user_type = models.IntegerField(choices=USER_CHOICES, default=1)
    email = models.EmailField(unique=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=10, null=True)
    is_register = models.IntegerField(choices=REGISTER_CHOICE, default=0)
    external_login_provider=models.BooleanField(default=False)
    date_joined = models.DateField(auto_now_add=True)
    profile_image = models.CharField(max_length=255, blank=True, null=True) 

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    # Add other required fields for creating a user
    class Meta:
        db_table = "users"
    def __str__(self):
        return self.email

    def json_object(self):
        return {
            "name": self.username,
            "email": self.email,
        }


class OTP(models.Model):
    OTP_TYPE_CHOICES = (
        (0, "Forget Password"),
        (1, "Registration"),
    )

    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_type = models.IntegerField(choices=OTP_TYPE_CHOICES)
    class Meta:
        db_table = "otp"
