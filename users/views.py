from django.shortcuts import render
from rest_framework.views import APIView,Response,status
from .managers import CustomUserManager,PostManager
from django.contrib.auth import authenticate,login,logout
from .models import CustomUser,CustomToken,Post,Category,Comments
from .serializers import UserSerializer,PostSerializer,CategorySerializer,CommentSerializer,FilterCommentSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from django.utils import timezone
from .permissions import IsOwnerOrReadOnly
from django.db import IntegrityError
from django.db.models import Q

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
            "response":
            {
                "message":"",
                "code": ""
            },}
        all_post=Post.objects.all()
        SerializedPost=PostSerializer(all_post,many=True)
        response["response"]["data"]=SerializedPost.data
        response["response"]["status"]=status.HTTP_200_OK
        response["response"]["message"]="All post"
        return Response(response)
    def post(self,request):
        response={
                "response":
                {
                    "message": "",
                    "code": ""
                }
            }
        new_post_data=request.data
        new_post_data["userid"]=request.user
        try:
            category=Category.objects.get(pk=new_post_data.get("category"))
            if category is not None:
                new_post_data["category"]=category
                new_post=Post(**new_post_data)
                new_post.save()
                response["response"]["message"]="post created succsessfully"
                response["response"]["code"]=status.HTTP_201_CREATED
                return Response(response)
        except Exception as e:
            response["status"]["message"]=f"Error {e} "
            response["status"]["code"]=status.HTTP_400_BAD_REQUEST
            return Response(response)
        
    def patch(self,request,*args,**kwargs):
        response={
                "response":
                {
                    "message": "",
                    "code": ""
                }
            }
        if "id" in kwargs:
            try:
                post_id=kwargs.get("id")
                new_data_to_update=request.data
                user=request.user
                print(user)
                user_post=Post.objects.filter(userid_id=user,id=post_id).first()
                if not user_post:
                    response["response"]["message"]="your are not authorized or post does not exsist"
                    response["response"]["code"]=status.HTTP_400_BAD_REQUEST
                    return Response(response)
                for key,value in new_data_to_update.items():
                    if key=="category":
                        category=Category.objects.get(pk=value)
                        if category is None:
                            response["response"]["message"]="Category not exist"
                            response["response"]["code"]=status.HTTP_200_OK
                            return Response(response)
                        else:
                            new_data_to_update["category"]=category
                            setattr(user_post,key,category)
                    else:
                        setattr(user_post,key,value)   
                post_updated=user_post.save()
                if post_updated is None:
                    response["response"]["message"]="Post updated successfully"
                    response["response"]["code"]=status.HTTP_200_OK
            except Exception as e:
                response["response"]["message"]=f"Error {e} "
                response["response"]["code"]=status.HTTP_200_OK
        return Response(response)
    def delete(self,request,*args,**kwargs):
        response={
                "response":
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
                response["response"]["message"]="your are not authorized or post does not exsist"
                response["response"]["code"]=status.HTTP_400_BAD_REQUEST
                return Response(response)
            post_updated=Post.objects.filter(id=post_id).delete()
            if post_updated:
                response["response"]["message"]="Post deleted successfully"
                response["response"]["code"]=status.HTTP_200_OK
        return Response(response)
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]  # Allow access to unauthenticated users for GET requests
        return [IsAuthenticated()] 

class SingleCategoryApiView(APIView):
    def get(self,request):
        response={
            "status":
            {
                "message":"",
                "status": ""
            },}
        category_name=request.query_params.get('name')
        if category_name:
            single_category=Category.objects.filter(name=category_name).first()
            if single_category is None:
                response["status"]["data"]=""
                response["status"]["status"]=status.HTTP_404_NOT_FOUND
                response["status"]["message"]="No Data Found"
                return Response(response)
            else:
                SerializedCategory=CategorySerializer(single_category,many=False)
                response["status"]["data"]=SerializedCategory.data
                response["status"]["status"]=status.HTTP_200_OK
                response["status"]["message"]="Single Category"
                return Response(response)
        response["status"]["status"]=status.HTTP_400_BAD_REQUEST
        response["status"]["message"]="Category name not found"
        return Response(response)

class CategoryApiView(APIView):

    # permission_classes=[IsOwnerOrReadOnly]
    def get(self,request):
        response={
            "response":
            {
                "message":"",
                "code": ""
            },}
        all_category=Category.objects.all()
        if all_category is None:
            response["status"]["data"]=""
            response["status"]["status"]=status.HTTP_404_NOT_FOUND
            response["status"]["message"]="No Data Found"
            return Response(response)
        else:
            SerializedCategory=CategorySerializer(all_category,many=True)
            response["response"]["data"]=SerializedCategory.data
            response["response"]["status"]=status.HTTP_200_OK
            response["response"]["message"]="All Category"
            return Response(response)
    def post(self,request):
        response={
                "response":
                {
                    "message": "",
                    "code": ""
                }
            }
        category=request.data
        try:
            check_category=Category.objects.filter(name=category.get("name")).first()
            if check_category is None:
                Category.objects.create(**category)
            else:
                response["response"]["message"]="Category already exist"
                response["response"]["code"]=status.HTTP_400_BAD_REQUEST
                return Response(response)
        except Exception as e:
             response["response"]["message"]=f"Error {e} "
             response["response"]["code"]=status.HTTP_400_BAD_REQUEST
             return Response(response)
        response["response"]["message"]="Category created succsessfully"
        response["response"]["code"]=status.HTTP_201_CREATED
        return Response(response)
    def patch(self,request,*args,**kwargs):
        response={
                "response":
                {
                    "message": "",
                    "code": ""
                }
            }
        if "id" in kwargs:
            category_id=kwargs.get("id")
            new_data_to_update=request.data
            category_to_update=Category.objects.filter(id=category_id).first()
            if not category_to_update:
                response["response"]["message"]="Category does not exist"
                response["response"]["code"]=status.HTTP_400_BAD_REQUEST
                return Response(response)
            for key,value in new_data_to_update.items():
                setattr(category_to_update, key, value)
            category_updated= category_to_update.save()
            if category_updated is not None:
                response["response"]["message"]="Category updated successfully"
                response["response"]["code"]=status.HTTP_200_OK
                print("on 363",category_to_update)
        return Response(response)
    def delete(self,request,*args,**kwargs):
        response={
                "response":
                {
                    "message": "",
                    "code": ""
                }
            }
        # category_id=request.params.
        if "id" in kwargs:
            category_id=kwargs.get("id")
            post_user=Category.objects.filter(id=category_id).first()
            if not post_user:
                response["response"]["message"]="Category does not exist"
                response["response"]["code"]=status.HTTP_400_BAD_REQUEST
                return Response(response)
            category_deleted=Category.objects.filter(id=category_id).delete()
            if category_deleted:
                response["response"]["message"]="Category deleted successfully"
                response["response"]["code"]=status.HTTP_200_OK
        return Response(response)
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]  # Allow access to unauthenticated users for GET requests
        return [IsAuthenticated()] 
    

class Commentofpost(APIView):
    def get(self,request):
        response={
            "status":
            {
                "message":"",
                "status": ""
            },}
        postid=request.query_params.get('postid')
        print("geeeeee")
        if postid:
            single_category=Comments.objects.filter(Q(postid=postid)).all()
            print(single_category)
            if single_category is None:
                response["status"]["data"]=""
                response["status"]["status"]=status.HTTP_404_NOT_FOUND
                response["status"]["message"]="No Data Found"
                return Response(response)
            else:
                SerializedCategory=FilterCommentSerializer(single_category,many=True)
                response["status"]["data"]=SerializedCategory.data
                response["status"]["status"]=status.HTTP_200_OK
                response["status"]["message"]="Single Category"
                return Response(response)
        response["status"]["status"]=status.HTTP_400_BAD_REQUEST
        response["status"]["message"]="Category name not found"
        return Response(response)
class CommentApiView(APIView):
    def get(self,request):
        response={
            "response":
            {
                "message":"",
                "code": ""
            },}
        all_comments=Comments.objects.all()
        serialized_comments=CommentSerializer(all_comments,many=True)

        response["response"]["data"]=serialized_comments.data
        response["response"]["status"]=status.HTTP_200_OK
        response["response"]["message"]="Comment Added"
        return Response(response)
    def post(self,request):
        response={
            "response":
            {
                "message":"",
                "code": ""
            },}
        # type=request.params.get("type")
        new_comment_data=request.data
        new_comment=Comments()
        print("on 455")
        print(new_comment)
        # request_type=request.params.get("type")
        for column,value in new_comment_data.items():
            if column=="userid":
                userid_to_comment=CustomUser.objects.filter(id=value).first()
                print("on 459")
                print(userid_to_comment)
                setattr(new_comment,column,userid_to_comment)
                # pass
            elif column=="postid":
                postid_to_comment=Post.objects.filter(id=value).first()
                print("on 465")
                print(postid_to_comment)
                setattr(new_comment,column,postid_to_comment)
            # elif column=="parent_comment_id" and request_type=="reply":
            #     postid_to_reply=Post.objects.filter(id=value).first()
            #     setattr(new_comment,column,postid_to_reply)
            else:
                setattr(new_comment,column,value)
        print("on 470")   
        print(new_comment)
        # new_comment_data["userid"]=request.user
        # new_comment=Comments(**new_comment_data)
        # setattr(new_comment,"parent_comment_id",None)
        new_comment.save()
        response["response"]["status"]=status.HTTP_201_CREATED
        response["response"]["message"]="Comment Added"
        return Response(response)
    def delete(self,request):
        response={
            "response":
            {
                "message":"",
                "code": ""
            },}
        data=request.data
        userid,postid,commentid=data.get("userid"),data.get("postid"),data.get("commentid")
        print(userid)
        print(request.user.id)
        if request.user.id==userid:
            print("i m in...")
            comment_of_user=Comments.objects.filter(userid=userid,id=commentid).first()
            if comment_of_user:
                comment_deleted=comment_of_user.delete()
                print(comment_deleted)
                if comment_deleted:
                    response["response"]["status"]=status.HTTP_200_OK
                    response["response"]["message"]="Comment deleted"
            else:
                response["response"]["status"]=status.HTTP_400_BAD_REQUEST
                response["response"]["message"]="Comment does not exist"
            return Response(response)
        else:
            response["response"]["status"]=status.HTTP_400_BAD_REQUEST
            response["response"]["message"]="you are not authorized"
            return Response(response)
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]  # Allow access to unauthenticated users for GET requests
        return [IsAuthenticated()]    