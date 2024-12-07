from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

from api.v1.fields import Base64ImageField
from subscribe.models import Subscribe

User = get_user_model()


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
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscribe.objects.filter(
                user=request.user, author=obj).exists()
        return False


class AvatarSerializer(serializers.ModelSerializer):

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)
