from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .pagination import CustomPageNumberPagination
from .permissions import AuthorOrReadOnlyPermission
from .serializers import (
    IngredientsSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    TagSerializer
)


class TagIngredientBaseViewSet(viewsets.ModelViewSet):
    """
    Базовый вьюсет для тегов и ингредиентов.
    Разрешает создание, редактирование и удаление только администратору
    """
    pagination_class = None

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)


class TagViewSet(TagIngredientBaseViewSet):
    """Вьюсет для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(TagIngredientBaseViewSet):
    """Вьюсет для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для рецептов.
    Включает в себя несколько кастомных методов:
    -favorite: позволяет добавить/удалить рецепт из избранного.
    -shopping_cart: позволяет добавить/удалить рецепт из списка покупок.
    -download_shopping_cart: позволяет скачать список покупок в формате txt.
    Если ингредиенты в рецептах повторяются, количество этих продуктов
    суммируется.
    """
    queryset = Recipe.objects.all().order_by('-id')
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnlyPermission, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPagination

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
            if Favorite.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                return Response(
                    'Рецепт уже находится в избранном',
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = ShortRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    'Рецепт не был добавлен в избранное',
                    status=status.HTTP_400_BAD_REQUEST
                )
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
            if ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    'Рецепт уже находится в корзине',
                    status=status.HTTP_400_BAD_REQUEST
                )

            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = ShortRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    'Рецепт не был добавлен в корзину',
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()
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
