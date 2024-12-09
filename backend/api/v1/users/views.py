from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.v1.subscribe.serializers import (
    SubscriberSerializer, SubscriptionsSerializer
)
from api.v1.users.serializers import (
    AvatarSerializer, DjoserUserSerializer
)
from subscribe.models import Subscribe

User = get_user_model()


class DjoserUserViewSet(UserViewSet):

    queryset = User.objects.all()
    serializer_class = DjoserUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

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
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if request.user == author:
                return Response(
                    {'errors': 'Вы не можете подписаться на самого себя!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Subscribe.objects.filter(
                user=request.user, author=author
            ).exists():
                return Response(
                    {'errors': f'Вы уже подписаны на {author}'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            data = {
                'user': request.user.id,
                'author': author.id,
            }
            serializer = SubscriberSerializer(
                data=data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscribe = Subscribe.objects.filter(
            author_id=id, user=request.user
        )
        subscribe.delete()
        return Response('Подписка удалена!', status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscriptions(self, request):
        user = request.user
        quaryset = user.follower.annotate(
            recipes_count=Count('author__recipes')
        )
        serializer = SubscriptionsSerializer(
            self.paginate_queryset(quaryset),
            many=True,
        )
        return self.get_paginated_response(serializer.data)
