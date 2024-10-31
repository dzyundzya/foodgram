import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Favorite, Ingredient, IngredientInRecipe, Recipe, ShoppingCart, Tag, User
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

    name = serializers.SlugRelatedField(
        'name', source='ingredient', queryset=Ingredient.objects.all()
    )
    measurement_unit = serializers.SlugRelatedField(
        'measurement_unit',
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

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
    ingredients = IngredientInRecipesSerializer(
        source='ingredient_recipes', many=True
    )
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
        )

    def create(self, validate_data):
        ingredients = validate_data.pop('ingredients')
        tags = validate_data.pop('tags')
        recipe = Recipe.objects.create(**validate_data)
        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' != validated_data:
            raise serializers.ValidationError('Добавьте ингредиент')
        if 'tags' != validated_data:
            raise serializers.ValidationError('Добавьте тег')
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        instance = super().update(instance, validated_data)
        if ingredients is not None:
            instance.ingredients.clear()
            for ingredient in ingredients:
                IngredientInRecipe.objects.create(
                    recipe=instance,
                    ingredient=ingredient['id'],
                    amount=ingredient['amount'],
                )
        if tags is not None:
            instance.tags.set(tags)
        instance.save()
        return instance


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
        return Recipe.objects.filter(author=obj.author).count()
