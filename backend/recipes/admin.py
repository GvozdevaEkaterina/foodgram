from django.contrib import admin

from .models import Ingredient, IngredientRecipe, Recipe, Tag

admin.site.empty_value_display = 'Не задано'


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
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
        'ingredients',
    )

    inlines = (
        IngredientRecipeInline,
    )

    def get_favorites_count(self, obj):
        return obj.favorite_set.count()
    get_favorites_count.short_description = 'В избранном'


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


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
