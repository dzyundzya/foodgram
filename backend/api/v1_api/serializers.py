from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag, User


class IngredientInRecipesSerializer(serializers.ModelSerializer):

    name = serializers.SlugRelatedField(
        'name', source='ingredient', queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('name', 'amount')

class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class FullRecipeSerializer(serializers.ModelSerializer):

    ingredients = IngredientInRecipesSerializer(
        source='ingredient_recipes', many=True
    )

    class Meta:
        model = Recipe
        fields = '__all__'


class BriefRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'tags')



class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class CustomUserSerializer(UserSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
        )
