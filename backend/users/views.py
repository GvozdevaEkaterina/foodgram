from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from foodgram.serializers import UserDetailSerializer
from .models import Subscriptions
from .serializers import (
    UserCreateSerializer,
    SubscribeSerializer
)


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny, )
    pagination_class = PageNumberPagination 

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserDetailSerializer

    @action(detail=False, methods=['put', 'get', 'delete'], url_path='me/avatar')
    def add_avatar(self, request):
        user = request.user
        if (
            not user.is_authenticated and
            (request.method == 'PUT' or request.method == 'DELETE')
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

        serializer = UserDetailSerializer(
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
        pagination_class=PageNumberPagination
    )
    def subscriptions(self, request):
        subscribed_users = User.objects.filter(
            followers__user=request.user
        ).prefetch_related('recipes')

        page = self.paginate_queryset(subscribed_users)
        serializer = SubscribeSerializer(
            subscribed_users,
            many=True,
            context={'request': request}
        )
        return (self.get_paginated_response(serializer.data)
                if page is not None
                else Response(serializer.data)
        )
