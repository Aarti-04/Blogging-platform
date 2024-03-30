from typing import Any, Dict
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import Token
from .models import CustomUser,CustomToken,Post,Category,Comments
from django.utils.encoding import smart_str,force_bytes,DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.auth.password_validation import validate_password
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

class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomToken
        fields="__all__"
class CustomeUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    def validate_password(self,value):
        validate_password(value)
        return value
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user 
    class Meta:
        model=CustomUser
        fields="__all__"
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
    useremail=serializers.CharField(source='userid.email',read_only=True)
    categoryname=serializers.CharField(source="category.name",read_only=True)
    userid = serializers.UUIDField(write_only=True)  # Change to UUIDField for user ID
    category = serializers.UUIDField(write_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    # post_image = serializers.ImageField(required=False)
    class Meta:
        model=Post
        fields="__all__"
        # exclude = ['']
    def create(self, validated_data):
        return super().create(validated_data)
class FilterCommentSerializer(serializers.ModelSerializer):  
    postname = serializers.CharField(source='postid.title')
    username = serializers.CharField(source='userid.email')
    # reply=CommentSerializer(many=False)
    class Meta:
        model=Comments
        fields="__all__"


#--------------------------
        
from rest_framework import serializers
from .models import Comments, Post, CustomUser

class UserSerializer2(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username']  # Add other fields if needed

class CommentSerializer2(serializers.ModelSerializer):
    user = UserSerializer2(read_only=True)  # Serializer for the user who made the comment

    class Meta:
        model = Comments
        fields = ['id', 'user', 'comments', 'created_at']  # Add other fields if needed

class CommentReplySerializer2(serializers.ModelSerializer):
    user = UserSerializer2(read_only=True)  # Serializer for the user who made the reply

    class Meta:
        model = Comments
        fields = ['id', 'user', 'comments', 'created_at']  # Add other fields if needed

class PostSerializer2(serializers.ModelSerializer):
    comments = CommentSerializer2(many=True, read_only=True)  # Serializer for comments
    replies = CommentReplySerializer2(many=True, read_only=True, source='post_comment.parent_comment')  # Serializer for replies

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'comments', 'replies', 'created_at', 'updated_at']  # Add other fields if needed

