from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from recipes import constants


User = get_user_model()


class Recipe(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        'Название рецепта',
        max_length=constants.MAX_LENGTH_RECIPE_NAME,
        help_text=constants.HELP_TEXT_NAME,
    )
    image = models.ImageField(
        'Картинка рецепта',
        upload_to='images_recipe/',
    )
    text = models.TextField('Описание рецепта')
    ingredients = models.ManyToManyField(
        'Ingredient',
        related_name='recipes',
        verbose_name='Ингредиенты рецепта',
        through='IngredientInRecipe',
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='recipes',
        verbose_name='Теги рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=(MinValueValidator(1, message='Минимум одна!'),),
        help_text=constants.HELP_TEXT_COOKING_TIME,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('created_at',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(
        'Название инргедиента',
        max_length=constants.MAX_LENGTH_INGREDIENT_NAME,
    )
    measurement_unit = models.CharField(
        'Единица измерения ингредиента',
        max_length=constants.UNITS_OF_MEASUREMENT,
        help_text=constants.HELP_TEXT_UNIT,
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingtedient'
            )
        ]

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Tag(models.Model):

    name = models.CharField(
        'Название тега',
        max_length=constants.MAX_LENGTH_TAG,
        unique=True,
        help_text=constants.HELP_TEXT_TAG,
    )
    slug = models.SlugField(
        'Слаг тега',
        max_length=constants.MAX_LENGTH_TAG,
        unique=True,
        help_text=constants.HELP_TEXT_SLUG,
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'slug'],
                name='unique_tag'
            )
        ]

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=(MinValueValidator(1, message='Минимум один!'),),
    )

    class Meta:
        verbose_name = 'ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.amount} {self.ingredient}'


class ShoppingCart(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'Корзина'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'Рецепт - {self.recipe.name}, добавлен в корзину'
    

class Favorite(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorites'
            )
        ]

    def __str__(self):
        return f'Рецепт - {self.recipe.name}, добавлен в избранное'
