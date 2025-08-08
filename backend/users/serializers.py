from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as DjoserUserCS
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from foodgram.constants import MAX_NAME_LENGTH
from core.fields import Base64ImageField
from core.serializers import ShortRecipeSerializer
from recipes.pagination import RecipesLimitPagination
from .models import Subscriptions

User = get_user_model()


class UserDetailSerializer(serializers.ModelSerializer):
    """Сериализатор получения данных о пользователе."""
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


class UserCreateSerializer(DjoserUserCS):
    """Сериализатор создания пользователя."""
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(
        required=True,
        max_length=MAX_NAME_LENGTH
    )
    last_name = serializers.CharField(
        required=True,
        max_length=MAX_NAME_LENGTH
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError('Username "me" недоступен')
        return value


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с аватарками."""
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def validate(self, data):
        if 'avatar' not in data:
            raise serializers.ValidationError(
                {'avatar': 'Это поле обязательно при обновлении'},
            )
        return data


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки"""
    class Meta:
        model = Subscriptions
        fields = (
            'user',
            'author'
        )

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError('Нельзя подписаться на себя')
        if Subscriptions.objects.filter(
            user=data['user'],
            author=data['author']
        ).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя'
            )
        return data

    def to_representation(self, value):
        return SubscriptionsSerializer(
            value.author,
            context=self.context
        ).data


class SubscriptionsSerializer(UserDetailSerializer):
    """Сериализатор для работы с подписками."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        )

    def get_recipes(self, obj):
        """Получение рецептов пользователя."""
        request = self.context.get('request')
        recipes = obj.recipes.all().order_by('-id')
        paginator = RecipesLimitPagination()
        paginated_recipes = paginator.paginate_queryset(
            recipes,
            request
        )
        return ShortRecipeSerializer(
            paginated_recipes,
            many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        """Получение количества рецептов пользователя."""
        return obj.recipes.count()

