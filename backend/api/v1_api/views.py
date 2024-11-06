from django.db.models import Sum
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
    filterset_fields = ('tag',)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return FullRecipeSerializer
        return CreateRecipesSerializer

    def perform_create(self, serializer):
        self.object = serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        self.object = serializer.save()

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response(FullRecipeSerializer(instance=self.object).data)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response(FullRecipeSerializer(instance=self.object).data)        

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
                f'\n{ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]}) - '
                f'{ingredient["amount"]}'
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
        recipe_id = self.kwargs[self.lookup_field]
        frontend_url = 'https://fg'
        url_to_recipes = 'recipessss'
        short_link = f'{frontend_url}/{url_to_recipes}/{recipe_id}/'
        return Response({"short-link": short_link})


class TagViewSet(viewsets.ModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None
