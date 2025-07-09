from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .models import Favorite, Ingredient, Tag, Recipe
from .permissions import AdminOrReadOnlyPermission, AuthorOrReadOnlyPermission
from .serializers import (
    FavoriteRecipeSerializer,
    RecipeSerializer,
    IngredientsSerializer,
    TagSerializer,
)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnlyPermission, )
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (AdminOrReadOnlyPermission, )
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-id')
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnlyPermission, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
            detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            Favorite.objects.get_or_create(user=request.user, recipe=recipe)
            serializer = FavoriteRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            Favorite.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
