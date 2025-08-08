from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag
)

admin.site.empty_value_display = 'Не задано'


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1
    min_num = 1
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'get_favorites_count',
    )
    search_fields = (
        'author__username',
        'name',
    )
    list_filter = (
        'tags',
    )
    list_display_links = (
        'name',
    )
    readonly_fields = (
        'get_favorites_count',
    )
    filter_horizontal = (
        'tags',
    )

    inlines = (
        IngredientRecipeInline,
    )

    @admin.display(description='В избранном')
    def get_favorites_count(self, obj):
        return obj.favorite_recipe.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = (
        'name',
    )


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug'
    )


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
