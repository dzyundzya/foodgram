from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1_api.serializers import AvatarSerializer, DjoserUserSerializer
from api.v1_api.permission import AuthorOrAdminOrReadOnly


User = get_user_model()

class DjoserUserViewSet(UserViewSet):

    queryset = User.objects.all()
    serializer_class = DjoserUserSerializer
    permission_classes = (AuthorOrAdminOrReadOnly,)

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
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
            



