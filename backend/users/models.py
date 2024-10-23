from django.contrib.auth.models import AbstractUser
from django.db import models

from users import constants


class User(AbstractUser):

    username = models.CharField(
        'Имя пользователя',
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
    password = models.CharField(
        'Пароль',
        max_length=constants.MAX_LENGTH_PASSWORD,
        help_text=constants.HELP_TEXT_PASSWORD,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscribe(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = [ 
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_user_following'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.Q('fallowing')),
                name='cant_subscribe_to_yourself'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user.username}, подписался на {self.author.username}'
