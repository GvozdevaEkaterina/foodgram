from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .serializers import CustomUserCreateSerializer, UserDetailSerializer


User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserCreateSerializer
    permission_classes = (AllowAny, )
    pagination_class = PageNumberPagination 

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
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
