from django_filters import rest_framework as filters
from .models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='Tags'
    )
    is_favorited = filters.BooleanFilter(
        method='filter_favorited',
        label='Is_Favorited'
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'tags', )

    def filter_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(is_favorited__user=self.request.user)
        return queryset

