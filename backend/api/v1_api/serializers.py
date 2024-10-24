import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Favorite, Ingredient, IngredientInRecipe, Recipe, ShoppingCart, Tag, User


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class DjoserUserSerializer(UserSerializer):

    # is_subscribed 

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            # 'is_subscribed',
            'avatar',
        )


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

    author = DjoserUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientInRecipesSerializer(
        source='ingredient_recipes', many=True
    )

    class Meta:
        model = Recipe
        fields = '__all__'


class BriefRecipeSerializer(serializers.ModelSerializer):

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')



class TagSerializer(serializers.ModelSerializer):


    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class AvatarSerializer(serializers.ModelSerializer):

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)
