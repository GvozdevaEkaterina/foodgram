from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from foodgram.constants import (
    MAX_INGREDIENT_NAME,
    MAX_MEASUREMENT_UNIT,
    MAX_RECIPE_NAME,
    MAX_TAG_NAME,
    MAX_TAG_SLUG_NAME,
    MIN_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT
)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_TAG_NAME,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=MAX_TAG_SLUG_NAME,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'slug'],
                name='unique_tag_slug'
            )
        ]

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_INGREDIENT_NAME,
        db_index=True,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MAX_MEASUREMENT_UNIT,
        verbose_name='Единицы измерения'
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_unit'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    name = models.CharField(
        max_length=MAX_RECIPE_NAME,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='dish_picture',
        null=True,
        verbose_name='Изображение'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    cooking_time = models.IntegerField(
        validators=(
            MinValueValidator(
                MIN_COOKING_TIME,
                message=f'Время приготовления не может быть меньше '
                f'{MIN_COOKING_TIME}'
            ),
        ),
        verbose_name='Время приготовления'
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredientrecipe_set'
    )
    amount = models.PositiveIntegerField(
        validators=[
            MinValueValidator(
                MIN_INGREDIENT_AMOUNT,
                message=f'Количество ингридиента не может быть меньше '
                f'{MIN_INGREDIENT_AMOUNT}'
            )
        ],
        default=1
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class FavoriteShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_user'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)s_recipe'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='%(class)s_unique_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user} : {self.recipe}'


class Favorite(FavoriteShoppingCart):
    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'избранное'


class ShoppingCart(FavoriteShoppingCart):
    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'корзины'
