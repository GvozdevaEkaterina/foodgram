from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from foodgram.constants import MAX_NAME_LENGTH
from recipes.pagination import RecipesLimitPagination
from users.fields import Base64ImageField
from .models import Subscriptions

User = get_user_model()


def get_short_recipe_serializer():
    """Импорт ShortRecipeSerializer, чтобы избежать цикличного импорта."""
    from recipes.serializers import ShortRecipeSerializer
    return ShortRecipeSerializer


class CustomUserCreateSerializer(UserCreateSerializer):
    """Кастомный сериалайзер создания пользователя."""
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

class BaseAvatarSerializer(serializers.ModelSerializer):
    """Базовый сериалайзер для работы с аватарками."""
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        abstract = True

    def update(self, instance, validated_data):
        avatar = validated_data.pop('avatar', None)
        if avatar:
            if instance.avatar:
                instance.avatar.delete()
            instance.avatar = avatar
        instance.save()
        return instance


class UserDetailSerializer(BaseAvatarSerializer):
    """Кастомный сериалайзер получения данных о пользователе."""
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
        if request and request.user.is_authenticated:
            return Subscriptions.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        return False


class AvatarSerializer(BaseAvatarSerializer):
    """Сериалайзер для работы с аватарками."""
    class Meta:
        model = User
        fields = (
            'avatar',
        )


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериалайзер для работы с подписками."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

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

        serializer = get_short_recipe_serializer()
        paginator = RecipesLimitPagination()
        paginated_recipes = paginator.paginate_queryset(
            recipes,
            request
        )

        if request and request.user.is_authenticated:
            return serializer(
                paginated_recipes,
                many=True,
                context={'request': request}
            ).data
        return []

    def get_recipes_count(self, obj):
        """Получение количества рецептов пользователя."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.recipes.count()
        return 0

    def get_is_subscribed(self, obj):
        """Проверка, подписан ли автор запроса на данного пользователя."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscriptions.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        return False
