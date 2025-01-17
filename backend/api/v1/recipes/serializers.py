from rest_framework import serializers

from api.v1.fields import Base64ImageField
from api.v1.tags.serializers import TagSerializer
from api.v1.users.serializers import DjoserUserSerializer
from favorite.models import Favorite
from recipes.models import Ingredient, IngredientInRecipe, Recipe
from shopping_cart.models import ShoppingCart
from tags.models import Tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class BriefRecipeSerializer(serializers.ModelSerializer):

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class CreateIngredientInRecipeSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientInRecipe
        fields = ['id', 'amount']


class IngredientInRecipeSerializer(CreateIngredientInRecipeSerializer):

    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta(CreateIngredientInRecipeSerializer.Meta):
        fields = CreateIngredientInRecipeSerializer.Meta.fields + [
            'name',
            'measurement_unit'
        ]


class DefaultRecipeSerializer(BriefRecipeSerializer):

    author = DjoserUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='recipe_ingredients',
        many=True
    )

    class Meta(BriefRecipeSerializer.Meta):
        fields = BriefRecipeSerializer.Meta.fields + [
            'author',
            'text',
            'ingredients',
            'tags',
        ]


class FullRecipeSerializer(DefaultRecipeSerializer):

    tags = TagSerializer(read_only=True, many=True)
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta(DefaultRecipeSerializer.Meta):
        fields = DefaultRecipeSerializer.Meta.fields + [
            'is_in_shopping_cart',
            'is_favorited'
        ]

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.shopping_cart.filter(user=request.user).exists()
        return False

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorites.filter(user=request.user).exists()
        return False


class CreateRecipeSerializer(DefaultRecipeSerializer):

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = CreateIngredientInRecipeSerializer(
        write_only=True, many=True
    )

    @staticmethod
    def create_ingredient_in_recipe(instance, ingredients):
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        user = self.context.get('request').user
        instance = Recipe.objects.create(**validated_data, author=user)
        instance.tags.set(tags)
        self.create_ingredient_in_recipe(instance, ingredients)
        return instance

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        instance.tags.set(tags)
        self.create_ingredient_in_recipe(instance, ingredients)
        return super().update(instance, validated_data)


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        if user.shopping_cart.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Вы уже добавили рецепт в корзину!'
            )
        return data

    def to_representation(self, instance):
        return BriefRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(ShoppingCartSerializer):

    class Meta(ShoppingCartSerializer.Meta):
        model = Favorite

    def validate(self, data):
        user = data['user']
        if user.favorites.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Вы уже добавили рецепт в избранное!'
            )
        return data
