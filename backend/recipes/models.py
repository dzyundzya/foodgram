from django.contrib.auth import get_user_model
from django.db import models

from recipes import constants


User = get_user_model()


class Recipe(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        'Название рецепта',
        max_length=constants.MAX_LENGTH_NAME_AND_SLUG,
    )
    image = models.ImageField(
        'Картинка рецепта',
        upload_to='images_recipe/',
    )
    text = models.TextField('Описание рецепта')
    ingredients = models.ManyToManyField(
        'Ingredient',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='recipes',
    )
    cooking_time = models.DurationField('Время приготовления')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(
        'Название инргедиента',
        max_length=constants.MAX_LENGTH_NAME_AND_SLUG,
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=constants.UNITS_OF_MEASUREMENT,
    )

    class Meta:
        verbose_name = 'Ингредиент'
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
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name
