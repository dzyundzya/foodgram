from django.contrib.auth import get_user_model
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
        max_length=constants.MAX_LENGTH_NAME_AND_SLUG,
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
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='recipes',
        verbose_name='Теги рецепта',
    )
    cooking_time = models.DurationField(
        'Время приготовления',
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
        max_length=constants.MAX_LENGTH_NAME_AND_SLUG,
    )
    measurement_unit = models.CharField(
        'Единица измерения ингредиента',
        max_length=constants.UNITS_OF_MEASUREMENT,
        help_text=constants.HELP_TEXT_UNIT,
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):

    name = models.CharField(
        'Название тега',
        max_length=constants.MAX_LENGTH_NAME_AND_SLUG,
        unique=True,
    )
    slug = models.SlugField(
        'Слаг тега',
        max_length=constants.MAX_LENGTH_NAME_AND_SLUG,
        unique=True,
        help_text=constants.HELP_TEXT_SLUG,
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name
