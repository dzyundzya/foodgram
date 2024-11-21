from rest_framework import viewsets

from api.v1_api.permission import AdminOrReadOnly
from .serializers import TagSerializer
from tags.models import Tag


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None
