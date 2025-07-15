import base64

from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework.validators import UniqueValidator
from rest_framework import serializers

from .models import Subscriptions
from foodgram.constants import MAX_NAME_LENGTH
from foodgram.serializers import ShortRecipeSerializer, UserDetailSerializer


User = get_user_model()

# class Base64ImageField(serializers.ImageField):

#     def to_internal_value(self, data):
#         if isinstance(data, str) and data.startswith('data:image'):
#             format, imgstr = data.split(';base64,')
#             ext = format.split('/')[-1]
#             data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

#         return super().to_internal_value(data)


class UserCreateSerializer(UserCreateSerializer):

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

# class UserDetailSerializer(serializers.ModelSerializer):

#     avatar = Base64ImageField(required=False, allow_null=True)

#     class Meta:
#         model = User
#         fields = (
#             'id',
#             'email',
#             'username',
#             'first_name',
#             'last_name',
#             'is_subscribed',
#             'avatar'
#         )

#     def update(self, instance, validated_data):
#         avatar = validated_data.pop('avatar', None)
#         if avatar:
#             if instance.avatar:
#                 instance.avatar.delete()
#             instance.avatar = avatar
#         instance.save()
#         return instance


class SubscribeSerializer(serializers.ModelSerializer):
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
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            recipes = obj.recipes.all()
            return ShortRecipeSerializer(
                recipes,
                many=True,
                context={'request': request}
            ).data
        return []

    def get_recipes_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.recipes.count()
        return 0

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscriptions.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        return False
