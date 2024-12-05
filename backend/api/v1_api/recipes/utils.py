from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe


def post_favorite_shopping_cart(request, pk, models, serializers):
    recipe = get_object_or_404(Recipe, pk=pk)
    if models.objects.filter(recipe=recipe, user=request.user).exists():
        return Response(
            {'errors': f'Вы уже добавили {recipe.name}!'},
            status=status.HTTP_400_BAD_REQUEST
        )
    models.objects.get_or_create(recipe=recipe, user=request.user)
    data = serializers(recipe).data
    return Response(data, status=status.HTTP_201_CREATED)


def delete_favorite_shopping_cart(request, pk, models):
    recipe = get_object_or_404(Recipe, pk=pk)
    if models.objects.filter(recipe=recipe, user=request.user).exists():
        favorite_shopping_cart = get_object_or_404(
            models, recipe=recipe, user=request.user)
        favorite_shopping_cart.delete()
        return Response(f'{recipe.name} - удален!')
    return Response(
        {'errors': f'{recipe.name} - нет в избранном/корзине!'},
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
