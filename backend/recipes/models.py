from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from foodgram.constants import (
    MAX_TAG_NAME,
    MAX_TAG_SLUG_NAME,
    MAX_INGREDIENT_NAME,
    MAX_MEASUREMENT_UNIT,
    MAX_RECIPE_NAME,
    MIN_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT
)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_TAG_NAME,
        unique=True,
        blank=False,
        null=False
    )
    slug = models.SlugField(
        max_length=MAX_TAG_SLUG_NAME,
        unique=True,
        blank=False,
        null=False
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_INGREDIENT_NAME,
        db_index=True,
        blank=False,
        null=False
    )
    measurement_unit = models.CharField(
        max_length=MAX_MEASUREMENT_UNIT,
        blank=False,
        null=False
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        related_name='recipes',
        default=False
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes'
    )
    is_favorited = models.BooleanField(
        default=False
    )
    is_in_shopping_cart = models.BooleanField(
        default=False
    )
    name = models.CharField(
        max_length=MAX_RECIPE_NAME,
        blank=False,
        null=False
    )
    image = models.ImageField(
        'Фото готового блюда',
        upload_to='dish_picture',
        null=True,
        default=None
    )
    text = models.TextField()
    cooking_time = models.IntegerField(
        validators=(MinValueValidator(MIN_COOKING_TIME), )
    )


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
