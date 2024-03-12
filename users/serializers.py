from typing import Any, Dict
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import Token
from .models import CustomUser,CustomToken,Post
class CustomTokenObtainPairSerializers(TokenObtainPairSerializer):
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        credentials={
            "email":attrs.get("email"),
            "password":attrs.get("password")
            }
        user=authenticate(**credentials)
        if user:
            return attrs
            
        else:
            raise AuthenticationFailed('Invalid credentials')
    @classmethod
    def get_token(cls, user)->Token:
        print("in get token")
        token= super().get_token(user)
        token["email"]=user.email
        # token[""]
        return token
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model=CustomUser
        # fields="__all__"
        exclude=['password']
        read_only_fields = ["id", "is_active", "is_staff"]
class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomToken
        fields="__all__"
class CustomeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        fields=["email"]
class PostSerializer(serializers.ModelSerializer):  
    userid=CustomeUserSerializer(many=False)
    class Meta:
        model=Post
        fields="__all__"
    
