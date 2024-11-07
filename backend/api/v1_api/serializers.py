import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag, User
from users.models import Subscribe


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


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


class IngredientInRecipeSerializer(serializers.ModelSerializer):

    name = serializers.SlugRelatedField(
        'name',
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    measurement_unit = serializers.SlugRelatedField(
        'measurement_unit',
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientInRecipe
        fields = ['id', 'name', 'amount', 'measurement_unit']


class DefaultRecipeSerializer(serializers.ModelSerializer):

    author = DjoserUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientInRecipeSerializer(
        source='recipe_ingredients',
        many=True
    )

    class Meta:
        model = Recipe
        fields = [
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
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


class CreateRecipesSerializer(DefaultRecipeSerializer):

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )

    MANY_FIELDS = {'recipe_ingredients': 'update_ingredients'}

    @classmethod
    def update_ingredients(cls, instance, new_ingredients):
        old_ingredients_dict = {ri.ingredient_id: ri for ri in instance.recipe_ingredients.all()}
        new_ingredients_dict = {ri['ingredient'].id: ri for ri in new_ingredients if ri['ingredient'].id not in old_ingredients_dict}
        updated_ingredients_dict = {ri['ingredient'].id: ri for ri in new_ingredients if ri['ingredient'].id in old_ingredients_dict}
        old_ingredients_set = set(old_ingredients_dict.keys()) - set(new_ingredients_dict.keys())
        updated_ingredients_dict = dict(filter(
            lambda kv: kv[1]['amount'] != old_ingredients_dict[kv[0]].amount
            and (kv[1]['amount'] is not None or old_ingredients_dict[kv[0]].amount is not None),
            updated_ingredients_dict.items()
        ))
        IngredientInRecipe.objects.filter(recipe_id=instance.id, ingredient_id__in=old_ingredients_set).delete()
        IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(recipe_id=instance.id, **ri) for ri in new_ingredients_dict.values()
        ])
        IngredientInRecipe.objects.bulk_update([
            IngredientInRecipe(id=old_ingredients_dict[ri['ingredient'].id].id, **ri) for ri in updated_ingredients_dict.values()
        ], fields=['amount'])

    def update_many2us(self, instance, validated_data):
        for field, updater_name in self.MANY_FIELDS.items():
            data = validated_data.pop(field, None)
            updater = getattr(self, updater_name)
            if data is None or not self.partial:
                updater(instance, data or [])
        return instance

    def split_validated_data(self, validated_data):
        return {
            key: value for key, value in validated_data.items()
            if key not in self.MANY_FIELDS
        }, {
            key: validated_data[key] for key in self.MANY_FIELDS
        }

    def create(self, validated_data):
        basic, many2us = self.split_validated_data(validated_data)
        return self.update_many2us(super().create(basic), many2us)

    def update(self, instance, validated_data):
        basic, many2us = self.split_validated_data(validated_data)
        return self.update_many2us(super().update(instance, basic), many2us)


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
