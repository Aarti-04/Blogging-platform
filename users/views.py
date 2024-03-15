from rest_framework.views import APIView,Response,status
from django.contrib.auth import authenticate,login,logout
from .models import CustomUser,CustomToken,Post,Category,Comments
from .serializers import CustomeUserSerializer,PostSerializer,CategorySerializer,CommentSerializer,FilterCommentSerializer,UserChangedSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from django.utils import timezone
from .permissions import IsAuthorizedUser,IsAuthenticateUser
from django.db import IntegrityError
from django.db.models import Q
import jwt
from datetime import datetime,timedelta

def get_auth_token(authenticatedUser):
    access_token=AccessToken.for_user(authenticatedUser)
    refresh_token=RefreshToken.for_user(authenticatedUser)
    token={"access_token":str(access_token),"refresh_token":str(refresh_token)}
    return token

class AdminApiView(APIView):
    permission_classes=[IsAdminUser]
    def create_response(self,message,code,data=None):
        response={
                "status":
                {
                    "message": message,
                    "code":code,
                }
            }
    
    def get(self,request):

        return Response({"admin":"admin"})
    
    def patch(self,request):
        data =request.data
        type=request.data.get("type").lower().replace(" ","").strip()
        user=CustomUser.objects.get(pk=data.get("id"))
        if user:
            if type=="block":
                user.is_active=False
                user.save()
                return self.create_response("User Blocked successfully",status.HTTP_200_OK)
            else:
                user.is_active=True
                user.save()
                return self.create_response("User Unblocked successfully",status.HTTP_200_OK)
        else:
            return self.create_response("User Not Found",status.HTTP_404_NOT_FOUND)

    def delete(self,request,*args, **kwargs):
        try:
            if "id" in kwargs:
                user_id=kwargs.get("id")
                print(user_id)
            else:
                return self.create_response("User id not found",status.HTTP_400_BAD_REQUEST)
            user= CustomUser.objects.get(pk=user_id)
            if user is not None:
                user.delete()
                return self.create_response("User Permenently Deleted By Admin",status.HTTP_200_OK)
            else:
                return self.create_response("User Not Found",status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return self.create_response(f"Error {e} ",status.HTTP_400_BAD_REQUEST)
class UserApiView(APIView):
    permission_classes=[IsAuthenticateUser]
    def create_response(self,message,code,data=None):
        response={
                "status":
                {
                    "message": message,
                    "code":code,
                }
            }
        if data is not None:
            response["status"]["data"]=data
        return Response(response)
     
    def get(self,request):
        params=request.GET
        try:
            users_data=CustomUser.objects.all()
            if "orderby" in params:
                users=users_data.order_by(params.get("orderby"))
            if "search" in params:
                users=users_data.filter(Q(email__icontains=params.get("search"))|Q(first_name__icontains=params.get("search"))|Q(last_name__icontains=params.get("search")))
            if users_data:
                serialized_users=CustomeUserSerializer(users,many=True)
                return self.create_response("all users",status.HTTP_200_OK,serialized_users.data)
            else:
                return self.create_response("No User Found",status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return self.create_response(f"Error {e}",status.HTTP_400_BAD_REQUEST)

    def post(self,request):
        user=request.data
        if "email" not in user or "password" not in user:
            raise ValueError("Email and Password is required") 
        User=CustomeUserSerializer(data=user)
        try:
            if User.is_valid(raise_exception=True):
                User.save()
        except Exception as e:
             return self.create_response(f"Error {e} ",status.HTTP_400_BAD_REQUEST)
        return self.create_response("User Registered successfully ",status.HTTP_201_CREATED)
    
    def patch(self,request):
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
            return self.create_response("Updated successfully ",status.HTTP_200_OK)

        except Exception as e:
             return self.create_response(f"Error {e} ",status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,*args, **kwargs):
        try:
            if "id" in kwargs:
                user_id=kwargs.get("id")
            else:
                return self.create_response("User id not found",status.HTTP_400_BAD_REQUEST)
            user= CustomUser.objects.get(pk=user_id)
            if user == request.user:
                user.delete()
                return self.create_response("User Permenently Deleted Successfully",status.HTTP_200_OK)
            else:
                return self.create_response("You are are not Authorized to delete account",status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return self.create_response(f"Error{e}",status.HTTP_400_BAD_REQUEST)

class UserLoginApiView(APIView):
    def create_response(self,message,code,data=None,access_token=None,refresh_token=None):
        response={
                "status":
                {
                    "message": message,
                    "code":code,
                }
            }
        if data is not None:
            response["status"]["data"]=data
        if access_token and refresh_token is not None:
            response["status"]["access_token"]=access_token 
            response["status"]["refresh_token"]=access_token 
        return Response(response)
    
    def post(self,request):
        print("in login")
        user =request.data
        authenticatedUser=authenticate(request,**user)
        print("before login user")
        print(request.user)
        print(authenticatedUser)
        print("after login")
        print(request.user)
        if authenticatedUser is None:
            return self.create_response("Authentication failed",status.HTTP_401_UNAUTHORIZED)
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
        authenticate_user=CustomeUserSerializer(authenticatedUser)
        return self.create_response("User authenticated",status.HTTP_200_OK,authenticate_user.data,token["access_token"],token["refresh_token"])
class UserLogoutView(APIView):
    permission_classes=[IsAuthenticated]
    def create_response(self,message,code,data=None):
        response={
                "status":
                {
                    "message": message,
                    "code":code,
                }
            }
        if data is not None:
            response["status"]["data"]=data
        return Response(response)
    
    def post(self, request):
        print(request.user)
        # print(request.user.auth_token)
        token=request.headers["Authorization"].split()[1]
        token_obj=CustomToken.objects.filter(access_token=token).first()
        print(token_obj)
        payload = jwt.decode(token,'django-insecure--&)m)7+x@saihb(8-r#srb(%ivgb*#bd-45&ej+cc4ba4xajum',algorithms=['HS256'])
        print(payload)
        expiration = datetime.utcnow() + timedelta(seconds=0)
        payload['exp'] =expiration
        print(payload)
        print(token_obj)
        if token_obj:
            # user=CustomUser.objects.get(pk=request.user.id)
            # user.is_active=False
            # user.save()
            # logout(request)
            token_obj.delete()
            return self.create_response("logout successfully",status.HTTP_200_OK)
        return self.create_response("Something went wrong",status.HTTP_400_BAD_REQUEST)
class PostApiView(APIView):
    permission_classes=[IsAuthorizedUser]
    def create_response(self,message,code,data=None):
        response={
                "status":
                {
                    "message": message,
                    "code":code,
                }
            }
        if data is not None:
            response["status"]["data"]=data
        return Response(response)
    
    def get(self,request):
        params=request.GET
        filters={}
        for key,value in params.items():
            filters[key]=value
        all_post=Post.customCreate.get_post_and_related_comments()
        if "orderby" in filters:
            all_post=all_post.order_by(filters.get("orderby"))
        if "title" in filters:
            all_post=all_post.filter(title__istartswith=filters.get("title"))
        if "search" in filters:
            all_post=all_post.filter(Q(title__icontains=filters.get("search")) | Q(category__name__icontains=filters.get("search"))|Q(content__icontains=filters.get("search")))
        posts_data=[]
        for post in all_post:
            post_data = {
            'id':post.id,
            'title': post.title,
            'content': post.content,
            'userid':post.userid,
            'category':post.category,
            'created_at':post.created_at,
            'updated_at':post.updated_at,
            'comments': [{'comments': comment.comments,'id':comment.id,"userid":comment.userid,"postid":comment.postid,"parent_comment_id":comment.parent_comment_id,"created_at":comment.created_at,"updated_at":comment.updated_at} for comment in post.post_comment.all()]
            }
            posts_data.append(post_data)
        print(posts_data)
        SerializedPost=PostSerializer(posts_data,many=True)
        return self.create_response("All post",status.HTTP_200_OK,SerializedPost.data)
   
    def post(self,request):
        new_post_data=request.data
        new_post_data["userid"]=request.user
        try:
            category=Category.objects.get(pk=new_post_data.get("category"))
            if category is not None:
                new_post_data["category"]=category
                new_post=Post(**new_post_data)
                new_post.save()
                return self.create_response("post created successful",status.HTTP_201_CREATED)
        except Exception as e:
            return self.create_response(f"Error {e} ",status.HTTP_400_BAD_REQUEST)
    
    def patch(self,request,*args,**kwargs):
        if "id" in kwargs:
            try:
                post_id=kwargs.get("id")
                new_data_to_update=request.data
                user=request.user
                print(user)
                user_post=Post.objects.filter(userid_id=user,id=post_id).first()
                print(user_post)
                if not user_post:
                    return self.create_response("your are not authorized or post does not exist",status.HTTP_400_BAD_REQUEST)
                for key,value in new_data_to_update.items():
                    if key=="category":
                        category=Category.objects.get(pk=value)
                        if category is None:
                            return self.create_response("Category not exist",status.HTTP_200_OK)
                        else:
                            new_data_to_update["category"]=category
                            setattr(user_post,key,category)
                    else:
                        setattr(user_post,key,value)   
                post_updated=user_post.save()
                if post_updated is None:
                    return self.create_response("Post updated successfully",status.HTTP_200_OK)
            except Exception as e:
                return self.create_response(f"Error {e} ",status.HTTP_200_OK)
    
    def delete(self,request,*args,**kwargs):
        if "id" in kwargs:
            post_id=kwargs.get("id")
            user=request.user
            post_user=Post.objects.filter(userid_id=user,id=post_id).first()
            if not post_user:
                return self.create_response("you are not authorized or post does not exist",status.HTTP_400_BAD_REQUEST)
            post_updated=Post.objects.filter(id=post_id).delete()
            if post_updated:
                return self.create_response("Post deleted successfully",status.HTTP_200_OK)
class CategoryApiView(APIView):

    permission_classes=[IsAuthorizedUser]
    def create_response(self,message,code,data=None):
        response={
                "status":
                {
                    "message": message,
                    "code":code,
                }
            }
        if data is not None:
            response["status"]["data"]=data
        return Response(response)

    def get(self,request):
        category_name=request.query_params.get('name')
        if category_name:
            all_category=Category.objects.filter(name__icontains=category_name)
        else:
            all_category=Category.objects.all()
        if all_category is None:
            return self.create_response("No Data Found",status.HTTP_404_NOT_FOUND)
        else:
            SerializedCategory=CategorySerializer(all_category,many=True)
            return self.create_response("All Category",status.HTTP_200_OK,SerializedCategory.data)
    
    def post(self,request):
        category=request.data
        category_name=category.get("name").lower()
        category["name"]=category_name
        print(category_name)
        try:
            check_category=Category.objects.filter(name=category_name).first()
            if check_category is None:
                Category.objects.create(**category)
            else:
                return self.create_response("Category already exist",status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return self.create_response(f"Error {e} ",status.HTTP_400_BAD_REQUEST)
        return self.create_response("Category created successfully",status.HTTP_201_CREATED)
    
    def patch(self,request,*args,**kwargs):
        if "id" in kwargs:
            category_id=kwargs.get("id")
            new_data_to_update=request.data
            category_to_update=Category.objects.filter(id=category_id).first()
            if not category_to_update:
                return self.create_response("Category does not exist",status.HTTP_400_BAD_REQUEST)
            for key,value in new_data_to_update.items():
                setattr(category_to_update, key, value)
            category_updated= category_to_update.save()
            if category_updated is None:
                return self.create_response("Category updated successfully",status.HTTP_200_OK)
    
    def delete(self,request,*args,**kwargs):
        if "id" in kwargs:
            category_id=kwargs.get("id")
            post_user=Category.objects.filter(id=category_id).first()
            if not post_user:
                return self.create_response("Category does not exist",status.HTTP_400_BAD_REQUEST)
            category_deleted=Category.objects.filter(id=category_id).delete()
            if category_deleted:
                return self.create_response("Category deleted successfully",status.HTTP_200_OK)

# class Commentofpost(APIView):
#     def create_response(self,message,code,data=None):
#         response={
#                 "status":
#                 {
#                     "message": message,
#                     "code":code,
#                 }
#             }
#         if data is not None:
#             response["status"]["data"]=data
#         return Response(response)
#     def get(self,request):
#         comment_type=request.GET.get("type")
#         comment_type=str(comment_type).strip().lower().replace(" ","")
#         params=request.GET
#         if comment_type=="comment":
#             postid=request.query_params.get('postid')
#             # print("geeeeee")
#             if postid:
#                 single_category=Comments.objects.filter(Q(postid=postid) | Q(parent_comment_id=None)).all()
#                 print(single_category)
#                 if single_category is None:
#                     return self.create_response("No Data Found",status.HTTP_404_NOT_FOUND)
#                 else:
#                     SerializedCategory=FilterCommentSerializer(single_category,many=True)
#                     return self.create_response("All comments of single post",status.HTTP_200_OK,SerializedCategory.data)
#             return self.create_response("post id not found",status.HTTP_400_BAD_REQUEST)
        
class CommentApiView(APIView):
    permission_classes=[IsAuthorizedUser]
    def create_response(self,message,code,data=None):
        response={
                "status":
                {
                    "message": message,
                    "code":code,
                }
            }
        if data is not None:
            response["status"]["data"]=data
        return Response(response)
    
    def assign_comment_data_to_comment_object(self,new_comment_data,new_comment):
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
            elif column=="parent_comment_id":
                parent_post_to_reply=Comments.objects.filter(id=value).first()
                print("on 465")
                print(parent_post_to_reply)
                setattr(new_comment,column,parent_post_to_reply)
            else:
                setattr(new_comment,column,value)
        return new_comment
    
    def get(self,request):
        params=request.GET
        print(params)
        filters={}
        comment_type=request.GET.get("type")
        try:
            if comment_type=="reply":
                reply_of_perticular_comments=Comments.objects.filter(parent_comment_id=params.get("search"))
                if reply_of_perticular_comments:
                    Serialized_comment_reply=FilterCommentSerializer(reply_of_perticular_comments,many=True)
                    return self.create_response("Reply of comments",status.HTTP_200_OK,Serialized_comment_reply.data)
            else:
                all_comments=Comments.objects.all()
            serialized_comments=CommentSerializer(all_comments,many=True)
            return self.create_response("All comments of post",status.HTTP_200_OK,serialized_comments.data)
        except Exception as e:
            return self.create_response(f"Error {e}",status.HTTP_400_BAD_REQUEST)
   
    def post(self,request):
        try:
            comment_type=request.data.get("type")
            comment_type=str(comment_type).strip().lower().replace(" ","")
            new_comment_data=request.data
            print(new_comment_data.get("userid"))
            print(request.user)
            if request.user.id==new_comment_data.get("userid"):
                if comment_type=="comment":
                    new_comment=Comments()
                    new_comment=self.assign_comment_data_to_comment_object(new_comment_data,new_comment)
                    new_comment.save()
                    return self.create_response("Comment Added",status.HTTP_201_CREATED)
                if comment_type=="reply":
                    new_comment_data=request.data
                    reply_to_comment=Comments()
                    reply_to_comment=self.assign_comment_data_to_comment_object(new_comment_data,reply_to_comment)
                    reply_to_comment.save()
                    return self.create_response("Replied to comment Successfully",status.HTTP_201_CREATED)
            else:
                return self.create_response("You can't add comment from other's user id",status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                return self.create_response(f"Error {e}",status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        data=request.data
        userid,commentid=data.get("userid"),data.get("commentid")
        if request.user.id==userid:
            print("i m in...")
            comment_of_user=Comments.objects.filter(userid=userid,id=commentid).first()
            if comment_of_user:
                comment_deleted=comment_of_user.delete()
                print(comment_deleted)
                if comment_deleted:
                    return self.create_response("Comment deleted",status.HTTP_200_OK)
            else:
                return self.create_response("Comment does not exist",status.HTTP_400_BAD_REQUEST)
        else:
            return self.create_response("you are not authorized",status.HTTP_400_BAD_REQUEST)   
        
class UserChangePassword(APIView):
    def create_response(self,message,code,data=None):
        response={
                "status":
                {
                    "message": message,
                    "code":code,
                }
            }
        if data is not None:
            response["status"]["data"]=data
        return Response(response)
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            serializer=UserChangedSerializer(data=request.data,context={'user':request.user})
            if serializer.is_valid(raise_exception=True):
                return self.create_response("password changed successfully",status.HTTP_200_OK)
        except Exception as e:
            return self.create_response(f"Error {e}",status.HTTP_400_BAD_REQUEST)
# class SendResetPasswordEmailView(APIView):
#     def create_response(self,message,code,data=None):
#         response={
#                 "status":
#                 {
#                     "message": message,
#                     "code":code,
#                 }
#             }
#         if data is not None:
#             response["status"]["data"]=data
#         return Response(response)
#     permission_classes=[IsAuthenticated]
#     def post(self,request):
#         try:
#             serializer=SendResetPasswordEmailSerializer(data=request.data)
#             if serializer.is_valid(raise_exception=True):
#                 return self.create_response("password reset link send successfully!Please check your email",status.HTTP_200_OK)
#         except Exception as e:
#             return self.create_response(f"Error {e}",status.HTTP_400_BAD_REQUEST)