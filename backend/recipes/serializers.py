from rest_framework import serializers

from foodgram.constants import MIN_INGREDIENT_AMOUNT
from core.fields import Base64ImageField
from core.serializers import ShortRecipeSerializer
from users.serializers import UserDetailSerializer
from .models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag
)


class CreateTagSerializer(serializers.ModelSerializer):
    """Сериализатор для создания тегов."""
    id = serializers.IntegerField()

    class Meta:
        model = Tag
        fields = ('id')


class DisplayTagSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения тегов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class CreateIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ингредиентов."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=MIN_INGREDIENT_AMOUNT)

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class DisplayIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов в рецептах."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания рецептов.
    Проводит валидацию данных полей ingredients и tags.
    """
    image = Base64ImageField(
        required=True,
        allow_null=False
    )
    ingredients = CreateIngredientsSerializer(
        many=True,
        required=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def to_representation(self, instance):
        return DisplayRecipeSerializer(instance, context=self.context).data

    def create_recipe_ingredients(self, recipe, ingredients):
        return [
            IngredientRecipe(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        ingredient_recipe = self.create_recipe_ingredients(recipe, ingredients)
        IngredientRecipe.objects.bulk_create(ingredient_recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        instance.tags.set(tags)
        instance.ingredientrecipe_set.all().delete()
        IngredientRecipe.objects.bulk_create(
            self.create_recipe_ingredients(instance, ingredients)
        )
        return super().update(instance, validated_data)

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError('Это поле не может быть пустым')
        ingredient_ids = [
            ingredient.get('id') for ingredient in value
        ]
        if len(set(ingredient_ids)) < len(ingredient_ids):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться'
            )
        for ingredient in value:
            if not Ingredient.objects.filter(
                id=ingredient['id']
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
        if 'tags' not in data:
            raise serializers.ValidationError(
                {'tags': 'Это поле является обязательным'},
            )
        if 'ingredients' not in data:
            raise serializers.ValidationError(
                {'ingredients': 'Это поле является обязательным'},
            )
        return data


class DisplayRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения рецептов (полная версия).
    Вычисляет поля is_favorited и is_in_shopping_cart.
    """

    author = UserDetailSerializer(read_only=True)
    ingredients = IngredientsRecipeSerializer(
        many=True,
        source='ingredientrecipe_set'
    )
    tags = DisplayTagSerializer(
        many=True,
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

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and obj.favorite_recipe.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and obj.shoppingcart_recipe.filter(user=request.user).exists()
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранного."""
    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe'
        )

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, data):
        if Favorite.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                 'Рецепт уже находится в избранном'
            )
        return data

    def to_representation(self, value):
        return ShortRecipeSerializer(
            value.recipe,
            context=self.context
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор корзины."""
    class Meta:
        model = ShoppingCart
        fields = (
            'user',
            'recipe'
        )

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, data):
        if ShoppingCart.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                 'Рецепт уже находится в корзине'
            )
        return data

    def to_representation(self, value):
        return ShortRecipeSerializer(
            value.recipe,
            context=self.context
        ).data
