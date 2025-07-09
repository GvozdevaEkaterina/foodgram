import base64
from django.core.files.base import ContentFile
from rest_framework import serializers

from .models import Ingredient, IngredientRecipe, Tag, Recipe
from users.serializers import UserDetailSerializer


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)
    

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientField(serializers.RelatedField):

    def get_queryset(self):
        return Ingredient.objects.all()
    
    def to_representation(self, value):
        return {
            'id': value.ingredient.id,
            'name': value.ingredient.name,
            'measurement_unit': value.ingredient.measurement_unit,
            'amount': value.amount
        }

    def to_internal_value(self, data):
        try:
            return {
                'ingredient_id': data['id'],
                'amount': data['amount']
            }
        except Ingredient.DoesNotExist:
            raise serializers.ValidationError('Ингредиент не найден')
        except KeyError:
            raise serializers.ValidationError("Необходимы 'id' и 'amount' ингредиента")


class TagField(serializers.RelatedField):

    def to_representation(self, value):
        return {
            'id': value.id,
            'name': value.name,
            'slug': value.slug
        }
    
    def to_internal_value(self, data):
        try:
            return Tag.objects.get(id=data)
        except Tag.DoesNotExist:
            raise serializers.ValidationError(f'Тег с ID {data} не существует')


class RecipeSerializer(serializers.ModelSerializer):

    author = UserDetailSerializer()

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
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_favorited.filter(user=request.user).exists()
        return False


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
