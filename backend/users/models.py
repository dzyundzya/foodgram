from django.contrib.auth.models import AbstractUser
from django.db import models

from users import constants


class User(AbstractUser):

    username = models.CharField(
        'Никнейм',
        max_length=constants.MAX_LENGTH_NAME,
        unique=True,
        help_text=constants.HELP_TEXT_NAME,
    )
    email = models.EmailField(
        'email',
        max_length=constants.MAX_LENGTH_EMAIL,
        unique=True,
        help_text=constants.HELP_TEXT_EMAIL,
    )
    first_name = models.CharField(
        'Имя',
        max_length=constants.MAX_LENGTH_NAME,
        help_text=constants.HELP_TEXT_NAME,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=constants.MAX_LENGTH_NAME,
        help_text=constants.HELP_TEXT_NAME,
    )
    avatar = models.ImageField(
        'Аватар пользователя',
        upload_to='images_avatar/',
        blank=True,
        null=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name'
    ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username
