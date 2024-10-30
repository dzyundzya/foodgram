from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .permission import AdminOrReadOnly, AuthorOrAdminOrReadOnly
from .serializers import  BriefRecipeSerializer, CreateRecipesSerializer, FullRecipeSerializer, IngredientSerializer, TagSerializer
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag, User


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):

    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action == 'list' or 'retrieve':
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


class TagViewSet(viewsets.ModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None
