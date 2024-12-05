from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_GET
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .filters import RecipeFilter
from .serializers import (
    BriefRecipeSerializer, CreateRecipeSerializer,
    FullRecipeSerializer, IngredientSerializer
)
from utils import (
    delete_favorite_shopping_cart,
    post_favorite_shopping_cart,
    create_shopping_cart
)
from api.v1_api.permission import AdminOrReadOnly, AuthorOrAdminOrReadOnly
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

    queryset = Recipe.objects.all().select_related(
        'author'
    ).prefetch_related(
        'tags', 'ingredients'
    )
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
            return post_favorite_shopping_cart(
                request, pk, ShoppingCart, BriefRecipeSerializer
            )
        return delete_favorite_shopping_cart(request, pk, ShoppingCart)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return post_favorite_shopping_cart(
                request, pk, Favorite, BriefRecipeSerializer
            )
        return delete_favorite_shopping_cart(request, pk, Favorite)

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
        shopping_cart = create_shopping_cart(ingredients)
        filename = 'shopping_cart.txt'
        response = HttpResponse(
            shopping_cart, content_type='text.txt; charset=utf-8'
        )
        response['Content-Desposition'] = f'attachment; filename={filename}'
        return response

    @action(
        detail=True,
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        short_link = reverse('short_url', kwargs={'pk': recipe.pk})
        return Response(
            {'short-link': request.build_absolute_uri(short_link)},
            status=status.HTTP_200_OK
        )


@require_GET
def short_url(request, pk):
    return redirect(f'/recipes/{pk}/')
