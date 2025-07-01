from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()

class AdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_staff
            )
