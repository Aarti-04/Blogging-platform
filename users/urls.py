from django.urls import path
from .views import UserApiView,UserLoginApiView,UserLogoutView,PostApiView,AdminApiView,CategoryApiView,CommentApiView,UserChangePassword
urlpatterns = [
    #users
    path("user/",UserApiView.as_view(),name="user_api"),
    path("user/delete/<int:id>",UserApiView.as_view(),name="user_account_delete"),
    path("login/",UserLoginApiView.as_view(),name="user_login"),
    path("logout/",UserLogoutView.as_view(),name="logout"),
    path("user/changepassword",UserChangePassword.as_view(),name="change_password"),
    #admin
    path("admin/",AdminApiView.as_view(),name="admin_api"),
    path("admin/deleteuser/<int:id>",AdminApiView.as_view(),name="admin_user_delete"),
    #post
    path("post/",PostApiView.as_view(),name="post_api"),
    path("post/<int:id>",PostApiView.as_view(),name="Post_update"),
    #category
    path("category/",CategoryApiView.as_view(),name="category_api"),
    path("category/<int:id>",CategoryApiView.as_view(),name="category_update"),
    # path("singlecategory/",SingleCategoryApiView.as_view(),name="get_single_category"),
    #comment
    path("comment/",CommentApiView.as_view(),name="add_comment"),
    # path("commentfilter/",Commentofpost.as_view(),name="single_comment")





]
