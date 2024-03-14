from typing import Any, Dict
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import Token
from .models import CustomUser,CustomToken,Post,Category,Comments
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
class CategorySerializer(serializers.ModelSerializer):  
    # userid=CustomeUserSerializer(many=False)
    class Meta:
        model=Category
        fields="__all__"

class CommentSerializer(serializers.ModelSerializer):  
    useremail=serializers.CharField(source='userid.email')
    postitle=serializers.CharField(source='postid.title')
    class Meta:
        model=Comments
        fields=["id","useremail","postitle","comments","created_at","updated_at","parent_comment_id"]
class PostSerializer(serializers.ModelSerializer):  
    useremail=serializers.CharField(source='userid.email')
    categoryname=serializers.CharField(source="category.name")
    # comments=serializers.CharField(source="")
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model=Post
        exclude = ['userid', 'category']
class FilterCommentSerializer(serializers.ModelSerializer):  
    postname = serializers.CharField(source='postid.title')
    username = serializers.CharField(source='userid.email')
    # reply=CommentSerializer(many=False)
    class Meta:
        model=Comments
        fields="__all__"
