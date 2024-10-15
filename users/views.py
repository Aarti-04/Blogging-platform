from rest_framework.views import APIView,Response,status
from django.contrib.auth import authenticate,login,logout
from .models import CustomUser,CustomToken,Post,Category,Comments
from .serializers import CustomeUserSerializer,PostSerializer,PostSerializer2,CommentReplySerializer2,CommentSerializer2,CategorySerializer,CommentSerializer,FilterCommentSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from django.utils import timezone
from .permissions import IsAuthorizedUser,IsAuthenticateUser
from django.db import IntegrityError
from django.db.models import Q
import jwt
from datetime import datetime,timedelta
import json
import os
# from rest_framework.parsers import MultiPartParser, FormParser
def get_auth_token(authenticatedUser):
    access_token=AccessToken.for_user(authenticatedUser)
    refresh_token=RefreshToken.for_user(authenticatedUser)
    token={"access_token":str(access_token),"refresh_token":str(refresh_token)}
    return token

class AdminApiView(APIView):
    permission_classes=[IsAdminUser]
    def create_response(self,message,code,data=None):
        response={
                "data":
                {
                    "message": message,
                    "code":code,
                }
            }
        if data is not None:
            response["data"]["data"]=data
        return Response(response)
    
    def get(self,request):
        userscount=CustomUser.objects.filter(is_active=True).count()
        Postcount=Post.objects.all().count()
        dashboard={
            "post":Postcount,
            "users":userscount
            }
        return self.create_response("Dashboard data",status.HTTP_200_OK,dashboard) 
    def patch(self,request):
        data =request.GET
        try:
            type=data.get("type") or "block"
            type=type.lower().replace(" ","").strip()
            print(data.get("id"))
            user=CustomUser.objects.get(id=data.get("id"))
            print(user)
            if user:
                if type=="block":
                    print("in block")
                    user.is_active=False
                    user.save()
                    return self.create_response("User Blocked successfully",status.HTTP_200_OK)
                else:
                    user.is_active=True
                    user.save()
                    return self.create_response("User Unblocked successfully",status.HTTP_200_OK)
            else:
                return self.create_response("User Not Found",status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return self.create_response(f"Error {e}",status.HTTP_404_NOT_FOUND)


    def delete(self,request,*args, **kwargs):
        
        try:
            userid = int(self.request.GET['userid'])
            print(userid)
            if userid is not None:
                user= CustomUser.objects.get(id=userid)
                print(user)
                if user:
                    user.delete()
                    return self.create_response("User Permenently Deleted By Admin",status.HTTP_200_OK)
                else:
                    return self.create_response("User Not Found",status.HTTP_404_NOT_FOUND)
            else:
                return self.create_response("User id not found",status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return self.create_response(f"Error",status.HTTP_400_BAD_REQUEST)
class UserApiView(APIView):
    permission_classes=[IsAuthenticateUser]
    def create_response(self,message,code,data=None):
        response={
                "data":
                {
                    "message": message,
                    "code":code,
                }
            }
        if data is not None:
            response["data"]["data"]=data
        return Response(response)
     
    def get(self,request):
        params=request.GET
        users_data=CustomUser.objects.filter(is_active=True)
        if "orderby" in params:
            users_data=users_data.order_by(params.get("orderby"))
        if "search" in params:
            users_data=users_data.filter(Q(email__icontains=params.get("search"))|Q(first_name__icontains=params.get("search"))|Q(last_name__icontains=params.get("search")))
        if users_data:
            serialized_users=CustomeUserSerializer(users_data,many=True)
            return self.create_response("all users",status.HTTP_200_OK,serialized_users.data)
        else:
            return self.create_response("No User Found",status.HTTP_404_NOT_FOUND)
    def post(self,request):
        user=request.data
        if "email" not in user or "password" not in user:
            raise ValueError("Email and Password is required") 
        password=user["password"]

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
            userid=int(self.request.GET['id'])
            print(userid)
            print(request.user.id)
            print(int(userid) == request.user.id)
            if userid:
                if userid==request.user.id:
                    user= CustomUser.objects.get(pk=userid)
                    user.delete()
                    return self.create_response("User Permenently Deleted Successfully",status.HTTP_200_OK)
                else:
                    return self.create_response("You are are not Authorized to delete account",status.HTTP_401_UNAUTHORIZED)

            else:
                return self.create_response("User id not found",status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return self.create_response(f"Error{e}",status.HTTP_400_BAD_REQUEST)

class UserLoginApiView(APIView):
    def create_response(self,message,code,data=None,access_token=None,refresh_token=None):
        response={
                "data":
                {
                    "message": message,
                    "code":code,
                }
            }
        if data is not None:
            response["data"]["data"]=data
        if access_token and refresh_token is not None:
            response["data"]["access_token"]=access_token 
            response["data"]["refresh_token"]=access_token 
        return Response(response)
    
    def post(self,request):
        user =request.data
        authenticatedUser=authenticate(request,**user)
        if authenticatedUser is None:
            return self.create_response("Authentication failed",status.HTTP_401_UNAUTHORIZED)
        login(request,authenticatedUser)
        token=get_auth_token(authenticatedUser)
        authenticate_user=CustomeUserSerializer(authenticatedUser)
        return self.create_response("User authenticated",status.HTTP_200_OK,authenticate_user.data,token["access_token"],token["refresh_token"])
class UserLogoutView(APIView):
    # logout api is not working (WIP)
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
        token=request.headers["Authorization"].split()[1]
        token_obj=CustomToken.objects.filter(access_token=token).first()
        payload = jwt.decode(token,'django-insecure--&)m)7+x@saihb(8-r#srb(%ivgb*#bd-45&ej+cc4ba4xajum',algorithms=['HS256'])
        expiration = datetime.utcnow() + timedelta(seconds=0)
        payload['exp'] =expiration
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
                "data":
                {
                    "message": message,
                    "code":code,
                }
            }
        if data is not None:
            response["data"]["data"]=data
        return Response(response)
    # def reply_of_comment(self,post):
    #     comment_reply={}
    #     for comment in post.post_comment.all():
    #         comment_reply['comments']= [{'comments': comment.comments,'id':comment.id,"userid":comment.userid,"postid":comment.postid,"created_at":comment.created_at,"updated_at":comment.updated_at}]
    #         if comment.parent_comment_id:
    #             comment_reply['reply']=[{'comments': comment.comments,'id':comment.id,"userid":comment.userid,"postid":comment.postid,"created_at":comment.created_at,"updated_at":comment.updated_at}]
    #     print(comment_reply)
    #     return comment_reply
    def reply_of_comment(self, post):
        comment_reply = []

    # Iterate through each comment associated with the post
        for comment in post.post_comment.all():
            comment_data = {
                'id': comment.id,
                'comments': comment.comments,
                'userid': comment.userid,
                'postid': comment.postid,
                'created_at': comment.created_at,
                'updated_at': comment.updated_at,
                'reply': []  # Initialize an empty list for replies
            }
            print("parent",comment.parent_comment_id)
            if comment.parent_comment_id:
                print("in parent")
                reply=Comments.objects.get(id=comment.parent_comment_id)
                print("reply....",reply.comment)
        #     # Check if the comment has a parent (i.e., it's a reply)
            # if comment.parent_comment_id:
            #     if comment_data['id'] == comment.parent_comment_id:
            #         reply=Comments.objects.filter(parent_comment_id=comment.parent_comment_id)
            #         print("on 274",reply)


        #         if parent_comment:

        #             parent_comment['reply'].append(comment_data)
        #     else:
        #         # If it's not a reply (i.e., it's a top-level comment), append it directly to the list
        #         comment_reply.append(comment_data)
        # print("on 278")
        # print(comment_reply)
        # return list(comment_reply)
    def get(self,request):
        params=request.GET
        order_by=request.GET.get("orderby") or "updated_at" 
        search_by=request.GET.get("search") or ""
        print(order_by)
        try:
            all_post=Post.customCreate.post_filter(search_by,order_by)
            # all_reply=Comments.objects.filter(parent_comment_id__isnull=False)

            # print(all_reply)
            # # d=self.comment_reply(all_post)
            # return self.create_response("h","200")
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
                'post_image':post.post_image.url if post.post_image else None,
                # 'post_comment':print(self.reply_of_comment(post))
                'comments': [{'comments': comment.comments,'id':comment.id,"userid":comment.userid,"postid":comment.postid,"parent_comment_id":comment.parent_comment_id,"created_at":comment.created_at,"updated_at":comment.updated_at} for comment in post.post_comment.all()]
                }
                # print("innnn")
                # p=post
                # print("on 314",self.reply_of_comment(p))
                posts_data.append(post_data)
            # print(posts_data)
            SerializedPost=PostSerializer(posts_data,many=True)
            # if SerializedPost.is_valid(raise_exception=True):
            return self.create_response("All post",status.HTTP_200_OK,SerializedPost.data)
        except Exception as e:
            return self.create_response(f"Error {e}",status.HTTP_400_BAD_REQUEST)

    def post(self,request):
        new_post_data=request.data
        new_post_data["userid"]=request.user.id
        try:
            category=Category.objects.get(pk=new_post_data.get("category"))
            if category is not None:
                new_post_data["category"]=category.id
                # new_post=Post(**new_post_data)
                # new_post.save()
                new_post=PostSerializer(data=new_post_data)
                if new_post.is_valid(raise_exception=False):
                    new_post.save()

                return self.create_response("post created successful",status.HTTP_201_CREATED)
        except Exception as e:
            return self.create_response(f"Error {e} ",status.HTTP_400_BAD_REQUEST)
    
    def patch(self,request,*args,**kwargs):
        postid=request.GET.get("postid")
        if postid:
            try:
                # post_id=kwargs.get("id")
                new_data_to_update=request.data
                user=request.user.id
                print("on 283")
                print(user)
                user_post=Post.objects.filter(userid_id=user,id=postid).first()
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
        else:
            return self.create_response("Postid not found",status.HTTP_404_NOT_FOUND)

    
    def delete(self,request,*args,**kwargs):
        id=request.GET
        print("*******id",id)
        post_id=str(id.get("id"))
        if id:
            # post_id=str(kwargs.get("id"))
            user=request.user.id
            print(post_id)
            post_user=Post.objects.filter(userid_id=user,id=post_id).first()
            if not post_user:
                return self.create_response("you are not authorized or post does not exist",status.HTTP_400_BAD_REQUEST)
            post_to_delete=Post.objects.filter(id=post_id).first()
            post_image_path=post_to_delete.post_image
            print(post_image_path)
            image_to_remove=str(post_image_path).split("/")[-1]
            if os.path.exists(str(image_to_remove)):
                print("ssss")
                os.remove(image_to_remove)
            print(image_to_remove)
            post_updated=post_to_delete.delete()
            if post_updated:
                return self.create_response("Post deleted successfully",status.HTTP_200_OK)
class CategoryApiView(APIView):

    permission_classes=[IsAuthorizedUser]
    def create_response(self,message,code,data=None):
        response={
                "data":
                {
                    "message": message,
                    "code":code,
                }
            }
        if data is not None:
            response["data"]["data"]=data
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

class Commentofpost(APIView):
    def get(self,request):
        response={
            "data":
            {
                "message":"",
                "status": ""
            },}
        comment_type=request.GET.get("type")
        comment_type=str(comment_type).strip().lower().replace(" ","")
        if comment_type=="comment":
            postid=request.query_params.get('postid')
            # print("geeeeee")
            if postid:
                single_category=Comments.objects.filter(Q(postid=postid) | Q(parent_comment_id=None)).all()
                print(single_category)
                if single_category is None:
                    response["data"]["data"]=""
                    response["data"]["status"]=status.HTTP_404_NOT_FOUND
                    response["data"]["message"]="No Data Found"
                    return Response(response)
                else:
                    SerializedCategory=FilterCommentSerializer(single_category,many=True)
                    response["data"]["data"]=SerializedCategory.data
                    response["data"]["status"]=status.HTTP_200_OK
                    response["data"]["message"]="All comments of single post"
                    return Response(response)
            response["data"]["status"]=status.HTTP_400_BAD_REQUEST
            response["data"]["message"]="postid not found"
            return Response(response)
class CommentApiView(APIView):
    permission_classes=[IsAuthorizedUser]
    def create_response(self,message,code,data=None):
        response={
                "data":
                {
                    "message": message,
                    "code":code,
                }
            }
        if data is not None:
            response["data"]["data"]=data
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
                print(value)
                parent_post_to_reply=Comments.objects.filter(id=value).first()
                print("on 465")
                print("ppppppppppppp")
                print(parent_post_to_reply)
                setattr(new_comment,column,parent_post_to_reply)
            else:
                setattr(new_comment,column,value)
        print(new_comment)
        return new_comment
    
    def get(self,request):
        params=request.GET
        order_by=request.GET.get("orderby") or "updated_at" 
        search_by=request.GET.get("search") or ""
        type=request.GET.get("reply")
        comment_id=request.GET.get("id")
        print(search_by)

        print(params)
        try:
            all_comments=Comments.objects.all()
            if not type and not comment_id:
                
                all_comments=Comments.commentManager.comment_filter(search_by,order_by)
            else:
                pass
                # print(search_by)
                # all_comments=all_comments.filter(Q(parent_comment_id=comment_id)|Q(comments__icontains=search_by)).order_by(order_by)
                # all_comments=all_comments.filter(Q(comments__icontains=search_by)).order_by(order_by)
            serialized_comments=CommentSerializer(all_comments,many=True)
            return self.create_response("All comments of post",status.HTTP_200_OK,serialized_comments.data)
        except Exception as e:
            return self.create_response(f"Error {e}",status.HTTP_400_BAD_REQUEST)
    def post(self,request):
        try:
            comment_type=request.data.get("type")
            comment_type=str(comment_type).strip().lower().replace(" ","") or "comment"
            new_comment_data=request.data
            # new_comment_data["userid"]=request.user.id
            print(new_comment_data.get("userid"))
            print(request.user.id)
            if str(request.user.id)==str(new_comment_data.get("userid")):
                if comment_type=="comment":
                    new_comment=Comments()
                    new_comment=self.assign_comment_data_to_comment_object(new_comment_data,new_comment)
                    new_comment.save()
                    return self.create_response("Comment Added",status.HTTP_201_CREATED)
                if comment_type=="reply":
                    print("in reply")
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