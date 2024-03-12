from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager,CustomeUserMethods,CustomTokenManager,PostManager
from django.conf import settings
from django.utils import timezone

class CustomUser(AbstractUser):
    username=None
    email=models.EmailField(_("Email Address"),unique=True)
    USERNAME_FIELD="email"
    updated_at=models.DateTimeField(auto_now=True)
    REQUIRED_FIELDS=[]
    objects=CustomUserManager()
    customMethods=CustomeUserMethods()
class Category(models.Model):
    name = models.CharField(max_length=100)
    objects=models.Manager()

    def __str__(self):
        return str(self.name)
class Post(models.Model):
    title=models.CharField(_("post title"),max_length=20)
    content=models.CharField(_("post content"),max_length=200)
    userid=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)
    objects=models.Manager()
    postManager=PostManager()
    def save(self, *args, **kwargs):
        # Check if the category exists, if not, create it
        if not self.category.id:
            try:
                existing_category = Category.objects.get(name=self.category.name)
                self.category = existing_category
            except Exception as e:
                print(e)
                self.category.save()

        super().save(*args, **kwargs)

class Comments(models.Model):
    postid=models.ForeignKey(Post, on_delete=models.CASCADE)
    userid=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    parent_comment_id=models.ForeignKey("self",blank=True,on_delete=models.CASCADE,related_name="parent_comment")
    comments=models.CharField(max_length=200)
class CustomToken(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    objects=models.Manager()
    # c_token=CustomTokenManager()
    def __str__(self) -> str:
        return str(self.access_token)
# Create your models here.
