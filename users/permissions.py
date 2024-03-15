# from rest_framework.permissions import BasePermission
# from rest_framework.permissions import IsAuthenticated

# class IsOwnerOrReadOnly(BasePermission):
#     """
#     Custom permission to only allow owners of an object to edit it.
#     """
#     def has_object_permission(self, request, view, obj):
#         # print("in permission")
#         # Read permissions are allowed to any request,
#         # so we'll always allow GET, HEAD or OPTIONS requests.
#         if request.method in ['GET', 'HEAD', 'OPTIONS']:
#             return True
        
#         # Write permissions are only allowed to the owner of the post.
#         return obj.user == request.user
#     # def get_permission(self,request):
#     #     if request.method == 'GET':
#     #         return [AllowAny()]  # Allow access to unauthenticated users for GET requests
#     #     return [IsAuthenticated()] 
from rest_framework import permissions

class IsAuthorizedUser(permissions.BasePermission):
    #Custome Permission
    def has_permission(self, request, view):
        if request.method =='GET':
            return True
        return request.user and request.user.is_authenticated
    def has_object_permission(self, request, view, obj):
        return obj.userid == request.user
class IsAuthenticateUser(permissions.BasePermission):
    #Custome Permission
    def has_permission(self, request, view):
        if request.method in ['GET','POST']:
            return True
        return request.user and request.user.is_authenticated
    def has_object_permission(self, request, view, obj):
        return obj.userid == request.user