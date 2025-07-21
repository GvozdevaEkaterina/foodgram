from rest_framework import serializers

from foodgram.constants import MIN_INGREDIENT_AMOUNT
from users.fields import Base64ImageField
from users.serializers import UserDetailSerializer
from .fields import IngredientField, TagField
from .models import Ingredient, IngredientRecipe, Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для тегов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериалайзер для рецептов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для рецептов (сокращённая версия)."""
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для рецептов (полная версия).
    Вычисляет поля is_favorited и is_in_shopping_cart.
    Проводит валидацию данных полей ingredients и tags.
    """

    author = UserDetailSerializer(read_only=True)

    ingredients = IngredientField(
        source='ingredientrecipe_set',
        many=True,
        required=True
    )

    tags = TagField(
        queryset=Tag.objects.all(),
        many=True,
        required=True
    )
    image = Base64ImageField(
        required=True,
        allow_null=False
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        ingredients = validated_data.pop('ingredientrecipe_set', [])
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        ingredient_recipe = [
            IngredientRecipe(
                recipe=recipe,
                ingredient_id=ingredient['ingredient_id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        IngredientRecipe.objects.bulk_create(ingredient_recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredientrecipe_set', [])
        tags = validated_data.pop('tags', [])

        if tags:
            instance.tags.set(tags)

        if ingredients:
            instance.ingredientrecipe_set.all().delete()
            for ingredient in ingredients:
                IngredientRecipe.objects.create(
                    recipe=instance,
                    ingredient_id=ingredient['ingredient_id'],
                    amount=ingredient['amount']
                )
        return super().update(instance, validated_data)

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError('Это поле не может быть пустым')

        ingredient_ids = [
            ingredient.get('ingredient_id') for ingredient in value
        ]
        if len(set(ingredient_ids)) < len(ingredient_ids):
            raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться'
                )
        for ingredient in value:
            if not Ingredient.objects.filter(
                id=ingredient['ingredient_id']
            ).exists():
                raise serializers.ValidationError(
                    'Нельзя добавить несуществующий ингредиент'
                )
            try:
                amount = int(ingredient['amount'])
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    'Количество должно быть целым числом'
                )

            if amount < MIN_INGREDIENT_AMOUNT:
                raise serializers.ValidationError(
                    f'Нельзя добавить ингредиент в количестве меньше '
                    f'{MIN_INGREDIENT_AMOUNT}'
                )
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError('Это поле не может быть пустым')

        tag_ids = [tag.id for tag in value]
        if len(set(tag_ids)) < len(tag_ids):
            raise serializers.ValidationError('Теги не должны повторяться')
        return value

    def validate(self, data):
        print(data)
        if self.context['request'].method in ['PATCH']:
            if 'tags' not in data:
                raise serializers.ValidationError(
                    {'tags': 'Это поле обязательно при обновлении'},
                )
            if 'ingredientrecipe_set' not in data:
                raise serializers.ValidationError(
                    {'ingredients': 'Это поле обязательно при обновлении'},
                )
        return data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_favorited.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_in_shopping_cart.filter(user=request.user).exists()
        return False
