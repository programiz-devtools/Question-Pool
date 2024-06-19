from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import re
from rest_framework.exceptions import PermissionDenied
from rest_framework import serializers
from .models import User



class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20,min_length=4,error_messages={
    "min_length":"E13001",
    "max_length":"E13002",
    "required":"E13003",
    "invalid":"E13017"
     })
    
    email = serializers.EmailField(max_length=230,error_messages={
        "max_length":"E13005",
        "required":"E13006",
        "invalid":"E13007",
     })
    contact_number = serializers.CharField(max_length=10, error_messages={
        "max_length":"E13009",
        "required":"E13010",
        "invalid":"E13011",
    })
    password = serializers.CharField(write_only=True,min_length=8,error_messages={
        "min_length":"E13013",
        "required":"E13014",
        "invalid":"E10111",

    })
    class Meta:
        model = User
        fields = ('id', 'user_type', 'status', 'address', 'username', 'email','contact_number','date_joined','is_register','password',)
   
    

    def validate_username(self, value):
        username_pattern = re.compile(r'^[a-zA-Z\s\'-]+$')
        if not username_pattern.match(value):
            raise serializers.ValidationError('E13017') 
        return value

    def validate_password(self, value):
        password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
        if not password_pattern.match(value):
            raise serializers.ValidationError('E13015')
        return value
    
     
    def validate_contact_number(self, value):
        contact_pattern = re.compile(r'^[6-9]\d{9}$')
        if not contact_pattern.match(value):
            raise serializers.ValidationError('E13011')
        return value

   

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def get_token(cls,user: User):
        token = super().get_token(user)
        token['user_type'] = user.user_type
        return token 
    def validate(self, attrs):
        super().validate(attrs)        
        if self.user.status == 0 or self.user.is_register==0:
            raise PermissionDenied("The account is currently blocked")
        data = super().validate(attrs)
        data["role"]=self.user.user_type
        return data   
    
class OrganizationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20,min_length=4,error_messages={
    "min_length":"E13001",
    "max_length":"E13002",
    "required":"E13003",
    "invalid":"E13017"
     })
    contact_number = serializers.CharField(max_length=10, error_messages={
        "max_length":"E13009",
        "required":"E13010",
        "invalid":"E13011",
    })
    class Meta:
        model = User
        fields = ['username','email','contact_number', 'address']

    def validate_username(self, value):
        username_pattern = re.compile(r'^[a-zA-Z\s\'-]+$')
        if not username_pattern.match(value):
            raise serializers.ValidationError('E13017') 
        return value
    
    def validate_contact_number(self, value):
        contact_pattern = re.compile(r'^[6-9]\d{9}$')
        if not contact_pattern.match(value):
            raise serializers.ValidationError('E13011')
        return value

    
class LoginWithGoogleSerializer(serializers.Serializer):
    cred_token = serializers.CharField(max_length=255) 

    def validate_cred_token(self, value):
       
        if not isinstance(value, str):
            raise serializers.ValidationError("cred_token must be a string.")
        return value
    



class LoginWithGoogleSerializer(serializers.Serializer):
    cred_token = serializers.CharField(max_length=255) 

    def validate_cred_token(self, value):
      
        if not isinstance(value, str):
            raise serializers.ValidationError("cred_token must be a string.")
        return value
    




class ViewProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','contact_number', 'address','profile_image','user_type']
