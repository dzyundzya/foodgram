from rest_framework import  viewsets

from .permission import AdminOrReadOnly, AuthorOrAdminOrReadOnly
from .serializers import  BriefRecipeSerializer, FullRecipeSerializer, IngredientSerializer, TagSerializer
from recipes.models import Ingredient, Recipe, Tag, User


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):

    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action == 'list':
            return BriefRecipeSerializer
        return FullRecipeSerializer


class TagViewSet(viewsets.ModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)

