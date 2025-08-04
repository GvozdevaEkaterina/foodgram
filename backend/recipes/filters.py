from django.db.models import Case, IntegerField, Q, Value, When
from django_filters import rest_framework as filters

from .models import Ingredient, Recipe, Tag


class IngredientFilter(filters.FilterSet):
    """
    Фильтрует ингредиенты для рецепта по вхождению в начало и в середину слова.
    """
    name = filters.CharFilter(method='filter_by_name')

    class Meta:
        model = Ingredient
        fields = ('name', )

    def filter_by_name(self, queryset, name, value):

        if not value:
            return queryset

        starts_with = Q(name__istartswith=value)
        contains = Q(name__icontains=value)

        result = queryset.filter(contains).annotate(
            priority=Case(
                When(starts_with, then=Value(0)),
                When(contains, then=Value(1)),
                default=Value(2),
                output_field=IntegerField()
            )
        ).order_by('priority', 'name')

        return result


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
            return queryset.filter(favorite_recipe__user=self.request.user)
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shoppingcart_recipe__user=self.request.user)
        return queryset
