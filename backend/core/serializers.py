from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.fields import Base64ImageField
from recipes.models import Recipe
from users.models import Subscriptions

User = get_user_model()


class UserDetailSerializer(serializers.ModelSerializer):
    """Сериализатор получения данных о пользователе."""
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and Subscriptions.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        )


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
