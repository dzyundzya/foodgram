from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1_api.permission import AuthorOrAdminOrReadOnly
from api.v1_api.subscribe.serializers import (
    SubscriberSerializer, SubscriptionsSerializer
)
from api.v1_api.users.serializers import (
    AvatarSerializer, DjoserUserSerializer
)
from subscribe.models import Subscribe

User = get_user_model()


class DjoserUserViewSet(UserViewSet):

    queryset = User.objects.all()
    serializer_class = DjoserUserSerializer
    permission_classes = (AuthorOrAdminOrReadOnly,)

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        serializer = DjoserUserSerializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['PUT', 'DELETE'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        url_path='me/avatar',
    )
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = AvatarSerializer(request.user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            user = self.request.user
            user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, id):
        if request.method == 'POST':
            queryset = Subscribe.objects.create(
                author=User.objects.get(id=id),
                user=request.user
            )
            serializer = SubscriberSerializer(
                queryset,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscibe = Subscribe.objects.get(
                author=User.objects.get(id=id),
                user=request.user
            )
            subscibe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscriptions(self, request):
        user = request.user
        quaryset = user.follower.all()
        serializer = SubscriptionsSerializer(
            self.paginate_queryset(quaryset),
            many=True,
        )
        return self.get_paginated_response(serializer.data)
