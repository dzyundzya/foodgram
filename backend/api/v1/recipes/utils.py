from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe


def post_favorite_shopping_cart(request, pk, serializers):
    recipe = get_object_or_404(Recipe, pk=pk)
    data = {
        'user': request.user.id,
        'recipe': recipe.id,
    }
    serializer = serializers(data=data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_favorite_shopping_cart(request, pk, models):
    favorite_shopping_cart = models.objects.filter(
        recipe_id=pk, user_id=request.user.id
    )
    if favorite_shopping_cart:
        favorite_shopping_cart.delete()
        return Response(
            'Рецепт удален!', status=status.HTTP_204_NO_CONTENT
        )
    return Response(
        {'errors': 'Данного рецепта нет в избранном/корзине!'},
        status=status.HTTP_400_BAD_REQUEST
    )


def create_shopping_cart(ingredients):
    shopping_cart = 'Список покупок:'
    for ingredient in ingredients:
        shopping_cart += (
            f'\n{ingredient["ingredient__name"]} - '
            f'{ingredient["amount"]}'
            f'({ingredient["ingredient__measurement_unit"]})'
        )
    return shopping_cart
