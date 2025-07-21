from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()


class AuthorOrReadOnlyPermission(permissions.BasePermission):
    """
    Контролирует доступ к объектам по авторству:
    Чтение доступно всем пользователям, изменение - только аутентифицированным
    пользователям, для существующих объектов - только автору объекта.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            or request.method in permissions.SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
