from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Subscribe(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )

    class Meta:
        verbose_name = 'подписку'
        verbose_name_plural = 'Подписки'
        db_table = 'Subscribe'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_user_following'
            ),
        ]

    def __str__(self) -> str:
        return f'{self.user}, подписался на {self.author}'
