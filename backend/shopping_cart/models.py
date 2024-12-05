from django.db import models

from common.models import CommonFavoriteShoppingCart


class ShoppingCart(CommonFavoriteShoppingCart):

    class Meta:
        default_related_name = 'shopping_cart'
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
