from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from foodgram.serializers import ShortRecipeSerializer
from .filters import IngredientFilter, RecipeFilter
from .models import Favorite, Ingredient, Tag, Recipe, ShoppingCart
from .permissions import AdminOrReadOnlyPermission, AuthorOrReadOnlyPermission
from .serializers import (
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
            serializer = ShortRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            Favorite.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


    @action(
            detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            ShoppingCart.objects.get_or_create(user=request.user, recipe=recipe)
            serializer = ShortRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            ShoppingCart.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


    @action(
            detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(
            user=request.user
        ).select_related(
            'recipe'
        ).prefetch_related(
            'recipe__ingredientrecipe_set__ingredient'
        )
        shopping_list = {}

        for item in shopping_cart:
            recipe = item.recipe
            for ingredient_recipe in item.recipe.ingredientrecipe_set.all():
                ingredient = ingredient_recipe.ingredient
                if ingredient.name not in shopping_list:
                    shopping_list[ingredient.name] = [
                        ingredient_recipe.amount,
                        ingredient.measurement_unit
                    ]
                else:
                    shopping_list[ingredient.name][0] += ingredient_recipe.amount

        file_content = 'Список покупок:\n\n'
        for ingredient in shopping_list:
            file_content += (
                f'- {ingredient}: {shopping_list[ingredient][0]} {shopping_list[ingredient][1]}\n'
            )
        response = HttpResponse(file_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response
