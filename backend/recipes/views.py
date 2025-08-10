from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .mixins import PatchModelMixin
from .models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag
)
from .permissions import AuthorOrReadOnlyPermission
from .serializers import (
    RecipeCreateSerializer,
    IngredientDisplaySerializer,
    RecipeDisplaySerializer,
    TagReadSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer
)


class TagIngredientBaseViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Базовый вьюсет для тегов и ингредиентов."""
    pagination_class = None


class TagViewSet(TagIngredientBaseViewSet):
    """Вьюсет для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagReadSerializer


class IngredientViewSet(TagIngredientBaseViewSet):
    """Вьюсет для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientDisplaySerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter


class RecipeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    PatchModelMixin,
    viewsets.GenericViewSet
):
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
    permission_classes = (AuthorOrReadOnlyPermission, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeDisplaySerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_to_favorite_or_shopping_cart(self, request, pk, serializer):
        recipe = self.get_object()
        user = request.user
        serializer = serializer(
            data={
                'recipe': recipe.id,
                'user': user.id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from_favorite_or_shopping_cart(self, request, pk, model, text):
        recipe = self.get_object()
        if model.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()[0]:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            text,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        return self.add_to_favorite_or_shopping_cart(
            request,
            pk,
            FavoriteSerializer
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self.delete_from_favorite_or_shopping_cart(
            request,
            pk,
            model=Favorite,
            text='Рецепт не был добавлен в избранное'
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        return self.add_to_favorite_or_shopping_cart(
            request,
            pk,
            ShoppingCartSerializer
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self.delete_from_favorite_or_shopping_cart(
            request,
            pk,
            model=ShoppingCart,
            text='Рецепт не был добавлен в корзину'
        )

    def _create_shopping_list(self, shopping_list):
        file_content = 'Список покупок:\n\n'
        for ingredient in shopping_list:
            file_content += (
                f'- {ingredient["ingredient__name"]}: '
                f'{ingredient["total_amount"]} '
                f'{ingredient["ingredient__measurement_unit"]}\n'
            )
        return file_content

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        shopping_list = IngredientRecipe.objects.filter(
            recipe__shoppingcart_recipe__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by(
            'ingredient__name'
        )
        file_content = self._create_shopping_list(shopping_list)
        response = HttpResponse(file_content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response
