from django.db.models import F, Sum
from django.http.response import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .permission import AdminOrReadOnly, AuthorOrAdminOrReadOnly
from .serializers import (
    BriefRecipeSerializer, CreateRecipesSerializer,
    FullRecipeSerializer, IngredientInRecipe,
    IngredientSerializer, TagSerializer,
)
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


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
    filterset_fields = ('author',)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'get-link'):
            return FullRecipeSerializer
        return CreateRecipesSerializer

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
    def create_shopping_cart(user):
        shopping_cart = [
            'Список покупок:'
        ]
        ingredients = (
            IngredientInRecipe.objects.filter(
                recipe__recipe__shopping_cart__user=user
            ).values('name', unit=F('measurement_unit')
                     ).annotate(amount=Sum('recipe__amount'))
        )
        ingredients_list = [
            f'{ingr["name"]}: {ingr["amount"]} {ingr["unit"]}'
            for ingr in ingredients
        ]
        shopping_cart.extend(ingredients_list)
        return "\n".join(shopping_cart)

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        filename = f'{user.username}_shopping_cart.txt'
        shopping_cart = self.create_shopping_cart(user)
        response = HttpResponse(
            shopping_cart, content_type='text.txt; charset=utf-8'
        )
        response['Content-Desposition'] = f'attachment; filename={filename}'
        return response


class TagViewSet(viewsets.ModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None
