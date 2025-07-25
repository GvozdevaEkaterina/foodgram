from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Subscriptions
from .serializers import (AvatarSerializer, CustomUserCreateSerializer,
                          SubscribeSerializer, UserDetailSerializer)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с пользователями.
    Использует разные сериалайзеры для создания и просмотра профиля
    пользователя.
    Имеет кастомные эндпоинты:
    '/me/avatar': Добавление/удаление аватара
    '/me': Страница текущего пользователя
    'subscribe': Подписка на пользователя / отписка от него
    'subscriptions': Просмотр всех пользователей, на которых подписан автор
    запроса.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny, )
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return CustomUserCreateSerializer
        return UserDetailSerializer

    @action(
        detail=False,
        methods=['put', 'get', 'delete'],
        url_path='me/avatar'
    )
    def add_avatar(self, request):
        user = request.user
        if (
            not user.is_authenticated
            and (request.method == 'PUT' or request.method == 'DELETE')
        ):
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if request.method == 'GET':
            return Response(
                {'avatar': request.build_absolute_uri(user.avatar.url)}
            )
        if request.method == 'DELETE':
            user.avatar.delete()
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if 'avatar' not in request.data:
            return Response(
                {'error': 'File "avatar" is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = AvatarSerializer(
            user,
            data={'avatar': request.data['avatar']},
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='me')
    def get_me(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = UserDetailSerializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        following = self.get_object()
        if request.method == 'POST':
            if request.user == following:
                return Response(
                    {'error': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            object, created = Subscriptions.objects.get_or_create(
                user=request.user,
                author=following
            )
            if not created:
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscribeSerializer(
                following,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            deleted, details = Subscriptions.objects.filter(
                user=request.user,
                author=following
            ).delete()

            if not deleted:
                return Response(
                    {'error': 'Вы не подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        pagination_class=LimitOffsetPagination
    )
    def subscriptions(self, request):
        subscribed_users = User.objects.filter(
            followers__user=request.user
        ).prefetch_related('recipes')

        page = self.paginate_queryset(subscribed_users)
        serializer = SubscribeSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return (
            self.get_paginated_response(serializer.data)
            if page is not None
            else Response(serializer.data)
        )
