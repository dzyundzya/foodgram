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
    title = models.CharField(
        'Название рецепта',
        max_length=constants.MAX_LENGTH_TITLE_AND_SLUG,
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


class Ingredient(models.Model):
    
    title = models.CharField(
        'Название инргедиента',
        max_length=constants.MAX_LENGTH_TITLE_AND_SLUG,
    )
    units_of_measurement = models.CharField(
        'Единицы измерения',
        max_length=constants.UNITS_OF_MEASUREMENT,
    )


class Tag(models.Model):

    title = models.CharField(
        'Название тега',
        max_length=constants.MAX_LENGTH_TITLE_AND_SLUG,
    )
    slug = models.SlugField(max_length=constants.MAX_LENGTH_TITLE_AND_SLUG)
