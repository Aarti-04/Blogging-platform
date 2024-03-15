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
class UserChangedSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=200,write_only=True)
    confirm_password=serializers.CharField(max_length=200,write_only=True)
    
    class Meta:
        fields=["password","confirm_password"]
    def validate(self, attrs):
        password=attrs.get("password")
        confirm_password=attrs.get("confirm_password")
        user=self.context.get('user')
        if password !=confirm_password:
            raise serializers.ValidationError("Password and confirm password should be same")
        user.set_password(password)
        user.save()
        return attrs

# class SendResetPasswordEmailSerializer(serializers.Serializer):
#     email=serializers.EmailField(max_length=255)
#     def validate(self, attrs):
#         email=attrs.get("email")
#         if CustomUser.objects.filter(email=email).exists():
#             user=CustomUser.objects.get(email=email)
#             uid=user.id
#             uid=urlsafe_base64_encode(force_bytes(uid))
#             print("encoded uid",uid)
#             token=PasswordResetTokenGenerator().make_token(user)
#             print("Token",token)
#             link="http://localhost:3000/api/user/reset/"+uid;
#         else:
#             raise serializers.ValidationError("You are not a registered user")
#         return super().validate(attrs)
    # class Meta:
    #     fields=["email"]