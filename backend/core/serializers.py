from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import Recipe

User = get_user_model()


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов (сокращённая версия)."""
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
