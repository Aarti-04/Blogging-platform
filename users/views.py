from django.shortcuts import render
from rest_framework.views import APIView,Response,status
from .managers import CustomUserManager,PostManager
from django.contrib.auth import authenticate,login,logout
from .models import CustomUser,CustomToken,Post
from .serializers import UserSerializer,PostSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from django.utils import timezone
from .permissions import IsOwnerOrReadOnly
from django.db import IntegrityError

def get_auth_token(authenticatedUser):
    # token_serializer = CustomTokenObtainPairSerializers()
    # token = token_serializer.get_token(authenticatedUser)
    # refresh = RefreshToken.for_user(authenticatedUser)
    # token["refresh"]=str(refresh)
    # token["userid"]=int( authenticatedUser.id)
    access_token=AccessToken.for_user(authenticatedUser)
    refresh_token=RefreshToken.for_user(authenticatedUser)
    token={"access_token":str(access_token),"refresh_token":str(refresh_token)}
    return token

class AdminApiView(APIView):
    permission_classes=[IsAdminUser]
    def get(self,request):

        return Response({"admin":"admin"})
    
    def delete(self,request,*args, **kwargs):
        response={
                "status":
                {
                    "message": "",
                    "code": ""
                }
        }
        try:
            if "id" in kwargs:
                user_id=kwargs.get("id")
                print(user_id)
            else:
                response["status"]["message"]="User id not found"
                response["status"]["code"]=status.HTTP_400_BAD_REQUEST
                return Response(response)
            user= CustomUser.objects.get(pk=user_id)
            if user is not None:
                user.delete()
                response["status"]["message"]="User Permenently Deleted By Admin"
                response["status"]["code"]=status.HTTP_200_OK
            else:
                response["status"]["message"]="User Not Found"
                response["status"]["code"]=status.HTTP_404_NOT_FOUND
        except Exception as e:
             response["status"]["message"]=f"Error {e} "
             response["status"]["code"]=status.HTTP_400_BAD_REQUEST
        return Response(response) 
class UserApiView(APIView):
    # permission_classes=[IsAuthenticated]
    def get(self,request):
        users=CustomUser.objects.all()
        users=UserSerializer(users,many=True)
        response={
                "status":
                {
                    "message": "",
                    "code": ""
                }
            }
        response["status"]["data"]=users.data
        response["status"]["message"]="All users"
        response["status"]["code"]=status.HTTP_200_OK
        return Response(response)
    def post(self,request):
        response={
                "status":
                {
                    "message": "",
                    "code": ""
                }
        }
        user=request.data
        if "email" not in user or "password" not in user:
            raise ValueError("Email and Password is required")
                # return Response({"errors":""},status=status.HTTP_400_BAD_REQUEST) 
        password=user["password"]
        user= CustomUser(**user)
        user.set_password(password)
        try:
            user.save()
        except Exception as e:
             response["status"]["message"]=f"Error {e} "
             response["status"]["code"]=status.HTTP_400_BAD_REQUEST
             return Response(response)
        response["status"]["message"]="User Registered successfully"
        response["status"]["code"]=status.HTTP_201_CREATED
        return Response(response)   
    def patch(self,request):
        response={
                "status":
                {
                    "message": "",
                    "code": ""
                }
        }
        data_to_update=request.data
        user=request.user
        try:
            user= CustomUser.objects.get(pk=user.id)
            for key, value in data_to_update.items():
                if key =="password":
                    user.set_password(value)
                else:
                    setattr(user, key, value)
            user.save()
            response["status"]["message"]="Updated successfully"
            response["status"]["code"]=status.HTTP_200_OK
        except Exception as e:
             response["status"]["message"]=f"Error {e} "
             response["status"]["code"]=status.HTTP_400_BAD_REQUEST
        return Response(response)    
    def delete(self,request,*args, **kwargs):
        response={
                "status":
                {
                    "message": "",
                    "code": ""
                }
        }
        try:
            if "id" in kwargs:
                user_id=kwargs.get("id")
                print(user_id)
            else:
                response["status"]["message"]="User id not found"
                response["status"]["code"]=status.HTTP_400_BAD_REQUEST
                return Response(response)
            user= CustomUser.objects.get(pk=user_id)
            if user == request.user:
                user.delete()
                response["status"]["message"]="User Permenently Deleted Successfully"
                response["status"]["code"]=status.HTTP_200_OK
            else:
                response["status"]["message"]="Your are not Authorized to delete account"
                response["status"]["code"]=status.HTTP_401_UNAUTHORIZED
        except Exception as e:
             response["status"]["message"]=f"Error {e} "
             response["status"]["code"]=status.HTTP_400_BAD_REQUEST
        return Response(response) 
    def get_permissions(self):
        if self.request.method in ['GET','POST']:
            return [AllowAny()]  # Allow access to unauthenticated users for GET requests
        return [IsAuthenticated()]  
class UserLoginApiView(APIView):
    def post(self,request):
        user =request.data
        authenticatedUser=authenticate(request,**user)
        print("before login user")
        print(request.user)
        print(authenticatedUser)
        print("after login")
        print(request.user)
        if authenticatedUser is None:
            return Response({"Error":"Authentication failed"},status=status.HTTP_401_UNAUTHORIZED)  
        login(request,authenticatedUser)
        token=get_auth_token(authenticatedUser)
        custom_token, created = CustomToken.objects.get_or_create(user=authenticatedUser,defaults={"refresh_token":token["refresh_token"],"access_token":token["access_token"]})
        print("token created",created)
        if not created:
            custom_token.refresh_token = token["refresh_token"]
            custom_token.access_token = token["access_token"]
            custom_token.save(update_fields=['refresh_token',"access_token"])
            print("token updated")
        print(request.user)
        serializeduser=UserSerializer(authenticatedUser)
        res={
            "user":serializeduser.data,
            "status":
            {
                "message": "user authenticated",
                "code": status.HTTP_200_OK,
            },
            "token":
            {
                "access_token":token["access_token"],
                "refresh_token":token["refresh_token"]
            }
        }
        return Response(res)
class UserLogoutView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        print(request.user)
        # print(request.user.auth_token)
        token=request.headers["Authorization"].split()[1]
        token_obj=CustomToken.objects.filter(access_token=token).first()
        response={
                "status":
                {
                    "message": "",
                    "code": ""
                }
            }
        print(token_obj)
        if token_obj:
            logout(request)
            token_obj.delete()
          
            response["status"]["message"]="logout successfully"
            response["status"]["code"]=status.HTTP_200_OK
            return Response(response)
        response["status"]["message"]="Something went wrong"
        response["status"]["code"]=status.HTTP_400_BAD_REQUEST
        return Response(response)

class PostApiView(APIView):
    # permission_classes=[IsOwnerOrReadOnly]
    def get(self,request):
        response={
            "post":"",
            "status":
            {
                "message":"",
                "code": ""
            },}
        all_post=Post.objects.all()
        SerializedPost=PostSerializer(all_post,many=True)
        # if SerializedPost.is_valid():
        response["status"]["data"]=SerializedPost.data
        response["status"]["status"]=status.HTTP_200_OK
        response["status"]["message"]="All post"
        return Response(response)
    def post(self,request):
        response={
                "status":
                {
                    "message": "",
                    "code": ""
                }
            }
        # permission_classes=[IsAuthenticated]
        print(request.user)
        post=request.data
        post["userid"]=request.user
        try:
            Post.objects.create(**post)
        except Exception as e:
             response["status"]["message"]=f"Error {e} "
             response["status"]["code"]=status.HTTP_400_BAD_REQUEST
             return Response(response)
        response["status"]["message"]="post created succsessfully"
        response["status"]["code"]=status.HTTP_201_CREATED
        return Response(response)
    def patch(self,request,*args,**kwargs):
        response={
                "status":
                {
                    "message": "",
                    "code": ""
                }
            }
        if "id" in kwargs:
            post_id=kwargs.get("id")
            new_data_to_update=request.data
            user=request.user
            post_user=Post.objects.filter(userid_id=user,id=post_id).first()
            if not post_user:
                response["status"]["message"]="your are not authorized or post does not exsist"
                response["status"]["code"]=status.HTTP_400_BAD_REQUEST
                return Response(response)
            post_updated=Post.objects.filter(id=post_id).update(**new_data_to_update)
            if post_updated:
                response["status"]["message"]="Post updated successfully"
                response["status"]["code"]=status.HTTP_200_OK
        return Response(response)
    def delete(self,request,*args,**kwargs):
        response={
                "status":
                {
                    "message": "",
                    "code": ""
                }
            }
        if "id" in kwargs:
            post_id=kwargs.get("id")
            user=request.user
            post_user=Post.objects.filter(userid_id=user,id=post_id).first()
            if not post_user:
                response["status"]["message"]="your are not authorized or post does not exsist"
                response["status"]["code"]=status.HTTP_400_BAD_REQUEST
                return Response(response)
            post_updated=Post.objects.filter(id=post_id).delete()
            if post_updated:
                response["status"]["message"]="Post deleted successfully"
                response["status"]["code"]=status.HTTP_200_OK
        return Response(response)
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]  # Allow access to unauthenticated users for GET requests
        return [IsAuthenticated()] 