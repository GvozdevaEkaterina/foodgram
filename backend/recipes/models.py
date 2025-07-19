from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from foodgram.constants import (MAX_INGREDIENT_NAME, MAX_MEASUREMENT_UNIT,
                                MAX_RECIPE_NAME, MAX_TAG_NAME,
                                MAX_TAG_SLUG_NAME, MIN_COOKING_TIME,
                                MIN_INGREDIENT_AMOUNT)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_TAG_NAME,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=MAX_TAG_SLUG_NAME,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_INGREDIENT_NAME,
        db_index=True,
        blank=False,
        null=False,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MAX_MEASUREMENT_UNIT,
        blank=False,
        null=False,
        verbose_name='Единицы измерения'
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        related_name='recipes',
        default=False,
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
        blank=False,
        null=False,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='dish_picture',
        null=True,
        default=None,
        verbose_name='Изображение'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    cooking_time = models.IntegerField(
        validators=(MinValueValidator(MIN_COOKING_TIME), ),
        verbose_name='Время приготовления'
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

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
        validators=[MinValueValidator(MIN_INGREDIENT_AMOUNT)],
        default=1
    )

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='is_favorited'
    )

    class Meta:
        unique_together = ('user', 'recipe', )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='is_in_shopping_cart'
    )

    class Meta:
        unique_together = ('user', 'recipe', )
