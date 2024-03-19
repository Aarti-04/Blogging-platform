from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager,PostManager,CommentManager
from django.conf import settings
from django.utils import timezone
import uuid

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username=None
    email=models.EmailField(_("Email Address"),unique=True)
    USERNAME_FIELD="email"
    updated_at=models.DateTimeField(auto_now=True)
    REQUIRED_FIELDS=[]
    objects=CustomUserManager()
    # customMethods=CustomeUserMethods()
class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    objects=models.Manager()

    def __str__(self):
        return str(self.name)
class Post(models.Model):
    # def upload_to(instance, filename):
    #     return 'images/{filename}'.format(filename=filename)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title=models.CharField(_("post title"),max_length=100)
    content=models.CharField(_("post content"),max_length=200)
    userid=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    post_image=models.ImageField(upload_to="post_images/", blank=True, null=True)
    objects=models.Manager()
    customCreate=PostManager()

    

class Comments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    postid=models.ForeignKey(Post, on_delete=models.CASCADE,related_name="post_comment")
    userid=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="user_comment")
    parent_comment_id=models.ForeignKey("self",null=True,default=None,blank=True,on_delete=models.CASCADE,related_name="parent_comment")
    comments=models.CharField(max_length=200)
    objects=models.Manager()
    commentManager=CommentManager()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
class CustomToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    objects=models.Manager()
    # c_token=CustomTokenManager()
    def __str__(self) -> str:
        return str(self.access_token)
# Create your models here.
