from django.db import models

from common.models import CommonFavoriteShoppingCart


class Favorite(CommonFavoriteShoppingCart):

    class Meta:
        default_related_name = 'favorites'
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
