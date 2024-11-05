import base64

from django.db.models import F
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers, validators

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag, User
from users.models import Subscribe


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class DjoserUserSerializer(UserSerializer):

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscribe.objects.filter(
                user=request.user, author=obj).exists()
        return False


class IngredientInRecipesSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class FullRecipeSerializer(serializers.ModelSerializer):

    author = DjoserUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(read_only=True, many=True)
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
            'is_in_shopping_cart',
            'is_favorited',
        )

    def get_ingredients(self, obj):
        recipe = obj
        return recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredientinrecipe__amount')
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=request.user).exists()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user).exists()


class CreateRecipesSerializer(serializers.ModelSerializer):

    image = Base64ImageField()
    ingredients = IngredientInRecipesSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
        )

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ingredients_list = []
        for ingredient_data in ingredients:
            ingredients_list.append(
                IngredientInRecipe(
                    ingredient=Ingredient.objects.get(
                        id=ingredient_data['id']
                    ),
                    amount=ingredient_data['amount'],
                    recipe=recipe
                )
            )
        try:
            IngredientInRecipe.objects.bulk_create(ingredients_list)
        except Exception as e:
            raise validators.ValidationError(
                f'Ошибка при создании ингредиентов: {e}'
            )

    def create(self, validated_data):
        request = self.context.get('request', None)
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        try:
            recipe = Recipe.objects.create(
                author=request.user, **validated_data)
            recipe.tags.set(tags)
            self.create_ingredients(recipe, ingredients)
        except Exception as e:
            raise validators.ValidationError(
                f'Ошибка при создании рецепта: {e}'
            )
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        try:
            IngredientInRecipe.objects.filter(recipe=instance).delete()
        except Exception as e:
            raise validators.ValidationError(
                f'Ошибка при удалении ингредиентов: {e}'
            )
        instance.tags.set(validated_data.pop('tags'))
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            self.create_ingredients(instance, ingredients)
        else:
            raise KeyError('ingredients key is missing')
        return super().update(instance, validated_data)


class BriefRecipeSerializer(serializers.ModelSerializer):

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class AvatarSerializer(serializers.ModelSerializer):

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class SubscriberSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
        fields = ('id', 'author', 'user')


class SubscriptionsSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = Base64ImageField(source='author.avatar')

    class Meta:
        model = Subscribe
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        return Subscribe.objects.filter(
            user=obj.user, author=obj.author).exists()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)
        return BriefRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
