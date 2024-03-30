from django.urls import path
from .views import UserApiView,UserLoginApiView,UserLogoutView,PostApiView,AdminApiView,CategoryApiView,CommentApiView
urlpatterns = [
    #users
    path("user/",UserApiView.as_view(),name="user_api"),
    path("login/",UserLoginApiView.as_view(),name="user_login"),
    path("logout/",UserLogoutView.as_view(),name="logout"),
    # path("user/changepassword",UserChangePassword.as_view(),name="change_password"),
    # path("user/send-reset-password-email/",SendResetPasswordEmailView.as_view(),name="reset_password_email"),
    #admin
    path("admin/",AdminApiView.as_view(),name="admin_api"),
    #post
    path("post/",PostApiView.as_view(),name="post_api"),
    path("post/<int:id>",PostApiView.as_view(),name="Post_update"),
    #category
    path("category/",CategoryApiView.as_view(),name="category_api"),
    path("category/<int:id>",CategoryApiView.as_view(),name="category_update"),
    #comment
    path("comment/",CommentApiView.as_view(),name="add_comment"),
]
