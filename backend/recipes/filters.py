from django_filters import rest_framework as filters

from .models import Ingredient, Recipe, Tag


class IngredientFilter(filters.FilterSet):
    """Фильтрует ингредиенты для рецепта по вхождению в начало слова."""

    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(filters.FilterSet):
    """
    Фильтрует рецепты по полям 'tags', 'is_favorited', 'is_in_shopping_cart',
    'author'.
    """
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
        label='Tags',
    )
    is_favorited = filters.BooleanFilter(
        method='filter_favorited',
        label='Is_Favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_shopping_cart',
        label='Is_In_Shopping_Cart'
    )
    author = filters.NumberFilter(
        field_name='author__id',
        label='author_id',
        lookup_expr='exact',
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'tags', 'is_in_shopping_cart', 'author')

    def filter_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(is_favorited__user=self.request.user)
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(is_in_shopping_cart__user=self.request.user)
        return queryset
