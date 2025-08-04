from django.contrib.auth import get_user_model
from djoser.serializers import SetPasswordSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from core.serializers import UserDetailSerializer
from .models import Subscriptions
from .serializers import (
    AvatarSerializer,
    UserCreateSerializer,
    SubscribeSerializer,
    SubscriptionsSerializer,
)

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
    'set_password': Смена пароля текущего пользователя
    """
    permission_classes = (AllowAny, )
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return UserCreateSerializer
        return UserDetailSerializer

    def get_queryset(self):
        if self.action == 'subscriptions':
            return User.objects.filter(
                followers__user=self.request.user
            ).prefetch_related('recipes')
        return User.objects.all()

    @action(
        detail=False,
        methods=['put'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def avatar(self, request):
        serializer = AvatarSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Аватар не найден'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @avatar.mapping.get
    def get_avatar(self, request):
        user = request.user
        return Response(
            {'avatar': request.build_absolute_uri(user.avatar.url)}
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='me',
        permission_classes=[IsAuthenticated]
    )
    def get_me(self, request):
        serializer = UserDetailSerializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        author = self.get_object()
        user = request.user
        serializer = SubscribeSerializer(
            data={
                'author': author.id,
                'user': user.id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscription(self, request, pk=None):
        following = self.get_object()
        if Subscriptions.objects.filter(
            user=request.user,
            author=following
        ).delete()[0]:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Вы не подписаны на этого пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        pagination_class=LimitOffsetPagination
    )
    def subscriptions(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def set_password(self, request, *args, **kwargs):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(
            serializer.validated_data['new_password']
        )
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
