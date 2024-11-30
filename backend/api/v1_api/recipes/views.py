from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_GET
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.reverse import reverse

from api.v1_api.permission import AdminOrReadOnly, AuthorOrAdminOrReadOnly
from .filters import RecipeFilter
from .serializers import (
    BriefRecipeSerializer, CreateRecipeSerializer,
    FullRecipeSerializer, IngredientSerializer
)
from favorite.models import Favorite
from recipes.models import Ingredient, IngredientInRecipe, Recipe
from shopping_cart.models import ShoppingCart


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):

    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return FullRecipeSerializer
        return CreateRecipeSerializer

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                user=request.user, recipe__id=pk
            ).exists():
                return Response(
                    {'errors': 'Вы уже добавили этот рецепт!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(
                recipe=Recipe.objects.get(id=pk), user=request.user
            )
            serializer = BriefRecipeSerializer(
                Recipe.objects.get(id=pk)
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            cart = ShoppingCart.objects.filter(
                recipe__id=pk, user=request.user)
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            if Favorite.objects.filter(
                user=request.user, recipe__id=pk
            ).exists():
                return Response(
                    {'errors': 'Вы уже добавили этот рецепт!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(
                recipe=Recipe.objects.get(id=pk), user=request.user
            )
            serializer = BriefRecipeSerializer(
                Recipe.objects.get(id=pk)
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            favorite = Favorite.objects.filter(
                recipe__id=pk, user=request.user)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def create_shopping_cart(ingredients):
        shopping_cart = 'Список покупок:'
        filename = 'shopping_cart.txt'
        for ingredient in ingredients:
            shopping_cart += (
                f'\n{ingredient["ingredient__name"]} - '
                f'{ingredient["amount"]}'
                f'({ingredient["ingredient__measurement_unit"]})'
            )
        response = HttpResponse(
            shopping_cart, content_type='text.txt; charset=utf-8'
        )
        response['Content-Desposition'] = f'attachment; filename={filename}'
        return response

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return self.create_shopping_cart(ingredients)

    @action(
        detail=True,
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        recipe = Recipe.objects.get(pk=pk)
        short_link = reverse('short_url', kwargs={'pk': recipe.pk})
        return Response(
            {"short-link": request.build_absolute_uri(short_link)},
            status=status.HTTP_200_OK
        )


@require_GET
def short_url(request, pk):
    try:
        Recipe.objects.filter(pk=pk).exists()
        return redirect(f'/recipes/{pk}/')
    except Exception as e:
        raise ValidationError(e)
