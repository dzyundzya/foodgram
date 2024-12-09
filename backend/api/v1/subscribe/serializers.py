from rest_framework import serializers

from api.v1.recipes.serializers import BriefRecipeSerializer
from api.v1.fields import Base64ImageField
from recipes.models import Recipe
from subscribe.models import Subscribe


class SubscriptionsSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)
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


class SubscriberSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
        fields = ('author', 'user')

    def to_representation(self, instance):
        return SubscriptionsSerializer(instance, context=self.context).data
