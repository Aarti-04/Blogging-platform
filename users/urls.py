from django.urls import path
from .views import UserApiView,UserLoginApiView,UserLogoutView,PostApiView,AdminApiView
urlpatterns = [
    path("user/",UserApiView.as_view(),name="user_api"),
    path("user/delete/<int:id>",UserApiView.as_view(),name="user_account_delete"),
    path("login/",UserLoginApiView.as_view(),name="user_login"),
    path("logout/",UserLogoutView.as_view(),name="logout"),
    #admin
    path("admin/",AdminApiView.as_view(),name="admin_api"),
    path("admin/deleteuser/<int:id>",AdminApiView.as_view(),name="admin_userdeleteapi"),
    path("post/",PostApiView.as_view(),name="post_api"),
     path("post/<int:id>",PostApiView.as_view(),name="Post_update")

]
